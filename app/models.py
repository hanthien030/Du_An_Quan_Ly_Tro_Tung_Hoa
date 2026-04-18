from app.extensions import db
from app.utils import utc_now
from datetime import date

class Phong(db.Model):
    __tablename__ = 'phong'
    phong_id   = db.Column(db.Integer, primary_key=True)
    so_phong   = db.Column(db.String(10), nullable=False, unique=True)
    tang       = db.Column(db.Integer, default=1)
    dien_tich  = db.Column(db.Float)
    cap_phong  = db.Column(db.String(10), default='cap1')   # 'cap1' | 'cap2'
    trang_thai = db.Column(db.String(20), default='trong')  # 'trong'|'dang_thue'|'sua_chua'
    mo_ta      = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utc_now)

    hop_dongs  = db.relationship('HopDong', backref='phong', lazy=True)

    def to_dict(self):
        return {
            'phong_id':  self.phong_id,
            'so_phong':  self.so_phong,
            'tang':      self.tang,
            'dien_tich': self.dien_tich,
            'cap_phong': self.cap_phong,
            'trang_thai':self.trang_thai,
            'mo_ta':     self.mo_ta,
        }

class KhachThue(db.Model):
    __tablename__ = 'khach_thue'
    khach_id   = db.Column(db.Integer, primary_key=True)
    ho_ten     = db.Column(db.String(100), nullable=False)
    cccd       = db.Column(db.String(20), unique=True)
    ngay_sinh  = db.Column(db.Date)
    sdt        = db.Column(db.String(15))
    dia_chi    = db.Column(db.Text)
    email      = db.Column(db.String(100))
    la_chinh   = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    hop_dongs  = db.relationship('HopDong', backref='khach', lazy=True)

    def to_dict(self):
        return {
            'khach_id': self.khach_id,
            'ho_ten':   self.ho_ten,
            'cccd':     self.cccd,
            'ngay_sinh':str(self.ngay_sinh) if self.ngay_sinh else None,
            'sdt':      self.sdt,
            'dia_chi':  self.dia_chi,
            'email':    self.email,
            'la_chinh': self.la_chinh,
        }

class HopDong(db.Model):
    __tablename__ = 'hop_dong'
    hopdong_id    = db.Column(db.Integer, primary_key=True)
    phong_id      = db.Column(db.Integer, db.ForeignKey('phong.phong_id'), nullable=False)
    khach_id      = db.Column(db.Integer, db.ForeignKey('khach_thue.khach_id'), nullable=False)
    ngay_bat_dau  = db.Column(db.Date, nullable=False)
    ngay_ket_thuc = db.Column(db.Date)
    trang_thai    = db.Column(db.String(20), default='hieu_luc')
    ghi_chu       = db.Column(db.Text)
    created_at    = db.Column(db.DateTime, default=utc_now)

    thanh_toans   = db.relationship('ThanhToanThang', backref='hop_dong', lazy=True)

    def update_trang_thai(self):
        days = self.days_remaining()
        if self.ngay_ket_thuc is None:
            self.trang_thai = 'hieu_luc'
        elif days > 30:
            self.trang_thai = 'hieu_luc'
        elif 0 < days <= 30:
            self.trang_thai = 'sap_het_han'
        else:
            self.trang_thai = 'het_han'

        if self.phong and self.phong.trang_thai != 'sua_chua':
            self.phong.trang_thai = 'trong' if self.trang_thai == 'het_han' else 'dang_thue'

        return self.trang_thai

    def days_remaining(self):
        if self.ngay_ket_thuc:
            return (self.ngay_ket_thuc - date.today()).days
        return None

    def to_dict(self):
        return {
            'hopdong_id':    self.hopdong_id,
            'phong_id':      self.phong_id,
            'so_phong':      self.phong.so_phong,
            'khach_id':      self.khach_id,
            'ho_ten':        self.khach.ho_ten,
            'ngay_bat_dau':  str(self.ngay_bat_dau),
            'ngay_ket_thuc': str(self.ngay_ket_thuc) if self.ngay_ket_thuc else None,
            'trang_thai':    self.trang_thai,
            'days_remaining':self.days_remaining(),
            'ghi_chu':       self.ghi_chu,
        }

