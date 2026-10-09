import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import {
  BookOpen,
  Users,
  Repeat,
  AlertTriangle,
  CreditCard,
  Bookmark,
  TrendingUp,
  BarChart3,
  ArrowRight,
  ShieldAlert,
  CheckCircle,
  RefreshCw
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';

const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#06b6d4', '#3b82f6', '#f43f5e'];

export const AdminDashboardPage = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [rebuilding, setRebuilding] = useState(false);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const data = await api.getAdminStats();
      setStats(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const handleRebuildModels = async () => {
    setRebuilding(true);
    try {
      await api.rebuildRecommendations();
      alert('Recommendation matrices successfully re-trained with latest loans & ratings data!');
    } catch (err) {
      alert('Failed to rebuild recommendation matrices');
    } finally {
      setRebuilding(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-sm text-slate-500">Loading admin analytics...</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Admin Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-bold uppercase tracking-widest text-indigo-600 dark:text-indigo-400">
            Librarian Command Center
          </span>
          <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white mt-1">
            Library Operations Dashboard
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Real-time circulation metrics, inventory health, and fine audit
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleRebuildModels}
            disabled={rebuilding}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-indigo-500 ${rebuilding ? 'animate-spin' : ''}`} />
            {rebuilding ? 'Retraining...' : 'Retrain ML Models'}
          </button>
          <Link
            to="/admin/circulation"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/20 transition-all"
          >
            <Repeat className="w-4 h-4" /> Issue / Return Desk
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {/* Total Books */}
        <div className="glass-panel p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>Total Titles</span>
            <BookOpen className="w-4 h-4 text-indigo-500" />
          </div>
          <p className="text-2xl font-black text-slate-900 dark:text-white mt-2">{stats?.total_books}</p>
        </div>

        {/* Total Members */}
        <div className="glass-panel p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>Members</span>
            <Users className="w-4 h-4 text-purple-500" />
          </div>
          <p className="text-2xl font-black text-slate-900 dark:text-white mt-2">{stats?.total_members}</p>
        </div>

        {/* Active Loans */}
        <div className="glass-panel p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>Active Loans</span>
            <Repeat className="w-4 h-4 text-emerald-500" />
          </div>
          <p className="text-2xl font-black text-slate-900 dark:text-white mt-2">{stats?.active_loans}</p>
        </div>

        {/* Overdue Loans */}
        <div className="glass-panel p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>Overdue Loans</span>
            <AlertTriangle className="w-4 h-4 text-rose-500" />
          </div>
          <p className="text-2xl font-black text-rose-600 mt-2">{stats?.overdue_loans}</p>
        </div>

        {/* Fines Collected */}
        <div className="glass-panel p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>Fines Collected</span>
            <CheckCircle className="w-4 h-4 text-emerald-500" />
          </div>
          <p className="text-2xl font-black text-emerald-600 mt-2">Rs. {stats?.total_fines_collected?.toFixed(0)}</p>
        </div>

        {/* Pending Fines */}
        <div className="glass-panel p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>Pending Fines</span>
            <CreditCard className="w-4 h-4 text-amber-500" />
          </div>
          <p className="text-2xl font-black text-amber-600 mt-2">Rs. {stats?.total_pending_fines?.toFixed(0)}</p>
        </div>
      </div>

      {/* Analytics Charts Grid (Recharts) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Circulation Trends Chart */}
        <div className="lg:col-span-7 glass-panel p-6 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-lg space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-slate-900 dark:text-white">Borrowing Volume Trends</h2>
              <p className="text-xs text-slate-500">Monthly book checkout frequency</p>
            </div>
            <BarChart3 className="w-5 h-5 text-indigo-500" />
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats?.loans_per_month || []}>
                <XAxis dataKey="month" stroke="#94a3b8" fontSize={11} />
                <YAxis stroke="#94a3b8" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', color: '#fff', fontSize: '12px' }}
                />
                <Bar dataKey="loans" fill="#6366f1" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Genre Distribution Chart */}
        <div className="lg:col-span-5 glass-panel p-6 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-lg space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-slate-900 dark:text-white">Catalog Genre Distribution</h2>
              <p className="text-xs text-slate-500">Inventory share across major categories</p>
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={stats?.genres_distribution || []}
                  dataKey="count"
                  nameKey="genre"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  innerRadius={45}
                  paddingAngle={3}
                >
                  {(stats?.genres_distribution || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', color: '#fff', fontSize: '12px' }}
                />
                <Legend iconSize={8} wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Top Borrowed Books & Recent Activities */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Top Borrowed Books */}
        <div className="lg:col-span-6 glass-panel p-6 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-lg space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-indigo-500" />
              Top Borrowed Titles
            </h2>
            <Link to="/admin/books" className="text-xs font-semibold text-indigo-600 hover:underline">
              Manage Catalog
            </Link>
          </div>

          <div className="divide-y divide-slate-100 dark:divide-slate-800/80">
            {stats?.top_borrowed_books?.map((tb, idx) => (
              <div key={tb.book_id} className="py-3 flex items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <span className="font-mono font-bold text-slate-400 text-sm w-4">#{idx + 1}</span>
                  <img
                    src={tb.cover_image}
                    alt={tb.title}
                    className="w-10 h-14 object-cover rounded shadow-xs"
                  />
                  <div>
                    <Link to={`/books/${tb.book_id}`} className="font-bold text-sm text-slate-900 dark:text-white hover:underline">
                      {tb.title}
                    </Link>
                    <p className="text-xs text-slate-500">{tb.author} • {tb.genre}</p>
                  </div>
                </div>
                <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-indigo-50 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300">
                  {tb.borrow_count} checkouts
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Circulation Activities */}
        <div className="lg:col-span-6 glass-panel p-6 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-lg space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Repeat className="w-5 h-5 text-purple-500" />
              Recent Circulation Feed
            </h2>
            <Link to="/admin/reports" className="text-xs font-semibold text-indigo-600 hover:underline">
              Detailed Reports
            </Link>
          </div>

          <div className="divide-y divide-slate-100 dark:divide-slate-800/80">
            {stats?.recent_activities?.map((act) => (
              <div key={act.id} className="py-3 flex items-center justify-between text-xs">
                <div>
                  <p className="font-semibold text-slate-900 dark:text-white">
                    <span className="text-indigo-600 dark:text-indigo-400 font-bold">{act.member_name}</span> borrowed '{act.book_title}'
                  </p>
                  <p className="text-[11px] text-slate-400 mt-0.5">
                    {new Date(act.date).toLocaleString()}
                  </p>
                </div>
                <div>
                  <span className={`px-2 py-0.5 rounded-full text-[11px] font-semibold capitalize ${
                    act.status === 'returned'
                      ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                      : act.status === 'overdue'
                      ? 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300'
                      : 'bg-indigo-100 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-300'
                  }`}>
                    {act.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
