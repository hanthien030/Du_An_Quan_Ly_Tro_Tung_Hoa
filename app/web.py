from flask import Blueprint, redirect, render_template, request, url_for

from app.extensions import db
from app.models import HoaDon, Phong
from app.utils import get_or_404

web_bp = Blueprint('web', __name__)

ROOM_LEVELS = {'cap1', 'cap2'}
ROOM_STATUSES = {'trong', 'dang_thue', 'sua_chua'}


def _room_form_data(source=None):
    source = source or {}
    if hasattr(source, 'so_phong'):
        return {
            'so_phong': source.so_phong or '',
            'tang': source.tang or 1,
            'dien_tich': source.dien_tich if source.dien_tich is not None else '',
            'cap_phong': source.cap_phong or 'cap1',
            'trang_thai': source.trang_thai or 'trong',
            'mo_ta': source.mo_ta or '',
        }

    return {
        'so_phong': (source.get('so_phong') or '').strip(),
        'tang': source.get('tang') or 1,
        'dien_tich': source.get('dien_tich') or '',
        'cap_phong': source.get('cap_phong') or 'cap1',
        'trang_thai': source.get('trang_thai') or 'trong',
        'mo_ta': (source.get('mo_ta') or '').strip(),
    }


def _save_room_from_form(phong=None):
    form_data = _room_form_data(request.form)
    so_phong = form_data['so_phong']
    if not so_phong:
        return None, 'Thiếu số phòng', form_data

    try:
        tang = int(form_data['tang'])
        if tang < 1:
            raise ValueError
    except (TypeError, ValueError):
        return None, 'Tầng phải là số nguyên dương', form_data

    dien_tich = None
    if str(form_data['dien_tich']).strip():
        try:
            dien_tich = float(form_data['dien_tich'])
        except ValueError:
            return None, 'Diện tích phải là số hợp lệ', form_data

    if form_data['cap_phong'] not in ROOM_LEVELS:
        return None, 'Cấp phòng không hợp lệ', form_data

    if form_data['trang_thai'] not in ROOM_STATUSES:
        return None, 'Trạng thái phòng không hợp lệ', form_data

    duplicate_query = Phong.query.filter(Phong.so_phong == so_phong)
    if phong is not None:
        duplicate_query = duplicate_query.filter(Phong.phong_id != phong.phong_id)
    if duplicate_query.first():
        return None, f"Số phòng '{so_phong}' đã tồn tại", form_data

    phong = phong or Phong()
    phong.so_phong = so_phong
    phong.tang = tang
    phong.dien_tich = dien_tich
    phong.cap_phong = form_data['cap_phong']
    phong.trang_thai = form_data['trang_thai']
    phong.mo_ta = form_data['mo_ta']

    if phong.phong_id is None:
        db.session.add(phong)
    db.session.commit()
    return phong, None, _room_form_data(phong)


@web_bp.route('/')
@web_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@web_bp.route('/phong')
def phong_index():
    return render_template('phong/index.html')


@web_bp.route('/phong/form', methods=['GET', 'POST'])
def phong_form_create():
    if request.method == 'POST':
        phong, error, form_data = _save_room_from_form()
        if not error:
            return redirect(url_for('web.phong_index'))
        return render_template(
            'phong/form.html',
            room_data=form_data,
            error=error,
            form_mode='create',
            form_action=url_for('web.phong_form_create'),
        )

    return render_template(
        'phong/form.html',
        room_data=_room_form_data(),
        error=None,
        form_mode='create',
        form_action=url_for('web.phong_form_create'),
    )


@web_bp.route('/phong/form/<int:phong_id>', methods=['GET', 'POST'])
def phong_form_edit(phong_id):
    phong = get_or_404(Phong, phong_id)
    if request.method == 'POST':
        phong, error, form_data = _save_room_from_form(phong)
        if not error:
            return redirect(url_for('web.phong_index'))
        return render_template(
            'phong/form.html',
            room_data=form_data,
            error=error,
            form_mode='edit',
            form_action=url_for('web.phong_form_edit', phong_id=phong_id),
            phong_id=phong_id,
        )

    return render_template(
        'phong/form.html',
        room_data=_room_form_data(phong),
        error=None,
        form_mode='edit',
        form_action=url_for('web.phong_form_edit', phong_id=phong_id),
        phong_id=phong_id,
    )


@web_bp.route('/khach-thue')
def khach_thue_index():
    return render_template('khach_thue/index.html')


@web_bp.route('/hop-dong')
def hop_dong_index():
    return render_template('hop_dong/index.html')


@web_bp.route('/bang-gia')
def bang_gia_index():
    return render_template('bang_gia/index.html')


@web_bp.route('/thanh-toan')
def thanh_toan_index():
    return render_template('thanh_toan/index.html')


@web_bp.route('/hoa-don')
def hoa_don_index():
    return render_template('hoa_don/index.html')


@web_bp.route('/hoa-don/detail/<int:hoadon_id>')
def hoa_don_detail_page(hoadon_id):
    hoa_don = get_or_404(HoaDon, hoadon_id)
    return render_template('hoa_don/detail.html', hd=hoa_don.to_dict())


@web_bp.route('/thong-ke')
def thong_ke_index():
    return render_template('thong_ke/index.html')
