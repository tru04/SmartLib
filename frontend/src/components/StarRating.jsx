import React from 'react';
import { Star } from 'lucide-react';

export const StarRating = ({ rating = 0, maxRating = 5, onRate = null, size = 'sm' }) => {
  const sizeClass = size === 'lg' ? 'w-6 h-6' : size === 'md' ? 'w-5 h-5' : 'w-4 h-4';

  return (
    <div className="flex items-center gap-1">
      {[...Array(maxRating)].map((_, i) => {
        const starIndex = i + 1;
        const isFilled = starIndex <= Math.round(rating);
        const isClickable = !!onRate;

        return (
          <button
            key={i}
            type="button"
            disabled={!isClickable}
            onClick={() => onRate && onRate(starIndex)}
            className={`${isClickable ? 'cursor-pointer hover:scale-110 transition-transform' : 'cursor-default'} p-0.5`}
          >
            <Star
              className={`${sizeClass} ${
                isFilled
                  ? 'fill-amber-400 text-amber-400'
                  : 'text-slate-300 dark:text-slate-600'
              }`}
            />
          </button>
        );
      })}
    </div>
  );
};
