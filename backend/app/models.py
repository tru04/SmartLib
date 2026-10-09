from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
)
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="member", nullable=False)  # 'admin' or 'member'
    membership_status = Column(String(20), default="active", nullable=False)  # 'active', 'suspended'
    borrow_limit = Column(Integer, default=5, nullable=False)
    favorite_genres = Column(Text, default="", nullable=True)  # Comma-separated or JSON string
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    loans = relationship("Loan", back_populates="member", cascade="all, delete-orphan")
    reservations = relationship("Reservation", back_populates="member", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="member", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    author = Column(String(255), index=True, nullable=False)
    isbn = Column(String(50), unique=True, index=True, nullable=False)
    genre = Column(String(100), index=True, nullable=False)
    language = Column(String(50), default="English", nullable=False)
    publisher = Column(String(150), default="Universal Press", nullable=False)
    year = Column(Integer, default=2020, nullable=False)
    description = Column(Text, default="", nullable=False)
    cover_image = Column(String(500), default="", nullable=False)
    total_copies = Column(Integer, default=1, nullable=False)
    available_copies = Column(Integer, default=1, nullable=False)
    shelf_location = Column(String(50), default="General-1", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    loans = relationship("Loan", back_populates="book", cascade="all, delete-orphan")
    reservations = relationship("Reservation", back_populates="book", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="book", cascade="all, delete-orphan")


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    issue_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    due_date = Column(DateTime, nullable=False)
    return_date = Column(DateTime, nullable=True)
    status = Column(String(20), default="active", nullable=False)  # 'active', 'returned', 'overdue'
    renewal_count = Column(Integer, default=0, nullable=False)
    fine_amount = Column(Float, default=0.0, nullable=False)
    fine_paid = Column(Boolean, default=False, nullable=False)

    book = relationship("Book", back_populates="loans")
    member = relationship("User", back_populates="loans")


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reserved_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String(20), default="pending", nullable=False)  # 'pending', 'ready', 'fulfilled', 'cancelled'
    ready_until = Column(DateTime, nullable=True)

    book = relationship("Book", back_populates="reservations")
    member = relationship("User", back_populates="reservations")


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1 to 5
    review_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    book = relationship("Book", back_populates="ratings")
    member = relationship("User", back_populates="ratings")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(30), default="system", nullable=False)  # 'due_soon', 'overdue', 'reservation_ready', 'system'
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="notifications")
