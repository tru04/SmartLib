const BASE_URL = '/api/v1';

export async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem('smartlib_token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 204) {
    return null;
  }

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const errorMsg = data?.detail || `Error ${response.status}: ${response.statusText}`;
    throw new Error(errorMsg);
  }

  return data;
}

export const api = {
  // Auth
  login: (email, password) => apiRequest('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password })
  }),
  register: (name, email, password, favorite_genres) => apiRequest('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ name, email, password, favorite_genres })
  }),
  getMe: () => apiRequest('/auth/me'),
  updateMe: (data) => apiRequest('/auth/me', {
    method: 'PUT',
    body: JSON.stringify(data)
  }),

  // Books
  getBooks: (params = {}) => {
    const query = new URLSearchParams();
    if (params.search) query.append('search', params.search);
    if (params.genre && params.genre !== 'All') query.append('genre', params.genre);
    if (params.available_only) query.append('available_only', 'true');
    if (params.sort_by) query.append('sort_by', params.sort_by);
    if (params.sort_dir) query.append('sort_dir', params.sort_dir);
    if (params.page) query.append('page', params.page);
    if (params.page_size) query.append('page_size', params.page_size);
    return apiRequest(`/books?${query.toString()}`);
  },
  getGenres: () => apiRequest('/books/genres'),
  getBookDetails: (bookId) => apiRequest(`/books/${bookId}`),
  createBook: (data) => apiRequest('/books', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  updateBook: (bookId, data) => apiRequest(`/books/${bookId}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  }),
  deleteBook: (bookId) => apiRequest(`/books/${bookId}`, { method: 'DELETE' }),
  rateBook: (bookId, rating, review_text) => apiRequest(`/books/${bookId}/rate`, {
    method: 'POST',
    body: JSON.stringify({ book_id: bookId, rating, review_text })
  }),

  // Loans
  issueBook: (book_id, member_id) => apiRequest('/loans/issue', {
    method: 'POST',
    body: JSON.stringify({ book_id, member_id })
  }),
  renewLoan: (loanId) => apiRequest(`/loans/${loanId}/renew`, { method: 'POST' }),
  returnLoan: (loanId, fine_paid = false) => apiRequest(`/loans/${loanId}/return?fine_paid=${fine_paid}`, { method: 'POST' }),
  payFine: (loanId) => apiRequest(`/loans/${loanId}/pay-fine`, { method: 'POST' }),
  getMyLoans: (status) => apiRequest(`/loans/my${status ? `?status_filter=${status}` : ''}`),
  getAllLoans: (status, memberId) => {
    const query = new URLSearchParams();
    if (status) query.append('status_filter', status);
    if (memberId) query.append('member_id', memberId);
    return apiRequest(`/loans/all?${query.toString()}`);
  },

  // Reservations
  makeReservation: (book_id) => apiRequest('/reservations', {
    method: 'POST',
    body: JSON.stringify({ book_id })
  }),
  cancelReservation: (reservationId) => apiRequest(`/reservations/${reservationId}`, { method: 'DELETE' }),
  getMyReservations: () => apiRequest('/reservations/my'),
  getAllReservations: () => apiRequest('/reservations/all'),

  // Recommendations
  getMyRecommendations: (limit = 8) => apiRequest(`/recommendations/me?limit=${limit}`),
  getSimilarBooks: (bookId, limit = 6) => apiRequest(`/recommendations/books/${bookId}/similar?limit=${limit}`),
  getReadersAlsoBorrowed: (bookId, limit = 6) => apiRequest(`/recommendations/books/${bookId}/readers-also-borrowed?limit=${limit}`),
  rebuildRecommendations: () => apiRequest('/recommendations/rebuild', { method: 'POST' }),

  // Dashboard & Admin
  getAdminStats: () => apiRequest('/admin/stats'),
  getMemberDashboard: () => apiRequest('/members/dashboard'),
  listMembers: (search, status) => {
    const query = new URLSearchParams();
    if (search) query.append('search', search);
    if (status) query.append('status_filter', status);
    return apiRequest(`/members?${query.toString()}`);
  },
  getMember: (memberId) => apiRequest(`/members/${memberId}`),
  updateMember: (memberId, data) => apiRequest(`/members/${memberId}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  }),
  deleteMember: (memberId) => apiRequest(`/members/${memberId}`, { method: 'DELETE' }),

  // Notifications
  getNotifications: () => apiRequest('/notifications'),
  getUnreadCount: () => apiRequest('/notifications/unread-count'),
  markNotificationRead: (id) => apiRequest(`/notifications/${id}/read`, { method: 'PUT' }),
  markAllNotificationsRead: () => apiRequest('/notifications/read-all', { method: 'PUT' }),

  // AI Assistant
  chatWithAI: (query, conversation_history = []) => apiRequest('/ai/chat', {
    method: 'POST',
    body: JSON.stringify({ query, conversation_history })
  }),
  nlSearch: (q, limit = 8) => apiRequest(`/ai/nl-search?q=${encodeURIComponent(q)}&limit=${limit}`),
};
