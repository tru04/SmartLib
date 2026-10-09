from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc, asc

from app.database import get_db
from app import models, schemas
from app.auth import get_current_admin, get_current_active_user, get_optional_current_user
from app.recommender import recommender

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("", response_model=schemas.BookListResponse)
def list_books(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search across title, author, isbn, description"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    available_only: bool = Query(False, description="Filter only available copies"),
    sort_by: str = Query("title", description="Sort by title, author, year, rating, available_copies"),
    sort_dir: str = Query("asc", description="asc or desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100)
):
    query = db.query(models.Book)

    if search:
        search_filter = f"%{search.strip()}%"
        query = query.filter(
            or_(
                models.Book.title.ilike(search_filter),
                models.Book.author.ilike(search_filter),
                models.Book.isbn.ilike(search_filter),
                models.Book.genre.ilike(search_filter),
                models.Book.description.ilike(search_filter)
            )
        )

    if genre and genre.strip() and genre.lower() != "all":
        query = query.filter(models.Book.genre.ilike(genre.strip()))

    if available_only:
        query = query.filter(models.Book.available_copies > 0)

    # Sorting
    if sort_by == "author":
        order_col = models.Book.author
    elif sort_by == "year":
        order_col = models.Book.year
    elif sort_by == "available_copies":
        order_col = models.Book.available_copies
    elif sort_by == "created_at":
        order_col = models.Book.created_at
    else:
        order_col = models.Book.title

    if sort_dir.lower() == "desc":
        query = query.order_by(desc(order_col))
    else:
        query = query.order_by(asc(order_col))

    total = query.count()
    total_pages = max(1, (total + page_size - 1) // page_size)
    books = query.offset((page - 1) * page_size).limit(page_size).all()

    # Calculate average rating for each book
    items = []
    for b in books:
        rating_stats = db.query(
            func.avg(models.Rating.rating).label("avg_rating"),
            func.count(models.Rating.id).label("count")
        ).filter(models.Rating.book_id == b.id).first()
        
        b_dict = {
            "id": b.id,
            "title": b.title,
            "author": b.author,
            "isbn": b.isbn,
            "genre": b.genre,
            "language": b.language,
            "publisher": b.publisher,
            "year": b.year,
            "description": b.description,
            "cover_image": b.cover_image,
            "total_copies": b.total_copies,
            "available_copies": b.available_copies,
            "shelf_location": b.shelf_location,
            "created_at": b.created_at,
            "avg_rating": round(float(rating_stats.avg_rating or 0.0), 1),
            "ratings_count": int(rating_stats.count or 0)
        }
        items.append(schemas.BookResponse(**b_dict))

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


@router.get("/genres", response_model=List[str])
def list_genres(db: Session = Depends(get_db)):
    results = db.query(models.Book.genre).distinct().order_by(models.Book.genre).all()
    return [r[0] for r in results if r[0]]


@router.get("/{book_id}", response_model=schemas.BookDetailResponse)
def get_book_details(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_optional_current_user)
):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Ratings
    ratings = db.query(models.Rating).filter(models.Rating.book_id == book_id).order_by(desc(models.Rating.created_at)).all()
    rating_stats = db.query(
        func.avg(models.Rating.rating).label("avg_rating"),
        func.count(models.Rating.id).label("count")
    ).filter(models.Rating.book_id == book_id).first()

    ratings_list = []
    user_rating_val = None
    for r in ratings:
        ratings_list.append(schemas.RatingResponse(
            id=r.id,
            book_id=r.book_id,
            member_id=r.member_id,
            rating=r.rating,
            review_text=r.review_text,
            created_at=r.created_at,
            member_name=r.member.name if r.member else "Anonymous"
        ))
        if current_user and r.member_id == current_user.id:
            user_rating_val = r.rating

    is_borrowed = False
    is_reserved = False
    if current_user:
        active_loan = db.query(models.Loan).filter(
            models.Loan.book_id == book_id,
            models.Loan.member_id == current_user.id,
            models.Loan.status.in_(["active", "overdue"])
        ).first()
        is_borrowed = bool(active_loan)

        active_res = db.query(models.Reservation).filter(
            models.Reservation.book_id == book_id,
            models.Reservation.member_id == current_user.id,
            models.Reservation.status.in_(["pending", "ready"])
        ).first()
        is_reserved = bool(active_res)

    return schemas.BookDetailResponse(
        id=book.id,
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        genre=book.genre,
        language=book.language,
        publisher=book.publisher,
        year=book.year,
        description=book.description,
        cover_image=book.cover_image,
        total_copies=book.total_copies,
        available_copies=book.available_copies,
        shelf_location=book.shelf_location,
        created_at=book.created_at,
        avg_rating=round(float(rating_stats.avg_rating or 0.0), 1),
        ratings_count=int(rating_stats.count or 0),
        ratings=ratings_list,
        is_currently_borrowed_by_me=is_borrowed,
        has_active_reservation_by_me=is_reserved,
        user_rating=user_rating_val
    )


@router.post("", response_model=schemas.BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(
    book_in: schemas.BookCreate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    existing_isbn = db.query(models.Book).filter(models.Book.isbn == book_in.isbn).first()
    if existing_isbn:
        raise HTTPException(status_code=400, detail="A book with this ISBN already exists")

    book = models.Book(**book_in.dict())
    db.add(book)
    db.commit()
    db.refresh(book)

    # Re-train recommender
    recommender.build_models(db)

    return schemas.BookResponse(
        **book.__dict__,
        avg_rating=0.0,
        ratings_count=0
    )


@router.put("/{book_id}", response_model=schemas.BookResponse)
def update_book(
    book_id: int,
    book_update: schemas.BookUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    update_data = book_update.dict(exclude_unset=True)
    if "isbn" in update_data and update_data["isbn"] != book.isbn:
        exist = db.query(models.Book).filter(models.Book.isbn == update_data["isbn"]).first()
        if exist:
            raise HTTPException(status_code=400, detail="ISBN already in use by another book")

    for key, val in update_data.items():
        setattr(book, key, val)

    db.commit()
    db.refresh(book)
    recommender.build_models(db)

    rating_stats = db.query(
        func.avg(models.Rating.rating).label("avg_rating"),
        func.count(models.Rating.id).label("count")
    ).filter(models.Rating.book_id == book.id).first()

    return schemas.BookResponse(
        **book.__dict__,
        avg_rating=round(float(rating_stats.avg_rating or 0.0), 1),
        ratings_count=int(rating_stats.count or 0)
    )


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Check active loans
    active_loans = db.query(models.Loan).filter(
        models.Loan.book_id == book_id,
        models.Loan.status.in_(["active", "overdue"])
    ).count()
    if active_loans > 0:
        raise HTTPException(status_code=400, detail="Cannot delete book that currently has active loans")

    db.delete(book)
    db.commit()
    recommender.build_models(db)
    return None


@router.post("/{book_id}/rate", response_model=schemas.RatingResponse)
def rate_book(
    book_id: int,
    rating_in: schemas.RatingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Upsert rating
    existing_rating = db.query(models.Rating).filter(
        models.Rating.book_id == book_id,
        models.Rating.member_id == current_user.id
    ).first()

    if existing_rating:
        existing_rating.rating = rating_in.rating
        existing_rating.review_text = rating_in.review_text
        rating_obj = existing_rating
    else:
        rating_obj = models.Rating(
            book_id=book_id,
            member_id=current_user.id,
            rating=rating_in.rating,
            review_text=rating_in.review_text
        )
        db.add(rating_obj)

    db.commit()
    db.refresh(rating_obj)

    # Invalidate recommender matrix to learn from new rating
    recommender.build_models(db)

    return schemas.RatingResponse(
        id=rating_obj.id,
        book_id=rating_obj.book_id,
        member_id=rating_obj.member_id,
        rating=rating_obj.rating,
        review_text=rating_obj.review_text,
        created_at=rating_obj.created_at,
        member_name=current_user.name
    )
