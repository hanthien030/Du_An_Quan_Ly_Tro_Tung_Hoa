from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import KhachThue, HopDong, Phong
from app.services.warning_service import update_all_hop_dong_status
from app.utils import get_or_404
from datetime import date

bp = Blueprint('khach_thue', __name__)


def ok(data, status=200):
    return jsonify({'data': data, 'success': True}), status

def err(msg, status=400):
    return jsonify({'error': msg, 'success': False}), status


def parse_optional_date(raw_value):
    if not raw_value:
        return None
    try:
        return date.fromisoformat(raw_value)
    except ValueError:
        raise ValueError('Định dạng ngày không hợp lệ (YYYY-MM-DD)')


@bp.route('', methods=['GET'])
def list_khach():
    update_all_hop_dong_status()
    q_str    = request.args.get('q', '').strip()
    so_phong = request.args.get('so_phong', '').strip()

    query = KhachThue.query

    if q_str:
        like = f'%{q_str}%'
        query = query.filter(
            db.or_(
                KhachThue.ho_ten.ilike(like),
                KhachThue.cccd.ilike(like),
                KhachThue.sdt.ilike(like),
            )
        )
    if so_phong:
        # Lọc theo số phòng qua HopDong
        phong = Phong.query.filter_by(so_phong=so_phong).first()
        if phong:
            khach_ids = db.session.query(HopDong.khach_id).filter_by(phong_id=phong.phong_id).subquery()
            query = query.filter(KhachThue.khach_id.in_(khach_ids))
        else:
            return ok([])

    khachs = query.order_by(KhachThue.ho_ten).all()

    # Thêm thông tin phòng hiện tại
    result = []
    for k in khachs:
        d = k.to_dict()
        active = HopDong.query.filter(
            HopDong.khach_id == k.khach_id,
            HopDong.trang_thai.in_(['hieu_luc', 'sap_het_han'])
        ).first()
        d['so_phong_hien_tai'] = active.phong.so_phong if active else None
        d['hopdong_id']        = active.hopdong_id if active else None
        result.append(d)
    return ok(result)


@bp.route('/<int:khach_id>', methods=['GET'])
def get_khach(khach_id):
    update_all_hop_dong_status()
    k = get_or_404(KhachThue, khach_id)
    return ok(k.to_dict())


@bp.route('', methods=['POST'])
def create_khach():
    body = request.get_json() or {}
    if not body.get('ho_ten'):
        return err('Thiếu họ tên', 400)
    if body.get('cccd') and KhachThue.query.filter_by(cccd=body['cccd']).first():
        return err('CCCD đã tồn tại', 409)

    try:
        ngay_sinh = parse_optional_date(body.get('ngay_sinh'))
    except ValueError as exc:
        return err(str(exc), 400)

    k = KhachThue(
        ho_ten    = body['ho_ten'],
        cccd      = body.get('cccd'),
        ngay_sinh = ngay_sinh,
        sdt       = body.get('sdt'),
        dia_chi   = body.get('dia_chi'),
        email     = body.get('email'),
        la_chinh  = body.get('la_chinh', True),
    )
    db.session.add(k)
    db.session.commit()
    return ok(k.to_dict(), 201)


@bp.route('/<int:khach_id>', methods=['PUT'])
def update_khach(khach_id):
    k = get_or_404(KhachThue, khach_id)
    body = request.get_json() or {}
    if body.get('cccd'):
        dup = KhachThue.query.filter(
            KhachThue.cccd == body['cccd'],
            KhachThue.khach_id != khach_id,
        ).first()
        if dup:
            return err('CCCD đã tồn tại', 409)

    try:
        ngay_sinh = parse_optional_date(body.get('ngay_sinh')) if 'ngay_sinh' in body else None
    except ValueError as exc:
        return err(str(exc), 400)

    fields = ['ho_ten', 'cccd', 'sdt', 'dia_chi', 'email', 'la_chinh']
    for f in fields:
        if f in body:
            setattr(k, f, body[f])
    if 'ngay_sinh' in body:
        k.ngay_sinh = ngay_sinh
    db.session.commit()
    return ok(k.to_dict())


@bp.route('/<int:khach_id>', methods=['DELETE'])
def delete_khach(khach_id):
    k = get_or_404(KhachThue, khach_id)
    active = HopDong.query.filter(
        HopDong.khach_id == khach_id,
        HopDong.trang_thai.in_(['hieu_luc', 'sap_het_han'])
    ).first()
    if active:
        return err('Khách đang có hợp đồng hiệu lực, không thể xóa', 400)
    if HopDong.query.filter_by(khach_id=khach_id).first():
        return err('Không thể xóa khách đã có lịch sử hợp đồng', 400)
    db.session.delete(k)
    db.session.commit()
    return ok({'deleted': khach_id})
