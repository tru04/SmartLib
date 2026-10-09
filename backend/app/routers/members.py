from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app import models, schemas
from app.auth import get_current_admin, get_current_active_user

from app.services.loan_service import LoanService

router = APIRouter(prefix="/members", tags=["Members Management"])


class MemberAdminSummary(schemas.UserResponse):
    active_loans_count: int
    overdue_loans_count: int
    unpaid_fines_total: float
    total_borrows_count: int


@router.get("/dashboard", response_model=schemas.MemberDashboardStats)
def get_member_dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    LoanService.update_overdue_statuses(db)

    active_loans = db.query(models.Loan).filter(
        models.Loan.member_id == current_user.id,
        models.Loan.status.in_(["active", "overdue"])
    ).order_by(models.Loan.due_date.asc()).all()

    active_loans_resp = []
    for l in active_loans:
        active_loans_resp.append(schemas.LoanResponse.from_orm(l))

    overdue_count = sum(1 for l in active_loans if l.status == "overdue")

    unpaid_fines_sum = db.query(func.sum(models.Loan.fine_amount)).filter(
        models.Loan.member_id == current_user.id,
        models.Loan.fine_paid == False,
        models.Loan.fine_amount > 0
    ).scalar() or 0.0

    from app.services.reservation_service import ReservationService
    reservations = db.query(models.Reservation).filter(
        models.Reservation.member_id == current_user.id,
        models.Reservation.status.in_(["pending", "ready"])
    ).order_by(models.Reservation.reserved_at.desc()).all()

    active_res_resp = []
    for r in reservations:
        r_dict = schemas.ReservationResponse.from_orm(r)
        r_dict.queue_position = ReservationService.get_queue_position(db, r)
        active_res_resp.append(r_dict)

    return schemas.MemberDashboardStats(
        current_loans_count=len(active_loans),
        borrow_limit=current_user.borrow_limit,
        overdue_loans_count=overdue_count,
        total_pending_fines=round(float(unpaid_fines_sum), 2),
        active_reservations_count=len(reservations),
        active_loans=active_loans_resp,
        active_reservations=active_res_resp
    )


@router.get("", response_model=List[MemberAdminSummary])
def list_members(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
    admin: models.User = Depends(get_current_admin)
):
    query = db.query(models.User)
    if search:
        search_filter = f"%{search.strip()}%"
        query = query.filter(
            (models.User.name.ilike(search_filter)) | (models.User.email.ilike(search_filter))
        )
    if status_filter:
        query = query.filter(models.User.membership_status == status_filter)

    users = query.order_by(models.User.created_at.desc()).all()

    results = []
    for u in users:
        active_cnt = db.query(models.Loan).filter(
            models.Loan.member_id == u.id,
            models.Loan.status == "active"
        ).count()
        overdue_cnt = db.query(models.Loan).filter(
            models.Loan.member_id == u.id,
            models.Loan.status == "overdue"
        ).count()
        total_borrows = db.query(models.Loan).filter(models.Loan.member_id == u.id).count()

        fines_sum = db.query(func.sum(models.Loan.fine_amount)).filter(
            models.Loan.member_id == u.id,
            models.Loan.fine_paid == False,
            models.Loan.fine_amount > 0
        ).scalar() or 0.0

        results.append(MemberAdminSummary(
            id=u.id,
            name=u.name,
            email=u.email,
            role=u.role,
            membership_status=u.membership_status,
            borrow_limit=u.borrow_limit,
            favorite_genres=u.favorite_genres,
            created_at=u.created_at,
            active_loans_count=active_cnt,
            overdue_loans_count=overdue_cnt,
            unpaid_fines_total=round(float(fines_sum), 2),
            total_borrows_count=total_borrows
        ))

    return results


@router.get("/{member_id}", response_model=MemberAdminSummary)
def get_member(
    member_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    u = db.query(models.User).filter(models.User.id == member_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Member not found")

    active_cnt = db.query(models.Loan).filter(
        models.Loan.member_id == u.id,
        models.Loan.status == "active"
    ).count()
    overdue_cnt = db.query(models.Loan).filter(
        models.Loan.member_id == u.id,
        models.Loan.status == "overdue"
    ).count()
    total_borrows = db.query(models.Loan).filter(models.Loan.member_id == u.id).count()
    fines_sum = db.query(func.sum(models.Loan.fine_amount)).filter(
        models.Loan.member_id == u.id,
        models.Loan.fine_paid == False
    ).scalar() or 0.0

    return MemberAdminSummary(
        id=u.id,
        name=u.name,
        email=u.email,
        role=u.role,
        membership_status=u.membership_status,
        borrow_limit=u.borrow_limit,
        favorite_genres=u.favorite_genres,
        created_at=u.created_at,
        active_loans_count=active_cnt,
        overdue_loans_count=overdue_cnt,
        unpaid_fines_total=round(float(fines_sum), 2),
        total_borrows_count=total_borrows
    )


@router.put("/{member_id}", response_model=schemas.UserResponse)
def update_member(
    member_id: int,
    update_data: schemas.UserUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    u = db.query(models.User).filter(models.User.id == member_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Member not found")

    if update_data.membership_status is not None:
        u.membership_status = update_data.membership_status
    if update_data.borrow_limit is not None:
        u.borrow_limit = update_data.borrow_limit
    if update_data.name is not None:
        u.name = update_data.name

    db.commit()
    db.refresh(u)
    return u


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(
    member_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    u = db.query(models.User).filter(models.User.id == member_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Member not found")

    active_loans = db.query(models.Loan).filter(
        models.Loan.member_id == u.id,
        models.Loan.status.in_(["active", "overdue"])
    ).count()
    if active_loans > 0:
        raise HTTPException(status_code=400, detail="Cannot delete member who currently has active or overdue loans")

    db.delete(u)
    db.commit()
    return None
