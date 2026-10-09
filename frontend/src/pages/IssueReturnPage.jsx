import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { useToast } from '../context/ToastContext';
import {
  Repeat,
  BookOpen,
  User,
  CheckCircle,
  AlertTriangle,
  CreditCard,
  Search,
  RotateCcw
} from 'lucide-react';

export const IssueReturnPage = () => {
  const [tab, setTab] = useState('issue'); // 'issue' or 'return'
  const { success, error } = useToast();

  // Issue Tab State
  const [members, setMembers] = useState([]);
  const [books, setBooks] = useState([]);
  const [selectedMemberId, setSelectedMemberId] = useState('');
  const [selectedBookId, setSelectedBookId] = useState('');
  const [issueLoading, setIssueLoading] = useState(false);

  // Return Tab State
  const [activeLoans, setActiveLoans] = useState([]);
  const [returnSearch, setReturnSearch] = useState('');
  const [returnLoading, setReturnLoading] = useState(false);
  const [actionLoanId, setActionLoanId] = useState(null);

  useEffect(() => {
    // Load members and available books
    api.listMembers().then((res) => setMembers(res || [])).catch(() => {});
    api.getBooks({ page_size: 100 }).then((res) => setBooks(res.items || [])).catch(() => {});
    loadActiveLoans();
  }, []);

  const loadActiveLoans = async () => {
    setReturnLoading(true);
    try {
      const data = await api.getAllLoans();
      setActiveLoans(data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setReturnLoading(false);
    }
  };

  const handleIssue = async (e) => {
    e.preventDefault();
    if (!selectedMemberId || !selectedBookId) {
      error('Please select both a member and a book');
      return;
    }
    setIssueLoading(true);
    try {
      await api.issueBook(parseInt(selectedBookId, 10), parseInt(selectedMemberId, 10));
      success('Book issued successfully! 14-day borrowing cycle started.');
      setSelectedBookId('');
      // Refresh books & active loans
      api.getBooks({ page_size: 100 }).then((res) => setBooks(res.items || [])).catch(() => {});
      loadActiveLoans();
    } catch (err) {
      error(err.message || 'Failed to issue book');
    } finally {
      setIssueLoading(false);
    }
  };

  const handleReturn = async (loanId, markPaid = false) => {
    setActionLoanId(loanId);
    try {
      const updated = await api.returnLoan(loanId, markPaid);
      if (updated.fine_amount > 0) {
        success(`Book returned. Overdue fine: Rs. ${updated.fine_amount.toFixed(2)} (${updated.fine_paid ? 'Paid' : 'Unpaid'})`);
      } else {
        success('Book returned on time with zero fines!');
      }
      loadActiveLoans();
      api.getBooks({ page_size: 100 }).then((res) => setBooks(res.items || [])).catch(() => {});
    } catch (err) {
      error(err.message || 'Failed to return book');
    } finally {
      setActionLoanId(null);
    }
  };

  const handlePayFine = async (loanId) => {
    setActionLoanId(loanId);
    try {
      await api.payFine(loanId);
      success('Fine marked as paid!');
      loadActiveLoans();
    } catch (err) {
      error(err.message || 'Failed to settle fine');
    } finally {
      setActionLoanId(null);
    }
  };

  const filteredLoans = activeLoans.filter((l) => {
    if (!returnSearch.trim()) return true;
    const term = returnSearch.toLowerCase();
    return (
      l.book?.title?.toLowerCase().includes(term) ||
      l.member?.name?.toLowerCase().includes(term) ||
      l.member?.email?.toLowerCase().includes(term)
    );
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2">
          <Repeat className="w-8 h-8 text-indigo-600 dark:text-indigo-400" />
          Circulation & Issue/Return Desk
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Fast checkout of library inventory, return processing, and overdue fine collection
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200 dark:border-slate-800 space-x-8 text-sm font-semibold">
        <button
          onClick={() => setTab('issue')}
          className={`pb-3 relative transition-colors ${
            tab === 'issue'
              ? 'text-indigo-600 dark:text-indigo-400 border-b-2 border-indigo-600'
              : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
          }`}
        >
          Issue Book (Checkout)
        </button>
        <button
          onClick={() => setTab('return')}
          className={`pb-3 relative transition-colors ${
            tab === 'return'
              ? 'text-indigo-600 dark:text-indigo-400 border-b-2 border-indigo-600'
              : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
          }`}
        >
          Return & Fines Desk
        </button>
      </div>

      {/* Issue Book Tab */}
      {tab === 'issue' && (
        <div className="max-w-2xl glass-panel p-8 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-xl">
          <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-6">
            Issue Book to Member
          </h2>

          <form onSubmit={handleIssue} className="space-y-5 text-xs">
            <div>
              <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Select Member Account *
              </label>
              <select
                value={selectedMemberId}
                onChange={(e) => setSelectedMemberId(e.target.value)}
                required
                className="w-full p-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white text-xs"
              >
                <option value="">-- Choose Member --</option>
                {members.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.name} ({m.email}) - {m.active_loans_count}/{m.borrow_limit} Borrowed
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Select Book from Catalog *
              </label>
              <select
                value={selectedBookId}
                onChange={(e) => setSelectedBookId(e.target.value)}
                required
                className="w-full p-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white text-xs"
              >
                <option value="">-- Choose Book --</option>
                {books.map((b) => (
                  <option
                    key={b.id}
                    value={b.id}
                    disabled={b.available_copies <= 0}
                  >
                    {b.title} by {b.author} [{b.available_copies} available] (Shelf: {b.shelf_location})
                  </option>
                ))}
              </select>
            </div>

            <div className="p-4 rounded-2xl bg-indigo-50/60 dark:bg-indigo-950/40 text-indigo-900 dark:text-indigo-300 text-[11px] leading-relaxed">
              Standard borrowing period: <strong>14 days</strong> from today. Members may renew up to 2 times provided no reservations exist. Overdue fines accrue at <strong>Rs. 5.00/day</strong>.
            </div>

            <button
              type="submit"
              disabled={issueLoading}
              className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold shadow-md shadow-indigo-600/20 text-sm transition-all disabled:opacity-50"
            >
              {issueLoading ? 'Issuing...' : 'Complete Book Issue'}
            </button>
          </form>
        </div>
      )}

      {/* Return & Fines Tab */}
      {tab === 'return' && (
        <div className="space-y-4">
          <div className="glass-panel p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800 flex items-center gap-3">
            <Search className="w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={returnSearch}
              onChange={(e) => setReturnSearch(e.target.value)}
              placeholder="Search loans by member name, book title, or email..."
              className="w-full bg-transparent text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none"
            />
          </div>

          {returnLoading ? (
            <div className="text-center py-16">
              <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
              <p className="text-xs text-slate-400">Loading loans...</p>
            </div>
          ) : (
            <div className="glass-panel rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-xl overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-600 dark:text-slate-300">
                  <thead className="bg-slate-100/70 dark:bg-slate-900/70 text-slate-700 dark:text-slate-200 uppercase font-semibold border-b border-slate-200 dark:border-slate-800">
                    <tr>
                      <th className="p-4">Book Title</th>
                      <th className="p-4">Borrower</th>
                      <th className="p-4">Issue Date</th>
                      <th className="p-4">Due Date</th>
                      <th className="p-4">Status & Fine</th>
                      <th className="p-4 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800/80">
                    {filteredLoans.map((l) => {
                      const isOverdue = l.status === 'overdue' || (l.status === 'active' && new Date() > new Date(l.due_date));
                      const isReturned = l.status === 'returned';

                      return (
                        <tr key={l.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/40 transition-colors">
                          <td className="p-4">
                            <p className="font-bold text-sm text-slate-900 dark:text-white">{l.book?.title}</p>
                            <p className="text-slate-400 text-xs">by {l.book?.author}</p>
                          </td>
                          <td className="p-4">
                            <p className="font-semibold text-slate-900 dark:text-white">{l.member?.name}</p>
                            <p className="text-slate-400 text-xs">{l.member?.email}</p>
                          </td>
                          <td className="p-4">{new Date(l.issue_date).toLocaleDateString()}</td>
                          <td className="p-4 font-semibold text-slate-800 dark:text-slate-200">
                            {new Date(l.due_date).toLocaleDateString()}
                          </td>
                          <td className="p-4">
                            {isReturned ? (
                              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
                                <CheckCircle className="w-3 h-3" /> Returned
                              </span>
                            ) : isOverdue ? (
                              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300">
                                <AlertTriangle className="w-3 h-3" /> Overdue (Rs. {l.fine_amount.toFixed(2)})
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-indigo-100 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-300">
                                Active
                              </span>
                            )}
                          </td>
                          <td className="p-4 text-right space-x-2">
                            {!isReturned && (
                              <>
                                <button
                                  onClick={() => handleReturn(l.id, false)}
                                  disabled={actionLoanId === l.id}
                                  className="px-3 py-1.5 rounded-xl font-semibold bg-indigo-600 hover:bg-indigo-500 text-white"
                                >
                                  Process Return
                                </button>
                                {isOverdue && (
                                  <button
                                    onClick={() => handleReturn(l.id, true)}
                                    disabled={actionLoanId === l.id}
                                    className="px-3 py-1.5 rounded-xl font-semibold bg-emerald-600 hover:bg-emerald-500 text-white"
                                  >
                                    Return & Pay Fine
                                  </button>
                                )}
                              </>
                            )}

                            {isReturned && l.fine_amount > 0 && !l.fine_paid && (
                              <button
                                onClick={() => handlePayFine(l.id)}
                                disabled={actionLoanId === l.id}
                                className="px-3 py-1.5 rounded-xl font-semibold bg-amber-600 hover:bg-amber-500 text-white"
                              >
                                Collect Fine (Rs. {l.fine_amount.toFixed(2)})
                              </button>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
