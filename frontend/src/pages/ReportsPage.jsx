import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import {
  BarChart3,
  CreditCard,
  AlertTriangle,
  BookOpen,
  Printer,
  Download,
  CheckCircle2
} from 'lucide-react';

export const ReportsPage = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getAdminStats().then((data) => setStats(data)).finally(() => setLoading(false));
  }, []);

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-sm text-slate-500">Generating reports...</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2">
            <BarChart3 className="w-8 h-8 text-indigo-600 dark:text-indigo-400" />
            Library Circulation & Financial Audit Reports
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Official summary statements for overdue fines, inventory circulation, and member statistics
          </p>
        </div>

        <button
          onClick={handlePrint}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors self-start sm:self-auto shadow-xs"
        >
          <Printer className="w-4 h-4" /> Print Report Statement
        </button>
      </div>

      {/* Financial Health Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel p-6 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-md">
          <div className="flex items-center justify-between text-xs text-slate-500 font-semibold mb-2">
            <span>Collected Overdue Fines</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
          </div>
          <p className="text-3xl font-black text-emerald-600">
            Rs. {stats?.total_fines_collected?.toFixed(2)}
          </p>
          <p className="text-[11px] text-slate-400 mt-2">
            Settled and marked paid across all loans
          </p>
        </div>

        <div className="glass-panel p-6 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-md">
          <div className="flex items-center justify-between text-xs text-slate-500 font-semibold mb-2">
            <span>Outstanding Pending Fines</span>
            <CreditCard className="w-4 h-4 text-amber-500" />
          </div>
          <p className="text-3xl font-black text-amber-600">
            Rs. {stats?.total_pending_fines?.toFixed(2)}
          </p>
          <p className="text-[11px] text-slate-400 mt-2">
            Accruing at Rs. 5.00/day on {stats?.overdue_loans} overdue loans
          </p>
        </div>

        <div className="glass-panel p-6 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-md">
          <div className="flex items-center justify-between text-xs text-slate-500 font-semibold mb-2">
            <span>Active Borrower Ratio</span>
            <BookOpen className="w-4 h-4 text-indigo-500" />
          </div>
          <p className="text-3xl font-black text-slate-900 dark:text-white">
            {stats?.active_loans} / {stats?.total_books}
          </p>
          <p className="text-[11px] text-slate-400 mt-2">
            Total active loans out of catalog collection
          </p>
        </div>
      </div>

      {/* Top Titles Audit Table */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-xl space-y-4">
        <h2 className="text-lg font-bold text-slate-900 dark:text-white">
          Highest Circulating Book Inventory
        </h2>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600 dark:text-slate-300">
            <thead className="bg-slate-100/70 dark:bg-slate-900/70 text-slate-700 dark:text-slate-200 uppercase font-semibold border-b border-slate-200 dark:border-slate-800">
              <tr>
                <th className="p-3">Rank</th>
                <th className="p-3">Book Title</th>
                <th className="p-3">Author</th>
                <th className="p-3">Genre</th>
                <th className="p-3 text-right">Lifetime Checkouts</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/80">
              {stats?.top_borrowed_books?.map((tb, idx) => (
                <tr key={tb.book_id}>
                  <td className="p-3 font-mono font-bold">#{idx + 1}</td>
                  <td className="p-3 font-bold text-slate-900 dark:text-white">{tb.title}</td>
                  <td className="p-3">{tb.author}</td>
                  <td className="p-3">{tb.genre}</td>
                  <td className="p-3 text-right font-bold text-indigo-600 dark:text-indigo-400">
                    {tb.borrow_count}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
