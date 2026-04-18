/* thanh_toan.js */
let bangGia = null;
let ttData  = [];

document.addEventListener('DOMContentLoaded', () => {
  fillMonthYearSelects('sel-thang', 'sel-nam');
  loadTT();
});

async function loadTT() {
  const thang = document.getElementById('sel-thang').value;
  const nam   = document.getElementById('sel-nam').value;

  // Lấy bảng giá để tính tạm tính
  try {
    const bgRes = await fetchAPI(`/api/bang-gia/${thang}/${nam}`);
    bangGia = bgRes.data;
    if (bangGia) {
      document.getElementById('bg-info').textContent =
        `Đơn giá: điện ${formatVND(bangGia.don_gia_dien)}/kWh, nước ${formatVND(bangGia.don_gia_nuoc)}/m³`;
    } else {
      document.getElementById('bg-info').textContent = '⚠️ Chưa có bảng giá tháng này';
    }
  } catch (e) { bangGia = null; }

  // Lấy danh sách thanh toán
  try {
    const { data } = await fetchAPI(`/api/thanh-toan/${thang}/${nam}`);
    ttData = data;
    renderTable(data);
  } catch (e) {
    showToast(e.message, 'danger');
  }
}

function renderTable(rows) {
  const tbody = document.getElementById('tt-tbody');
  if (!rows.length) {
    tbody.innerHTML = '<tr><td colspan="6" class="text-muted text-center py-4">Chưa có dữ liệu. Bấm "Tạo tháng mới" để khởi tạo.</td></tr>';
    document.getElementById('tfoot-tong').textContent = formatVND(0);
    return;
  }

  tbody.innerHTML = rows.map(tt => {
    const tamTinh = calcTamTinh(tt, tt.so_dien, tt.so_nuoc);
    const isDone  = tt.trang_thai === 'da_tt';
    return `
      <tr id="row-${tt.tt_id}">
        <td><strong>${tt.so_phong || '—'}</strong></td>
        <td>${tt.ho_ten || '—'}</td>
        <td class="text-end">
          <input type="number" class="inline-num" id="dien-${tt.tt_id}"
            value="${tt.so_dien}" min="0" step="0.1"
            onchange="autoSave(${tt.tt_id})"
            oninput="updateTamTinh(${tt.tt_id})">
        </td>
        <td class="text-end">
          <input type="number" class="inline-num" id="nuoc-${tt.tt_id}"
            value="${tt.so_nuoc}" min="0" step="0.1"
            onchange="autoSave(${tt.tt_id})"
            oninput="updateTamTinh(${tt.tt_id})">
        </td>
        <td class="text-end fw-semibold" id="tam-${tt.tt_id}">${formatVND(tamTinh)}</td>
        <td class="text-center">
          <button class="btn btn-sm ${isDone ? 'btn-success' : 'btn-outline-secondary'}"
            onclick="toggleTT(${tt.tt_id})" title="${isDone ? 'Click để hủy' : 'Click để đánh dấu đã TT'}">
            ${isDone ? '<i class="bi bi-check-circle-fill"></i> Đã TT' : '<i class="bi bi-circle"></i> Chưa TT'}
          </button>
        </td>
      </tr>`;
  }).join('');

  updateFooter();
}

function calcTamTinh(tt, dien, nuoc) {
  if (!bangGia || !tt) return 0;
  const giaPhong = tt.cap_phong === 'cap2' ? bangGia.gia_phong_cap2 : bangGia.gia_phong_cap1;
  const tienDien = (parseFloat(dien) || 0) * bangGia.don_gia_dien;
  const tienNuoc = (parseFloat(nuoc) || 0) * bangGia.don_gia_nuoc;
  const phi = bangGia.phi_wifi + bangGia.phi_ve_sinh + bangGia.phi_gui_xe;
  return giaPhong + tienDien + tienNuoc + phi;
}

function updateTamTinh(ttId) {
  const record = ttData.find(item => item.tt_id === ttId);
  const dien = parseFloat(document.getElementById(`dien-${ttId}`)?.value) || 0;
  const nuoc = parseFloat(document.getElementById(`nuoc-${ttId}`)?.value) || 0;
  const el   = document.getElementById(`tam-${ttId}`);
  if (record) {
    record.so_dien = dien;
    record.so_nuoc = nuoc;
  }
  if (el) el.textContent = formatVND(calcTamTinh(record, dien, nuoc));
  updateFooter();
}

function updateFooter() {
  let tong = 0;
  document.querySelectorAll('[id^="tam-"]').forEach(el => {
    const v = parseFloat(el.textContent.replace(/[^0-9]/g, '')) || 0;
    tong += v;
  });
  document.getElementById('tfoot-tong').textContent = formatVND(tong);
}

let saveTimers = {};
function autoSave(ttId) {
  clearTimeout(saveTimers[ttId]);
  saveTimers[ttId] = setTimeout(() => doSave(ttId), 800);
}

async function doSave(ttId) {
  const dien = parseFloat(document.getElementById(`dien-${ttId}`)?.value) || 0;
  const nuoc = parseFloat(document.getElementById(`nuoc-${ttId}`)?.value) || 0;
  try {
    const { data } = await fetchAPI(`/api/thanh-toan/${ttId}`, 'PUT', { so_dien: dien, so_nuoc: nuoc });
    const idx = ttData.findIndex(item => item.tt_id === ttId);
    if (idx >= 0) ttData[idx] = data;
  } catch (e) { showToast(e.message, 'danger'); }
}

async function toggleTT(ttId) {
  try {
    const { data } = await fetchAPI(`/api/thanh-toan/${ttId}/tick`, 'PATCH');
    const idx = ttData.findIndex(item => item.tt_id === ttId);
    if (idx >= 0) ttData[idx] = data;
    // Update row button
    const row = document.getElementById(`row-${ttId}`);
    const isDone = data.trang_thai === 'da_tt';
    const btn = row.querySelector('button');
    btn.className = `btn btn-sm ${isDone ? 'btn-success' : 'btn-outline-secondary'}`;
    btn.innerHTML = isDone
      ? '<i class="bi bi-check-circle-fill"></i> Đã TT'
      : '<i class="bi bi-circle"></i> Chưa TT';
  } catch (e) { showToast(e.message, 'danger'); }
}

async function taoThang() {
  const thang = parseInt(document.getElementById('sel-thang').value);
  const nam   = parseInt(document.getElementById('sel-nam').value);
  if (!confirm(`Tạo bản ghi thanh toán cho tháng ${thang}/${nam}?`)) return;
  try {
    const { data } = await fetchAPI('/api/thanh-toan/tao-thang', 'POST', { thang, nam });
    showToast(`Đã tạo ${data.created} bản ghi (bỏ qua ${data.skipped})`);
    loadTT();
  } catch (e) { showToast(e.message, 'danger'); }
}
