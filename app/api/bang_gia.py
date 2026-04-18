from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import BangGia
from app.utils import get_or_404

bp = Blueprint('bang_gia', __name__)


def ok(data, status=200):
    return jsonify({'data': data, 'success': True}), status

def err(msg, status=400):
    return jsonify({'error': msg, 'success': False}), status


@bp.route('', methods=['GET'])
def list_bang_gia():
    bgs = BangGia.query.order_by(BangGia.nam.desc(), BangGia.thang.desc()).all()
    return ok([b.to_dict() for b in bgs])


@bp.route('/<int:thang>/<int:nam>', methods=['GET'])
def get_bang_gia(thang, nam):
    bg = BangGia.query.filter_by(thang=thang, nam=nam).first()
    if not bg:
        return ok(None)
    return ok(bg.to_dict())


@bp.route('', methods=['POST'])
def create_bang_gia():
    body = request.get_json() or {}
    required = ['thang', 'nam', 'gia_phong_cap1', 'gia_phong_cap2', 'don_gia_dien', 'don_gia_nuoc']
    for f in required:
        if body.get(f) is None:
            return err(f'Thiếu trường: {f}', 400)

    if BangGia.query.filter_by(thang=body['thang'], nam=body['nam']).first():
        return err(f"Bảng giá tháng {body['thang']}/{body['nam']} đã tồn tại", 409)

    bg = BangGia(
        thang          = body['thang'],
        nam            = body['nam'],
        gia_phong_cap1 = body['gia_phong_cap1'],
        gia_phong_cap2 = body['gia_phong_cap2'],
        don_gia_dien   = body['don_gia_dien'],
        don_gia_nuoc   = body['don_gia_nuoc'],
        phi_wifi       = body.get('phi_wifi', 0),
        phi_ve_sinh    = body.get('phi_ve_sinh', 0),
        phi_gui_xe     = body.get('phi_gui_xe', 0),
    )
    db.session.add(bg)
    db.session.commit()
    return ok(bg.to_dict(), 201)


@bp.route('/<int:bangia_id>', methods=['PUT'])
def update_bang_gia(bangia_id):
    bg = get_or_404(BangGia, bangia_id)
    # Rule 1: chặn sửa nếu đã khóa
    if bg.is_locked:
        return jsonify({'error': 'Bảng giá đã bị khóa (đã có hóa đơn). Không thể chỉnh sửa.', 'success': False}), 423

    body = request.get_json() or {}
    fields = ['gia_phong_cap1', 'gia_phong_cap2', 'don_gia_dien', 'don_gia_nuoc',
              'phi_wifi', 'phi_ve_sinh', 'phi_gui_xe']
    for f in fields:
        if f in body:
            setattr(bg, f, body[f])
    db.session.commit()
    return ok(bg.to_dict())


@bp.route('/copy', methods=['POST'])
def copy_bang_gia():
    """Sao chép bảng giá từ tháng trước sang tháng mới."""
    body = request.get_json() or {}
    required = ['from_thang', 'from_nam', 'to_thang', 'to_nam']
    for f in required:
        if body.get(f) is None:
            return err(f'Thiếu: {f}', 400)

    src = BangGia.query.filter_by(thang=body['from_thang'], nam=body['from_nam']).first()
    if not src:
        return err(f"Không tìm thấy bảng giá tháng {body['from_thang']}/{body['from_nam']}", 404)

    if BangGia.query.filter_by(thang=body['to_thang'], nam=body['to_nam']).first():
        return err(f"Bảng giá tháng {body['to_thang']}/{body['to_nam']} đã tồn tại", 409)

    new_bg = BangGia(
        thang          = body['to_thang'],
        nam            = body['to_nam'],
        gia_phong_cap1 = src.gia_phong_cap1,
        gia_phong_cap2 = src.gia_phong_cap2,
        don_gia_dien   = src.don_gia_dien,
        don_gia_nuoc   = src.don_gia_nuoc,
        phi_wifi       = src.phi_wifi,
        phi_ve_sinh    = src.phi_ve_sinh,
        phi_gui_xe     = src.phi_gui_xe,
    )
    db.session.add(new_bg)
    db.session.commit()
    return ok(new_bg.to_dict(), 201)
