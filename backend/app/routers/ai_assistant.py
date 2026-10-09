import re
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from sklearn.metrics.pairwise import cosine_similarity

from app.database import get_db
from app import models, schemas
from app.auth import get_current_active_user, get_optional_current_user
from app.config import settings
from app.recommender import recommender

router = APIRouter(prefix="/ai", tags=["AI Book Assistant & Semantic Search"])


@router.post("/chat", response_model=schemas.AIChatResponse)
def chat_assistant(
    request: schemas.AIChatRequest,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_optional_current_user)
):
    if not settings.ENABLE_AI_FEATURES:
        raise HTTPException(status_code=400, detail="AI features are disabled by system configuration")

    query = request.query.strip().lower()
    recommender.ensure_trained(db)

    # 1. Check if user is asking for personalized "What should I read next" or general recommendation
    is_recommendation_prompt = any(
        phrase in query for phrase in [
            "what should i read", "recommend", "suggest", "what to read", "next book",
            "what do you suggest", "give me a book", "help me choose"
        ]
    )

    recommended_books = []
    reply = ""

    if is_recommendation_prompt and current_user:
        items = recommender.get_personalized_recommendations(current_user, db, limit=4)
        if items:
            top_titles = [f"**{it['book'].title}** by {it['book'].author} ({it['explanation']})" for it in items]
            reply = (
                f"Based on your library borrowing history and interests, I curated these top recommendations for you:\n\n"
                + "\n".join([f"• {t}" for t in top_titles])
                + "\n\nWould you like more details on any of these titles?"
            )
            for it in items:
                b = it["book"]
                rating_stats = db.query(
                    func.avg(models.Rating.rating).label("avg_rating"),
                    func.count(models.Rating.id).label("count")
                ).filter(models.Rating.book_id == b.id).first()
                recommended_books.append(schemas.BookResponse(
                    **b.__dict__,
                    avg_rating=round(float(rating_stats.avg_rating or 0.0), 1),
                    ratings_count=int(rating_stats.count or 0)
                ))
            return schemas.AIChatResponse(reply=reply, recommended_books=recommended_books)

    # 2. Natural language query matching using TF-IDF feature space
    if recommender.books_df is not None and not recommender.books_df.empty:
        from sklearn.feature_extraction.text import TfidfVectorizer
        tfidf = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        tfidf_matrix = tfidf.fit_transform(recommender.books_df["features"])
        query_vec = tfidf.transform([request.query])
        scores = cosine_similarity(query_vec, tfidf_matrix)[0]

        top_indices = scores.argsort()[::-1]
        matches = []
        for idx in top_indices:
            if scores[idx] > 0.08:
                b_id = recommender.idx_to_id[idx]
                book = db.query(models.Book).filter(models.Book.id == b_id).first()
                if book:
                    matches.append(book)
            if len(matches) >= 3:
                break

        if matches:
            for b in matches:
                rating_stats = db.query(
                    func.avg(models.Rating.rating).label("avg_rating"),
                    func.count(models.Rating.id).label("count")
                ).filter(models.Rating.book_id == b.id).first()
                recommended_books.append(schemas.BookResponse(
                    **b.__dict__,
                    avg_rating=round(float(rating_stats.avg_rating or 0.0), 1),
                    ratings_count=int(rating_stats.count or 0)
                ))

            reply = (
                f"I found {len(matches)} fantastic books matching your description '{request.query}':\n\n"
                + "\n".join([f"• **{b.title}** ({b.genre}) by {b.author}: {b.description[:120]}..." for b in matches])
                + "\n\nYou can click on any card to reserve or view shelf details!"
            )
            return schemas.AIChatResponse(reply=reply, recommended_books=recommended_books)

    # Fallback conversational response
    popular_books = db.query(models.Book).limit(3).all()
    for b in popular_books:
        rating_stats = db.query(
            func.avg(models.Rating.rating).label("avg_rating"),
            func.count(models.Rating.id).label("count")
        ).filter(models.Rating.book_id == b.id).first()
        recommended_books.append(schemas.BookResponse(
            **b.__dict__,
            avg_rating=round(float(rating_stats.avg_rating or 0.0), 1),
            ratings_count=int(rating_stats.count or 0)
        ))

    reply = (
        f"I'd love to help you find your next great read! You can ask me for specific genres, themes (like 'philosophical sci-fi' or 'mindset & productivity'), or check out our most popular titles below."
    )
    return schemas.AIChatResponse(reply=reply, recommended_books=recommended_books)


@router.get("/nl-search", response_model=List[schemas.BookResponse])
def natural_language_search(
    q: str = Query(..., description="Natural language search query like 'dystopian society with surveillance'"),
    limit: int = Query(8, ge=1, le=20),
    db: Session = Depends(get_db)
):
    if not settings.ENABLE_AI_FEATURES:
        raise HTTPException(status_code=400, detail="AI features disabled")

    recommender.ensure_trained(db)
    if recommender.books_df is None or recommender.books_df.empty:
        return []

    from sklearn.feature_extraction.text import TfidfVectorizer
    tfidf = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    tfidf_matrix = tfidf.fit_transform(recommender.books_df["features"])
    query_vec = tfidf.transform([q])
    scores = cosine_similarity(query_vec, tfidf_matrix)[0]

    top_indices = scores.argsort()[::-1]
    results = []
    for idx in top_indices:
        if scores[idx] <= 0.02:
            break
        b_id = recommender.idx_to_id[idx]
        b = db.query(models.Book).filter(models.Book.id == b_id).first()
        if b:
            rating_stats = db.query(
                func.avg(models.Rating.rating).label("avg_rating"),
                func.count(models.Rating.id).label("count")
            ).filter(models.Rating.book_id == b.id).first()
            results.append(schemas.BookResponse(
                **b.__dict__,
                avg_rating=round(float(rating_stats.avg_rating or 0.0), 1),
                ratings_count=int(rating_stats.count or 0)
            ))
        if len(results) >= limit:
            break

    return results
