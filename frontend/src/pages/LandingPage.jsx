import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { BookCard } from '../components/BookCard';
import {
  Sparkles,
  BookOpen,
  ArrowRight,
  TrendingUp,
  BrainCircuit,
  Clock,
  ShieldCheck,
  Search,
  BookMarked
} from 'lucide-react';

export const LandingPage = ({ onOpenAIChat }) => {
  const [trendingBooks, setTrendingBooks] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [stats, setStats] = useState({ total_books: 120, total_members: 20, active_loans: 45 });
  const navigate = useNavigate();

  useEffect(() => {
    api.getBooks({ page_size: 6, sort_by: 'available_copies', sort_dir: 'asc' })
      .then((res) => setTrendingBooks(res.items || []))
      .catch(() => {});
  }, []);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/catalog?search=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-20 lg:pt-20 lg:pb-28">
        {/* Background Gradients */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-gradient-to-tr from-indigo-500/20 via-purple-500/20 to-pink-500/10 blur-[100px] rounded-full pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
          {/* Smart Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-semibold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800/80 mb-6 shadow-xs">
            <Sparkles className="w-4 h-4 text-indigo-500 animate-pulse" />
            <span>AI-Driven Book Recommendations & Smart Library Circulation</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 dark:text-white tracking-tight max-w-4xl mx-auto leading-tight">
            Discover Your Next Favorite Book with <span className="gradient-text">SmartLib</span>
          </h1>

          <p className="mt-6 text-lg sm:text-xl text-slate-600 dark:text-slate-300 max-w-2xl mx-auto leading-relaxed">
            Borrow books seamlessly, track 14-day loans with automated fine tracking, and receive tailored machine learning recommendations powered by TF-IDF & collaborative filtering.
          </p>

          {/* Quick Search Bar */}
          <form
            onSubmit={handleSearchSubmit}
            className="mt-8 max-w-2xl mx-auto flex items-center p-2 rounded-2xl glass-panel shadow-xl border border-slate-200/80 dark:border-slate-800"
          >
            <div className="flex items-center pl-3 pr-2 text-slate-400">
              <Search className="w-5 h-5" />
            </div>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by title, author, genre, or keyword (e.g. 'Project Hail Mary', 'Frank Herbert')..."
              className="flex-1 bg-transparent px-2 py-2 text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none"
            />
            <button
              type="submit"
              className="px-5 py-2.5 rounded-xl text-sm font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/25 transition-all"
            >
              Search
            </button>
          </form>

          {/* CTA Buttons */}
          <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
            <Link
              to="/catalog"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/20 transition-all"
            >
              <BookOpen className="w-4 h-4" />
              Explore 120+ Books
            </Link>
            <button
              onClick={onOpenAIChat}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-semibold bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-800 dark:text-white border border-slate-200 dark:border-slate-800 shadow-sm transition-all"
            >
              <Sparkles className="w-4 h-4 text-purple-500" />
              Ask AI Librarian
            </button>
          </div>

          {/* Stats Bar */}
          <div className="mt-14 max-w-4xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-4 p-6 rounded-2xl glass-panel border border-slate-200/60 dark:border-slate-800/60 text-left">
            <div>
              <p className="text-2xl font-black text-slate-900 dark:text-white">120+</p>
              <p className="text-xs text-slate-500 font-medium">Curated Titles</p>
            </div>
            <div>
              <p className="text-2xl font-black text-indigo-600 dark:text-indigo-400">12</p>
              <p className="text-xs text-slate-500 font-medium">Diverse Genres</p>
            </div>
            <div>
              <p className="text-2xl font-black text-emerald-600 dark:text-emerald-400">Rs. 5/day</p>
              <p className="text-xs text-slate-500 font-medium">Fair Overdue Rate</p>
            </div>
            <div>
              <p className="text-2xl font-black text-purple-600 dark:text-purple-400">14 Days</p>
              <p className="text-xs text-slate-500 font-medium">Standard Loan Period</p>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Highlights */}
      <section className="py-16 bg-slate-100/50 dark:bg-slate-900/40 border-y border-slate-200/60 dark:border-slate-800/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white">
              Why Readers & Librarians Love SmartLib
            </h2>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">
              Next-generation library operations paired with smart discovery engines.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-6 rounded-2xl glass-panel border border-slate-200 dark:border-slate-800">
              <div className="w-12 h-12 rounded-xl bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mb-4">
                <BrainCircuit className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">Smart Recommendations</h3>
              <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                Dual-engine machine learning: Content-based TF-IDF cosine similarity plus item-item collaborative filtering based on actual borrowing history.
              </p>
            </div>

            <div className="p-6 rounded-2xl glass-panel border border-slate-200 dark:border-slate-800">
              <div className="w-12 h-12 rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400 flex items-center justify-center mb-4">
                <Clock className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">Automated Circulation & Fines</h3>
              <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                Enjoy 14-day loans, up to 2 easy renewals, FIFO book reservations with 48-hour pickup holds, and clear Rs. 5/day overdue calculations.
              </p>
            </div>

            <div className="p-6 rounded-2xl glass-panel border border-slate-200 dark:border-slate-800">
              <div className="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mb-4">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">Role-Based Portals</h3>
              <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                Full-featured Admin dashboard with real-time Recharts analytics, instant book & member CRUD, rapid circulation desk, and revenue audit reports.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Featured / Trending Section */}
      <section className="py-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <TrendingUp className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
              Popular Titles in Circulation
            </h2>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
              Top requested books currently in our catalog
            </p>
          </div>
          <Link
            to="/catalog"
            className="text-sm font-semibold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1"
          >
            View all books <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-5">
          {trendingBooks.map((book) => (
            <BookCard key={book.id} book={book} />
          ))}
        </div>
      </section>
    </div>
  );
};
