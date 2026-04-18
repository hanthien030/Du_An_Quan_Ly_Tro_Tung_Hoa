from datetime import date, timedelta
from decimal import Decimal

from app.extensions import db
from app.models import BangGia, HoaDon, HopDong, KhachThue, Phong, ThanhToanThang


def _create_contract_bundle(*, so_phong="M101", cap_phong="cap1", ngay_ket_thuc=None):
    phong = Phong(
        so_phong=so_phong,
        tang=1,
        dien_tich=20,
        cap_phong=cap_phong,
        trang_thai="trong",
        mo_ta="Phong test",
    )
    khach = KhachThue(
        ho_ten=f"Khach {so_phong}",
        cccd=f"{so_phong}123456",
        ngay_sinh=date(2000, 1, 1),
        sdt="0901234567",
        dia_chi="TP.HCM",
        email=f"{so_phong.lower()}@example.com",
        la_chinh=True,
    )
    hop_dong = HopDong(
        phong=phong,
        khach=khach,
        ngay_bat_dau=date.today() - timedelta(days=15),
        ngay_ket_thuc=ngay_ket_thuc,
        trang_thai="hieu_luc",
        ghi_chu="Hop dong test",
    )
    db.session.add_all([phong, khach, hop_dong])
    db.session.commit()
    return phong, khach, hop_dong


def _create_payment_bundle(*, cap_phong="cap2"):
    phong, khach, hop_dong = _create_contract_bundle(
        so_phong="M201",
        cap_phong=cap_phong,
        ngay_ket_thuc=date.today() + timedelta(days=45),
    )
    thanh_toan = ThanhToanThang(
        hop_dong=hop_dong,
        thang=4,
        nam=2026,
        so_dien=32.5,
        so_nuoc=3.0,
        trang_thai="da_tt",
        ngay_thanh_toan=date(2026, 4, 15),
        ghi_chu="Da thu tien",
    )
    db.session.add(thanh_toan)
    db.session.commit()
    return phong, khach, hop_dong, thanh_toan


def test_hop_dong_update_trang_thai_sets_hieu_luc_for_future_contract(app):
    with app.app_context():
        phong, _, hop_dong = _create_contract_bundle(
            so_phong="M301",
            ngay_ket_thuc=date.today() + timedelta(days=45),
        )

        trang_thai = hop_dong.update_trang_thai()
        db.session.commit()

        assert trang_thai == "hieu_luc"
        assert hop_dong.trang_thai == "hieu_luc"
        assert phong.trang_thai == "dang_thue"


def test_hop_dong_update_trang_thai_sets_sap_het_han_near_expiry(app):
    with app.app_context():
        phong, _, hop_dong = _create_contract_bundle(
            so_phong="M302",
            ngay_ket_thuc=date.today() + timedelta(days=7),
        )

        trang_thai = hop_dong.update_trang_thai()
        db.session.commit()

        assert trang_thai == "sap_het_han"
        assert hop_dong.trang_thai == "sap_het_han"
        assert phong.trang_thai == "dang_thue"


def test_hop_dong_update_trang_thai_sets_het_han_after_expiry(app):
    with app.app_context():
        phong, _, hop_dong = _create_contract_bundle(
            so_phong="M303",
            ngay_ket_thuc=date.today() - timedelta(days=1),
        )

        trang_thai = hop_dong.update_trang_thai()
        db.session.commit()

        assert trang_thai == "het_han"
        assert hop_dong.trang_thai == "het_han"
        assert phong.trang_thai == "trong"


def test_hop_dong_update_trang_thai_keeps_hieu_luc_when_no_end_date(app):
    with app.app_context():
        phong, _, hop_dong = _create_contract_bundle(
            so_phong="M304",
            ngay_ket_thuc=None,
        )

        trang_thai = hop_dong.update_trang_thai()
        db.session.commit()

        assert trang_thai == "hieu_luc"
        assert hop_dong.trang_thai == "hieu_luc"
        assert phong.trang_thai == "dang_thue"


def test_hop_dong_to_dict_includes_room_tenant_and_remaining_days(app):
    with app.app_context():
        _, khach, hop_dong = _create_contract_bundle(
            so_phong="M401",
            cap_phong="cap2",
            ngay_ket_thuc=date.today() + timedelta(days=12),
        )

        data = hop_dong.to_dict()

        assert data["hopdong_id"] == hop_dong.hopdong_id
        assert data["phong_id"] == hop_dong.phong_id
        assert data["so_phong"] == "M401"
        assert data["khach_id"] == khach.khach_id
        assert data["ho_ten"] == khach.ho_ten
        assert data["ngay_bat_dau"] == str(hop_dong.ngay_bat_dau)
        assert data["ngay_ket_thuc"] == str(hop_dong.ngay_ket_thuc)
        assert data["days_remaining"] == hop_dong.days_remaining()
        assert data["ghi_chu"] == "Hop dong test"


