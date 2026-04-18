from flask import Blueprint, request, jsonify, send_file, current_app
from app.extensions import db
from app.models import HoaDon, ThanhToanThang
from app.services.invoice_service import generate_hoa_don
from app.utils import get_or_404
import io

bp = Blueprint('hoa_don', __name__)


def ok(data, status=200):
    return jsonify({'data': data, 'success': True}), status

def err(msg, status=400):
    return jsonify({'error': msg, 'success': False}), status


@bp.route('/<int:thang>/<int:nam>', methods=['GET'])
def list_hoa_don(thang, nam):
    records = (
        HoaDon.query
        .join(ThanhToanThang)
        .filter(ThanhToanThang.thang == thang, ThanhToanThang.nam == nam)
        .all()
    )
    return ok([h.to_dict() for h in records])


@bp.route('/detail/<int:hoadon_id>', methods=['GET'])
@bp.route('/<int:hoadon_id>', methods=['GET'])
def get_hoa_don(hoadon_id):
    hd = get_or_404(HoaDon, hoadon_id)
    return ok(hd.to_dict())


@bp.route('/<int:tt_id>/generate', methods=['POST'])
def generate(tt_id):
    try:
        hd = generate_hoa_don(tt_id)
        return ok(hd.to_dict(), 201)
    except ValueError as e:
        return err(str(e), 400)


@bp.route('/generate-all/<int:thang>/<int:nam>', methods=['POST'])
def generate_all(thang, nam):
    tts = ThanhToanThang.query.filter_by(thang=thang, nam=nam).all()
    results = []
    errors  = []
    for tt in tts:
        try:
            hd = generate_hoa_don(tt.tt_id)
            results.append(hd.to_dict())
        except ValueError as e:
            errors.append({'tt_id': tt.tt_id, 'error': str(e)})
    return ok({'generated': results, 'errors': errors})


@bp.route('/<int:hoadon_id>/pdf', methods=['GET'])
def export_pdf(hoadon_id):
    hd = get_or_404(HoaDon, hoadon_id)
    try:
        from app.services.pdf_service import generate_pdf_bytes
        pdf_bytes = generate_pdf_bytes(hd)
        tt = hd.thanh_toan
        filename = f"hoadon_{tt.hop_dong.phong.so_phong}_{tt.thang}_{tt.nam}.pdf"
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename,
        )
    except Exception as e:
        return err(f'Lỗi xuất PDF: {str(e)}', 500)
