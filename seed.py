from app import create_app
from app.extensions import db
from app.models import Phong, KhachThue, HopDong, BangGia, ThanhToanThang, HoaDon
from datetime import date, timedelta

app = create_app()

def seed_data():
    with app.app_context():
        today = date.today()
        current_month = today.month
        current_year = today.year

        print("Clearing old data...")
        db.drop_all()
        db.create_all()

        print("Seeding rooms...")
        phong1 = Phong(so_phong='101', tang=1, dien_tich=20.0, cap_phong='cap2', trang_thai='dang_thue', mo_ta='Phòng đầy đủ tiện nghi')
        phong2 = Phong(so_phong='102', tang=1, dien_tich=15.0, cap_phong='cap1', trang_thai='dang_thue', mo_ta='Phòng cơ bản')
        phong3 = Phong(so_phong='103', tang=1, dien_tich=15.0, cap_phong='cap1', trang_thai='trong', mo_ta='')
        phong4 = Phong(so_phong='104', tang=1, dien_tich=20.0, cap_phong='cap2', trang_thai='trong', mo_ta='')
        phong5 = Phong(so_phong='201', tang=2, dien_tich=20.0, cap_phong='cap2', trang_thai='sua_chua', mo_ta='Đang sửa điều hòa')
        
        db.session.add_all([phong1, phong2, phong3, phong4, phong5])
        db.session.commit()

        print("Seeding tenants...")
        khach1 = KhachThue(ho_ten='Nguyễn Văn An', cccd='001234567890', ngay_sinh=date(2000, 1, 1), sdt='0901234567', dia_chi='Hà Nội', email='an@example.com')
        khach2 = KhachThue(ho_ten='Trần Thị Bình', cccd='002345678901', ngay_sinh=date(1995, 5, 5), sdt='0912345678', dia_chi='Hải Phòng', email='binh@example.com')
        khach3 = KhachThue(ho_ten='Lê Văn Cường', cccd='003456789012', ngay_sinh=date(2002, 10, 10), sdt='0923456789', dia_chi='Đà Nẵng', email='')
        
        db.session.add_all([khach1, khach2, khach3])
        db.session.commit()

        print("Seeding contracts...")
        hd1 = HopDong(
            phong_id=phong1.phong_id,
            khach_id=khach1.khach_id,
            ngay_bat_dau=today - timedelta(days=60),
            ngay_ket_thuc=today + timedelta(days=120),
            ghi_chu='Hop dong con hieu luc de demo dashboard',
        )
        hd2 = HopDong(
            phong_id=phong2.phong_id,
            khach_id=khach2.khach_id,
            ngay_bat_dau=today - timedelta(days=30),
            ngay_ket_thuc=today + timedelta(days=15),
            ghi_chu='Hop dong sap het han de demo canh bao',
        )
        hd1.update_trang_thai()
        hd2.update_trang_thai()
        
        db.session.add_all([hd1, hd2])
        db.session.commit()

        print("Seeding price table...")
        bg = BangGia(
            thang=current_month,
            nam=current_year,
            gia_phong_cap1=2500000,
            gia_phong_cap2=3500000,
            don_gia_dien=3500,
            don_gia_nuoc=15000,
            phi_wifi=100000,
            phi_ve_sinh=50000,
            phi_gui_xe=50000,
            is_locked=True,
        )
        db.session.add(bg)
        db.session.commit()

        print("Seeding monthly payments...")
        tt1 = ThanhToanThang(
            hopdong_id=hd1.hopdong_id,
            thang=current_month,
            nam=current_year,
            so_dien=120,
            so_nuoc=4.5,
            trang_thai='da_tt',
            ngay_thanh_toan=today,
            ghi_chu='Da thanh toan',
        )
        tt2 = ThanhToanThang(
            hopdong_id=hd2.hopdong_id,
            thang=current_month,
            nam=current_year,
            so_dien=85,
            so_nuoc=3,
            trang_thai='chua_tt',
            ghi_chu='Cho nhap tien',
        )
        db.session.add_all([tt1, tt2])
        db.session.commit()

        print("Seeding one invoice...")
        hdon = HoaDon(
            tt_id=tt1.tt_id,
            tien_phong=3500000,
            tien_dien=420000,
            tien_nuoc=67500,
            phi_dich_vu=200000,
            tong_tien=4187500,
            ngay_tao=today,
            snapshot_don_gia_dien=3500,
            snapshot_don_gia_nuoc=15000,
            snapshot_gia_phong=3500000,
        )
        db.session.add(hdon)
        db.session.commit()

        print("Seed data completed successfully!")

if __name__ == '__main__':
    seed_data()
