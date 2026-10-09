from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app import models, schemas
from app.auth import get_current_active_user, get_current_admin
from app.services.reservation_service import ReservationService

router = APIRouter(prefix="/reservations", tags=["Reservations"])


@router.post("", response_model=schemas.ReservationResponse, status_code=status.HTTP_201_CREATED)
def make_reservation(
    res_in: schemas.ReservationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    res = ReservationService.create_reservation(db, res_in.book_id, current_user.id)
    pos = ReservationService.get_queue_position(db, res)
    res_dict = schemas.ReservationResponse.from_orm(res)
    res_dict.queue_position = pos
    return res_dict


@router.delete("/{reservation_id}", response_model=schemas.ReservationResponse)
def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    member_id_filter = None if current_user.role == "admin" else current_user.id
    res = ReservationService.cancel_reservation(db, reservation_id, member_id_filter)
    return res


@router.get("/my", response_model=List[schemas.ReservationResponse])
def get_my_reservations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    reservations = db.query(models.Reservation).filter(
        models.Reservation.member_id == current_user.id
    ).order_by(desc(models.Reservation.reserved_at)).all()

    results = []
    for r in reservations:
        r_resp = schemas.ReservationResponse.from_orm(r)
        r_resp.queue_position = ReservationService.get_queue_position(db, r)
        results.append(r_resp)
    return results


@router.get("/all", response_model=List[schemas.ReservationResponse])
def get_all_reservations(
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    reservations = db.query(models.Reservation).order_by(desc(models.Reservation.reserved_at)).all()
    results = []
    for r in reservations:
        r_resp = schemas.ReservationResponse.from_orm(r)
        r_resp.queue_position = ReservationService.get_queue_position(db, r)
        results.append(r_resp)
    return results
