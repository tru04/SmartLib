from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models


class ReservationService:
    @staticmethod
    def create_reservation(db: Session, book_id: int, member_id: int) -> models.Reservation:
        book = db.query(models.Book).filter(models.Book.id == book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        # Check existing active reservation by this user
        existing_res = db.query(models.Reservation).filter(
            models.Reservation.book_id == book_id,
            models.Reservation.member_id == member_id,
            models.Reservation.status.in_(["pending", "ready"])
        ).first()
        if existing_res:
            raise HTTPException(status_code=400, detail="You already have an active reservation for this book")

        # Check if user already holds active loan
        existing_loan = db.query(models.Loan).filter(
            models.Loan.book_id == book_id,
            models.Loan.member_id == member_id,
            models.Loan.status.in_(["active", "overdue"])
        ).first()
        if existing_loan:
            raise HTTPException(status_code=400, detail="You already currently borrow this book")

        # Create reservation
        reservation = models.Reservation(
            book_id=book_id,
            member_id=member_id,
            reserved_at=datetime.utcnow(),
            status="pending"
        )
        db.add(reservation)
        db.commit()
        db.refresh(reservation)
        return reservation

    @staticmethod
    def cancel_reservation(db: Session, reservation_id: int, member_id: Optional[int] = None) -> models.Reservation:
        res = db.query(models.Reservation).filter(models.Reservation.id == reservation_id).first()
        if not res:
            raise HTTPException(status_code=404, detail="Reservation not found")
        if member_id and res.member_id != member_id:
            raise HTTPException(status_code=403, detail="Not authorized to cancel this reservation")

        res.status = "cancelled"
        db.commit()
        db.refresh(res)
        return res

    @staticmethod
    def get_queue_position(db: Session, reservation: models.Reservation) -> int:
        if reservation.status != "pending":
            return 1
        pos = db.query(models.Reservation).filter(
            models.Reservation.book_id == reservation.book_id,
            models.Reservation.status == "pending",
            models.Reservation.reserved_at <= reservation.reserved_at
        ).count()
        return max(1, pos)
