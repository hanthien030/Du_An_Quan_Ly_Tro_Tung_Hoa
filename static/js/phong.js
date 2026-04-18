/* phong.js */
let roomModal, detailModal, currentRoom;

document.addEventListener('DOMContentLoaded', () => {
  roomModal = new bootstrap.Modal(document.getElementById('roomModal'));
  detailModal = new bootstrap.Modal(document.getElementById('detailModal'));
  loadRooms();
});

async function loadRooms() {
  const tt = document.getElementById('filter-tt').value;
  const url = tt ? `/api/phong/grid?trang_thai=${tt}` : '/api/phong/grid';
  try {
    const { data } = await fetchAPI(url);
    renderGrid(data);
  } catch (e) {
    showToast(e.message, 'danger');
  }
}

function renderGrid(rooms) {
  const grid = document.getElementById('room-grid');
  if (!rooms.length) {
    grid.innerHTML = '<div class="col text-muted">Không có phòng nào.</div>';
    return;
  }
  grid.innerHTML = rooms.map(r => {
    const statusLabel = { trong: 'Trống', dang_thue: 'Đang thuê', sua_chua: 'Sửa chữa' }[r.trang_thai] || r.trang_thai;
    const statusColor = { trong: 'secondary', dang_thue: 'success', sua_chua: 'danger' }[r.trang_thai] || 'secondary';
    const cap = r.cap_phong === 'cap2' ? 'Cấp 2' : 'Cấp 1';
    const khach = r.khach_chinh ? `<div class="small text-truncate">${r.khach_chinh}</div>` : '<div class="small text-muted">—</div>';
    const days = r.days_remaining != null ? `<div class="small text-muted">${r.days_remaining} ngày</div>` : '';
    return `
      <div class="col-6 col-sm-4 col-md-3 col-lg-2">
        <div class="room-card status-${r.trang_thai} p-3 text-center" onclick="showDetail(${r.phong_id})">
          <div class="fw-bold fs-5">${r.so_phong}</div>
          <div class="text-muted small">${cap}</div>
          <span class="badge bg-${statusColor} room-badge mt-1">${statusLabel}</span>
          ${khach}
          ${days}
        </div>
      </div>`;
  }).join('');
}

async function showDetail(id) {
  try {
    const { data: r } = await fetchAPI(`/api/phong/${id}`);
    currentRoom = r;
    document.getElementById('detail-title').textContent = `Phòng ${r.so_phong}`;
    document.getElementById('detail-body').innerHTML = `
      <dl class="row mb-0 small">
        <dt class="col-5">Tầng</dt><dd class="col-7">${r.tang}</dd>
        <dt class="col-5">Diện tích</dt><dd class="col-7">${r.dien_tich ? r.dien_tich + ' m²' : '—'}</dd>
        <dt class="col-5">Cấp phòng</dt><dd class="col-7">${r.cap_phong === 'cap2' ? 'Cấp 2' : 'Cấp 1'}</dd>
        <dt class="col-5">Trạng thái</dt><dd class="col-7">${r.trang_thai}</dd>
        <dt class="col-5">Ghi chú</dt><dd class="col-7">${r.mo_ta || '—'}</dd>
      </dl>`;
    document.getElementById('btn-edit-detail').onclick = () => { window.location.href = `/phong/form/${r.phong_id}`; };
    document.getElementById('btn-edit-modal').onclick = () => { detailModal.hide(); openModal(r); };
    document.getElementById('btn-del-detail').onclick = () => deleteRoom(r.phong_id);
    detailModal.show();
  } catch (e) {
    showToast(e.message, 'danger');
  }
}

function openModal(room = null) {
  document.getElementById('modal-title').textContent = room ? 'Sửa Phòng' : 'Thêm Phòng';
  document.getElementById('edit-id').value = room?.phong_id || '';
  document.getElementById('f-so_phong').value = room?.so_phong || '';
  document.getElementById('f-tang').value = room?.tang || 1;
  document.getElementById('f-dien_tich').value = room?.dien_tich || '';
  document.getElementById('f-mo_ta').value = room?.mo_ta || '';
  document.getElementById('f-trang_thai').value = room?.trang_thai || 'trong';
  document.querySelector(`input[name="cap"][value="${room?.cap_phong || 'cap1'}"]`).checked = true;
  roomModal.show();
}

async function saveRoom() {
  const id = document.getElementById('edit-id').value;
  const body = {
    so_phong: document.getElementById('f-so_phong').value.trim(),
    tang: parseInt(document.getElementById('f-tang').value),
    dien_tich: parseFloat(document.getElementById('f-dien_tich').value) || null,
    cap_phong: document.querySelector('input[name="cap"]:checked').value,
    trang_thai: document.getElementById('f-trang_thai').value,
    mo_ta: document.getElementById('f-mo_ta').value.trim(),
  };
  if (!body.so_phong) {
    showToast('Nhập số phòng', 'warning');
    return;
  }
  try {
    if (id) {
      await fetchAPI(`/api/phong/${id}`, 'PUT', body);
      showToast('Đã cập nhật phòng');
    } else {
      await fetchAPI('/api/phong', 'POST', body);
      showToast('Đã thêm phòng');
    }
    roomModal.hide();
    loadRooms();
  } catch (e) {
    showToast(e.message, 'danger');
  }
}

async function deleteRoom(id) {
  if (!confirm('Xóa phòng này?')) return;
  try {
    await fetchAPI(`/api/phong/${id}`, 'DELETE');
    showToast('Đã xóa phòng');
    detailModal.hide();
    loadRooms();
  } catch (e) {
    showToast(e.message, 'danger');
  }
}
