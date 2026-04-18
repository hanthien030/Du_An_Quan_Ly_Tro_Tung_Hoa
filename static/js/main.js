/* ============================================================
   main.js — Shared utility functions
   ============================================================ */

// ---- API helper ----
async function fetchAPI(url, method = 'GET', body = null) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(url, opts);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || `Lỗi ${res.status}`);
  return data;
}

// ---- Formatting ----
function formatVND(amount) {
  if (amount === null || amount === undefined) return '—';
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency', currency: 'VND', maximumFractionDigits: 0,
  }).format(amount);
}

function formatDate(str) {
  if (!str) return '—';
  const [y, m, d] = str.split('-');
  return `${d}/${m}/${y}`;
}

// ---- Toast ----
function showToast(message, type = 'success') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }
  const id = `toast-${Date.now()}`;
  const bg = type === 'success' ? 'bg-success' : type === 'warning' ? 'bg-warning' : 'bg-danger';
  const html = `
    <div id="${id}" class="toast align-items-center text-white ${bg} border-0 mb-2" role="alert" aria-live="assertive">
      <div class="d-flex">
        <div class="toast-body">${message}</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
      </div>
    </div>`;
  container.insertAdjacentHTML('beforeend', html);
  const el = document.getElementById(id);
  const t = new bootstrap.Toast(el, { delay: 3000 });
  t.show();
  el.addEventListener('hidden.bs.toast', () => el.remove());
}

// ---- Sidebar toggle (mobile) ----
document.addEventListener('DOMContentLoaded', () => {
  const toggler = document.getElementById('sidebar-toggler');
  const sidebar = document.getElementById('sidebar');
  if (toggler && sidebar) {
    toggler.addEventListener('click', () => sidebar.classList.toggle('show'));
  }

  // Close sidebar when clicking outside (mobile)
  document.addEventListener('click', (e) => {
    if (sidebar && sidebar.classList.contains('show')
        && !sidebar.contains(e.target)
        && e.target !== toggler) {
      sidebar.classList.remove('show');
    }
  });

  // Highlight active nav link
  const path = window.location.pathname;
  document.querySelectorAll('#sidebar .nav-link').forEach(link => {
    const href = link.getAttribute('href');
    if (!href) return;
    const isActive = href === '/' ? (path === '/' || path === '/dashboard') : path.startsWith(href);
    if (isActive) {
      link.classList.add('active');
    }
  });
});

// ---- Month/year picker helper ----
function getMonthYear() {
  const now = new Date();
  return { thang: now.getMonth() + 1, nam: now.getFullYear() };
}

function fillMonthYearSelects(thangId, namId, years = 3) {
  const thangEl = document.getElementById(thangId);
  const namEl   = document.getElementById(namId);
  if (!thangEl || !namEl) return;

  for (let m = 1; m <= 12; m++) {
    thangEl.insertAdjacentHTML('beforeend', `<option value="${m}">${m}</option>`);
  }
  const now = new Date();
  for (let y = now.getFullYear(); y >= now.getFullYear() - years; y--) {
    namEl.insertAdjacentHTML('beforeend', `<option value="${y}">${y}</option>`);
  }
  thangEl.value = now.getMonth() + 1;
  namEl.value   = now.getFullYear();
}
