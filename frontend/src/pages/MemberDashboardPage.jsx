import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { api } from '../api/client';
import { BookCard } from '../components/BookCard';
import {
  BookOpen,
  Calendar,
  AlertTriangle,
  CreditCard,
  Bookmark,
  Sparkles,
  ArrowRight,
  RotateCcw,
  Clock,
  CheckCircle2,
  TrendingUp
} from 'lucide-react';

export const MemberDashboardPage = () => {
  const { user, refreshUser } = useAuth();
  const { success, error } = useToast();

  const [dashboardData, setDashboardData] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionId, setActionId] = useState(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [dash, recs] = await Promise.all([
        api.getMemberDashboard(),
        api.getMyRecommendations(6),
      ]);
      setDashboardData(dash);
      setRecommendations(recs);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRenew = async (loanId) => {
    setActionId(loanId);
    try {
      await api.renewLoan(loanId);
      success('Loan renewed successfully for 14 days!');
      loadData();
    } catch (err) {
      error(err.message || 'Renewal failed');
    } finally {
      setActionId(null);
    }
  };

  const handlePayFine = async (loanId) => {
    setActionId(loanId);
    try {
      await api.payFine(loanId);
      success('Fine paid successfully!');
      loadData();
      refreshUser();
    } catch (err) {
      error(err.message || 'Payment failed');
    } finally {
      setActionId(null);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-sm text-slate-500">Loading your member dashboard...</p>
      </div>
    );
  }

  const activeLoans = dashboardData?.active_loans || [];
  const activeReservations = dashboardData?.active_reservations || [];
  const pendingFines = dashboardData?.total_pending_fines || 0;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
      {/* Welcome Banner */}
      <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-xl flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs uppercase font-bold tracking-wider text-indigo-600 dark:text-indigo-400">
            Member Portal
          </span>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white mt-1">
            Welcome back, {user?.name}!
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Favorite Genres: <span className="font-semibold text-slate-700 dark:text-slate-300">{user?.favorite_genres || 'General Fiction'}</span>
          </p>
        </div>

        <Link
          to="/catalog"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/20 transition-all self-start sm:self-auto"
        >
          <BookOpen className="w-4 h-4" /> Browse Catalog
        </Link>
      </div>

      {/* KPI Stats Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Active Loans */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-200/80 dark:border-slate-800">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500">Active Borrowings</span>
            <div className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600">
              <BookOpen className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-black text-slate-900 dark:text-white">
              {dashboardData?.current_loans_count || 0}
            </span>
            <span className="text-xs text-slate-400">
              / {dashboardData?.borrow_limit || 5} limit
            </span>
          </div>
        </div>

        {/* Overdue Loans */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-200/80 dark:border-slate-800">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500">Overdue Books</span>
            <div className="p-2 rounded-xl bg-rose-50 dark:bg-rose-950/60 text-rose-600">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <span className={`text-2xl font-black ${dashboardData?.overdue_loans_count > 0 ? 'text-rose-600' : 'text-slate-900 dark:text-white'}`}>
              {dashboardData?.overdue_loans_count || 0}
            </span>
          </div>
        </div>

        {/* Outstanding Fines */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-200/80 dark:border-slate-800">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500">Outstanding Fines</span>
            <div className="p-2 rounded-xl bg-amber-50 dark:bg-amber-950/60 text-amber-600">
              <CreditCard className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-2xl font-black text-amber-600 dark:text-amber-400">
              Rs. {pendingFines.toFixed(2)}
            </span>
          </div>
        </div>

        {/* Active Reservations */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-200/80 dark:border-slate-800">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500">Queued Reservations</span>
            <div className="p-2 rounded-xl bg-purple-50 dark:bg-purple-950/60 text-purple-600">
              <Bookmark className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-2xl font-black text-slate-900 dark:text-white">
              {dashboardData?.active_reservations_count || 0}
            </span>
          </div>
        </div>
      </div>

      {/* Outstanding Fines Warning Banner if any */}
      {pendingFines > 0 && (
        <div className="p-4 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0" />
            <div>
              <p className="text-xs font-bold text-amber-900 dark:text-amber-200">
                You have Rs. {pendingFines.toFixed(2)} in overdue library fines.
              </p>
              <p className="text-[11px] text-amber-700 dark:text-amber-300">
                Overdue fine calculated at Rs. 5.00 per day. Please return overdue items or settle fees below.
              </p>
            </div>
          </div>
          <Link
            to="/my-loans?status=overdue"
            className="px-4 py-2 rounded-xl text-xs font-bold bg-amber-600 hover:bg-amber-500 text-white self-start sm:self-auto shadow-sm"
          >
            Review & Pay Fines
          </Link>
        </div>
      )}

      {/* Personalized Recommendations Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-indigo-500" />
              Recommended for You
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Personalized via machine learning blending your reading tastes, author affinities & ratings
            </p>
          </div>
          <Link to="/catalog" className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1">
            More in Catalog <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {recommendations?.recommended_for_you?.length > 0 ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-5">
            {recommendations.recommended_for_you.map((item) => (
              <BookCard
                key={item.book.id}
                book={item.book}
                explanation={item.explanation}
              />
            ))}
          </div>
        ) : (
          <p className="text-xs text-slate-400 italic">No recommendations available yet.</p>
        )}
      </div>

      {/* Active Loans Table */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-xl space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Calendar className="w-5 h-5 text-indigo-500" />
            Currently Borrowed Books ({activeLoans.length})
          </h2>
          <Link to="/my-loans" className="text-xs font-semibold text-indigo-600 hover:underline">
            View All History
          </Link>
        </div>

        {activeLoans.length === 0 ? (
          <div className="text-center py-10 text-xs text-slate-400">
            You do not currently have any active borrowed books.
          </div>
        ) : (
          <div className="divide-y divide-slate-100 dark:divide-slate-800/80 overflow-x-auto">
            {activeLoans.map((loan) => {
              const dueDate = new Date(loan.due_date);
              const now = new Date();
              const isOverdue = loan.status === 'overdue' || now > dueDate;
              const daysLeft = Math.ceil((dueDate - now) / (1000 * 60 * 60 * 24));

              return (
                <div key={loan.id} className="py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <img
                      src={loan.book?.cover_image}
                      alt={loan.book?.title}
                      className="w-12 h-16 object-cover rounded-lg shadow-xs flex-shrink-0"
                    />
                    <div>
                      <Link
                        to={`/books/${loan.book_id}`}
                        className="text-sm font-bold text-slate-900 dark:text-white hover:text-indigo-600 dark:hover:text-indigo-400"
                      >
                        {loan.book?.title}
                      </Link>
                      <p className="text-xs text-slate-500">by {loan.book?.author} • Shelf: {loan.book?.shelf_location}</p>
                      <div className="flex items-center gap-2 mt-1.5 text-xs">
                        {isOverdue ? (
                          <span className="px-2 py-0.5 rounded-full font-bold bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-300">
                            Overdue! Fine: Rs. {loan.fine_amount?.toFixed(2)}
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 rounded-full font-semibold bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
                            Due in {daysLeft} days ({dueDate.toLocaleDateString()})
                          </span>
                        )}
                        <span className="text-slate-400 text-[11px]">
                          Renewals: {loan.renewal_count} / 2
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 self-end sm:self-auto">
                    {loan.renewal_count < 2 && !isOverdue && (
                      <button
                        onClick={() => handleRenew(loan.id)}
                        disabled={actionId === loan.id}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 transition-colors"
                      >
                        <RotateCcw className="w-3.5 h-3.5" /> Renew (+14d)
                      </button>
                    )}
                    {isOverdue && !loan.fine_paid && loan.fine_amount > 0 && (
                      <button
                        onClick={() => handlePayFine(loan.id)}
                        disabled={actionId === loan.id}
                        className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl text-xs font-bold bg-amber-600 hover:bg-amber-500 text-white transition-colors"
                      >
                        <CreditCard className="w-3.5 h-3.5" /> Pay Rs. {loan.fine_amount.toFixed(2)}
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Active Reservations Table */}
      {activeReservations.length > 0 && (
        <div className="glass-panel p-6 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Bookmark className="w-5 h-5 text-purple-500" />
              Active Reservations Queue
            </h2>
            <Link to="/reservations" className="text-xs font-semibold text-indigo-600 hover:underline">
              Manage Reservations
            </Link>
          </div>

          <div className="divide-y divide-slate-100 dark:divide-slate-800/80">
            {activeReservations.map((res) => (
              <div key={res.id} className="py-3 flex items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <img
                    src={res.book?.cover_image}
                    alt={res.book?.title}
                    className="w-10 h-14 object-cover rounded shadow-xs"
                  />
                  <div>
                    <Link to={`/books/${res.book_id}`} className="text-sm font-bold text-slate-900 dark:text-white hover:underline">
                      {res.book?.title}
                    </Link>
                    <p className="text-xs text-slate-500">Reserved on {new Date(res.reserved_at).toLocaleDateString()}</p>
                  </div>
                </div>

                <div>
                  {res.status === 'ready' ? (
                    <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
                      Ready for Pickup!
                    </span>
                  ) : (
                    <span className="px-3 py-1 rounded-full text-xs font-semibold bg-purple-100 text-purple-800 dark:bg-purple-950 dark:text-purple-300">
                      Position #{res.queue_position} in FIFO Queue
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
