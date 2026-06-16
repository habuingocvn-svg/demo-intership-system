const API = 'http://127.0.0.1:5000/api';

// ===== TOKEN HELPERS =====
const getToken = () => localStorage.getItem('token');
const getUser  = () => {
  const raw = localStorage.getItem('user');
  if (!raw || raw === 'undefined') return null;
  try { return JSON.parse(raw); } catch (e) { return null; }
};
const setAuth  = (token, user) => { localStorage.setItem('token', token); localStorage.setItem('user', JSON.stringify(user)); };
const clearAuth = () => { localStorage.removeItem('token'); localStorage.removeItem('user'); };

// ===== API HELPER =====
async function api(method, path, body = null) {
  const headers = { 'Content-Type': 'application/json' };
  const token = getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(API + path, { method, headers, body: body ? JSON.stringify(body) : null });
  const data = await res.json();
  if (!res.ok) throw new Error(data.message || 'Something went wrong');
  return data;
}

// ===== TOAST =====
function toast(msg, type = 'default') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.innerHTML = `${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'} ${msg}`;
  container.appendChild(t);
  setTimeout(() => t.remove(), 3500);
}

// ===== MODAL =====
function openModal(id) { document.getElementById(id)?.classList.add('active'); }
function closeModal(id) { document.getElementById(id)?.classList.remove('active'); }

// ===== REDIRECT BY ROLE =====
function redirectByRole(role) {
  if (role === 'student') window.location.href = '/student/dashboard';
  else if (role === 'company') window.location.href = '/company/dashboard';
  else if (role === 'admin') window.location.href = '/admin/dashboard';
}

// ===== AUTH GUARD =====
function requireAuth(role = null) {
  const user = getUser();
  if (!user || !getToken()) { window.location.href = '/login'; return null; }
  if (role && user.role !== role) { window.location.href = '/'; return null; }
  return user;
}

// ===== FORMAT DATE =====
function formatDate(dateStr) {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

// ===== SKILL TAGS =====
function renderSkills(skills = []) {
  return skills.map(s => `<span class="skill-tag">${s.name || s}</span>`).join('');
}

// ===== STATUS BADGE =====
function statusBadge(status) {
  const map = {
    open: ['badge-success', '🟢 Open'],
    closed: ['badge-danger', '🔴 Closed'],
    pending: ['badge-warning', '⏳ Pending'],
    accepted: ['badge-success', '✅ Accepted'],
    rejected: ['badge-danger', '❌ Rejected'],
    withdrawn: ['badge-primary', '↩️ Withdrawn'],
  };
  const [cls, label] = map[status] || ['badge-primary', status];
  return `<span class="badge ${cls}">${label}</span>`;
}
