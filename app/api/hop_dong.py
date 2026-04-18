from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import HopDong, Phong, KhachThue
from app.services.warning_service import update_all_hop_dong_status, get_sap_het_han
from app.utils import get_or_404
from datetime import date

bp = Blueprint('hop_dong', __name__)


def ok(data, status=200):
    return jsonify({'data': data, 'success': True}), status

def err(msg, status=400):
    return jsonify({'error': msg, 'success': False}), status


@bp.route('', methods=['GET'])
def list_hop_dong():
    update_all_hop_dong_status()
    trang_thai = request.args.get('trang_thai')
    q = HopDong.query
    if trang_thai:
        q = q.filter_by(trang_thai=trang_thai)
    hds = q.order_by(HopDong.ngay_bat_dau.desc()).all()
    return ok([h.to_dict() for h in hds])


@bp.route('/sap-het-han', methods=['GET'])
def sap_het_han():
    update_all_hop_dong_status()
    days = int(request.args.get('days', 30))
    hds = get_sap_het_han(days)
    return ok([h.to_dict() for h in hds])


@bp.route('/<int:hopdong_id>', methods=['GET'])
def get_hop_dong(hopdong_id):
    hd = get_or_404(HopDong, hopdong_id)
    hd.update_trang_thai()
    db.session.commit()
    return ok(hd.to_dict())


@bp.route('', methods=['POST'])
def create_hop_dong():
    body = request.get_json() or {}
    if not body.get('phong_id') or not body.get('khach_id') or not body.get('ngay_bat_dau'):
        return err('Thiếu thông tin: phong_id, khach_id, ngay_bat_dau', 400)

    phong = get_or_404(Phong, body['phong_id'])
    get_or_404(KhachThue, body['khach_id'])
    if phong.trang_thai == 'dang_thue':
        return err('Phòng đang được thuê', 400)
    if phong.trang_thai == 'sua_chua':
        return err('Phòng đang sửa chữa', 400)
    existing = HopDong.query.filter(
        HopDong.phong_id == body['phong_id'],
        HopDong.trang_thai.in_(['hieu_luc', 'sap_het_han'])
    ).first()
    if existing:
        return err('Phòng đang có hợp đồng hiệu lực', 400)

    # Parse ngày
    try:
        ngay_bd = date.fromisoformat(body['ngay_bat_dau'])
        ngay_kt = date.fromisoformat(body['ngay_ket_thuc']) if body.get('ngay_ket_thuc') else None
    except ValueError:
        return err('Định dạng ngày không hợp lệ (YYYY-MM-DD)', 400)
    if ngay_kt and ngay_kt < ngay_bd:
        return err('Ngày kết thúc phải lớn hơn hoặc bằng ngày bắt đầu', 400)

    hd = HopDong(
        phong_id      = body['phong_id'],
        khach_id      = body['khach_id'],
        ngay_bat_dau  = ngay_bd,
        ngay_ket_thuc = ngay_kt,
        ghi_chu       = body.get('ghi_chu'),
    )
    hd.update_trang_thai()

    # Rule 4: set phòng → đang thuê
    phong.trang_thai = 'dang_thue'

    db.session.add(hd)
    db.session.commit()
    return ok(hd.to_dict(), 201)


@bp.route('/<int:hopdong_id>', methods=['PUT'])
def update_hop_dong(hopdong_id):
    hd = get_or_404(HopDong, hopdong_id)
    body = request.get_json() or {}

    if 'ngay_ket_thuc' in body:
        try:
            hd.ngay_ket_thuc = date.fromisoformat(body['ngay_ket_thuc']) if body['ngay_ket_thuc'] else None
        except ValueError:
            return err('Định dạng ngày không hợp lệ', 400)
        if hd.ngay_ket_thuc and hd.ngay_ket_thuc < hd.ngay_bat_dau:
            return err('Ngày kết thúc phải lớn hơn hoặc bằng ngày bắt đầu', 400)

    if 'ghi_chu' in body:
        hd.ghi_chu = body['ghi_chu']

    # Kết thúc sớm
    if body.get('ket_thuc_som'):
        hd.ngay_ket_thuc = date.today()
        hd.trang_thai    = 'het_han'
        hd.phong.trang_thai = 'trong'
    else:
        hd.update_trang_thai()

    db.session.commit()
    return ok(hd.to_dict())
