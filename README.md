# SmartLib — Intelligent Library Management & Recommendation Platform

SmartLib is a modern, production-ready, full-stack library management and book recommendation platform. Built with Python FastAPI, React (Vite), Tailwind CSS, SQLAlchemy ORM, and scikit-learn machine learning algorithms, SmartLib automates everyday library circulation while delivering personalized reading discovery.

---

## 🌟 Key Highlights & Features

### 1. Smart Book Recommendation Engine (`recommender.py`)
- **Content-Based Filtering**: TF-IDF vectorization over book titles, authors, genres, and synopsis descriptions with cosine similarity to calculate "Similar Books" on every book page.
- **Collaborative Filtering**: Item-item cosine similarity computed from the member borrowing and 5-star rating matrix for "Readers Also Borrowed" suggestions.
- **Personalized Recommendations**: Hybrid scoring engine that blends member history, top genres, high-rated titles, and collaborative affinities.
- **Cold-Start Handling**: New members select their top 3 favorite genres at signup, instantly priming recommendations with popular community favorites and curated picks.
- **Explainable AI**: Every recommendation includes a clear rationale badge (e.g., *"Because you enjoyed 'Dune'"*, *"Popular in your favorite genre: Science Fiction"*, *"Another acclaimed title by Brandon Sanderson"*).
- **In-Memory Caching & Real-Time Retraining**: The similarity matrix is automatically retrained on checkout/return/rating events, and can also be rebuilt manually by the administrator.

### 2. Conversational AI Librarian Assistant
- **AI Recommendation Chatbot**: Interactive slide-over assistant answering *"What should I read next?"* and natural theme queries (e.g., *"a fast-paced mystery with a detective"*).
- **Semantic Natural Language Search**: Describe a vibe, mood, or plot to find ranked matching books in the catalog.

### 3. Circulation & Loan Lifecycle Management
- **Borrowing Rules**: 14-day standard loan duration with up to 2 renewals (provided no other reader has placed a hold).
- **Automated Fine Tracking**: Overdue loans calculate fines at **Rs. 5.00 per day**, clearly tracked on member dashboards and payable online or at the circulation desk.
- **FIFO Reservations Queue**: Members can place reservations on unavailable books. When a copy is returned, the reservation at position #1 is flagged **Ready for Pickup** with a 48-hour hold and in-app notification.
- **Borrow Limits**: Configurable member limit (default: 5 books) enforced on checkout.

### 4. Role-Based Portals & Dashboards
- **Member Portal**:
  - Live greeting & KPI cards (Active Borrowings, Overdue items, Pending Fines, Queued Reservations).
  - Countdown badges for due dates (e.g., *"Due in 4 days"*, *"Overdue by 2 days"*).
  - 1-click renewal and fine payment.
  - Interactive star rating & review submission.
- **Admin & Librarian Portal**:
  - Real-time KPI statistics (Total Titles, Members, Active Loans, Overdue Loans, Fines Collected, Pending Fines).
  - Interactive Recharts analytics: Monthly Circulation Trends and Genre Distribution donut charts.
  - Book Inventory CRUD (Add, Edit, Delete, Shelf Locations, Stock Quantities).
  - Member Management (Adjust borrowing limits, activate or suspend accounts).
  - Issue & Return Desk (Rapid borrower & book selection, return processing, fine settlements).
  - Circulation & Financial Audit Reports.

### 5. Design & User Experience
- Responsive, mobile-first design with Glassmorphism and vibrant gradients.
- Persistent **Dark Mode & Light Mode** toggle.
- In-app notification center for due-soon alerts, overdue warnings, and reservation pickups.
- Toast notifications for user feedback on actions.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, Vite, Tailwind CSS, React Router v6, Lucide React, Recharts |
| **Backend** | Python 3.11, FastAPI, SQLAlchemy 2.0, Pydantic v2, Uvicorn |
| **Database** | SQLite (`smartlib.db`), Alembic database migrations |
| **Authentication** | JWT Bearer Tokens with bcrypt password hashing & RBAC |
| **Machine Learning** | scikit-learn (`TfidfVectorizer`, cosine similarity), NumPy, Pandas |

---

## 📁 Project Structure

