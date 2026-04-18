from datetime import date
from decimal import Decimal

from app.extensions import db
from app.models import BangGia, HoaDon, ThanhToanThang
from app.utils import get_or_404


def _to_decimal(value):
    return Decimal(str(value or 0))


def tinh_hoa_don(thanh_toan):
    bang_gia = BangGia.query.filter_by(
        thang=thanh_toan.thang,
        nam=thanh_toan.nam,
    ).first()
    if not bang_gia:
        raise ValueError('Chua co bang gia cho thang nay')

    hop_dong = thanh_toan.hop_dong
    phong = hop_dong.phong

    gia_phong = bang_gia.gia_phong_cap1 if phong.cap_phong == 'cap1' else bang_gia.gia_phong_cap2
    tien_dien = _to_decimal(thanh_toan.so_dien) * _to_decimal(bang_gia.don_gia_dien)
    tien_nuoc = _to_decimal(thanh_toan.so_nuoc) * _to_decimal(bang_gia.don_gia_nuoc)
    phi_dv = (
        _to_decimal(bang_gia.phi_wifi)
        + _to_decimal(bang_gia.phi_ve_sinh)
        + _to_decimal(bang_gia.phi_gui_xe)
    )
    tong = _to_decimal(gia_phong) + tien_dien + tien_nuoc + phi_dv

    return {
        'tien_phong': gia_phong,
        'tien_dien': tien_dien,
        'tien_nuoc': tien_nuoc,
        'phi_dich_vu': phi_dv,
        'tong_tien': tong,
        'snapshot_don_gia_dien': bang_gia.don_gia_dien,
        'snapshot_don_gia_nuoc': bang_gia.don_gia_nuoc,
        'snapshot_gia_phong': gia_phong,
    }


def generate_hoa_don(tt_id):
    thanh_toan = get_or_404(ThanhToanThang, tt_id)
    payload = tinh_hoa_don(thanh_toan)

    hoa_don = HoaDon.query.filter_by(tt_id=tt_id).first()
    if not hoa_don:
        hoa_don = HoaDon(tt_id=tt_id)
        db.session.add(hoa_don)

    for key, value in payload.items():
        setattr(hoa_don, key, value)
    hoa_don.ngay_tao = date.today()

    bang_gia = BangGia.query.filter_by(
        thang=thanh_toan.thang,
        nam=thanh_toan.nam,
    ).first()
    if bang_gia:
        bang_gia.is_locked = True

    db.session.commit()
    return hoa_don
