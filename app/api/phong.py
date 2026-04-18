from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Phong, HopDong
from app.services.warning_service import update_all_hop_dong_status
from app.utils import get_or_404

bp = Blueprint('phong', __name__)


def ok(data, status=200):
    return jsonify({'data': data, 'success': True}), status

def err(msg, status=400):
    return jsonify({'error': msg, 'success': False}), status


@bp.route('', methods=['GET'])
def list_phong():
    update_all_hop_dong_status()
    trang_thai = request.args.get('trang_thai')
    q = Phong.query
    if trang_thai:
        q = q.filter_by(trang_thai=trang_thai)
    rooms = q.order_by(Phong.so_phong).all()
    return ok([r.to_dict() for r in rooms])


@bp.route('/grid', methods=['GET'])
def grid_phong():
    """Dữ liệu grid: mỗi phòng kèm tên khách đang thuê + ngày hết hạn."""
    update_all_hop_dong_status()
    trang_thai = request.args.get('trang_thai')
    q = Phong.query
    if trang_thai:
        q = q.filter_by(trang_thai=trang_thai)
    rooms = q.order_by(Phong.so_phong).all()
    result = []
    for r in rooms:
        d = r.to_dict()
        # Lấy hợp đồng hiệu lực
        active_hd = HopDong.query.filter(
            HopDong.phong_id == r.phong_id,
            HopDong.trang_thai.in_(['hieu_luc', 'sap_het_han'])
        ).first()
        if active_hd:
            d['khach_chinh']   = active_hd.khach.ho_ten
            d['ngay_het_han']  = str(active_hd.ngay_ket_thuc) if active_hd.ngay_ket_thuc else None
            d['days_remaining'] = active_hd.days_remaining()
            d['hopdong_id']    = active_hd.hopdong_id
        else:
            d['khach_chinh']   = None
            d['ngay_het_han']  = None
            d['days_remaining'] = None
            d['hopdong_id']    = None
        result.append(d)
    return ok(result)


@bp.route('/<int:phong_id>', methods=['GET'])
def get_phong(phong_id):
    update_all_hop_dong_status()
    p = get_or_404(Phong, phong_id)
    return ok(p.to_dict())


@bp.route('', methods=['POST'])
def create_phong():
    body = request.get_json() or {}
    if not body.get('so_phong'):
        return err('Thiếu số phòng', 400)
    if Phong.query.filter_by(so_phong=body['so_phong']).first():
        return err(f"Số phòng '{body['so_phong']}' đã tồn tại", 409)

    p = Phong(
        so_phong  = body['so_phong'],
        tang      = body.get('tang', 1),
        dien_tich = body.get('dien_tich'),
        cap_phong = body.get('cap_phong', 'cap1'),
        trang_thai= body.get('trang_thai', 'trong'),
        mo_ta     = body.get('mo_ta'),
    )
    db.session.add(p)
    db.session.commit()
    return ok(p.to_dict(), 201)


@bp.route('/<int:phong_id>', methods=['PUT'])
def update_phong(phong_id):
    p = get_or_404(Phong, phong_id)
    body = request.get_json() or {}
    if body.get('so_phong'):
        dup = Phong.query.filter(
            Phong.so_phong == body['so_phong'],
            Phong.phong_id != phong_id,
        ).first()
        if dup:
            return err(f"Số phòng '{body['so_phong']}' đã tồn tại", 409)
    fields = ['so_phong', 'tang', 'dien_tich', 'cap_phong', 'trang_thai', 'mo_ta']
    for f in fields:
        if f in body:
            setattr(p, f, body[f])
    db.session.commit()
    return ok(p.to_dict())


@bp.route('/<int:phong_id>', methods=['DELETE'])
def delete_phong(phong_id):
    update_all_hop_dong_status()
    p = get_or_404(Phong, phong_id)
    active_hd = HopDong.query.filter(
        HopDong.phong_id == phong_id,
        HopDong.trang_thai.in_(['hieu_luc', 'sap_het_han'])
    ).first()
    if active_hd:
        return err('Không thể xóa phòng đang có hợp đồng hiệu lực', 400)
    if HopDong.query.filter_by(phong_id=phong_id).first():
        return err('Không thể xóa phòng đã có lịch sử hợp đồng', 400)
    db.session.delete(p)
    db.session.commit()
    return ok({'deleted': phong_id})
