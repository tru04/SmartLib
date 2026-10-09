from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ================= USER / AUTH SCHEMAS =================
class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    favorite_genres: Optional[str] = ""  # Comma-separated favorite genres for cold start


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    membership_status: Optional[str] = None
    borrow_limit: Optional[int] = None
    favorite_genres: Optional[str] = None


class UserResponse(UserBase):
    id: int
    role: str
    membership_status: str
    borrow_limit: int
    favorite_genres: Optional[str] = ""
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = None


# ================= BOOK SCHEMAS =================
class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    isbn: str = Field(..., min_length=3, max_length=50)
    genre: str = Field(..., min_length=1, max_length=100)
    language: str = "English"
    publisher: str = "Universal Press"
    year: int = 2023
    description: str = ""
    cover_image: str = ""
    total_copies: int = Field(1, ge=1)
    available_copies: int = Field(1, ge=0)
    shelf_location: str = "A-1"


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    genre: Optional[str] = None
    language: Optional[str] = None
    publisher: Optional[str] = None
    year: Optional[int] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None
    total_copies: Optional[int] = None
    available_copies: Optional[int] = None
    shelf_location: Optional[str] = None


class BookResponse(BookBase):
    id: int
    created_at: datetime
    avg_rating: Optional[float] = 0.0
    ratings_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


class BookListResponse(BaseModel):
    items: List[BookResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ================= RATING SCHEMAS =================
class RatingCreate(BaseModel):
    book_id: int
    rating: int = Field(..., ge=1, le=5)
    review_text: Optional[str] = None


class RatingResponse(BaseModel):
    id: int
    book_id: int
    member_id: int
    rating: int
    review_text: Optional[str]
    created_at: datetime
    member_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class BookDetailResponse(BookResponse):
    ratings: List[RatingResponse] = []
    is_currently_borrowed_by_me: bool = False
    has_active_reservation_by_me: bool = False
    user_rating: Optional[int] = None


# ================= LOAN SCHEMAS =================
class LoanCreate(BaseModel):
    book_id: int
    member_id: int


class LoanResponse(BaseModel):
    id: int
    book_id: int
    member_id: int
    issue_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    status: str
    renewal_count: int
    fine_amount: float
    fine_paid: bool
    book: Optional[BookResponse] = None
    member: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


class LoanReturnRequest(BaseModel):
    loan_id: int
    fine_paid: Optional[bool] = False


# ================= RESERVATION SCHEMAS =================
class ReservationCreate(BaseModel):
    book_id: int


class ReservationResponse(BaseModel):
    id: int
    book_id: int
    member_id: int
    reserved_at: datetime
    status: str
    ready_until: Optional[datetime] = None
    queue_position: Optional[int] = 1
    book: Optional[BookResponse] = None
    member: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


# ================= NOTIFICATION SCHEMAS =================
class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ================= RECOMMENDATION SCHEMAS =================
class RecommendedBookItem(BaseModel):
    book: BookResponse
    score: float
    explanation: str


class RecommendationsResponse(BaseModel):
    recommended_for_you: List[RecommendedBookItem]
    trending_popular: List[BookResponse]
    top_by_favorite_genres: List[BookResponse]


# ================= DASHBOARD & REPORTS =================
class AdminDashboardStats(BaseModel):
    total_books: int
    total_members: int
    active_loans: int
    overdue_loans: int
    total_fines_collected: float
    total_pending_fines: float
    total_reservations: int
    loans_per_month: List[dict]
    genres_distribution: List[dict]
    top_borrowed_books: List[dict]
    recent_activities: List[dict]


class MemberDashboardStats(BaseModel):
    current_loans_count: int
    borrow_limit: int
    overdue_loans_count: int
    total_pending_fines: float
    active_reservations_count: int
    active_loans: List[LoanResponse]
    active_reservations: List[ReservationResponse]


# ================= AI ASSISTANT SCHEMAS =================
class AIChatRequest(BaseModel):
    query: str
    conversation_history: Optional[List[dict]] = []


class AIChatResponse(BaseModel):
    reply: str
    recommended_books: List[BookResponse] = []
