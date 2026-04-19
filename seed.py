from datetime import date, timedelta

from app import create_app
from app.extensions import db
from app.models import BangGia, HoaDon, HopDong, KhachThue, Phong, ThanhToanThang
from app.services.invoice_service import generate_hoa_don

app = create_app()


def month_shift(year, month, offset):
    index = year * 12 + (month - 1) + offset
    return index // 12, index % 12 + 1


def seeded_months(today):
    months = []
    for offset in (-2, -1, 0):
        year, month = month_shift(today.year, today.month, offset)
        months.append({
            'offset': offset,
            'year': year,
            'month': month,
            'label': f'{month:02d}/{year}',
        })
    return months


def payment_date(year, month, day):
    return date(year, month, day)


def seed_data():
    with app.app_context():
        today = date.today()
        months = seeded_months(today)
        month_by_offset = {item['offset']: item for item in months}

        print('Resetting demo database with db.drop_all() + db.create_all()...')
        db.drop_all()
        db.create_all()

        print('Seeding 12 rooms...')
        room_specs = [
            {'so_phong': '101', 'tang': 1, 'dien_tich': 18.5, 'cap_phong': 'cap1', 'trang_thai': 'dang_thue', 'mo_ta': 'Phòng cơ bản, cửa sổ thoáng.'},
            {'so_phong': '102', 'tang': 1, 'dien_tich': 22.0, 'cap_phong': 'cap2', 'trang_thai': 'dang_thue', 'mo_ta': 'Phòng có máy lạnh và nước nóng.'},
            {'so_phong': '103', 'tang': 1, 'dien_tich': 17.5, 'cap_phong': 'cap1', 'trang_thai': 'trong', 'mo_ta': 'Vừa trống sau khi khách cũ trả phòng.'},
            {'so_phong': '104', 'tang': 1, 'dien_tich': 23.0, 'cap_phong': 'cap2', 'trang_thai': 'trong', 'mo_ta': 'Phòng trống, sẵn sàng cho khách mới.'},
            {'so_phong': '201', 'tang': 2, 'dien_tich': 19.0, 'cap_phong': 'cap1', 'trang_thai': 'dang_thue', 'mo_ta': 'Phòng hướng giếng trời.'},
            {'so_phong': '202', 'tang': 2, 'dien_tich': 24.0, 'cap_phong': 'cap2', 'trang_thai': 'dang_thue', 'mo_ta': 'Phòng mới nhận khách đầu tháng này.'},
            {'so_phong': '203', 'tang': 2, 'dien_tich': 18.0, 'cap_phong': 'cap1', 'trang_thai': 'sua_chua', 'mo_ta': 'Đang thay máy lạnh và sơn lại tường.'},
            {'so_phong': '204', 'tang': 2, 'dien_tich': 25.0, 'cap_phong': 'cap2', 'trang_thai': 'dang_thue', 'mo_ta': 'Phòng đôi, ở lâu dài.'},
            {'so_phong': '301', 'tang': 3, 'dien_tich': 20.5, 'cap_phong': 'cap1', 'trang_thai': 'dang_thue', 'mo_ta': 'Phòng góc, đón gió tốt.'},
            {'so_phong': '302', 'tang': 3, 'dien_tich': 26.0, 'cap_phong': 'cap2', 'trang_thai': 'dang_thue', 'mo_ta': 'Phòng cao cấp, hợp đồng sắp đến hạn.'},
            {'so_phong': '303', 'tang': 3, 'dien_tich': 16.5, 'cap_phong': 'cap1', 'trang_thai': 'trong', 'mo_ta': 'Phòng trống lâu, đang chờ khách.'},
            {'so_phong': '304', 'tang': 3, 'dien_tich': 24.5, 'cap_phong': 'cap2', 'trang_thai': 'dang_thue', 'mo_ta': 'Phòng đủ nội thất cơ bản.'},
        ]
        rooms = {}
        for spec in room_specs:
            room = Phong(**spec)
            db.session.add(room)
            rooms[spec['so_phong']] = room
        db.session.commit()

        print('Seeding tenants...')
        tenant_specs = [
            {'key': 'an', 'ho_ten': 'Nguyễn Minh An', 'cccd': '079201000101', 'ngay_sinh': date(1999, 2, 14), 'sdt': '0903123456', 'dia_chi': 'Quận Bình Tân, TP.HCM', 'email': 'minhan@example.com'},
            {'key': 'linh', 'ho_ten': 'Trần Ngọc Linh', 'cccd': '079201000102', 'ngay_sinh': date(1997, 7, 8), 'sdt': '0914234567', 'dia_chi': 'TP. Biên Hòa, Đồng Nai', 'email': 'ngoclinh@example.com'},
            {'key': 'phuc', 'ho_ten': 'Lê Hoàng Phúc', 'cccd': '079201000103', 'ngay_sinh': date(2000, 11, 22), 'sdt': '0925345678', 'dia_chi': 'TP. Thủ Đức, TP.HCM', 'email': 'hoangphuc@example.com'},
            {'key': 'thao', 'ho_ten': 'Phạm Thu Thảo', 'cccd': '079201000104', 'ngay_sinh': date(1998, 5, 17), 'sdt': '0936456789', 'dia_chi': 'TP. Dĩ An, Bình Dương', 'email': 'thuthao@example.com'},
            {'key': 'khoa', 'ho_ten': 'Đỗ Quốc Khoa', 'cccd': '079201000105', 'ngay_sinh': date(1996, 9, 3), 'sdt': '0947567890', 'dia_chi': 'TP. Tân An, Long An', 'email': 'quockhoa@example.com'},
            {'key': 'nhi', 'ho_ten': 'Võ Gia Nhi', 'cccd': '079201000106', 'ngay_sinh': date(2001, 1, 29), 'sdt': '0958678901', 'dia_chi': 'Quận Gò Vấp, TP.HCM', 'email': 'gianhi@example.com'},
            {'key': 'viet', 'ho_ten': 'Bùi Quốc Việt', 'cccd': '079201000107', 'ngay_sinh': date(1995, 12, 11), 'sdt': '0969789012', 'dia_chi': 'TP. Mỹ Tho, Tiền Giang', 'email': 'quocviet@example.com'},
            {'key': 'mai', 'ho_ten': 'Ngô Khánh Mai', 'cccd': '079201000108', 'ngay_sinh': date(2002, 4, 6), 'sdt': '0970890123', 'dia_chi': 'Quận 12, TP.HCM', 'email': 'khanhmai@example.com'},
            {'key': 'duy', 'ho_ten': 'Phan Anh Duy', 'cccd': '079201000109', 'ngay_sinh': date(1994, 8, 19), 'sdt': '0981901234', 'dia_chi': 'TP. Vũng Tàu, Bà Rịa - Vũng Tàu', 'email': 'anhduy@example.com'},
        ]
        tenants = {}
        for spec in tenant_specs:
            tenant = KhachThue(
                ho_ten=spec['ho_ten'],
                cccd=spec['cccd'],
                ngay_sinh=spec['ngay_sinh'],
                sdt=spec['sdt'],
                dia_chi=spec['dia_chi'],
                email=spec['email'],
                la_chinh=True,
            )
            db.session.add(tenant)
            tenants[spec['key']] = tenant
        db.session.commit()

        print('Seeding contracts with active / near-expiry / expired cases...')
        contract_specs = [
            {
                'room': '101',
                'tenant': 'an',
                'start': today - timedelta(days=120),
                'end': today + timedelta(days=150),
                'note': 'Khách thuê ổn định, thanh toán đều.',
            },
            {
                'room': '102',
                'tenant': 'linh',
                'start': today - timedelta(days=45),
                'end': today + timedelta(days=12),
                'note': 'Hợp đồng sắp hết hạn để demo cảnh báo.',
            },
            {
                'room': '201',
                'tenant': 'phuc',
                'start': today - timedelta(days=90),
                'end': today + timedelta(days=180),
                'note': 'Khách ở dài hạn, dữ liệu điện nước trung bình.',
            },
            {
                'room': '202',
                'tenant': 'thao',
                'start': today - timedelta(days=20),
                'end': today + timedelta(days=200),
                'note': 'Khách mới vào đầu tháng hiện tại.',
            },
            {
                'room': '204',
                'tenant': 'khoa',
                'start': today - timedelta(days=70),
                'end': today + timedelta(days=100),
                'note': 'Có tháng chưa đóng để demo follow-up công nợ.',
            },
            {
                'room': '301',
                'tenant': 'nhi',
                'start': today - timedelta(days=160),
                'end': today + timedelta(days=60),
                'note': 'Khách thuê lâu, tiêu thụ ổn định.',
            },
            {
                'room': '302',
                'tenant': 'viet',
                'start': today - timedelta(days=25),
                'end': today + timedelta(days=5),
                'note': 'Hợp đồng sắp hết hạn trong vài ngày tới.',
            },
            {
                'room': '304',
                'tenant': 'mai',
                'start': today - timedelta(days=75),
                'end': today + timedelta(days=240),
                'note': 'Khách thuê ổn định, hóa đơn cao do phòng lớn.',
            },
            {
                'room': '103',
                'tenant': 'duy',
                'start': today - timedelta(days=140),
                'end': today - timedelta(days=15),
                'note': 'Khách đã trả phòng sớm, phòng quay về trạng thái trống.',
            },
        ]
        contracts = {}
        for spec in contract_specs:
            contract = HopDong(
                phong_id=rooms[spec['room']].phong_id,
                khach_id=tenants[spec['tenant']].khach_id,
                ngay_bat_dau=spec['start'],
                ngay_ket_thuc=spec['end'],
                ghi_chu=spec['note'],
            )
            db.session.add(contract)
            db.session.flush()
            contract.update_trang_thai()
            contracts[spec['room']] = contract
        db.session.commit()

        print(f"Seeding price tables for {', '.join(item['label'] for item in months)}...")
        price_specs = {
            -2: {
                'gia_phong_cap1': 2450000,
                'gia_phong_cap2': 3350000,
                'don_gia_dien': 3600,
                'don_gia_nuoc': 15500,
                'phi_wifi': 100000,
                'phi_ve_sinh': 50000,
                'phi_gui_xe': 70000,
            },
            -1: {
                'gia_phong_cap1': 2500000,
                'gia_phong_cap2': 3450000,
                'don_gia_dien': 3700,
                'don_gia_nuoc': 16000,
                'phi_wifi': 110000,
                'phi_ve_sinh': 50000,
                'phi_gui_xe': 70000,
            },
            0: {
                'gia_phong_cap1': 2550000,
                'gia_phong_cap2': 3550000,
                'don_gia_dien': 3800,
                'don_gia_nuoc': 17000,
                'phi_wifi': 120000,
                'phi_ve_sinh': 60000,
                'phi_gui_xe': 80000,
            },
        }
        for offset, values in price_specs.items():
            month_item = month_by_offset[offset]
            db.session.add(BangGia(
                thang=month_item['month'],
                nam=month_item['year'],
                is_locked=False,
                **values,
            ))
        db.session.commit()

        print('Seeding monthly payments for 3 months...')
        payment_specs = [
            {
                'offset': -2, 'room': '101', 'dien': 118, 'nuoc': 4.2,
                'status': 'da_tt', 'paid_day': 8, 'note': 'Thanh toán đúng hạn.'
            },
            {
                'offset': -2, 'room': '201', 'dien': 95, 'nuoc': 3.4,
                'status': 'da_tt', 'paid_day': 10, 'note': 'Đóng trực tiếp tại nhà trọ.'
            },
            {
                'offset': -2, 'room': '204', 'dien': 80, 'nuoc': 2.8,
                'status': 'da_tt', 'paid_day': 18, 'note': 'Đã chuyển khoản.'
            },
            {
                'offset': -2, 'room': '301', 'dien': 110, 'nuoc': 4.0,
                'status': 'da_tt', 'paid_day': 12, 'note': 'Khách cũ, thanh toán sớm.'
            },
            {
                'offset': -2, 'room': '304', 'dien': 135, 'nuoc': 5.1,
                'status': 'da_tt', 'paid_day': 14, 'note': 'Có dùng thêm bếp điện.'
            },
            {
                'offset': -2, 'room': '103', 'dien': 88, 'nuoc': 3.1,
                'status': 'da_tt', 'paid_day': 9, 'note': 'Tháng cuối trước khi trả phòng.'
            },
            {
                'offset': -1, 'room': '101', 'dien': 125, 'nuoc': 4.4,
                'status': 'da_tt', 'paid_day': 7, 'note': 'Thanh toán qua ngân hàng.'
            },
            {
                'offset': -1, 'room': '102', 'dien': 92, 'nuoc': 3.2,
                'status': 'da_tt', 'paid_day': 11, 'note': 'Khách vừa gia hạn ngắn hạn.'
            },
            {
                'offset': -1, 'room': '201', 'dien': 98, 'nuoc': 3.6,
                'status': 'da_tt', 'paid_day': 10, 'note': 'Không phát sinh ghi chú.'
            },
            {
                'offset': -1, 'room': '204', 'dien': 86, 'nuoc': 3.0,
                'status': 'chua_tt', 'paid_day': None, 'note': 'Khách xin dời sang đầu tháng sau.'
            },
            {
                'offset': -1, 'room': '301', 'dien': 118, 'nuoc': 4.2,
                'status': 'da_tt', 'paid_day': 15, 'note': 'Đã thanh toán cùng tiền gửi xe.'
            },
            {
                'offset': -1, 'room': '302', 'dien': 70, 'nuoc': 2.5,
                'status': 'da_tt', 'paid_day': 16, 'note': 'Tháng đầu vào ở.'
            },
            {
                'offset': -1, 'room': '304', 'dien': 142, 'nuoc': 5.3,
                'status': 'da_tt', 'paid_day': 18, 'note': 'Có tăng điện do làm ca tối.'
            },
            {
                'offset': -1, 'room': '103', 'dien': 60, 'nuoc': 2.2,
                'status': 'da_tt', 'paid_day': 6, 'note': 'Chốt công tơ trước khi dọn đi.'
            },
            {
                'offset': 0, 'room': '101', 'dien': 132, 'nuoc': 4.6,
                'status': 'da_tt', 'paid_day': 6, 'note': 'Khách đã đóng đầu tháng.'
            },
            {
                'offset': 0, 'room': '102', 'dien': 96, 'nuoc': 3.1,
                'status': 'chua_tt', 'paid_day': None, 'note': 'Đang chờ chốt gia hạn hợp đồng.'
            },
            {
                'offset': 0, 'room': '201', 'dien': 104, 'nuoc': 3.8,
                'status': 'da_tt', 'paid_day': 8, 'note': 'Đã thanh toán đúng hẹn.'
            },
            {
                'offset': 0, 'room': '202', 'dien': 88, 'nuoc': 3.0,
                'status': 'da_tt', 'paid_day': 14, 'note': 'Tháng đầu thuê, khách đóng ngay sau khi nhận phòng.'
            },
            {
                'offset': 0, 'room': '204', 'dien': 90, 'nuoc': 3.4,
                'status': 'chua_tt', 'paid_day': None, 'note': 'Khách hẹn chuyển khoản cuối tuần.'
            },
            {
                'offset': 0, 'room': '301', 'dien': 121, 'nuoc': 4.0,
                'status': 'da_tt', 'paid_day': 9, 'note': 'Đã tất toán sớm.'
            },
            {
                'offset': 0, 'room': '302', 'dien': 75, 'nuoc': 2.7,
                'status': 'chua_tt', 'paid_day': None, 'note': 'Khách đang làm thủ tục gia hạn thêm 1 quý.'
            },
            {
                'offset': 0, 'room': '304', 'dien': 148, 'nuoc': 5.4,
                'status': 'da_tt', 'paid_day': 11, 'note': 'Hóa đơn cao nhất nhóm phòng cap2.'
            },
        ]

        payments = []
        for spec in payment_specs:
            month_item = month_by_offset[spec['offset']]
            paid_on = None
            if spec['status'] == 'da_tt' and spec['paid_day']:
                paid_on = payment_date(month_item['year'], month_item['month'], spec['paid_day'])

            payment = ThanhToanThang(
                hopdong_id=contracts[spec['room']].hopdong_id,
                thang=month_item['month'],
                nam=month_item['year'],
                so_dien=spec['dien'],
                so_nuoc=spec['nuoc'],
                trang_thai=spec['status'],
                ngay_thanh_toan=paid_on,
                ghi_chu=spec['note'],
            )
            db.session.add(payment)
            payments.append((payment, spec))
        db.session.commit()

        print('Generating invoices for all seeded monthly payments...')
        for payment, spec in payments:
            month_item = month_by_offset[spec['offset']]
            issue_day = spec['paid_day'] if spec['paid_day'] else 5
            invoice = generate_hoa_don(payment.tt_id)
            invoice.ngay_tao = payment_date(month_item['year'], month_item['month'], issue_day)
            db.session.commit()

        room_status_counts = {
            'tong': Phong.query.count(),
            'dang_thue': Phong.query.filter_by(trang_thai='dang_thue').count(),
            'trong': Phong.query.filter_by(trang_thai='trong').count(),
            'sua_chua': Phong.query.filter_by(trang_thai='sua_chua').count(),
        }

        print('Seed data completed successfully!')
        print(f"Months seeded: {', '.join(item['label'] for item in months)}")
        print(f"Rooms: {room_status_counts['tong']} total | dang_thue={room_status_counts['dang_thue']} | trong={room_status_counts['trong']} | sua_chua={room_status_counts['sua_chua']}")
        print(f"Tenants: {KhachThue.query.count()} | Contracts: {HopDong.query.count()} | Price tables: {BangGia.query.count()}")
        print(f"Monthly payments: {ThanhToanThang.query.count()} | Invoices: {HoaDon.query.count()}")


if __name__ == '__main__':
    seed_data()