class BangGia(db.Model):
    __tablename__ = 'bang_gia'
    bangia_id      = db.Column(db.Integer, primary_key=True)
    thang          = db.Column(db.Integer, nullable=False)
    nam            = db.Column(db.Integer, nullable=False)
    gia_phong_cap1 = db.Column(db.Numeric(12,0), nullable=False)
    gia_phong_cap2 = db.Column(db.Numeric(12,0), nullable=False)
    don_gia_dien   = db.Column(db.Numeric(10,0), nullable=False)
    don_gia_nuoc   = db.Column(db.Numeric(10,0), nullable=False)
    phi_wifi       = db.Column(db.Numeric(10,0), default=0)
    phi_ve_sinh    = db.Column(db.Numeric(10,0), default=0)
    phi_gui_xe     = db.Column(db.Numeric(10,0), default=0)
    is_locked      = db.Column(db.Boolean, default=False)
    created_at     = db.Column(db.DateTime, default=utc_now)

    __table_args__ = (db.UniqueConstraint('thang', 'nam'),)

    def to_dict(self):
        return {
            'bangia_id':      self.bangia_id,
            'thang':          self.thang,
            'nam':            self.nam,
            'gia_phong_cap1': float(self.gia_phong_cap1),
            'gia_phong_cap2': float(self.gia_phong_cap2),
            'don_gia_dien':   float(self.don_gia_dien),
            'don_gia_nuoc':   float(self.don_gia_nuoc),
            'phi_wifi':       float(self.phi_wifi),
            'phi_ve_sinh':    float(self.phi_ve_sinh),
            'phi_gui_xe':     float(self.phi_gui_xe),
            'is_locked':      self.is_locked,
        }

class ThanhToanThang(db.Model):
    __tablename__ = 'thanh_toan_thang'
    tt_id           = db.Column(db.Integer, primary_key=True)
    hopdong_id      = db.Column(db.Integer, db.ForeignKey('hop_dong.hopdong_id'), nullable=False)
    thang           = db.Column(db.Integer, nullable=False)
    nam             = db.Column(db.Integer, nullable=False)
    so_dien         = db.Column(db.Float, default=0)
    so_nuoc         = db.Column(db.Float, default=0)
    trang_thai      = db.Column(db.String(20), default='chua_tt')  # 'chua_tt'|'da_tt'
    ngay_thanh_toan = db.Column(db.Date)
    ghi_chu         = db.Column(db.Text)
    created_at      = db.Column(db.DateTime, default=utc_now)

    __table_args__ = (db.UniqueConstraint('hopdong_id', 'thang', 'nam'),)

    hoa_don = db.relationship('HoaDon', backref='thanh_toan', uselist=False)

    def to_dict(self):
        hop_dong = self.hop_dong
        phong = hop_dong.phong if hop_dong else None
        khach = hop_dong.khach if hop_dong else None
        return {
            'tt_id': self.tt_id,
            'hopdong_id': self.hopdong_id,
            'thang': self.thang,
            'nam': self.nam,
            'so_dien': self.so_dien,
            'so_nuoc': self.so_nuoc,
            'trang_thai': self.trang_thai,
            'ngay_thanh_toan': str(self.ngay_thanh_toan) if self.ngay_thanh_toan else None,
            'ghi_chu': self.ghi_chu,
            'so_phong': phong.so_phong if phong else None,
            'cap_phong': phong.cap_phong if phong else None,
            'ho_ten': khach.ho_ten if khach else None,
        }

class HoaDon(db.Model):
    __tablename__ = 'hoa_don'
    hoadon_id              = db.Column(db.Integer, primary_key=True)
    tt_id                  = db.Column(db.Integer, db.ForeignKey('thanh_toan_thang.tt_id'), nullable=False, unique=True)
    tien_phong             = db.Column(db.Numeric(12,0), nullable=False)
    tien_dien              = db.Column(db.Numeric(12,0), nullable=False)
    tien_nuoc              = db.Column(db.Numeric(12,0), nullable=False)
    phi_dich_vu            = db.Column(db.Numeric(12,0), default=0)
    tong_tien              = db.Column(db.Numeric(12,0), nullable=False)
    ngay_tao               = db.Column(db.Date, default=date.today)
    snapshot_don_gia_dien  = db.Column(db.Numeric(10,0))
    snapshot_don_gia_nuoc  = db.Column(db.Numeric(10,0))
    snapshot_gia_phong     = db.Column(db.Numeric(12,0))

    def to_dict(self):
        tt = self.thanh_toan
        hd = tt.hop_dong
        return {
            'hoadon_id':    self.hoadon_id,
            'tt_id':        self.tt_id,
            'hopdong_id':   hd.hopdong_id,
            'so_phong':     hd.phong.so_phong,
            'ho_ten':       hd.khach.ho_ten,
            'thang':        tt.thang,
            'nam':          tt.nam,
            'so_dien':      tt.so_dien,
            'so_nuoc':      tt.so_nuoc,
            'tien_phong':   float(self.tien_phong),
            'tien_dien':    float(self.tien_dien),
            'tien_nuoc':    float(self.tien_nuoc),
            'phi_dich_vu':  float(self.phi_dich_vu),
            'tong_tien':    float(self.tong_tien),
            'snapshot_don_gia_dien': float(self.snapshot_don_gia_dien or 0),
            'snapshot_don_gia_nuoc': float(self.snapshot_don_gia_nuoc or 0),
            'snapshot_gia_phong': float(self.snapshot_gia_phong or 0),
            'trang_thai':   tt.trang_thai,
            'ngay_tao':     str(self.ngay_tao),
            'ghi_chu':      tt.ghi_chu,
        }
