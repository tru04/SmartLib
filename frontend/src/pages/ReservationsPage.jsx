import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import { useToast } from '../context/ToastContext';
import {
  Bookmark,
  Calendar,
  Clock,
  CheckCircle,
  XCircle,
  ArrowLeft,
  AlertCircle
} from 'lucide-react';

export const ReservationsPage = () => {
  const [reservations, setReservations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cancellingId, setCancellingId] = useState(null);

  const { success, error } = useToast();

  const fetchReservations = async () => {
    setLoading(true);
    try {
      const data = await api.getMyReservations();
      setReservations(data || []);
    } catch (err) {
      error('Failed to load reservations');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReservations();
  }, []);

  const handleCancel = async (id) => {
    if (!window.confirm('Are you sure you want to cancel this reservation?')) return;
    setCancellingId(id);
    try {
      await api.cancelReservation(id);
      success('Reservation cancelled');
      fetchReservations();
    } catch (err) {
      error(err.message || 'Failed to cancel reservation');
    } finally {
      setCancellingId(null);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div>
        <Link to="/dashboard" className="inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-indigo-600 font-semibold mb-2">
          <ArrowLeft className="w-4 h-4" /> Back to Dashboard
        </Link>
        <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2">
          <Bookmark className="w-8 h-8 text-indigo-600 dark:text-indigo-400" />
          My Book Reservations
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          FIFO queue positions and pickup holds for high-demand titles
        </p>
      </div>

      {loading ? (
        <div className="text-center py-16">
          <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-xs text-slate-400">Loading reservations...</p>
        </div>
      ) : reservations.length === 0 ? (
        <div className="text-center py-16 glass-panel rounded-3xl border border-slate-200 dark:border-slate-800">
          <Bookmark className="w-12 h-12 text-slate-400 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-900 dark:text-white">No active reservations</h3>
          <p className="text-xs text-slate-500 mt-1">
            When all copies of a book are checked out, you can reserve it to hold your place in line.
          </p>
          <Link to="/catalog" className="mt-4 inline-block px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 text-white">
            Browse Catalog
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {reservations.map((res) => {
            const isReady = res.status === 'ready';
            const isPending = res.status === 'pending';

            return (
              <div
                key={res.id}
                className="glass-panel p-5 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4"
              >
                <div className="flex items-center gap-4">
                  <img
                    src={res.book?.cover_image}
                    alt={res.book?.title}
                    className="w-14 h-20 object-cover rounded-xl shadow-xs flex-shrink-0"
                  />
                  <div className="space-y-1">
                    <Link
                      to={`/books/${res.book_id}`}
                      className="font-bold text-base text-slate-900 dark:text-white hover:text-indigo-600 dark:hover:text-indigo-400"
                    >
                      {res.book?.title}
                    </Link>
                    <p className="text-xs text-slate-500">
                      by {res.book?.author} • Shelf: {res.book?.shelf_location}
                    </p>
                    <div className="flex items-center gap-3 text-xs text-slate-400 pt-1">
                      <span>Reserved on {new Date(res.reserved_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>

                <div className="flex flex-col sm:flex-row sm:items-center gap-3 self-end sm:self-auto">
                  {/* Status Badge */}
                  <div>
                    {isReady ? (
                      <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
                        <CheckCircle className="w-4 h-4" /> Ready for Pickup! (Held 48h)
                      </span>
                    ) : isPending ? (
                      <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold bg-purple-100 text-purple-800 dark:bg-purple-950 dark:text-purple-300">
                        <Clock className="w-4 h-4" /> Position #{res.queue_position} in Queue
                      </span>
                    ) : (
                      <span className="px-3 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 capitalize">
                        {res.status}
                      </span>
                    )}
                  </div>

                  {/* Cancel Button */}
                  {(isPending || isReady) && (
                    <button
                      onClick={() => handleCancel(res.id)}
                      disabled={cancellingId === res.id}
                      className="px-3 py-1.5 rounded-xl text-xs font-semibold text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 border border-rose-200 dark:border-rose-900 transition-colors"
                    >
                      Cancel
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
