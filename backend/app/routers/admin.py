from datetime import datetime, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database import get_db
from app import models, schemas
from app.auth import get_current_admin
from app.services.loan_service import LoanService

router = APIRouter(prefix="/admin", tags=["Admin Analytics & Dashboard"])


@router.get("/stats", response_model=schemas.AdminDashboardStats)
def get_admin_dashboard_stats(
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    LoanService.update_overdue_statuses(db)

    total_books = db.query(models.Book).count()
    total_members = db.query(models.User).filter(models.User.role == "member").count()
    active_loans = db.query(models.Loan).filter(models.Loan.status == "active").count()
    overdue_loans = db.query(models.Loan).filter(models.Loan.status == "overdue").count()

    total_fines_collected = db.query(func.sum(models.Loan.fine_amount)).filter(
        models.Loan.fine_paid == True
    ).scalar() or 0.0

    total_pending_fines = db.query(func.sum(models.Loan.fine_amount)).filter(
        models.Loan.fine_paid == False,
        models.Loan.fine_amount > 0
    ).scalar() or 0.0

    total_reservations = db.query(models.Reservation).filter(
        models.Reservation.status.in_(["pending", "ready"])
    ).count()

    # Loans per month (last 6 months)
    loans_per_month = []
    now = datetime.utcnow()
    for i in range(5, -1, -1):
        month_start = (now.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1)
        month_label = month_start.strftime("%b %Y")
        
        count = db.query(models.Loan).filter(
            models.Loan.issue_date >= month_start,
            models.Loan.issue_date < month_end
        ).count()
        loans_per_month.append({"month": month_label, "loans": count})

    # Genre distribution
    genres_data = db.query(
        models.Book.genre,
        func.count(models.Book.id).label("count")
    ).group_by(models.Book.genre).order_by(desc("count")).limit(8).all()
    genres_distribution = [{"genre": g[0], "count": g[1]} for g in genres_data]

    # Top borrowed books
    top_books_data = db.query(
        models.Loan.book_id,
        func.count(models.Loan.id).label("loans_count")
    ).group_by(models.Loan.book_id).order_by(desc("loans_count")).limit(5).all()

    top_borrowed_books = []
    for b_id, cnt in top_books_data:
        book = db.query(models.Book).filter(models.Book.id == b_id).first()
        if book:
            top_borrowed_books.append({
                "book_id": book.id,
                "title": book.title,
                "author": book.author,
                "genre": book.genre,
                "cover_image": book.cover_image,
                "borrow_count": cnt
            })

    # Recent activities
    recent_loans = db.query(models.Loan).order_by(desc(models.Loan.issue_date)).limit(6).all()
    recent_activities = []
    for l in recent_loans:
        recent_activities.append({
            "id": l.id,
            "type": "loan",
            "member_name": l.member.name if l.member else "Member",
            "book_title": l.book.title if l.book else "Book",
            "date": l.issue_date.isoformat(),
            "status": l.status,
            "fine": l.fine_amount
        })

    return schemas.AdminDashboardStats(
        total_books=total_books,
        total_members=total_members,
        active_loans=active_loans,
        overdue_loans=overdue_loans,
        total_fines_collected=round(float(total_fines_collected), 2),
        total_pending_fines=round(float(total_pending_fines), 2),
        total_reservations=total_reservations,
        loans_per_month=loans_per_month,
        genres_distribution=genres_distribution,
        top_borrowed_books=top_borrowed_books,
        recent_activities=recent_activities
    )
