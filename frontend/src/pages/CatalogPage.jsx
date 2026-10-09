import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { api } from '../api/client';
import { BookCard } from '../components/BookCard';
import {
  Search,
  Filter,
  ArrowUpDown,
  CheckCircle,
  ChevronLeft,
  ChevronRight,
  BookOpen,
  Sparkles,
  X
} from 'lucide-react';

export const CatalogPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const [books, setBooks] = useState([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [genres, setGenres] = useState([]);

  // Filter States initialized from URL search params
  const [search, setSearch] = useState(searchParams.get('search') || '');
  const [selectedGenre, setSelectedGenre] = useState(searchParams.get('genre') || 'All');
  const [availableOnly, setAvailableOnly] = useState(searchParams.get('available_only') === 'true');
  const [sortBy, setSortBy] = useState('title');
  const [sortDir, setSortDir] = useState('asc');
  const [page, setPage] = useState(1);
  const [isNLSearch, setIsNLSearch] = useState(false);

  // Load distinct genres once
  useEffect(() => {
    api.getGenres().then((res) => setGenres(['All', ...(res || [])])).catch(() => {});
  }, []);

  // Fetch Books
  const fetchBooks = useCallback(async () => {
    setLoading(true);
    try {
      if (isNLSearch && search.trim()) {
        const results = await api.nlSearch(search.trim(), 12);
        setBooks(results || []);
        setTotal(results?.length || 0);
        setTotalPages(1);
      } else {
        const data = await api.getBooks({
          search: search.trim() || undefined,
          genre: selectedGenre !== 'All' ? selectedGenre : undefined,
          available_only: availableOnly,
          sort_by: sortBy,
          sort_dir: sortDir,
          page,
          page_size: 12,
        });
        setBooks(data.items || []);
        setTotal(data.total || 0);
        setTotalPages(data.total_pages || 1);
      }
    } catch (err) {
      console.error('Error fetching catalog:', err);
    } finally {
      setLoading(false);
    }
  }, [search, selectedGenre, availableOnly, sortBy, sortDir, page, isNLSearch]);

  useEffect(() => {
    fetchBooks();
  }, [fetchBooks]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchBooks();
  };

  const handleClearFilters = () => {
    setSearch('');
    setSelectedGenre('All');
    setAvailableOnly(false);
    setIsNLSearch(false);
    setPage(1);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Catalog Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2">
            <BookOpen className="w-8 h-8 text-indigo-600 dark:text-indigo-400" />
            Library Catalog
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Browse our extensive collection of {total} books across all disciplines
          </p>
        </div>

        {/* Natural Language Search Mode Toggle */}
        <button
          onClick={() => {
            setIsNLSearch(!isNLSearch);
            setPage(1);
          }}
          className={`inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold border transition-all ${
            isNLSearch
              ? 'bg-purple-600 text-white border-purple-600 shadow-md shadow-purple-600/25'
              : 'bg-white dark:bg-slate-900 text-purple-600 dark:text-purple-400 border-purple-200 dark:border-purple-800 hover:bg-purple-50 dark:hover:bg-purple-950/40'
          }`}
        >
          <Sparkles className="w-4 h-4" />
          <span>{isNLSearch ? 'Semantic AI Search Enabled' : 'Try Natural Language Search'}</span>
        </button>
      </div>

      {/* Filter & Search Bar */}
      <div className="glass-panel p-5 rounded-3xl shadow-xl border border-slate-200/80 dark:border-slate-800 mb-8 space-y-4">
        {/* Search input form */}
        <form onSubmit={handleSearchSubmit} className="flex gap-2">
          <div className="relative flex-1">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
              <Search className="w-4 h-4" />
            </div>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={
                isNLSearch
                  ? "Describe what you want to read (e.g. 'thought-provoking space journey', 'detective solving locked-room puzzle')..."
                  : "Search title, author, ISBN (e.g. 'Dune', 'Agatha Christie', '978-0441013593')..."
              }
              className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <button
            type="submit"
            className="px-6 py-2.5 rounded-xl text-sm font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/20 transition-all"
          >
            Search
          </button>
        </form>

        {/* Genre Filter Pills */}
        {!isNLSearch && (
          <div className="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar text-xs">
            <span className="text-slate-400 font-semibold flex items-center gap-1 pl-1">
              <Filter className="w-3.5 h-3.5" /> Genres:
            </span>
            {genres.map((genre) => (
              <button
                key={genre}
                onClick={() => {
                  setSelectedGenre(genre);
                  setPage(1);
                }}
                className={`whitespace-nowrap px-3 py-1.5 rounded-full font-medium transition-colors ${
                  selectedGenre === genre
                    ? 'bg-indigo-600 text-white shadow-xs'
                    : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
                }`}
              >
                {genre}
              </button>
            ))}
          </div>
        )}

        {/* Quick Toggles & Sorting */}
        <div className="flex flex-wrap items-center justify-between gap-4 pt-2 border-t border-slate-100 dark:border-slate-800 text-xs">
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 cursor-pointer select-none font-medium text-slate-700 dark:text-slate-300">
              <input
                type="checkbox"
                checked={availableOnly}
                onChange={(e) => {
                  setAvailableOnly(e.target.checked);
                  setPage(1);
                }}
                className="w-4 h-4 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500 cursor-pointer"
              />
              <span className="flex items-center gap-1">
                <CheckCircle className="w-3.5 h-3.5 text-emerald-500" />
                Available Copies Only
              </span>
            </label>

            {(search || selectedGenre !== 'All' || availableOnly || isNLSearch) && (
              <button
                onClick={handleClearFilters}
                className="inline-flex items-center gap-1 text-slate-400 hover:text-rose-500 transition-colors"
              >
                <X className="w-3.5 h-3.5" /> Clear Filters
              </button>
            )}
          </div>

          {!isNLSearch && (
            <div className="flex items-center gap-2">
              <span className="text-slate-400 font-medium flex items-center gap-1">
                <ArrowUpDown className="w-3.5 h-3.5" /> Sort by:
              </span>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 focus:outline-none"
              >
                <option value="title">Title</option>
                <option value="author">Author</option>
                <option value="year">Publication Year</option>
                <option value="available_copies">Available Stock</option>
              </select>
              <select
                value={sortDir}
                onChange={(e) => setSortDir(e.target.value)}
                className="px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 focus:outline-none"
              >
                <option value="asc">Ascending</option>
                <option value="desc">Descending</option>
              </select>
            </div>
          )}
        </div>
      </div>

      {/* Book Grid */}
      {loading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-5">
          {[...Array(12)].map((_, i) => (
            <div key={i} className="aspect-[3/4] rounded-2xl bg-slate-200 dark:bg-slate-800 animate-pulse" />
          ))}
        </div>
      ) : books.length === 0 ? (
        <div className="text-center py-20 p-8 glass-panel rounded-3xl border border-slate-200 dark:border-slate-800">
          <BookOpen className="w-12 h-12 text-slate-400 mx-auto mb-3" />
          <h3 className="text-lg font-bold text-slate-900 dark:text-white">No books match your criteria</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            Try adjusting your search terms, removing genre filters, or toggling off the available-only switch.
          </p>
          <button
            onClick={handleClearFilters}
            className="mt-4 px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 text-white"
          >
            Reset Filters
          </button>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-5">
            {books.map((b) => (
              <BookCard key={b.id} book={b} />
            ))}
          </div>

          {/* Pagination */}
          {!isNLSearch && totalPages > 1 && (
            <div className="mt-12 flex items-center justify-center gap-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="inline-flex items-center gap-1 px-3 py-2 rounded-xl text-xs font-semibold border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 disabled:opacity-40 transition-colors hover:bg-slate-50 dark:hover:bg-slate-800"
              >
                <ChevronLeft className="w-4 h-4" /> Previous
              </button>

              <div className="flex items-center gap-1">
                {[...Array(totalPages)].map((_, idx) => {
                  const pNum = idx + 1;
                  // Only show current, nearby, or extreme pages if many
                  if (totalPages > 7 && Math.abs(pNum - page) > 2 && pNum !== 1 && pNum !== totalPages) {
                    if (pNum === 2 || pNum === totalPages - 1) {
                      return <span key={pNum} className="px-1 text-slate-400">...</span>;
                    }
                    return null;
                  }
                  return (
                    <button
                      key={pNum}
                      onClick={() => setPage(pNum)}
                      className={`w-8 h-8 rounded-xl text-xs font-semibold transition-colors ${
                        page === pNum
                          ? 'bg-indigo-600 text-white shadow-xs'
                          : 'bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800'
                      }`}
                    >
                      {pNum}
                    </button>
                  );
                })}
              </div>

              <button
                disabled={page >= totalPages}
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                className="inline-flex items-center gap-1 px-3 py-2 rounded-xl text-xs font-semibold border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 disabled:opacity-40 transition-colors hover:bg-slate-50 dark:hover:bg-slate-800"
              >
                Next <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};
