from datetime import date, timedelta
from decimal import Decimal

import pytest

from app.extensions import db
from app.models import BangGia, HoaDon, HopDong, KhachThue, Phong, ThanhToanThang
from app.services.invoice_service import generate_hoa_don, tinh_hoa_don


def _create_invoice_context(
    *,
    so_phong,
    cap_phong,
    thang=4,
    nam=2026,
    so_dien=40,
    so_nuoc=2,
    include_bang_gia=True,
):
    phong = Phong(
        so_phong=so_phong,
        tang=1,
        dien_tich=18,
        cap_phong=cap_phong,
        trang_thai="dang_thue",
    )
    khach = KhachThue(
        ho_ten=f"Khach {so_phong}",
        cccd=f"{so_phong}999999",
        sdt="0900000000",
        la_chinh=True,
    )
    hop_dong = HopDong(
        phong=phong,
        khach=khach,
        ngay_bat_dau=date.today() - timedelta(days=10),
        ngay_ket_thuc=date.today() + timedelta(days=50),
        trang_thai="hieu_luc",
    )
    thanh_toan = ThanhToanThang(
        hop_dong=hop_dong,
        thang=thang,
        nam=nam,
        so_dien=so_dien,
        so_nuoc=so_nuoc,
        trang_thai="chua_tt",
    )
    db.session.add_all([phong, khach, hop_dong, thanh_toan])

    bang_gia = None
    if include_bang_gia:
        bang_gia = BangGia(
            thang=thang,
            nam=nam,
            gia_phong_cap1=Decimal("2500000"),
            gia_phong_cap2=Decimal("3500000"),
            don_gia_dien=Decimal("3500"),
            don_gia_nuoc=Decimal("15000"),
            phi_wifi=Decimal("100000"),
            phi_ve_sinh=Decimal("50000"),
            phi_gui_xe=Decimal("50000"),
            is_locked=False,
        )
        db.session.add(bang_gia)

    db.session.commit()
    return phong, khach, hop_dong, thanh_toan, bang_gia


def test_tinh_hoa_don_uses_cap1_price_and_rule2_formula(app):
    with app.app_context():
        _, _, _, thanh_toan, _ = _create_invoice_context(
            so_phong="S101",
            cap_phong="cap1",
            so_dien=40,
            so_nuoc=2.5,
        )

        result = tinh_hoa_don(thanh_toan)

        assert result["tien_phong"] == Decimal("2500000")
        assert result["tien_dien"] == Decimal("140000")
        assert result["tien_nuoc"] == Decimal("37500.0")
        assert result["phi_dich_vu"] == Decimal("200000")
        assert result["tong_tien"] == Decimal("2877500.0")
        assert result["snapshot_don_gia_dien"] == Decimal("3500")
        assert result["snapshot_don_gia_nuoc"] == Decimal("15000")
        assert result["snapshot_gia_phong"] == Decimal("2500000")


def test_tinh_hoa_don_uses_cap2_price_and_rule2_formula(app):
    with app.app_context():
        _, _, _, thanh_toan, _ = _create_invoice_context(
            so_phong="S201",
            cap_phong="cap2",
            so_dien=55,
            so_nuoc=3.25,
        )

        result = tinh_hoa_don(thanh_toan)

        assert result["tien_phong"] == Decimal("3500000")
        assert result["tien_dien"] == Decimal("192500")
        assert result["tien_nuoc"] == Decimal("48750.00")
        assert result["phi_dich_vu"] == Decimal("200000")
        assert result["tong_tien"] == Decimal("3941250.00")
        assert result["snapshot_don_gia_dien"] == Decimal("3500")
        assert result["snapshot_don_gia_nuoc"] == Decimal("15000")
        assert result["snapshot_gia_phong"] == Decimal("3500000")


def test_tinh_hoa_don_raises_when_month_has_no_bang_gia(app):
    with app.app_context():
        _, _, _, thanh_toan, _ = _create_invoice_context(
            so_phong="S301",
            cap_phong="cap1",
            include_bang_gia=False,
        )

        with pytest.raises(ValueError, match="Chua co bang gia cho thang nay"):
            tinh_hoa_don(thanh_toan)


def test_generate_hoa_don_creates_invoice_locks_bang_gia_and_saves_snapshots(app):
    with app.app_context():
        _, _, _, thanh_toan, bang_gia = _create_invoice_context(
            so_phong="S401",
            cap_phong="cap2",
            so_dien=60,
            so_nuoc=3,
        )

        hoa_don = generate_hoa_don(thanh_toan.tt_id)

        saved = db.session.get(HoaDon, hoa_don.hoadon_id)
        assert saved is not None
        assert HoaDon.query.count() == 1
        assert saved.tt_id == thanh_toan.tt_id
        assert saved.tien_phong == Decimal("3500000")
        assert saved.tien_dien == Decimal("210000")
        assert saved.tien_nuoc == Decimal("45000")
        assert saved.phi_dich_vu == Decimal("200000")
        assert saved.tong_tien == Decimal("3955000")
        assert saved.snapshot_don_gia_dien == Decimal("3500")
        assert saved.snapshot_don_gia_nuoc == Decimal("15000")
        assert saved.snapshot_gia_phong == Decimal("3500000")
        assert saved.ngay_tao == date.today()

        db.session.refresh(bang_gia)
        assert bang_gia.is_locked is True


def test_generate_hoa_don_updates_existing_invoice_instead_of_creating_duplicate(app):
    with app.app_context():
        _, _, _, thanh_toan, bang_gia = _create_invoice_context(
            so_phong="S402",
            cap_phong="cap1",
            so_dien=10,
            so_nuoc=1,
        )

        first_invoice = generate_hoa_don(thanh_toan.tt_id)
        first_invoice_id = first_invoice.hoadon_id

        thanh_toan.so_dien = 70
        thanh_toan.so_nuoc = 4
        bang_gia.don_gia_dien = Decimal("4000")
        bang_gia.phi_wifi = Decimal("120000")
        db.session.commit()

        updated_invoice = generate_hoa_don(thanh_toan.tt_id)

        assert updated_invoice.hoadon_id == first_invoice_id
        assert HoaDon.query.count() == 1
        assert updated_invoice.tien_phong == Decimal("2500000")
        assert updated_invoice.tien_dien == Decimal("280000")
        assert updated_invoice.tien_nuoc == Decimal("60000")
        assert updated_invoice.phi_dich_vu == Decimal("220000")
        assert updated_invoice.tong_tien == Decimal("3060000")
        assert updated_invoice.snapshot_don_gia_dien == Decimal("4000")
        assert updated_invoice.snapshot_don_gia_nuoc == Decimal("15000")
        assert updated_invoice.snapshot_gia_phong == Decimal("2500000")

        db.session.refresh(bang_gia)
        assert bang_gia.is_locked is True
