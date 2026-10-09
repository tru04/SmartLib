from datetime import datetime, timedelta
from typing import Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app import models
from app.config import settings
from app.recommender import recommender


class LoanService:
    @staticmethod
    def calculate_fine(due_date: datetime, return_date: Optional[datetime] = None) -> float:
        cutoff = return_date if return_date else datetime.utcnow()
        if cutoff <= due_date:
            return 0.0
        delta = cutoff - due_date
        # Every 24h period or partial day is counted
        days_overdue = max(1, delta.days if delta.seconds == 0 else delta.days + 1)
        return float(days_overdue * settings.FINE_RATE_PER_DAY)

    @staticmethod
    def update_overdue_statuses(db: Session):
        """
        Scans all active loans, updates status to overdue and updates fines.
        Also triggers notification alerts for due soon and overdue loans.
        """
        now = datetime.utcnow()
        active_loans = db.query(models.Loan).filter(models.Loan.status.in_(["active", "overdue"])).all()
        for loan in active_loans:
            if now > loan.due_date:
                loan.status = "overdue"
                loan.fine_amount = LoanService.calculate_fine(loan.due_date, None)
                
                # Check if overdue notification already sent today
                existing_notif = db.query(models.Notification).filter(
                    models.Notification.user_id == loan.member_id,
                    models.Notification.type == "overdue",
                    models.Notification.created_at >= now - timedelta(days=1)
                ).first()
                if not existing_notif:
                    db.add(models.Notification(
                        user_id=loan.member_id,
                        title="Book Overdue Alert",
                        message=f"'{loan.book.title}' is overdue. Outstanding fine: Rs. {loan.fine_amount:.2f}.",
                        type="overdue"
                    ))
            elif loan.due_date - now <= timedelta(days=2):
                # Due soon notification
                existing_notif = db.query(models.Notification).filter(
                    models.Notification.user_id == loan.member_id,
                    models.Notification.type == "due_soon",
                    models.Notification.created_at >= now - timedelta(days=1)
                ).first()
                if not existing_notif:
                    db.add(models.Notification(
                        user_id=loan.member_id,
                        title="Due Soon Reminder",
                        message=f"'{loan.book.title}' is due on {loan.due_date.strftime('%b %d, %Y')}. Please return or renew.",
                        type="due_soon"
                    ))
        db.commit()

    @staticmethod
    def issue_book(db: Session, book_id: int, member_id: int) -> models.Loan:
        member = db.query(models.User).filter(models.User.id == member_id).first()
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        if member.membership_status != "active":
            raise HTTPException(status_code=400, detail="Member account is not active")

        # Check borrow limit
        active_loans_count = db.query(models.Loan).filter(
            models.Loan.member_id == member_id,
            models.Loan.status.in_(["active", "overdue"])
        ).count()
        if active_loans_count >= member.borrow_limit:
            raise HTTPException(
                status_code=400,
                detail=f"Member has reached their maximum borrowing limit of {member.borrow_limit} books"
            )

        # Check if already has an active loan of this book
        existing_loan = db.query(models.Loan).filter(
            models.Loan.member_id == member_id,
            models.Loan.book_id == book_id,
            models.Loan.status.in_(["active", "overdue"])
        ).first()
        if existing_loan:
            raise HTTPException(status_code=400, detail="Member currently has an active loan for this book")

        book = db.query(models.Book).filter(models.Book.id == book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        if book.available_copies <= 0:
            raise HTTPException(status_code=400, detail="No copies available for issue. Consider placing a reservation.")

        # Check if there is a ready reservation for another member
        ready_res = db.query(models.Reservation).filter(
            models.Reservation.book_id == book_id,
            models.Reservation.status == "ready"
        ).first()
        if ready_res and ready_res.member_id != member_id:
            # Check if reservation is still valid
            if ready_res.ready_until and ready_res.ready_until > datetime.utcnow():
                raise HTTPException(
                    status_code=400,
                    detail=f"Available copy is currently held for member reservation (Hold valid until {ready_res.ready_until.strftime('%b %d')})"
                )

        # If this member had a reservation, fulfill it
        member_res = db.query(models.Reservation).filter(
            models.Reservation.book_id == book_id,
            models.Reservation.member_id == member_id,
            models.Reservation.status.in_(["pending", "ready"])
        ).first()
        if member_res:
            member_res.status = "fulfilled"

        now = datetime.utcnow()
        due = now + timedelta(days=settings.LOAN_PERIOD_DAYS)
        book.available_copies -= 1

        loan = models.Loan(
            book_id=book_id,
            member_id=member_id,
            issue_date=now,
            due_date=due,
            status="active",
            renewal_count=0,
            fine_amount=0.0,
            fine_paid=False
        )
        db.add(loan)
        db.commit()
        db.refresh(loan)

        # Retrain recommender on new interactions
        recommender.build_models(db)
        return loan

    @staticmethod
    def renew_book(db: Session, loan_id: int, member_id: Optional[int] = None) -> models.Loan:
        loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
        if not loan:
            raise HTTPException(status_code=404, detail="Loan record not found")
        if member_id and loan.member_id != member_id:
            raise HTTPException(status_code=403, detail="Cannot renew another member's loan")
        if loan.status != "active":
            raise HTTPException(status_code=400, detail="Only active loans can be renewed. Overdue loans must be returned.")
        if loan.renewal_count >= settings.MAX_RENEWALS:
            raise HTTPException(status_code=400, detail=f"Maximum renewal limit of {settings.MAX_RENEWALS} reached")

        # Check pending reservations on this book - FIFO fairness rule
        pending_res_count = db.query(models.Reservation).filter(
            models.Reservation.book_id == loan.book_id,
            models.Reservation.status == "pending"
        ).count()
        if pending_res_count > 0:
            raise HTTPException(
                status_code=400,
                detail="Renewal unavailable: another reader has reserved this book"
            )

        loan.renewal_count += 1
        loan.due_date = loan.due_date + timedelta(days=settings.LOAN_PERIOD_DAYS)
        db.commit()
        db.refresh(loan)
        return loan

    @staticmethod
    def return_book(db: Session, loan_id: int, fine_paid: bool = False) -> models.Loan:
        loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
        if not loan:
            raise HTTPException(status_code=404, detail="Loan record not found")
        if loan.status == "returned":
            raise HTTPException(status_code=400, detail="Book has already been returned")

        now = datetime.utcnow()
        fine = LoanService.calculate_fine(loan.due_date, now)

        loan.return_date = now
        loan.status = "returned"
        loan.fine_amount = fine
        loan.fine_paid = fine_paid or (fine == 0.0)

        # Increment book inventory
        book = loan.book
        book.available_copies = min(book.total_copies, book.available_copies + 1)

        # FIFO reservation fulfillment check
        earliest_res = db.query(models.Reservation).filter(
            models.Reservation.book_id == loan.book_id,
            models.Reservation.status == "pending"
        ).order_by(models.Reservation.reserved_at.asc()).first()

        if earliest_res:
            earliest_res.status = "ready"
            earliest_res.ready_until = now + timedelta(hours=48)
            # Notify member
            db.add(models.Notification(
                user_id=earliest_res.member_id,
                title="Reserved Book Ready for Pickup",
                message=f"Great news! Your reserved book '{book.title}' is now available. We will hold it for 48 hours.",
                type="reservation_ready"
            ))

        db.commit()
        db.refresh(loan)

        # Re-build recommendation weights
        recommender.build_models(db)
        return loan

    @staticmethod
    def settle_fine(db: Session, loan_id: int) -> models.Loan:
        loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
        if not loan:
            raise HTTPException(status_code=404, detail="Loan record not found")
        loan.fine_paid = True
        db.commit()
        db.refresh(loan)
        return loan
