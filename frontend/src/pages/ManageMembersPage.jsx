import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { useToast } from '../context/ToastContext';
import {
  Users,
  Search,
  Shield,
  UserCheck,
  UserX,
  CreditCard,
  BookOpen,
  AlertTriangle
} from 'lucide-react';

export const ManageMembersPage = () => {
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [updatingId, setUpdatingId] = useState(null);

  const { success, error } = useToast();

  const fetchMembers = async () => {
    setLoading(true);
    try {
      const data = await api.listMembers(search);
      setMembers(data || []);
    } catch (err) {
      error('Failed to load members list');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMembers();
  }, [search]);

  const handleToggleStatus = async (member) => {
    const nextStatus = member.membership_status === 'active' ? 'suspended' : 'active';
    setUpdatingId(member.id);
    try {
      await api.updateMember(member.id, { membership_status: nextStatus });
      success(`Updated status for ${member.name} to ${nextStatus}`);
      fetchMembers();
    } catch (err) {
      error(err.message || 'Failed to update member status');
    } finally {
      setUpdatingId(null);
    }
  };

  const handleUpdateLimit = async (member, newLimit) => {
    if (newLimit < 1 || newLimit > 15) return;
    setUpdatingId(member.id);
    try {
      await api.updateMember(member.id, { borrow_limit: newLimit });
      success(`Updated borrowing limit for ${member.name} to ${newLimit} books`);
      fetchMembers();
    } catch (err) {
      error(err.message || 'Failed to update limit');
    } finally {
      setUpdatingId(null);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white flex items-center gap-2">
          <Users className="w-8 h-8 text-indigo-600 dark:text-indigo-400" />
          Member Accounts & Access Management
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Review member borrowing status, overdue accounts, outstanding fines, and borrowing quotas
        </p>
      </div>

      {/* Search Header */}
      <div className="glass-panel p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800 flex items-center gap-3">
        <Search className="w-4 h-4 text-slate-400" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Filter members by name or email address..."
          className="w-full bg-transparent text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none"
        />
      </div>

      {loading ? (
        <div className="text-center py-16">
          <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-xs text-slate-400">Loading members...</p>
        </div>
      ) : (
        <div className="glass-panel rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-600 dark:text-slate-300">
              <thead className="bg-slate-100/70 dark:bg-slate-900/70 text-slate-700 dark:text-slate-200 uppercase font-semibold border-b border-slate-200 dark:border-slate-800">
                <tr>
                  <th className="p-4">Member</th>
                  <th className="p-4">Role</th>
                  <th className="p-4">Status</th>
                  <th className="p-4">Borrow Limit</th>
                  <th className="p-4">Active / Overdue</th>
                  <th className="p-4">Unpaid Fines</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/80">
                {members.map((m) => (
                  <tr key={m.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/40 transition-colors">
                    <td className="p-4">
                      <p className="font-bold text-sm text-slate-900 dark:text-white">{m.name}</p>
                      <p className="text-slate-400 text-xs">{m.email}</p>
                    </td>
                    <td className="p-4">
                      <span className={`px-2.5 py-1 rounded-full text-[11px] font-bold uppercase ${
                        m.role === 'admin'
                          ? 'bg-purple-100 text-purple-700 dark:bg-purple-950 dark:text-purple-300'
                          : 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300'
                      }`}>
                        {m.role}
                      </span>
                    </td>
                    <td className="p-4">
                      <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold ${
                        m.membership_status === 'active'
                          ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                          : 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300'
                      }`}>
                        {m.membership_status === 'active' ? <UserCheck className="w-3 h-3" /> : <UserX className="w-3 h-3" />}
                        {m.membership_status}
                      </span>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-1.5">
                        <button
                          onClick={() => handleUpdateLimit(m, m.borrow_limit - 1)}
                          disabled={m.borrow_limit <= 1 || updatingId === m.id}
                          className="w-5 h-5 rounded bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 flex items-center justify-center font-bold text-xs"
                        >
                          -
                        </button>
                        <span className="font-bold text-slate-900 dark:text-white w-6 text-center">{m.borrow_limit}</span>
                        <button
                          onClick={() => handleUpdateLimit(m, m.borrow_limit + 1)}
                          disabled={m.borrow_limit >= 15 || updatingId === m.id}
                          className="w-5 h-5 rounded bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 flex items-center justify-center font-bold text-xs"
                        >
                          +
                        </button>
                      </div>
                    </td>
                    <td className="p-4">
                      <span className="font-bold text-indigo-600 dark:text-indigo-400">{m.active_loans_count}</span> active
                      {m.overdue_loans_count > 0 && (
                        <span className="ml-2 font-bold text-rose-600">({m.overdue_loans_count} overdue)</span>
                      )}
                    </td>
                    <td className="p-4">
                      {m.unpaid_fines_total > 0 ? (
                        <span className="font-bold text-rose-600">Rs. {m.unpaid_fines_total.toFixed(2)}</span>
                      ) : (
                        <span className="text-slate-400">Rs. 0.00</span>
                      )}
                    </td>
                    <td className="p-4 text-right">
                      {m.role !== 'admin' && (
                        <button
                          onClick={() => handleToggleStatus(m)}
                          disabled={updatingId === m.id}
                          className={`px-3 py-1 rounded-xl text-xs font-semibold border transition-colors ${
                            m.membership_status === 'active'
                              ? 'text-rose-600 border-rose-200 hover:bg-rose-50 dark:hover:bg-rose-950/40'
                              : 'text-emerald-600 border-emerald-200 hover:bg-emerald-50 dark:hover:bg-emerald-950/40'
                          }`}
                        >
                          {m.membership_status === 'active' ? 'Suspend' : 'Activate'}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
