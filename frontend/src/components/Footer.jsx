import React from 'react';
import { BookMarked, Heart, Shield, Cpu, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Footer = () => {
  return (
    <footer className="border-t border-slate-200 dark:border-slate-800 bg-white/50 dark:bg-slate-950/50 backdrop-blur-md transition-colors mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand Info */}
          <div className="space-y-3 md:col-span-1">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white">
                <BookMarked className="w-4 h-4" />
              </div>
              <span className="font-extrabold text-lg text-slate-900 dark:text-white">
                Smart<span className="text-indigo-600 dark:text-indigo-400">Lib</span>
              </span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
              Intelligent library management platform featuring machine learning recommendation engines, automated loan circulation, and fine settlement.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white mb-3">
              Explore
            </h4>
            <ul className="space-y-2 text-xs text-slate-600 dark:text-slate-400">
              <li><Link to="/catalog" className="hover:text-indigo-600 dark:hover:text-indigo-400">Book Catalog</Link></li>
              <li><Link to="/catalog?available_only=true" className="hover:text-indigo-600 dark:hover:text-indigo-400">Available Books</Link></li>
              <li><Link to="/login" className="hover:text-indigo-600 dark:hover:text-indigo-400">Member Portal</Link></li>
              <li><Link to="/register" className="hover:text-indigo-600 dark:hover:text-indigo-400">Create Account</Link></li>
            </ul>
          </div>

          {/* Features */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white mb-3">
              Smart Engine
            </h4>
            <ul className="space-y-2 text-xs text-slate-600 dark:text-slate-400">
              <li className="flex items-center gap-1.5"><Sparkles className="w-3 h-3 text-indigo-500" /> TF-IDF Content Similarity</li>
              <li className="flex items-center gap-1.5"><Cpu className="w-3 h-3 text-purple-500" /> Collaborative Item Filtering</li>
              <li className="flex items-center gap-1.5"><Shield className="w-3 h-3 text-emerald-500" /> FIFO Reservation Queue</li>
              <li className="flex items-center gap-1.5"><Heart className="w-3 h-3 text-rose-500" /> Cold-Start Personalization</li>
            </ul>
          </div>

          {/* Tech Stack */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white mb-3">
              Built With
            </h4>
            <div className="flex flex-wrap gap-1.5">
              {['FastAPI', 'React Vite', 'TailwindCSS', 'scikit-learn', 'SQLAlchemy', 'Recharts', 'JWT Auth'].map((tech) => (
                <span
                  key={tech}
                  className="px-2 py-1 rounded-md text-[11px] font-medium bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300"
                >
                  {tech}
                </span>
              ))}
            </div>
            <div className="mt-4 text-[11px] text-slate-400">
              Overdue Fine Rate: <strong className="text-indigo-600 dark:text-indigo-400">Rs. 5/day</strong> • Max Renewals: <strong>2</strong>
            </div>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-slate-200 dark:border-slate-800 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 dark:text-slate-400 gap-2">
          <p>© {new Date().getFullYear()} SmartLib Systems. Built for high-volume library operations.</p>
          <p className="flex items-center gap-1">
            Engineered with FastAPI, React & scikit-learn
          </p>
        </div>
      </div>
    </footer>
  );
};
