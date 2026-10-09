import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { StarRating } from '../components/StarRating';
import { BookCard } from '../components/BookCard';
import {
  BookOpen,
  MapPin,
  Calendar,
  Layers,
  Sparkles,
  Users,
  CheckCircle,
  Clock,
  Send,
  ArrowLeft,
  BookmarkPlus,
  ShieldCheck,
  Building,
  Globe
} from 'lucide-react';

export const BookDetailPage = () => {
  const { id } = useParams();
  const bookId = parseInt(id, 10);
  const navigate = useNavigate();

  const { user, isAuthenticated, isAdmin } = useAuth();
  const { success, error, warning } = useToast();

  const [book, setBook] = useState(null);
  const [loading, setLoading] = useState(true);
  const [similarBooks, setSimilarBooks] = useState([]);
  const [collaborativeBooks, setCollaborativeBooks] = useState([]);

  // Rating Form
  const [myRating, setMyRating] = useState(5);
  const [myReviewText, setMyReviewText] = useState('');
  const [submittingRating, setSubmittingRating] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  const fetchBookData = async () => {
    setLoading(true);
    try {
      const data = await api.getBookDetails(bookId);
      setBook(data);
      if (data.user_rating) {
        setMyRating(data.user_rating);
      }

      // Fetch Content-based & Collaborative recommendations
      api.getSimilarBooks(bookId, 6).then((res) => setSimilarBooks(res || [])).catch(() => {});
      api.getReadersAlsoBorrowed(bookId, 6).then((res) => setCollaborativeBooks(res || [])).catch(() => {});
    } catch (err) {
      error('Failed to load book details');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBookData();
    window.scrollTo(0, 0);
  }, [bookId]);

  // Handle Borrow
  const handleBorrow = async () => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    setActionLoading(true);
    try {
      await api.issueBook(book.id, user.id);
      success(`Successfully borrowed '${book.title}'! Due date in 14 days.`);
      fetchBookData();
    } catch (err) {
      error(err.message || 'Failed to borrow book');
    } finally {
      setActionLoading(false);
    }
  };

  // Handle Reserve
  const handleReserve = async () => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    setActionLoading(true);
    try {
      const res = await api.makeReservation(book.id);
      success(`Book reserved! You are #${res.queue_position} in the reservation queue.`);
      fetchBookData();
    } catch (err) {
      error(err.message || 'Failed to place reservation');
    } finally {
      setActionLoading(false);
    }
  };

  // Handle Rating Submission
  const handleRateSubmit = async (e) => {
    e.preventDefault();
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    setSubmittingRating(true);
    try {
      await api.rateBook(book.id, myRating, myReviewText.trim() || undefined);
      success('Thank you! Your rating and review have been submitted.');
      setMyReviewText('');
      fetchBookData();
    } catch (err) {
      error(err.message || 'Failed to submit rating');
    } finally {
      setSubmittingRating(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-sm text-slate-500">Loading book details...</p>
      </div>
    );
  }

  if (!book) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Book not found</h2>
        <Link to="/catalog" className="mt-4 inline-flex items-center gap-2 text-indigo-600 font-semibold">
          <ArrowLeft className="w-4 h-4" /> Back to Catalog
        </Link>
      </div>
    );
  }

  const isAvailable = book.available_copies > 0;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-12">
      {/* Back button */}
      <div>
        <Link
          to="/catalog"
          className="inline-flex items-center gap-2 text-xs font-semibold text-slate-500 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back to catalog
        </Link>
      </div>

      {/* Main Book Detail Banner */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-8 lg:gap-12 glass-panel p-6 sm:p-10 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-xl">
        {/* Cover Column */}
        <div className="md:col-span-4 lg:col-span-4 flex flex-col items-center">
          <div className="w-full max-w-xs aspect-[3/4] rounded-2xl overflow-hidden shadow-2xl bg-slate-200 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
            <img
              src={book.cover_image}
              alt={book.title}
              className="w-full h-full object-cover"
            />
          </div>

          {/* Quick Shelf Badge */}
          <div className="mt-4 w-full max-w-xs flex items-center justify-between p-3 rounded-xl bg-slate-100 dark:bg-slate-800/80 text-xs">
            <span className="font-semibold text-slate-500 flex items-center gap-1.5">
              <MapPin className="w-4 h-4 text-indigo-500" /> Shelf Location
            </span>
            <span className="font-mono font-bold text-slate-900 dark:text-white bg-white dark:bg-slate-900 px-2 py-0.5 rounded border border-slate-200 dark:border-slate-700">
              {book.shelf_location}
            </span>
          </div>
        </div>

        {/* Info Column */}
        <div className="md:col-span-8 lg:col-span-8 flex flex-col justify-between space-y-6">
          <div>
            <div className="flex flex-wrap items-center gap-2 mb-3">
              <span className="px-3 py-1 rounded-full text-xs font-bold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800">
                {book.genre}
              </span>
              {isAvailable ? (
                <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                  <CheckCircle className="w-3.5 h-3.5" />
                  {book.available_copies} of {book.total_copies} Copies Available
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300 border border-rose-200 dark:border-rose-800">
                  <Clock className="w-3.5 h-3.5" />
                  All {book.total_copies} Copies Checked Out
                </span>
              )}
            </div>

            <h1 className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white tracking-tight">
              {book.title}
            </h1>
            <p className="text-base text-slate-600 dark:text-slate-300 mt-1 font-medium">
              by <span className="text-indigo-600 dark:text-indigo-400 font-semibold">{book.author}</span>
            </p>

            {/* Ratings & Score */}
            <div className="flex items-center gap-3 mt-3">
              <StarRating rating={book.avg_rating || 0} size="md" />
              <span className="text-sm font-bold text-slate-900 dark:text-white">
                {book.avg_rating ? book.avg_rating.toFixed(1) : 'New'} / 5.0
              </span>
              <span className="text-xs text-slate-400">
                ({book.ratings_count} {book.ratings_count === 1 ? 'review' : 'reviews'})
              </span>
            </div>

            {/* Synopsis Description */}
            <div className="mt-6">
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Synopsis</h2>
              <p className="text-sm sm:text-base text-slate-700 dark:text-slate-300 leading-relaxed">
                {book.description || 'No description available for this catalog item.'}
              </p>
            </div>

            {/* Metadata Grid */}
            <div className="mt-6 grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800 text-xs">
              <div>
                <p className="text-slate-400">ISBN</p>
                <p className="font-mono font-bold text-slate-900 dark:text-white mt-0.5">{book.isbn}</p>
              </div>
              <div>
                <p className="text-slate-400">Published</p>
                <p className="font-bold text-slate-900 dark:text-white mt-0.5">{book.year}</p>
              </div>
              <div>
                <p className="text-slate-400">Publisher</p>
                <p className="font-bold text-slate-900 dark:text-white mt-0.5 truncate">{book.publisher}</p>
              </div>
              <div>
                <p className="text-slate-400">Language</p>
                <p className="font-bold text-slate-900 dark:text-white mt-0.5">{book.language}</p>
              </div>
            </div>
          </div>

          {/* Action CTAs */}
          <div className="pt-4 border-t border-slate-200 dark:border-slate-800 flex flex-wrap items-center gap-4">
            {book.is_currently_borrowed_by_me ? (
              <div className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 text-sm font-semibold border border-indigo-200 dark:border-indigo-800">
                <CheckCircle className="w-5 h-5 text-indigo-500" />
                You currently borrow this book
              </div>
            ) : book.has_active_reservation_by_me ? (
              <div className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300 text-sm font-semibold border border-amber-200 dark:border-amber-800">
                <Clock className="w-5 h-5 text-amber-500" />
                You have reserved this book (Hold queued)
              </div>
            ) : isAvailable ? (
              <button
                onClick={handleBorrow}
                disabled={actionLoading}
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/25 transition-all disabled:opacity-50"
              >
                <BookOpen className="w-4 h-4" />
                {actionLoading ? 'Processing...' : 'Borrow Book (14 Days)'}
              </button>
            ) : (
              <button
                onClick={handleReserve}
                disabled={actionLoading}
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-semibold bg-amber-600 hover:bg-amber-500 text-white shadow-lg shadow-amber-600/25 transition-all disabled:opacity-50"
              >
                <BookmarkPlus className="w-4 h-4" />
                {actionLoading ? 'Reserving...' : 'Place FIFO Reservation'}
              </button>
            )}

            {isAdmin && (
              <Link
                to={`/admin/books`}
                className="inline-flex items-center gap-1.5 px-4 py-3 rounded-xl text-xs font-semibold bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 transition-colors"
              >
                <ShieldCheck className="w-4 h-4" /> Manage Inventory
              </Link>
            )}
          </div>
        </div>
      </div>

      {/* Ratings & Reviews Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Submit Review Card */}
        <div className="lg:col-span-5 glass-panel p-6 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-lg">
          <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-1">
            Rate & Review this Book
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">
            Help the collaborative filtering engine recommend books accurately!
          </p>

          <form onSubmit={handleRateSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Your Rating
              </label>
              <div className="flex items-center gap-3">
                <StarRating rating={myRating} onRate={setMyRating} size="lg" />
                <span className="text-sm font-bold text-slate-900 dark:text-white">{myRating} of 5 Stars</span>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Review Comments (Optional)
              </label>
              <textarea
                value={myReviewText}
                onChange={(e) => setMyReviewText(e.target.value)}
                placeholder="What did you think of the plot, style, or themes?..."
                rows={4}
                className="w-full p-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <button
              type="submit"
              disabled={submittingRating}
              className="w-full py-2.5 px-4 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white flex items-center justify-center gap-2 transition-all disabled:opacity-50"
            >
              <Send className="w-3.5 h-3.5" />
              {submittingRating ? 'Submitting...' : 'Submit Rating & Feedback'}
            </button>
          </form>
        </div>

        {/* Existing Reader Reviews */}
        <div className="lg:col-span-7 glass-panel p-6 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-lg">
          <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">
            Reader Reviews ({book.ratings?.length || 0})
          </h3>

          <div className="space-y-4 max-h-[350px] overflow-y-auto pr-2">
            {!book.ratings || book.ratings.length === 0 ? (
              <p className="text-xs text-slate-400 italic py-8 text-center">
                Be the first reader to rate and review this book!
              </p>
            ) : (
              book.ratings.map((rev) => (
                <div
                  key={rev.id}
                  className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200/60 dark:border-slate-800 text-xs"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-slate-900 dark:text-white">
                      {rev.member_name}
                    </span>
                    <StarRating rating={rev.rating} size="sm" />
                  </div>
                  {rev.review_text && (
                    <p className="text-slate-700 dark:text-slate-300 leading-relaxed">
                      "{rev.review_text}"
                    </p>
                  )}
                  <span className="text-[10px] text-slate-400 mt-2 block">
                    {new Date(rev.created_at).toLocaleDateString()}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Content-based: Similar Books Carousel / Grid */}
      {similarBooks.length > 0 && (
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-indigo-500" />
                Similar Books You Might Enjoy
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Matched via TF-IDF content similarity on genre, themes, author, and description
              </p>
            </div>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-5">
            {similarBooks.map((simBook) => (
              <BookCard key={simBook.id} book={simBook} />
            ))}
          </div>
        </section>
      )}

      {/* Collaborative Filtering: Readers Also Borrowed */}
      {collaborativeBooks.length > 0 && (
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <Users className="w-5 h-5 text-purple-500" />
                Readers Who Borrowed This Also Borrowed
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Matched via item-item collaborative filtering correlations
              </p>
            </div>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-5">
            {collaborativeBooks.map((collabBook) => (
              <BookCard key={collabBook.id} book={collabBook} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
};
