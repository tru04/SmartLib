import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app import models
from app.auth import get_password_hash
from app.services.loan_service import LoanService
from app.services.reservation_service import ReservationService
from app.recommender import recommender
from app.config import settings

# Test DB in memory
TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_data(db_session):
    # Create member
    member = models.User(
        name="Test Reader",
        email="reader@example.com",
        hashed_password=get_password_hash("password123"),
        role="member",
        membership_status="active",
        borrow_limit=3,
        favorite_genres="Science Fiction,Technology"
    )
    # Create another member
    member2 = models.User(
        name="Second Reader",
        email="second@example.com",
        hashed_password=get_password_hash("password123"),
        role="member",
        membership_status="active",
        borrow_limit=3,
        favorite_genres="Fantasy"
    )
    db_session.add_all([member, member2])
    db_session.commit()

    # Create books
    b1 = models.Book(
        title="Dune",
        author="Frank Herbert",
        isbn="TEST-DUNE-1",
        genre="Science Fiction",
        total_copies=2,
        available_copies=2,
        shelf_location="SF-1",
        description="Epic sci-fi desert planet"
    )
    b2 = models.Book(
        title="Children of Dune",
        author="Frank Herbert",
        isbn="TEST-DUNE-2",
        genre="Science Fiction",
        total_copies=1,
        available_copies=1,
        shelf_location="SF-2",
        description="Sequel sci-fi desert planet"
    )
    b3 = models.Book(
        title="Clean Code",
        author="Robert Martin",
        isbn="TEST-TECH-1",
        genre="Technology",
        total_copies=1,
        available_copies=1,
        shelf_location="TC-1",
        description="Software craftsmanship and agile principles"
    )
    db_session.add_all([b1, b2, b3])
    db_session.commit()

    return {"member": member, "member2": member2, "b1": b1, "b2": b2, "b3": b3}


def test_issue_and_return_book(db_session, sample_data):
    m = sample_data["member"]
    b = sample_data["b1"]

    assert b.available_copies == 2
    loan = LoanService.issue_book(db_session, b.id, m.id)
    assert loan.status == "active"
    assert loan.renewal_count == 0
    assert loan.fine_amount == 0.0

    # Verify inventory decreased
    db_session.refresh(b)
    assert b.available_copies == 1

    # Return book
    returned_loan = LoanService.return_book(db_session, loan.id, fine_paid=True)
    assert returned_loan.status == "returned"
    assert returned_loan.return_date is not None

    # Verify inventory restored
    db_session.refresh(b)
    assert b.available_copies == 2


def test_fine_calculation_overdue(db_session, sample_data):
    # Rs. 5 per day overdue
    due_date = datetime.utcnow() - timedelta(days=5)
    fine = LoanService.calculate_fine(due_date, datetime.utcnow())
    assert fine == 25.0  # 5 days * 5.0

    # Non-overdue loan has 0 fine
    future_due = datetime.utcnow() + timedelta(days=5)
    fine_future = LoanService.calculate_fine(future_due, datetime.utcnow())
    assert fine_future == 0.0


def test_max_renewals_enforcement(db_session, sample_data):
    m = sample_data["member"]
    b = sample_data["b1"]

    loan = LoanService.issue_book(db_session, b.id, m.id)

    # Renewal 1
    loan = LoanService.renew_book(db_session, loan.id)
    assert loan.renewal_count == 1

    # Renewal 2
    loan = LoanService.renew_book(db_session, loan.id)
    assert loan.renewal_count == 2

    # Renewal 3 should fail (max is 2)
    with pytest.raises(Exception):
        LoanService.renew_book(db_session, loan.id)


def test_reservation_fifo_and_hold_on_return(db_session, sample_data):
    m1 = sample_data["member"]
    m2 = sample_data["member2"]
    b = sample_data["b2"]  # only 1 copy

    # m1 borrows b2
    loan = LoanService.issue_book(db_session, b.id, m1.id)
    db_session.refresh(b)
    assert b.available_copies == 0

    # m2 reserves b2
    res = ReservationService.create_reservation(db_session, b.id, m2.id)
    assert res.status == "pending"
    assert ReservationService.get_queue_position(db_session, res) == 1

    # m1 tries to renew b2 -> should fail because of pending reservation
    with pytest.raises(Exception):
        LoanService.renew_book(db_session, loan.id)

    # m1 returns b2 -> m2's reservation becomes 'ready' with hold
    LoanService.return_book(db_session, loan.id)
    db_session.refresh(res)
    assert res.status == "ready"
    assert res.ready_until is not None


def test_recommender_engine(db_session, sample_data):
    # Train recommender on test data
    success = recommender.build_models(db_session)
    assert success is True

    # Check content similar to Dune
    b1 = sample_data["b1"]
    similar_books = recommender.get_similar_books(b1.id, db_session, limit=2)
    assert len(similar_books) > 0
    # Children of Dune should be very similar to Dune
    similar_titles = [b.title for b, _ in similar_books]
    assert "Children of Dune" in similar_titles

    # Test personalized recommendations for cold-start member
    m = sample_data["member"]
    recs = recommender.get_personalized_recommendations(m, db_session, limit=3)
    assert len(recs) > 0
    assert "explanation" in recs[0]
    assert "score" in recs[0]
