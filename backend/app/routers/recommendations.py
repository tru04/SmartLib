from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app import models, schemas
from app.auth import get_current_active_user, get_current_admin
from app.recommender import recommender

router = APIRouter(prefix="/recommendations", tags=["Smart Recommendations"])


@router.get("/me", response_model=schemas.RecommendationsResponse)
def get_my_recommendations(
    limit: int = Query(8, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # 1. Personalized recommendations
    personalized = recommender.get_personalized_recommendations(current_user, db, limit=limit)

    recommended_items = []
    for item in personalized:
        b = item["book"]
        rating_stats = db.query(
            func.avg(models.Rating.rating).label("avg_rating"),
            func.count(models.Rating.id).label("count")
        ).filter(models.Rating.book_id == b.id).first()

        book_resp = schemas.BookResponse(
            **b.__dict__,
            avg_rating=round(float(rating_stats.avg_rating or 0.0), 1),
            ratings_count=int(rating_stats.count or 0)
        )
        recommended_items.append(schemas.RecommendedBookItem(
            book=book_resp,
            score=item["score"],
            explanation=item["explanation"]
        ))

    # 2. Trending / Most borrowed books
    top_loans = db.query(
        models.Loan.book_id,
        func.count(models.Loan.id).label("loans_cnt")
    ).group_by(models.Loan.book_id).order_by(func.count(models.Loan.id).desc()).limit(6).all()

    trending_books = []
    for t in top_loans:
        b = db.query(models.Book).filter(models.Book.id == t[0]).first()
        if b:
            rating_stats = db.query(
                func.avg(models.Rating.rating).label("avg_rating"),
                func.count(models.Rating.id).label("count")
            ).filter(models.Rating.book_id == b.id).first()
            trending_books.append(schemas.BookResponse(
                **b.__dict__,
                avg_rating=round(float(rating_stats.avg_rating or 0.0), 1),
                ratings_count=int(rating_stats.count or 0)
            ))

    # If few loans, fallback to highest rated
    if len(trending_books) < 4:
        top_rated = db.query(models.Book).limit(6).all()
        for b in top_rated:
            if not any(tb.id == b.id for tb in trending_books):
                rating_stats = db.query(
                    func.avg(models.Rating.rating).label("avg_rating"),
                    func.count(models.Rating.id).label("count")
                ).filter(models.Rating.book_id == b.id).first()
                trending_books.append(schemas.BookResponse(
                    **b.__dict__,
                    avg_rating=round(float(rating_stats.avg_rating or 0.0), 1),
                    ratings_count=int(rating_stats.count or 0)
                ))

    # 3. Top in Favorite Genres
    fav_genres = [g.strip() for g in (current_user.favorite_genres or "").split(",") if g.strip()]
    top_genre_books = []
    if fav_genres:
        query = db.query(models.Book).filter(models.Book.genre.in_(fav_genres)).limit(6).all()
        for b in query:
            rating_stats = db.query(
                func.avg(models.Rating.rating).label("avg_rating"),
                func.count(models.Rating.id).label("count")
            ).filter(models.Rating.book_id == b.id).first()
            top_genre_books.append(schemas.BookResponse(
                **b.__dict__,
                avg_rating=round(float(rating_stats.avg_rating or 0.0), 1),
                ratings_count=int(rating_stats.count or 0)
            ))

    return schemas.RecommendationsResponse(
        recommended_for_you=recommended_items,
        trending_popular=trending_books,
        top_by_favorite_genres=top_genre_books
    )


@router.get("/books/{book_id}/similar", response_model=List[schemas.BookResponse])
def get_similar_books(
    book_id: int,
    limit: int = Query(6, ge=1, le=12),
    db: Session = Depends(get_db)
):
    similars = recommender.get_similar_books(book_id, db, limit=limit)
    results = []
    for b, _ in similars:
        rating_stats = db.query(
            func.avg(models.Rating.rating).label("avg_rating"),
            func.count(models.Rating.id).label("count")
        ).filter(models.Rating.book_id == b.id).first()
        results.append(schemas.BookResponse(
            **b.__dict__,
            avg_rating=round(float(rating_stats.avg_rating or 0.0), 1),
            ratings_count=int(rating_stats.count or 0)
        ))
    return results


@router.get("/books/{book_id}/readers-also-borrowed", response_model=List[schemas.BookResponse])
def get_readers_also_borrowed(
    book_id: int,
    limit: int = Query(6, ge=1, le=12),
    db: Session = Depends(get_db)
):
    similars = recommender.get_collaborative_similar_books(book_id, db, limit=limit)
    results = []
    for b, _ in similars:
        rating_stats = db.query(
            func.avg(models.Rating.rating).label("avg_rating"),
            func.count(models.Rating.id).label("count")
        ).filter(models.Rating.book_id == b.id).first()
        results.append(schemas.BookResponse(
            **b.__dict__,
            avg_rating=round(float(rating_stats.avg_rating or 0.0), 1),
            ratings_count=int(rating_stats.count or 0)
        ))
    return results


@router.post("/rebuild")
def rebuild_matrix(
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    success = recommender.build_models(db)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to rebuild recommendation matrices")
    return {"message": "Recommender matrices successfully rebuilt"}
