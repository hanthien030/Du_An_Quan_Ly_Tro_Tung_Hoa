from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Phong, HopDong, ThanhToanThang, HoaDon, BangGia
from app.services.warning_service import update_all_hop_dong_status
from sqlalchemy import func
from datetime import date

bp = Blueprint('thong_ke', __name__)


def ok(data, status=200):
    return jsonify({'data': data, 'success': True}), status


@bp.route('/dashboard', methods=['GET'])
def dashboard():
    update_all_hop_dong_status()
    today = date.today()
    thang, nam = today.month, today.year

    tong_phong      = Phong.query.count()
    phong_dang_thue = Phong.query.filter_by(trang_thai='dang_thue').count()
    phong_trong     = Phong.query.filter_by(trang_thai='trong').count()

    # Doanh thu tháng hiện tại — tổng tong_tien của các hóa đơn tháng này
    doanh_thu = db.session.query(func.sum(HoaDon.tong_tien))\
        .join(ThanhToanThang)\
        .filter(ThanhToanThang.thang == thang, ThanhToanThang.nam == nam)\
        .scalar() or 0

    # Phòng chưa đóng tiền tháng này
    chua_dong = ThanhToanThang.query.filter_by(
        thang=thang, nam=nam, trang_thai='chua_tt'
    ).count()

    # Hợp đồng sắp hết hạn (≤ 30 ngày)
    sap_het_han = HopDong.query.filter_by(trang_thai='sap_het_han').count()

    return ok({
        'tong_phong':          tong_phong,
        'phong_dang_thue':     phong_dang_thue,
        'phong_trong':         phong_trong,
        'doanh_thu_thang_nay': float(doanh_thu),
        'chua_dong_tien':      chua_dong,
        'sap_het_han':         sap_het_han,
        'thang':               thang,
        'nam':                 nam,
    })


@bp.route('/doanh-thu', methods=['GET'])
def doanh_thu():
    update_all_hop_dong_status()
    months = int(request.args.get('months', 6))
    today  = date.today()

    result = []
    for i in range(months - 1, -1, -1):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1

        tong = db.session.query(func.sum(HoaDon.tong_tien))\
            .join(ThanhToanThang)\
            .filter(ThanhToanThang.thang == m, ThanhToanThang.nam == y)\
            .scalar() or 0

        so_hd = db.session.query(func.count(HoaDon.hoadon_id))\
            .join(ThanhToanThang)\
            .filter(ThanhToanThang.thang == m, ThanhToanThang.nam == y)\
            .scalar() or 0

        result.append({
            'thang': m,
            'nam':   y,
            'label': f'{m}/{y}',
            'doanh_thu': float(tong),
            'so_hoa_don': so_hd,
        })

    return ok(result)


@bp.route('/chua-dong/<int:thang>/<int:nam>', methods=['GET'])
def chua_dong(thang, nam):
    update_all_hop_dong_status()
    records = ThanhToanThang.query.filter_by(
        thang=thang, nam=nam, trang_thai='chua_tt'
    ).all()

    result = []
    for tt in records:
        hd = tt.hop_dong
        result.append({
            'tt_id':    tt.tt_id,
            'so_phong': hd.phong.so_phong,
            'ho_ten':   hd.khach.ho_ten,
            'thang':    tt.thang,
            'nam':      tt.nam,
        })
    return ok(result)
