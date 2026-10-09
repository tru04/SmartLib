from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app import models, schemas
from app.auth import get_current_active_user, get_current_admin
from app.services.loan_service import LoanService

router = APIRouter(prefix="/loans", tags=["Loans & Circulation"])


@router.post("/issue", response_model=schemas.LoanResponse, status_code=status.HTTP_201_CREATED)
def issue_book(
    loan_in: schemas.LoanCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # If standard member, they can only borrow for themselves
    target_member_id = loan_in.member_id
    if current_user.role != "admin" and current_user.id != target_member_id:
        target_member_id = current_user.id

    loan = LoanService.issue_book(db, loan_in.book_id, target_member_id)
    return loan


@router.post("/{loan_id}/renew", response_model=schemas.LoanResponse)
def renew_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    member_id_filter = None if current_user.role == "admin" else current_user.id
    loan = LoanService.renew_book(db, loan_id, member_id=member_id_filter)
    return loan


@router.post("/{loan_id}/return", response_model=schemas.LoanResponse)
def return_loan(
    loan_id: int,
    fine_paid: bool = Query(False),
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    loan = LoanService.return_book(db, loan_id, fine_paid=fine_paid)
    return loan


@router.post("/{loan_id}/pay-fine", response_model=schemas.LoanResponse)
def pay_loan_fine(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    if current_user.role != "admin" and loan.member_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    return LoanService.settle_fine(db, loan_id)


@router.get("/my", response_model=List[schemas.LoanResponse])
def get_my_loans(
    status_filter: Optional[str] = Query(None, description="active, overdue, returned"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Refresh overdue states before returning
    LoanService.update_overdue_statuses(db)

    query = db.query(models.Loan).filter(models.Loan.member_id == current_user.id)
    if status_filter:
        query = query.filter(models.Loan.status == status_filter)

    loans = query.order_by(desc(models.Loan.issue_date)).all()
    return loans


@router.get("/all", response_model=List[schemas.LoanResponse])
def get_all_loans(
    status_filter: Optional[str] = Query(None),
    member_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    LoanService.update_overdue_statuses(db)

    query = db.query(models.Loan)
    if status_filter:
        query = query.filter(models.Loan.status == status_filter)
    if member_id:
        query = query.filter(models.Loan.member_id == member_id)

    loans = query.order_by(desc(models.Loan.issue_date)).all()
    return loans
