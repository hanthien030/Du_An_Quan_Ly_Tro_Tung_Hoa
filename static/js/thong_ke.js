/* thong_ke.js */
let yearChart = null;

document.addEventListener('DOMContentLoaded', () => {
  const namEl = document.getElementById('sel-nam');
  const now = new Date().getFullYear();
  for (let y = now; y >= now - 3; y--) {
    namEl.insertAdjacentHTML('beforeend', `<option value="${y}">${y}</option>`);
  }
  loadStats();
});

async function loadStats() {
  const nam = parseInt(document.getElementById('sel-nam').value);
  try {
    const { data: rows } = await fetchAPI(`/api/thong-ke/doanh-thu?months=12`);
    // Filter to selected year
    const filtered = rows.filter(r => r.nam === nam);
    // Fill all 12 months
    const months = Array.from({length:12}, (_,i) => {
      const found = filtered.find(r => r.thang === i+1);
      return found || { thang: i+1, nam, label: `${i+1}/${nam}`, doanh_thu: 0, so_hoa_don: 0 };
    });

    renderChart(months);
    renderTable(months);
  } catch (e) { showToast(e.message, 'danger'); }
}

function renderChart(months) {
  const ctx = document.getElementById('chart-yearly').getContext('2d');
  if (yearChart) yearChart.destroy();
  yearChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: months.map(r => `T${r.thang}`),
      datasets: [{
        label: 'Doanh thu',
        data: months.map(r => r.doanh_thu),
        backgroundColor: months.map(r =>
          r.doanh_thu > 0 ? 'rgba(59,130,246,.75)' : 'rgba(200,200,200,.4)'
        ),
        borderRadius: 5,
      }],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: c => formatVND(c.parsed.y) } },
      },
      scales: {
        y: {
          ticks: { callback: v => formatVND(v) },
          grid: { color: 'rgba(0,0,0,.05)' },
        },
      },
    },
  });
}

function renderTable(months) {
  const tbody = document.getElementById('stat-tbody');
  const total = months.reduce((s, r) => s + r.doanh_thu, 0);
  tbody.innerHTML = months.map(r => `
    <tr>
      <td>Tháng ${r.thang}/${r.nam}</td>
      <td class="text-end ${r.doanh_thu > 0 ? 'fw-semibold' : 'text-muted'}">${formatVND(r.doanh_thu)}</td>
      <td class="text-end">${r.so_hoa_don || 0}</td>
    </tr>`).join('') + `
    <tr class="table-secondary fw-bold">
      <td>Tổng cả năm</td>
      <td class="text-end">${formatVND(total)}</td>
      <td class="text-end">${months.reduce((s,r) => s + (r.so_hoa_don||0), 0)}</td>
    </tr>`;
}
