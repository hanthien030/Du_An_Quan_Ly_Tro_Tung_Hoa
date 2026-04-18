/* dashboard.js */
document.addEventListener('DOMContentLoaded', async () => {
  // KPI
  try {
    const { data: d } = await fetchAPI('/api/thong-ke/dashboard');
    document.getElementById('kpi-tong-phong').textContent  = d.tong_phong;
    document.getElementById('kpi-dang-thue').textContent   = d.phong_dang_thue;
    document.getElementById('kpi-phong-trong').textContent = d.phong_trong;
    document.getElementById('kpi-doanh-thu').textContent   = formatVND(d.doanh_thu_thang_nay);

    document.getElementById('txt-chua-dong').textContent =
      d.chua_dong_tien > 0
        ? `⚠️ ${d.chua_dong_tien} phòng chưa đóng tiền tháng ${d.thang}/${d.nam}`
        : `✅ Tất cả đã đóng tiền tháng ${d.thang}/${d.nam}`;

    document.getElementById('txt-sap-het').textContent =
      d.sap_het_han > 0
        ? `🔔 ${d.sap_het_han} hợp đồng sắp hết hạn`
        : `✅ Không có hợp đồng sắp hết hạn`;
  } catch (e) {
    console.error(e);
  }

  // Chart
  try {
    const { data: rows } = await fetchAPI('/api/thong-ke/doanh-thu?months=6');
    const ctx = document.getElementById('chart-doanh-thu').getContext('2d');
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: rows.map(r => r.label),
        datasets: [{
          label: 'Doanh thu (VNĐ)',
          data:  rows.map(r => r.doanh_thu),
          backgroundColor: 'rgba(59,130,246,.7)',
          borderRadius: 6,
        }],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: ctx => formatVND(ctx.parsed.y),
            },
          },
        },
        scales: {
          y: {
            ticks: { callback: v => formatVND(v) },
            grid: { color: 'rgba(0,0,0,.05)' },
          },
        },
      },
    });
  } catch (e) {
    console.error(e);
  }
});
