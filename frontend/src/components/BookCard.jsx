import React from 'react';
import { Link } from 'react-router-dom';
import { StarRating } from './StarRating';
import { BookOpen, MapPin, CheckCircle, Clock } from 'lucide-react';

export const BookCard = ({ book, explanation = null }) => {
  const isAvailable = book.available_copies > 0;

  return (
    <div className="group relative flex flex-col rounded-2xl glass-panel overflow-hidden transition-all duration-300 hover:shadow-xl hover:-translate-y-1 hover:border-indigo-500/50 dark:hover:border-indigo-400/50">
      {/* Cover Image Container */}
      <div className="relative aspect-[3/4] w-full overflow-hidden bg-slate-200 dark:bg-slate-800">
        <img
          src={book.cover_image || 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80'}
          alt={book.title}
          loading="lazy"
          className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-transparent to-transparent opacity-60 group-hover:opacity-80 transition-opacity" />

        {/* Availability Badge */}
        <div className="absolute top-3 right-3">
          {isAvailable ? (
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/90 text-white backdrop-blur-md shadow-sm">
              <CheckCircle className="w-3 h-3" />
              {book.available_copies} Available
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/90 text-white backdrop-blur-md shadow-sm">
              <Clock className="w-3 h-3" />
              Reserved
            </span>
          )}
        </div>

        {/* Genre Pill */}
        <div className="absolute top-3 left-3">
          <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-slate-900/70 text-slate-200 backdrop-blur-md border border-slate-700/50">
            {book.genre}
          </span>
        </div>

        {/* Shelf location */}
        <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between text-xs text-white/90">
          <span className="inline-flex items-center gap-1 bg-black/40 px-2 py-0.5 rounded backdrop-blur-sm">
            <MapPin className="w-3 h-3 text-indigo-300" />
            {book.shelf_location}
          </span>
          {book.year && <span className="text-slate-300 font-mono">{book.year}</span>}
        </div>
      </div>

      {/* Explanation Banner if provided by recommender */}
      {explanation && (
        <div className="bg-gradient-to-r from-indigo-500/10 via-purple-500/10 to-pink-500/10 px-4 py-2 border-b border-indigo-500/20 text-xs font-medium text-indigo-600 dark:text-indigo-300 flex items-center gap-1.5">
          <span className="inline-block w-2 h-2 rounded-full bg-indigo-500 animate-pulse" />
          <span className="truncate">{explanation}</span>
        </div>
      )}

      {/* Content */}
      <div className="flex flex-1 flex-col p-4 justify-between">
        <div>
          <h3 className="font-semibold text-slate-900 dark:text-white line-clamp-1 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors" title={book.title}>
            {book.title}
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 line-clamp-1">
            by {book.author}
          </p>

          <div className="flex items-center gap-2 mt-2">
            <StarRating rating={book.avg_rating || 0} size="sm" />
            <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">
              {book.avg_rating ? book.avg_rating.toFixed(1) : 'New'}
            </span>
            {book.ratings_count > 0 && (
              <span className="text-xs text-slate-400">({book.ratings_count})</span>
            )}
          </div>
        </div>

        <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
          <Link
            to={`/books/${book.id}`}
            className="w-full inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold bg-slate-100 hover:bg-indigo-600 text-slate-700 hover:text-white dark:bg-slate-800/80 dark:hover:bg-indigo-600 dark:text-slate-200 transition-all duration-200"
          >
            <BookOpen className="w-3.5 h-3.5" />
            View Details
          </Link>
        </div>
      </div>
    </div>
  );
};