def test_thanh_toan_thang_to_dict_includes_payment_room_and_tenant_fields(app):
    with app.app_context():
        _, khach, hop_dong, thanh_toan = _create_payment_bundle(cap_phong="cap2")

        data = thanh_toan.to_dict()

        expected_keys = {
            "tt_id",
            "hopdong_id",
            "thang",
            "nam",
            "so_dien",
            "so_nuoc",
            "trang_thai",
            "ngay_thanh_toan",
            "ghi_chu",
            "so_phong",
            "cap_phong",
            "ho_ten",
        }
        assert expected_keys.issubset(data.keys())
        assert data["tt_id"] == thanh_toan.tt_id
        assert data["hopdong_id"] == hop_dong.hopdong_id
        assert data["thang"] == 4
        assert data["nam"] == 2026
        assert data["so_dien"] == 32.5
        assert data["so_nuoc"] == 3.0
        assert data["trang_thai"] == "da_tt"
        assert data["ngay_thanh_toan"] == "2026-04-15"
        assert data["ghi_chu"] == "Da thu tien"
        assert data["so_phong"] == "M201"
        assert data["cap_phong"] == "cap2"
        assert data["ho_ten"] == khach.ho_ten


def test_hoa_don_to_dict_returns_expected_detail_shape(app):
    with app.app_context():
        _, khach, hop_dong, thanh_toan = _create_payment_bundle(cap_phong="cap2")
        hoa_don = HoaDon(
            tt_id=thanh_toan.tt_id,
            tien_phong=Decimal("3500000"),
            tien_dien=Decimal("113750"),
            tien_nuoc=Decimal("45000"),
            phi_dich_vu=Decimal("200000"),
            tong_tien=Decimal("3858750"),
            ngay_tao=date(2026, 4, 20),
            snapshot_don_gia_dien=Decimal("3500"),
            snapshot_don_gia_nuoc=Decimal("15000"),
            snapshot_gia_phong=Decimal("3500000"),
        )
        db.session.add(hoa_don)
        db.session.commit()

        data = hoa_don.to_dict()

        expected_keys = {
            "hoadon_id",
            "tt_id",
            "hopdong_id",
            "so_phong",
            "ho_ten",
            "thang",
            "nam",
            "so_dien",
            "so_nuoc",
            "tien_phong",
            "tien_dien",
            "tien_nuoc",
            "phi_dich_vu",
            "tong_tien",
            "snapshot_don_gia_dien",
            "snapshot_don_gia_nuoc",
            "snapshot_gia_phong",
            "trang_thai",
            "ngay_tao",
            "ghi_chu",
        }
        assert expected_keys.issubset(data.keys())
        assert data["hoadon_id"] == hoa_don.hoadon_id
        assert data["tt_id"] == thanh_toan.tt_id
        assert data["hopdong_id"] == hop_dong.hopdong_id
        assert data["so_phong"] == "M201"
        assert data["ho_ten"] == khach.ho_ten
        assert data["thang"] == 4
        assert data["nam"] == 2026
        assert data["so_dien"] == 32.5
        assert data["so_nuoc"] == 3.0
        assert data["tien_phong"] == 3500000.0
        assert data["tien_dien"] == 113750.0
        assert data["tien_nuoc"] == 45000.0
        assert data["phi_dich_vu"] == 200000.0
        assert data["tong_tien"] == 3858750.0
        assert data["snapshot_don_gia_dien"] == 3500.0
        assert data["snapshot_don_gia_nuoc"] == 15000.0
        assert data["snapshot_gia_phong"] == 3500000.0
        assert data["trang_thai"] == "da_tt"
        assert data["ngay_tao"] == "2026-04-20"
        assert data["ghi_chu"] == "Da thu tien"


def test_bang_gia_to_dict_converts_numeric_values_for_api_use(app):
    with app.app_context():
        bang_gia = BangGia(
            thang=4,
            nam=2026,
            gia_phong_cap1=Decimal("2500000"),
            gia_phong_cap2=Decimal("3500000"),
            don_gia_dien=Decimal("3500"),
            don_gia_nuoc=Decimal("15000"),
            phi_wifi=Decimal("100000"),
            phi_ve_sinh=Decimal("50000"),
            phi_gui_xe=Decimal("50000"),
            is_locked=True,
        )
        db.session.add(bang_gia)
        db.session.commit()

        data = bang_gia.to_dict()

        assert data == {
            "bangia_id": bang_gia.bangia_id,
            "thang": 4,
            "nam": 2026,
            "gia_phong_cap1": 2500000.0,
            "gia_phong_cap2": 3500000.0,
            "don_gia_dien": 3500.0,
            "don_gia_nuoc": 15000.0,
            "phi_wifi": 100000.0,
            "phi_ve_sinh": 50000.0,
            "phi_gui_xe": 50000.0,
            "is_locked": True,
        }