```text
smartlib/
├── backend/
│   ├── app/
│   │   ├── config.py             # App settings & library rule configuration
│   │   ├── database.py           # SQLite connection & SQLAlchemy sessionmaker
│   │   ├── models.py             # ORM models (User, Book, Loan, Reservation, Rating, Notification)
│   │   ├── schemas.py            # Pydantic v2 schemas for requests & responses
│   │   ├── auth.py               # JWT tokens, password hashing, RBAC guards
│   │   ├── recommender.py        # TF-IDF, cosine similarity & collaborative recommender
│   │   ├── main.py               # FastAPI application entrypoint & lifespan events
│   │   ├── routers/
│   │   │   ├── auth.py           # Login, register, profile
│   │   │   ├── books.py          # Book CRUD, catalog search, star ratings
│   │   │   ├── loans.py          # Issue, renew, return, pay fines
│   │   │   ├── reservations.py   # FIFO reservations queue
│   │   │   ├── recommendations.py# Personalized feeds & similar books
│   │   │   ├── admin.py          # Analytics KPIs, monthly trends & genre charts
│   │   │   ├── members.py        # Member administration & dashboard
│   │   │   ├── notifications.py  # In-app alerts
│   │   │   └── ai_assistant.py   # Conversational AI & semantic search
│   │   └── services/
│   │       ├── loan_service.py   # Circulation business logic & fine calculation
│   │       └── reservation_service.py # FIFO queue calculation
│   ├── migrations/               # Alembic database migration versions
│   ├── tests/
│   │   └── test_loans_and_recommender.py # Pytest unit tests
│   ├── seed.py                   # Seeds 120 books, 20+ members, 320+ loans, ratings
│   ├── requirements.txt          # Python dependencies
│   ├── alembic.ini               # Alembic configuration
│   └── .env.example              # Sample environment variables
├── frontend/
│   ├── src/
│   │   ├── api/client.js         # API client with token management
│   │   ├── context/
│   │   │   ├── AuthContext.jsx   # Authentication state & dark mode toggle
│   │   │   └── ToastContext.jsx  # Floating toast notifications
│   │   ├── components/
│   │   │   ├── Navbar.jsx        # Navigation, notifications dropdown, theme toggle
│   │   │   ├── Footer.jsx        # System footer
│   │   │   ├── BookCard.jsx      # Book card with cover, availability & ratings
│   │   │   ├── StarRating.jsx    # Interactive star rating widget
│   │   │   ├── AIChatDrawer.jsx  # Slide-over AI recommendation assistant
│   │   │   └── ToastContainer.jsx# Animated toast alerts
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx   # Hero search, statistics, featured titles
│   │   │   ├── LoginPage.jsx     # Login with 1-click demo credential autofill
│   │   │   ├── RegisterPage.jsx  # Signup with 3-genre cold-start selector
│   │   │   ├── CatalogPage.jsx   # Search, genre pills, available toggle, pagination
│   │   │   ├── BookDetailPage.jsx# Book metadata, reviews, similar & collaborative recs
│   │   │   ├── MemberDashboardPage.jsx # Active loans, overdue alerts, recommended feed
│   │   │   ├── MyLoansPage.jsx   # Active/overdue/returned tabs, renewals, fine payment
│   │   │   ├── ReservationsPage.jsx # FIFO queue position & 48h pickup holds
│   │   │   ├── AdminDashboardPage.jsx # KPIs, Recharts volume & genre charts
│   │   │   ├── ManageBooksPage.jsx# Inventory CRUD modals & shelf tracking
│   │   │   ├── ManageMembersPage.jsx# Member status toggle & borrow limits
│   │   │   ├── IssueReturnPage.jsx# Rapid circulation issue & return desk
│   │   │   └── ReportsPage.jsx   # Circulation & fine financial audit statements
│   │   ├── App.jsx               # Main router & protected route guards
│   │   ├── main.jsx              # DOM entrypoint
│   │   └── index.css             # Tailwind base & glassmorphism utilities
│   ├── package.json              # Node dependencies
│   ├── vite.config.js            # Vite configuration with proxy to port 8000
│   └── tailwind.config.js        # Custom colors & dark mode configuration
└── README.md
```

---

## 🚀 Quickstart & Setup Guide

### Prerequisites
- Python 3.10+ (or Python 3.11)
- Node.js 18+ and npm

### 1. Backend Setup & Run
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Seed realistic dataset (120 books, 20 members, 320 loans, ratings)
python seed.py

# Run backend server (runs at http://localhost:8000)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Interactive API documentation will be available at: **http://localhost:8000/docs**

### 2. Frontend Setup & Run
In a separate terminal:
```bash
# Navigate to frontend directory
cd frontend

# Install npm packages
npm install

# Start Vite dev server (runs at http://localhost:5173)
npm run dev
```
Open **http://localhost:5173** in your web browser.

---

## 🔑 Demo Login Accounts

| Role | Email | Password | Features Available |
|---|---|---|---|
| **Librarian Admin** | `admin@smartlib.com` | `Admin@123` | Full dashboard, Recharts analytics, Book CRUD, Member management, Issue/Return desk, Financial audit |
| **Reader Member** | `member@smartlib.com` | `Member@123` | Catalog, Personalized recommendations, Loans with renewals, Reservations queue, Star reviews |

*Tip: On the Login screen, click the **"Librarian Admin"** or **"Reader Member"** quick-fill button for 1-click access!*

---

## 🧪 Testing

To execute the unit test suite verifying circulation rules, fine calculations, FIFO reservations, and the recommendation engine:
```bash
cd backend
.\.venv\Scripts\pytest -v
```

---

## 🌐 Core API Endpoints

- `POST /api/v1/auth/login` — Authenticate and receive JWT token
- `POST /api/v1/auth/register` — Register member with favorite genres
- `GET /api/v1/books` — Paginated catalog with keyword search and genre filter
- `GET /api/v1/books/{id}` — Book details, average ratings, and review comments
- `POST /api/v1/books/{id}/rate` — Submit 1-5 star rating and review
- `GET /api/v1/recommendations/me` — Personalized ML recommendations with explanations
- `GET /api/v1/recommendations/books/{id}/similar` — TF-IDF content similar books
- `GET /api/v1/recommendations/books/{id}/readers-also-borrowed` — Collaborative filtering matches
- `POST /api/v1/loans/issue` — Issue book (14-day due date, checks borrow limit)
- `POST /api/v1/loans/{id}/renew` — Renew loan (max 2 renewals, checks holds)
- `POST /api/v1/loans/{id}/return` — Return book & calculate overdue fine (Rs. 5/day)
- `POST /api/v1/loans/{id}/pay-fine` — Settle overdue fine
- `POST /api/v1/reservations` — Place FIFO queue reservation
- `GET /api/v1/admin/stats` — Admin KPI metrics and Recharts aggregations
- `POST /api/v1/ai/chat` — Conversational AI book recommendation assistant
