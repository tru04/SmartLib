from datetime import datetime
import logging
from typing import List, Dict, Tuple, Optional, Set
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session
from sqlalchemy import func

from app import models

logger = logging.getLogger(__name__)


class RecommenderEngine:
    def __init__(self):
        self._is_trained = False
        self._last_trained_at: Optional[datetime] = None
        self.books_df: Optional[pd.DataFrame] = None
        self.id_to_idx: Dict[int, int] = {}
        self.idx_to_id: Dict[int, int] = {}
        self.content_sim_matrix: Optional[np.ndarray] = None
        self.collab_sim_matrix: Optional[np.ndarray] = None
        self.book_lookup: Dict[int, models.Book] = {}

    def build_models(self, db: Session) -> bool:
        """
        Builds both Content-Based (TF-IDF) and Collaborative (Item-Item) similarity matrices.
        """
        try:
            books = db.query(models.Book).all()
            if not books:
                logger.warning("No books in database to train recommender.")
                return False

            self.book_lookup = {b.id: b for b in books}
            data = []
            for b in books:
                # Combine textual features: title, author, genre, description, publisher
                features = f"{b.title} {b.title} {b.author} {b.author} {b.genre} {b.genre} {b.description} {b.publisher}"
                data.append({
                    "id": b.id,
                    "title": b.title,
                    "author": b.author,
                    "genre": b.genre,
                    "features": features
                })

            df = pd.DataFrame(data)
            self.books_df = df
            self.id_to_idx = {row["id"]: i for i, row in df.iterrows()}
            self.idx_to_id = {i: row["id"] for i, row in df.iterrows()}

            # 1. Content-based TF-IDF Matrix
            tfidf = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)
            tfidf_matrix = tfidf.fit_transform(df["features"])
            self.content_sim_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

            # 2. Collaborative Filtering (Item-Item)
            # Fetch borrowing history and ratings
            loans = db.query(models.Loan.member_id, models.Loan.book_id).all()
            ratings = db.query(models.Rating.member_id, models.Rating.book_id, models.Rating.rating).all()

            user_ids = list(set([l[0] for l in loans] + [r[0] for r in ratings]))
            n_users = len(user_ids)
            n_items = len(books)

            if n_users > 0 and n_items > 0:
                user_id_to_idx = {uid: i for i, uid in enumerate(user_ids)}
                ui_matrix = np.zeros((n_items, n_users), dtype=np.float32)

                # Base score for borrowing: 3.5
                for uid, bid in loans:
                    if bid in self.id_to_idx and uid in user_id_to_idx:
                        b_idx = self.id_to_idx[bid]
                        u_idx = user_id_to_idx[uid]
                        ui_matrix[b_idx, u_idx] = max(ui_matrix[b_idx, u_idx], 3.5)

                # Explicit ratings override with actual 1-5 score
                for uid, bid, score in ratings:
                    if bid in self.id_to_idx and uid in user_id_to_idx:
                        b_idx = self.id_to_idx[bid]
                        u_idx = user_id_to_idx[uid]
                        ui_matrix[b_idx, u_idx] = float(score)

                # Compute item-item cosine similarity
                norms = np.linalg.norm(ui_matrix, axis=1, keepdims=True)
                norms[norms == 0] = 1.0  # avoid division by zero
                normalized_ui = ui_matrix / norms
                self.collab_sim_matrix = np.dot(normalized_ui, normalized_ui.T)
            else:
                self.collab_sim_matrix = np.zeros((n_items, n_items), dtype=np.float32)

            self._is_trained = True
            self._last_trained_at = datetime.utcnow()
            logger.info("Recommender models successfully trained.")
            return True
        except Exception as e:
            logger.error(f"Error training recommender: {e}")
            return False

    def ensure_trained(self, db: Session):
        if not self._is_trained:
            self.build_models(db)

    def get_similar_books(self, book_id: int, db: Session, limit: int = 6) -> List[Tuple[models.Book, float]]:
        """
        Returns content-similar books for the Book Details page.
        """
        self.ensure_trained(db)
        if not self._is_trained or book_id not in self.id_to_idx or self.content_sim_matrix is None:
            # Fallback to same-genre books
            book = db.query(models.Book).filter(models.Book.id == book_id).first()
            if not book:
                return []
            fallback = db.query(models.Book).filter(
                models.Book.genre == book.genre,
                models.Book.id != book_id
            ).limit(limit).all()
            return [(b, 0.5) for b in fallback]

        idx = self.id_to_idx[book_id]
        scores = list(enumerate(self.content_sim_matrix[idx]))
        # Sort by similarity descending, exclude self (index idx)
        scores = sorted(scores, key=lambda x: x[1], reverse=True)

        results = []
        for i, score in scores:
            if i == idx:
                continue
            b_id = self.idx_to_id[i]
            book_obj = db.query(models.Book).filter(models.Book.id == b_id).first()
            if book_obj:
                results.append((book_obj, float(score)))
            if len(results) >= limit:
                break

        return results

    def get_collaborative_similar_books(self, book_id: int, db: Session, limit: int = 6) -> List[Tuple[models.Book, float]]:
        """
        Returns "Readers also borrowed" books based on collaborative item-item matrix.
        """
        self.ensure_trained(db)
        if not self._is_trained or book_id not in self.id_to_idx or self.collab_sim_matrix is None:
            return self.get_similar_books(book_id, db, limit)

        idx = self.id_to_idx[book_id]
        scores = list(enumerate(self.collab_sim_matrix[idx]))
        scores = sorted(scores, key=lambda x: x[1], reverse=True)

        results = []
        for i, score in scores:
            if i == idx:
                continue
            if score <= 0.05:  # Not enough collaborative correlation
                continue
            b_id = self.idx_to_id[i]
            book_obj = db.query(models.Book).filter(models.Book.id == b_id).first()
            if book_obj:
                results.append((book_obj, float(score)))
            if len(results) >= limit:
                break

        # If sparse collaborative results, fill with content-similar books
        if len(results) < limit:
            content_results = self.get_similar_books(book_id, db, limit=limit)
            seen_ids = {b.id for b, _ in results}
            for b, s in content_results:
                if b.id not in seen_ids and b.id != book_id:
                    results.append((b, float(s * 0.8)))
                    seen_ids.add(b.id)
                if len(results) >= limit:
                    break

        return results

    def get_personalized_recommendations(
        self, user: models.User, db: Session, limit: int = 8
    ) -> List[Dict]:
        """
        Blended personalized recommendations:
        - Content similarity to user's read/rated books
        - Collaborative filtering item affinities
        - Member favorite genres / authors
        - Cold-start handling for new members
        - Explanation strings ("Because you read...", "Popular in Sci-Fi...")
        """
        self.ensure_trained(db)

        # 1. Gather books user has already read or borrowed
        user_loans = db.query(models.Loan).filter(models.Loan.member_id == user.id).all()
        user_ratings = db.query(models.Rating).filter(models.Rating.member_id == user.id).all()

        borrowed_book_ids = {l.book_id for l in user_loans}
        rated_book_ids = {r.book_id for r in user_ratings}
        exclude_ids = borrowed_book_ids.union(rated_book_ids)

        all_books = db.query(models.Book).all()
        candidate_books = [b for b in all_books if b.id not in exclude_ids]

        # Calculate average ratings and popularity across catalog
        ratings_agg = db.query(
            models.Rating.book_id,
            func.avg(models.Rating.rating).label("avg_rating"),
            func.count(models.Rating.id).label("count")
        ).group_by(models.Rating.book_id).all()
        avg_rating_map = {row.book_id: float(row.avg_rating) for row in ratings_agg}
        rating_count_map = {row.book_id: int(row.count) for row in ratings_agg}

        loan_counts = db.query(
            models.Loan.book_id,
            func.count(models.Loan.id).label("loan_count")
        ).group_by(models.Loan.book_id).all()
        loan_count_map = {row.book_id: int(row.loan_count) for row in loan_counts}

        # Favorite genres list from user profile
        user_fav_genres = [g.strip().lower() for g in (user.favorite_genres or "").split(",") if g.strip()]

        # COLD START: User has no borrowing and no ratings history
        if not user_loans and not user_ratings:
            scored_candidates = []
            for b in candidate_books:
                b_genre = b.genre.lower()
                genre_match = 1.0 if any(fg in b_genre or b_genre in fg for fg in user_fav_genres) else 0.0
                popularity_score = loan_count_map.get(b.id, 0) * 0.1 + avg_rating_map.get(b.id, 3.5) * 0.2
                total_score = (genre_match * 0.6) + (popularity_score * 0.4)

                if genre_match > 0:
                    explanation = f"Popular in your favorite genre: {b.genre}"
                elif avg_rating_map.get(b.id, 0) >= 4.5:
                    explanation = "Top rated across our library community"
                else:
                    explanation = f"Trending book in {b.genre}"

                scored_candidates.append({
                    "book": b,
                    "score": round(float(total_score), 2),
                    "explanation": explanation
                })

            scored_candidates.sort(key=lambda x: x["score"], reverse=True)
            return scored_candidates[:limit]

        # WARM USER: Analyze user history
        # Identify anchor books (books the user rated highly or recently borrowed)
        anchor_books = []
        for r in sorted(user_ratings, key=lambda x: x.rating, reverse=True):
            if r.rating >= 4:
                anchor = db.query(models.Book).filter(models.Book.id == r.book_id).first()
                if anchor:
                    anchor_books.append((anchor, r.rating))

        if not anchor_books and user_loans:
            for l in sorted(user_loans, key=lambda x: x.issue_date, reverse=True)[:3]:
                anchor = db.query(models.Book).filter(models.Book.id == l.book_id).first()
                if anchor:
                    anchor_books.append((anchor, 4))

        # Identify user's preferred genres and authors from history
        history_genres = {}
        history_authors = {}
        for anchor, _ in anchor_books:
            history_genres[anchor.genre] = history_genres.get(anchor.genre, 0) + 1
            history_authors[anchor.author] = history_authors.get(anchor.author, 0) + 1

        top_history_genre = max(history_genres, key=history_genres.get) if history_genres else None

        scored_candidates = []
        for candidate in candidate_books:
            # 1. Content similarity against anchor books
            content_sim_score = 0.0
            best_anchor = None

            if self._is_trained and candidate.id in self.id_to_idx and self.content_sim_matrix is not None:
                c_idx = self.id_to_idx[candidate.id]
                for anchor, weight in anchor_books[:4]:
                    if anchor.id in self.id_to_idx:
                        a_idx = self.id_to_idx[anchor.id]
                        sim = self.content_sim_matrix[c_idx, a_idx] * (weight / 5.0)
                        if sim > content_sim_score:
                            content_sim_score = sim
                            best_anchor = anchor

            # 2. Collaborative similarity
            collab_score = 0.0
            if self._is_trained and candidate.id in self.id_to_idx and self.collab_sim_matrix is not None:
                c_idx = self.id_to_idx[candidate.id]
                for anchor, _ in anchor_books[:3]:
                    if anchor.id in self.id_to_idx:
                        a_idx = self.id_to_idx[anchor.id]
                        c_sim = self.collab_sim_matrix[c_idx, a_idx]
                        if c_sim > collab_score:
                            collab_score = c_sim

            # 3. Genre & Author preference affinity
            genre_affinity = 0.3 if (candidate.genre in history_genres or candidate.genre.lower() in user_fav_genres) else 0.0
            author_affinity = 0.4 if candidate.author in history_authors else 0.0

            # 4. Global popularity & rating bonus
            pop_score = (avg_rating_map.get(candidate.id, 3.5) / 5.0) * 0.15

            # Combined score
            final_score = (
                (content_sim_score * 0.40) +
                (collab_score * 0.25) +
                (genre_affinity * 0.15) +
                (author_affinity * 0.10) +
                pop_score
            )

            # Rationale explanation
            if best_anchor and content_sim_score > 0.15:
                explanation = f"Because you enjoyed '{best_anchor.title}'"
            elif author_affinity > 0:
                explanation = f"Another acclaimed title by {candidate.author}"
            elif candidate.genre in history_genres:
                explanation = f"Matches your interest in {candidate.genre}"
            elif any(fg in candidate.genre.lower() for fg in user_fav_genres):
                explanation = f"Popular in your favorite genre: {candidate.genre}"
            elif collab_score > 0.15:
                explanation = "Readers with similar taste loved this"
            else:
                explanation = f"Trending recommended read in {candidate.genre}"

            scored_candidates.append({
                "book": candidate,
                "score": round(float(final_score), 3),
                "explanation": explanation
            })

        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates[:limit]


# Global singleton instance
recommender = RecommenderEngine()
