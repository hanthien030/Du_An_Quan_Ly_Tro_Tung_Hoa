from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import ThanhToanThang, HopDong
from app.services.warning_service import update_all_hop_dong_status
from app.utils import get_or_404
from datetime import date

bp = Blueprint('thanh_toan', __name__)


def ok(data, status=200):
    return jsonify({'data': data, 'success': True}), status

def err(msg, status=400):
    return jsonify({'error': msg, 'success': False}), status


@bp.route('/<int:thang>/<int:nam>', methods=['GET'])
def list_thanh_toan(thang, nam):
    update_all_hop_dong_status()
    records = (
        ThanhToanThang.query
        .filter_by(thang=thang, nam=nam)
        .join(HopDong)
        .join(HopDong.phong)
        .order_by(HopDong.phong_id.asc())
        .all()
    )
    return ok([r.to_dict() for r in records])


@bp.route('/tao-thang', methods=['POST'])
def tao_thang():
    """Rule 5: Tạo bản ghi thanh toán cho tất cả hợp đồng hiệu lực/sắp hết hạn."""
    body = request.get_json() or {}
    if not body.get('thang') or not body.get('nam'):
        return err('Thiếu thang/nam', 400)

    thang, nam = body['thang'], body['nam']
    update_all_hop_dong_status()

    # Lấy các hợp đồng đang active
    hds = HopDong.query.filter(
        HopDong.trang_thai.in_(['hieu_luc', 'sap_het_han'])
    ).all()

    created, skipped = 0, 0
    for hd in hds:
        existing = ThanhToanThang.query.filter_by(
            hopdong_id=hd.hopdong_id, thang=thang, nam=nam
        ).first()
        if existing:
            skipped += 1
            continue
        tt = ThanhToanThang(
            hopdong_id=hd.hopdong_id,
            thang=thang,
            nam=nam,
            so_dien=0,
            so_nuoc=0,
            trang_thai='chua_tt',
        )
        db.session.add(tt)
        created += 1

    db.session.commit()
    return ok({'created': created, 'skipped': skipped}, 201)


@bp.route('/<int:tt_id>', methods=['PUT'])
def update_thanh_toan(tt_id):
    tt = get_or_404(ThanhToanThang, tt_id)
    body = request.get_json() or {}
    if 'so_dien' in body:
        tt.so_dien = float(body['so_dien'])
    if 'so_nuoc' in body:
        tt.so_nuoc = float(body['so_nuoc'])
    if 'trang_thai' in body:
        tt.trang_thai = body['trang_thai']
        if body['trang_thai'] == 'da_tt' and not tt.ngay_thanh_toan:
            tt.ngay_thanh_toan = date.today()
        if body['trang_thai'] == 'chua_tt':
            tt.ngay_thanh_toan = None
    if 'ghi_chu' in body:
        tt.ghi_chu = body['ghi_chu']
    db.session.commit()
    return ok(tt.to_dict())


@bp.route('/<int:tt_id>/tick', methods=['PATCH'])
def tick_thanh_toan(tt_id):
    tt = get_or_404(ThanhToanThang, tt_id)
    if tt.trang_thai == 'chua_tt':
        tt.trang_thai      = 'da_tt'
        tt.ngay_thanh_toan = date.today()
    else:
        tt.trang_thai      = 'chua_tt'
        tt.ngay_thanh_toan = None
    db.session.commit()
    return ok(tt.to_dict())
