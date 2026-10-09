import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { api } from '../api/client';
import { useToast } from '../context/ToastContext';
import {
  BookOpen,
  Calendar,
  RotateCcw,
  CreditCard,
  CheckCircle,
  AlertTriangle,
  Clock,
  ArrowLeft
} from 'lucide-react';

export const MyLoansPage = () => {
  const [searchParams] = useSearchParams();
  const initialStatus = searchParams.get('status') || 'all';

  const [loans, setLoans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterTab, setFilterTab] = useState(initialStatus);
  const [actionId, setActionId] = useState(null);

  const { success, error } = useToast();

  const fetchLoans = async () => {
    setLoading(true);
    try {
      const statusParam = filterTab === 'all' ? undefined : filterTab;
      const data = await api.getMyLoans(statusParam);
      setLoans(data || []);
    } catch (err) {
      error('Failed to load borrowing history');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLoans();
  }, [filterTab]);

  const handleRenew = async (loanId) => {
    setActionId(loanId);
    try {
      await api.renewLoan(loanId);
      success('Loan renewed successfully! Extended by 14 days.');
      fetchLoans();
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
      success('Fine settled successfully!');
      fetchLoans();
    } catch (err) {
      error(err.message || 'Payment failed');
    } finally {
      setActionId(null);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div>
        <Link to="/dashboard" className="inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-indigo-600 font-semibold mb-2">
          <ArrowLeft className="w-4 h-4" /> Back to Dashboard
        </Link>
        <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2">
          <BookOpen className="w-8 h-8 text-indigo-600 dark:text-indigo-400" />
          My Loans & Borrowing History
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Track active loans, renewal quotas, return dates, and settled fines
        </p>
      </div>

      {/* Filter Tabs */}
      <div className="flex border-b border-slate-200 dark:border-slate-800 space-x-6 text-sm font-semibold">
        {[
          { id: 'all', label: 'All Records' },
          { id: 'active', label: 'Active Loans' },
          { id: 'overdue', label: 'Overdue Books' },
          { id: 'returned', label: 'Returned History' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setFilterTab(tab.id)}
            className={`pb-3 transition-colors relative ${
              filterTab === tab.id
                ? 'text-indigo-600 dark:text-indigo-400 border-b-2 border-indigo-600'
                : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Loans Content */}
      {loading ? (
        <div className="text-center py-16">
          <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-xs text-slate-400">Loading loans...</p>
        </div>
      ) : loans.length === 0 ? (
        <div className="text-center py-16 glass-panel rounded-3xl border border-slate-200 dark:border-slate-800">
          <Calendar className="w-12 h-12 text-slate-400 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-900 dark:text-white">No loan records in this tab</h3>
          <p className="text-xs text-slate-500 mt-1">Visit the catalog to borrow your next read.</p>
          <Link to="/catalog" className="mt-4 inline-block px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 text-white">
            Browse Catalog
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {loans.map((loan) => {
            const dueDate = new Date(loan.due_date);
            const issueDate = new Date(loan.issue_date);
            const returnDate = loan.return_date ? new Date(loan.return_date) : null;
            const now = new Date();
            const isOverdue = loan.status === 'overdue' || (loan.status === 'active' && now > dueDate);

            return (
              <div
                key={loan.id}
                className="glass-panel p-5 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4 transition-all hover:shadow-md"
              >
                <div className="flex items-start sm:items-center gap-4">
                  <img
                    src={loan.book?.cover_image}
                    alt={loan.book?.title}
                    className="w-14 h-20 object-cover rounded-xl shadow-xs flex-shrink-0"
                  />
                  <div className="space-y-1">
                    <Link
                      to={`/books/${loan.book_id}`}
                      className="font-bold text-base text-slate-900 dark:text-white hover:text-indigo-600 dark:hover:text-indigo-400"
                    >
                      {loan.book?.title}
                    </Link>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      by {loan.book?.author} • Genre: {loan.book?.genre} • Shelf: {loan.book?.shelf_location}
                    </p>
                    <div className="flex flex-wrap items-center gap-3 text-xs text-slate-600 dark:text-slate-400 pt-1">
                      <span>Issued: {issueDate.toLocaleDateString()}</span>
                      <span>•</span>
                      {loan.status === 'returned' ? (
                        <span className="text-emerald-600 dark:text-emerald-400 font-medium">
                          Returned: {returnDate?.toLocaleDateString()}
                        </span>
                      ) : (
                        <span className={`font-semibold ${isOverdue ? 'text-rose-600' : 'text-indigo-600 dark:text-indigo-400'}`}>
                          Due: {dueDate.toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Status & Actions Column */}
                <div className="flex flex-col sm:flex-row sm:items-center gap-3 pt-3 md:pt-0 border-t md:border-t-0 border-slate-100 dark:border-slate-800 self-end md:self-auto w-full md:w-auto justify-between md:justify-end">
                  {/* Status Badge */}
                  <div>
                    {loan.status === 'returned' ? (
                      <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
                        <CheckCircle className="w-3.5 h-3.5" /> Returned
                      </span>
                    ) : isOverdue ? (
                      <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300">
                        <AlertTriangle className="w-3.5 h-3.5" /> Overdue (Fine: Rs. {loan.fine_amount.toFixed(2)})
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-100 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-300">
                        <Clock className="w-3.5 h-3.5" /> Active Loan
                      </span>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2">
                    {loan.status === 'active' && loan.renewal_count < 2 && !isOverdue && (
                      <button
                        onClick={() => handleRenew(loan.id)}
                        disabled={actionId === loan.id}
                        className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 transition-colors"
                      >
                        <RotateCcw className="w-3.5 h-3.5" />
                        Renew ({2 - loan.renewal_count} left)
                      </button>
                    )}

                    {loan.fine_amount > 0 && !loan.fine_paid && (
                      <button
                        onClick={() => handlePayFine(loan.id)}
                        disabled={actionId === loan.id}
                        className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold bg-amber-600 hover:bg-amber-500 text-white shadow-xs transition-colors"
                      >
                        <CreditCard className="w-3.5 h-3.5" /> Pay Fine (Rs. {loan.fine_amount.toFixed(2)})
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
