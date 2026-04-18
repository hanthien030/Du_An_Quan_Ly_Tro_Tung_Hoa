# PLAN.md — Hệ Thống Quản Lý Dãy Trọ Bình Dân

> **Hướng dẫn dùng file này:**
> File này là **single source of truth** cho toàn bộ dự án.
> Bất kỳ AI agent nào (Claude Code, Codex, Cursor, v.v.) đều có thể đọc file này và bắt đầu code một module độc lập mà không cần hỏi thêm context.
> Sau mỗi task hoàn thành → cập nhật checkbox `[ ]` → `[x]` trong phần **Checklist**.

---

## Mục Lục

1. [Tóm Tắt Dự Án](#1-tóm-tắt-dự-án)
2. [Quyết Định Công Nghệ](#2-quyết-định-công-nghệ)
3. [Cấu Trúc Thư Mục](#3-cấu-trúc-thư-mục)
4. [Database Schema](#4-database-schema)
5. [Business Logic Rules](#5-business-logic-rules)
6. [API Endpoints](#6-api-endpoints)
7. [Frontend — Đặc Tả Từng Màn Hình](#7-frontend--đặc-tả-từng-màn-hình)
8. [Checklist Tiến Độ](#8-checklist-tiến-độ)
9. [Conventions & Code Style](#9-conventions--code-style)
10. [Gợi Ý Phân Công Cho AI Tools](#10-gợi-ý-phân-công-cho-ai-tools)

---

## 1. Tóm Tắt Dự Án

### Mô tả
Ứng dụng web quản lý dãy trọ bình dân cho chủ nhà nhỏ (5–30 phòng). Thay thế việc ghi sổ tay bằng hệ thống số hóa, giúp theo dõi phòng, khách thuê, hóa đơn điện nước hàng tháng và doanh thu.

### Người dùng duy nhất
Chủ nhà trọ — **không cần hệ thống login phức tạp**, có thể là single-user với 1 tài khoản cố định (scope mức 3).

### Luồng nghiệp vụ cốt lõi (Happy Path)

```
[Tạo Phòng] → [Thêm Khách Thuê] → [Tạo Hợp Đồng]
      ↓
[Cuối tháng] → [Nhập Bảng Giá tháng mới (nếu thay đổi)]
             → [Nhập Số Điện + Số Nước từng phòng]
             → [Tick Đã Thanh Toán]
             → [Xem / Xuất Hóa Đơn PDF]
      ↓
[Dashboard] → Xem tổng doanh thu, cảnh báo chưa đóng tiền
```

### Các khái niệm quan trọng cần hiểu

| Khái niệm | Mô tả |
|-----------|-------|
| **Phòng Cấp 1** | Phòng cơ bản, không tiện nghi, giá rẻ hơn |
| **Phòng Cấp 2** | Phòng đầy đủ tiện nghi (điều hòa, máy giặt, nóng lạnh), giá cao hơn |
| **Bảng giá** | Bộ đơn giá áp dụng cho 1 tháng cụ thể. Không được sửa tháng đã có hóa đơn. |
| **Thanh toán tháng** | Bản ghi nhập tay số điện, số nước và trạng thái đóng tiền của 1 phòng trong 1 tháng |
| **Hóa đơn** | Được tính tự động từ Bảng giá + Thanh toán tháng. Không nhập tay. |

---

## 2. Quyết Định Công Nghệ

| Lớp | Công nghệ | Lý do |
|-----|-----------|-------|
| **Back-end** | Python 3.10+ + Flask 3.x | Nhẹ, ít boilerplate, phù hợp nhóm sinh viên |
| **ORM** | SQLAlchemy 2.x | Viết model thay vì SQL thuần, dễ migrate |
| **Database** | SQLite (dev) → MySQL (prod) | SQLite không cần cài server, migrate dễ |
| **Migration** | Flask-Migrate (Alembic) | Quản lý schema thay đổi |
| **Front-end** | HTML5 + Bootstrap 5.3 + Vanilla JS (ES6+) | Không cần build tool, dễ chỉnh |
| **Biểu đồ** | Chart.js 4.x | CDN, không cần npm |
| **PDF** | WeasyPrint hoặc pdfkit | Xuất HTML → PDF phía server |
| **API** | REST JSON (Flask Blueprint) | Tách biệt front/back |
| **Icons** | Bootstrap Icons 1.x (CDN) | Đồng bộ với Bootstrap |

### Cấu hình môi trường
```
# .env (không commit)
FLASK_ENV=development
SECRET_KEY=change-this-in-production
DATABASE_URL=sqlite:///nha_tro.db
# MySQL: mysql+pymysql://user:pass@localhost/nha_tro
```

---

## 3. Cấu Trúc Thư Mục

```
nha_tro/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models.py                # SQLAlchemy models (6 bảng)
│   ├── extensions.py            # db, migrate instances
│   │
│   ├── api/                     # REST API Blueprints
│   │   ├── __init__.py
│   │   ├── phong.py             # /api/phong
│   │   ├── khach_thue.py        # /api/khach-thue
│   │   ├── hop_dong.py          # /api/hop-dong
│   │   ├── bang_gia.py          # /api/bang-gia
│   │   ├── thanh_toan.py        # /api/thanh-toan
│   │   ├── hoa_don.py           # /api/hoa-don
│   │   └── thong_ke.py          # /api/thong-ke
│   │
│   ├── services/                # Business logic (tách khỏi route)
│   │   ├── invoice_service.py   # Tính tiền hóa đơn
│   │   ├── pdf_service.py       # Xuất PDF
│   │   └── warning_service.py   # Cảnh báo hợp đồng sắp hết hạn
│   │
│   └── templates/
│       ├── base.html            # Layout chung (sidebar + navbar)
│       ├── dashboard.html
│       ├── phong/
│       │   ├── index.html       # Grid phòng
│       │   └── form.html        # Thêm/sửa phòng
│       ├── khach_thue/
│       │   ├── index.html
│       │   └── form.html
│       ├── hop_dong/
│       │   ├── index.html
│       │   └── form.html
│       ├── bang_gia/
│       │   └── index.html
│       ├── thanh_toan/
│       │   └── index.html       # Bảng nhập điện nước (giống bảng điểm danh)
│       ├── hoa_don/
│       │   ├── index.html
│       │   └── detail.html      # Chi tiết 1 hóa đơn + nút xuất PDF
│       ├── thong_ke/
│       │   └── index.html
│       └── pdf/
│           └── hoa_don_pdf.html # Template riêng để render PDF
│
├── static/
│   ├── css/
│   │   └── style.css            # Override Bootstrap, custom styles
│   ├── js/
│   │   ├── main.js              # Utility functions dùng chung
│   │   ├── dashboard.js
│   │   ├── phong.js
│   │   ├── thanh_toan.js        # Logic bảng nhập điện nước
│   │   └── thong_ke.js          # Chart.js init
│   └── img/
│       └── logo.png
│
├── migrations/                  # Flask-Migrate auto-generated
├── tests/
│   ├── test_models.py
│   ├── test_api_phong.py
│   └── test_invoice_service.py
│
├── .env
├── .gitignore
├── config.py                    # Config classes (Dev/Prod)
├── requirements.txt
├── run.py                       # Entry point: flask run
└── PLAN.md                      # ← file này
```

---

## 4. Database Schema

### 4.1 SQL Tạo Bảng (SQLite compatible)

```sql
-- ============================================================
-- PHONG (Rooms)
-- ============================================================
CREATE TABLE phong (
    phong_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    so_phong    VARCHAR(10)  NOT NULL UNIQUE,   -- "101", "A2", ...
    tang        INTEGER      NOT NULL DEFAULT 1,
    dien_tich   FLOAT,
    cap_phong   VARCHAR(10)  NOT NULL DEFAULT 'cap1',  -- 'cap1' | 'cap2'
    trang_thai  VARCHAR(20)  NOT NULL DEFAULT 'trong', -- 'trong' | 'dang_thue' | 'sua_chua'
    mo_ta       TEXT,
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- KHACH_THUE (Tenants)
-- ============================================================
CREATE TABLE khach_thue (
    khach_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    ho_ten      VARCHAR(100) NOT NULL,
    cccd        VARCHAR(20)  UNIQUE,
    ngay_sinh   DATE,
    sdt         VARCHAR(15),
    dia_chi     TEXT,
    email       VARCHAR(100),
    la_chinh    BOOLEAN DEFAULT 1,   -- 1 = người thuê chính
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- HOP_DONG (Contracts)
-- ============================================================
CREATE TABLE hop_dong (
    hopdong_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    phong_id        INTEGER NOT NULL REFERENCES phong(phong_id),
    khach_id        INTEGER NOT NULL REFERENCES khach_thue(khach_id),
    ngay_bat_dau    DATE NOT NULL,
    ngay_ket_thuc   DATE,            -- NULL = chưa xác định ngày kết thúc
    trang_thai      VARCHAR(20) NOT NULL DEFAULT 'hieu_luc',
                    -- 'hieu_luc' | 'sap_het_han' | 'het_han'
    ghi_chu         TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
-- Index để tìm hợp đồng đang hiệu lực của phòng
CREATE INDEX idx_hopdong_phong ON hop_dong(phong_id, trang_thai);

-- ============================================================
-- BANG_GIA (Price Table — per month)
-- ============================================================
CREATE TABLE bang_gia (
    bangia_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    thang           INTEGER NOT NULL,   -- 1–12
    nam             INTEGER NOT NULL,
    gia_phong_cap1  DECIMAL(12,0) NOT NULL,
    gia_phong_cap2  DECIMAL(12,0) NOT NULL,
    don_gia_dien    DECIMAL(10,0) NOT NULL,  -- VNĐ/kWh
    don_gia_nuoc    DECIMAL(10,0) NOT NULL,  -- VNĐ/m³
    phi_wifi        DECIMAL(10,0) DEFAULT 0,
    phi_ve_sinh     DECIMAL(10,0) DEFAULT 0,
    phi_gui_xe      DECIMAL(10,0) DEFAULT 0,
    is_locked       BOOLEAN DEFAULT 0,  -- 1 = đã có hóa đơn, không được sửa
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(thang, nam)
);

-- ============================================================
-- THANH_TOAN_THANG (Monthly Payment Input)
-- ============================================================
CREATE TABLE thanh_toan_thang (
    tt_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    hopdong_id      INTEGER NOT NULL REFERENCES hop_dong(hopdong_id),
    thang           INTEGER NOT NULL,
    nam             INTEGER NOT NULL,
    so_dien         FLOAT NOT NULL DEFAULT 0,   -- kWh
    so_nuoc         FLOAT NOT NULL DEFAULT 0,   -- m³
    trang_thai      VARCHAR(20) NOT NULL DEFAULT 'chua_tt',
                    -- 'chua_tt' | 'da_tt'
    ngay_thanh_toan DATE,
    ghi_chu         TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(hopdong_id, thang, nam)
);

-- ============================================================
-- HOA_DON (Invoices — computed, never manually entered)
-- ============================================================
CREATE TABLE hoa_don (
    hoadon_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    tt_id           INTEGER NOT NULL UNIQUE REFERENCES thanh_toan_thang(tt_id),
    tien_phong      DECIMAL(12,0) NOT NULL,
    tien_dien       DECIMAL(12,0) NOT NULL,
    tien_nuoc       DECIMAL(12,0) NOT NULL,
    phi_dich_vu     DECIMAL(12,0) NOT NULL DEFAULT 0,
    tong_tien       DECIMAL(12,0) NOT NULL,
    ngay_tao        DATE NOT NULL,
    -- Snapshot đơn giá tại thời điểm tạo (để tra cứu sau)
    snapshot_don_gia_dien   DECIMAL(10,0),
    snapshot_don_gia_nuoc   DECIMAL(10,0),
    snapshot_gia_phong      DECIMAL(12,0)
);
```

### 4.2 SQLAlchemy Models (models.py)

```python
# app/models.py
from app.extensions import db
from datetime import datetime, date

class Phong(db.Model):
    __tablename__ = 'phong'
    phong_id   = db.Column(db.Integer, primary_key=True)
    so_phong   = db.Column(db.String(10), nullable=False, unique=True)
    tang       = db.Column(db.Integer, default=1)
    dien_tich  = db.Column(db.Float)
    cap_phong  = db.Column(db.String(10), default='cap1')   # 'cap1' | 'cap2'
    trang_thai = db.Column(db.String(20), default='trong')  # 'trong'|'dang_thue'|'sua_chua'
    mo_ta      = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    thanh_toans   = db.relationship('ThanhToanThang', backref='hop_dong', lazy=True)

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
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

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
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('hopdong_id', 'thang', 'nam'),)

    hoa_don = db.relationship('HoaDon', backref='thanh_toan', uselist=False)

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
            'so_phong':     hd.phong.so_phong,
            'ho_ten':       hd.khach.ho_ten,
            'thang':        tt.thang,
            'nam':          tt.nam,
            'tien_phong':   float(self.tien_phong),
            'tien_dien':    float(self.tien_dien),
            'tien_nuoc':    float(self.tien_nuoc),
            'phi_dich_vu':  float(self.phi_dich_vu),
            'tong_tien':    float(self.tong_tien),
            'trang_thai':   tt.trang_thai,
            'ngay_tao':     str(self.ngay_tao),
        }
```

---

## 5. Business Logic Rules

> **AI agent đọc section này trước khi viết service/API.**

### Rule 1 — Bảng giá bị khóa (CRITICAL)
```
Không được UPDATE bang_gia WHERE is_locked = true
Trigger khóa: Khi tạo hóa đơn đầu tiên của tháng đó → set is_locked = true
```

### Rule 2 — Tính tiền hóa đơn (invoice_service.py)
```python
def tinh_hoa_don(thanh_toan: ThanhToanThang) -> dict:
    bang_gia = BangGia.query.filter_by(
        thang=thanh_toan.thang,
        nam=thanh_toan.nam
    ).first_or_404(description="Chưa có bảng giá cho tháng này")

    hop_dong = thanh_toan.hop_dong
    phong    = hop_dong.phong

    gia_phong = bang_gia.gia_phong_cap1 if phong.cap_phong == 'cap1' else bang_gia.gia_phong_cap2
    tien_dien  = thanh_toan.so_dien * bang_gia.don_gia_dien
    tien_nuoc  = thanh_toan.so_nuoc * bang_gia.don_gia_nuoc
    phi_dv     = bang_gia.phi_wifi + bang_gia.phi_ve_sinh + bang_gia.phi_gui_xe
    tong       = gia_phong + tien_dien + tien_nuoc + phi_dv

    return {
        'tien_phong':           gia_phong,
        'tien_dien':            tien_dien,
        'tien_nuoc':            tien_nuoc,
        'phi_dich_vu':          phi_dv,
        'tong_tien':            tong,
        'snapshot_don_gia_dien':bang_gia.don_gia_dien,
        'snapshot_don_gia_nuoc':bang_gia.don_gia_nuoc,
        'snapshot_gia_phong':   gia_phong,
    }
```

### Rule 3 — Trạng thái hợp đồng (tự động cập nhật)
```
Mỗi lần GET /api/hop-dong → chạy update_trang_thai():
  - days_remaining > 30  → 'hieu_luc'
  - 0 < days_remaining <= 30 → 'sap_het_han'
  - days_remaining <= 0  → 'het_han'
  - ngay_ket_thuc = NULL → 'hieu_luc' (hợp đồng mở)
```

### Rule 4 — Trạng thái phòng
```
Khi tạo HopDong mới → set phong.trang_thai = 'dang_thue'
Khi HopDong → 'het_han' → set phong.trang_thai = 'trong'
Phòng 'sua_chua' chỉ set thủ công qua API PATCH /api/phong/{id}
```

### Rule 5 — Tạo bản ghi Thanh toán hàng tháng
```
Đầu mỗi tháng, hệ thống (hoặc chủ nhà bấm nút) tạo sẵn bản ghi ThanhToanThang
cho tất cả HopDong đang hieu_luc / sap_het_han.
Bản ghi ban đầu: so_dien=0, so_nuoc=0, trang_thai='chua_tt'
Chủ nhà nhập số điện/nước sau.
```

### Rule 6 — Hóa đơn được tạo/tái tính
```
POST /api/hoa-don/{tt_id}/generate
  - Tính tiền từ Rule 2
  - Nếu đã tồn tại HoaDon → UPDATE (overwrite)
  - Lock BangGia tháng đó (is_locked = true)
  - Trả về HoaDon đã tính
```

---

## 6. API Endpoints

> Base URL: `/api`
> Content-Type: `application/json`
> Lỗi trả về: `{"error": "message", "code": 400}`

### 6.1 Phòng — `/api/phong`

| Method | Path | Mô tả | Body |
|--------|------|-------|------|
| GET | `/api/phong` | Danh sách phòng (có filter `?trang_thai=trong`) | — |
| GET | `/api/phong/{id}` | Chi tiết 1 phòng | — |
| POST | `/api/phong` | Tạo phòng mới | `{so_phong, tang, dien_tich, cap_phong, mo_ta}` |
| PUT | `/api/phong/{id}` | Cập nhật phòng | fields cần update |
| DELETE | `/api/phong/{id}` | Xóa phòng (chỉ khi trang_thai='trong') | — |
| GET | `/api/phong/grid` | Dữ liệu cho grid view (all rooms + status) | — |

### 6.2 Khách Thuê — `/api/khach-thue`

| Method | Path | Mô tả | Body |
|--------|------|-------|------|
| GET | `/api/khach-thue` | Danh sách (filter `?q=tên` hoặc `?so_phong=101`) | — |
| GET | `/api/khach-thue/{id}` | Chi tiết khách | — |
| POST | `/api/khach-thue` | Tạo khách mới | `{ho_ten, cccd, ngay_sinh, sdt, dia_chi, email}` |
| PUT | `/api/khach-thue/{id}` | Cập nhật | fields |
| DELETE | `/api/khach-thue/{id}` | Xóa (chỉ khi không có hợp đồng hiệu lực) | — |

### 6.3 Hợp Đồng — `/api/hop-dong`

| Method | Path | Mô tả | Body |
|--------|------|-------|------|
| GET | `/api/hop-dong` | Danh sách (filter `?trang_thai=hieu_luc`) | — |
| GET | `/api/hop-dong/{id}` | Chi tiết | — |
| POST | `/api/hop-dong` | Tạo hợp đồng mới | `{phong_id, khach_id, ngay_bat_dau, ngay_ket_thuc}` |
| PUT | `/api/hop-dong/{id}` | Gia hạn / kết thúc sớm | `{ngay_ket_thuc, trang_thai}` |
| GET | `/api/hop-dong/sap-het-han` | Danh sách sắp hết hạn (≤30 ngày) | — |

### 6.4 Bảng Giá — `/api/bang-gia`

| Method | Path | Mô tả | Body |
|--------|------|-------|------|
| GET | `/api/bang-gia` | Danh sách tất cả bảng giá | — |
| GET | `/api/bang-gia/{thang}/{nam}` | Bảng giá của 1 tháng | — |
| POST | `/api/bang-gia` | Tạo bảng giá mới cho tháng | `{thang, nam, gia_phong_cap1, ...}` |
| PUT | `/api/bang-gia/{id}` | Cập nhật (chặn nếu is_locked=true → 423 Locked) | fields |
| POST | `/api/bang-gia/copy` | Sao chép bảng giá tháng trước sang tháng mới | `{from_thang, from_nam, to_thang, to_nam}` |

### 6.5 Thanh Toán Tháng — `/api/thanh-toan`

| Method | Path | Mô tả | Body |
|--------|------|-------|------|
| GET | `/api/thanh-toan/{thang}/{nam}` | Tất cả bản ghi tháng đó (dạng bảng) | — |
| POST | `/api/thanh-toan/tao-thang` | Tạo loạt bản ghi cho tháng mới (tất cả HĐ hiệu lực) | `{thang, nam}` |
| PUT | `/api/thanh-toan/{tt_id}` | Cập nhật số điện/nước/trạng thái | `{so_dien, so_nuoc, trang_thai}` |
| PATCH | `/api/thanh-toan/{tt_id}/tick` | Chuyển đổi trạng thái (toggle) | — |

### 6.6 Hóa Đơn — `/api/hoa-don`

| Method | Path | Mô tả | Body |
|--------|------|-------|------|
| GET | `/api/hoa-don/{thang}/{nam}` | Tất cả hóa đơn tháng đó | — |
| GET | `/api/hoa-don/{hoadon_id}` | Chi tiết 1 hóa đơn | — |
| POST | `/api/hoa-don/{tt_id}/generate` | Tính & lưu hóa đơn từ thanh toán tháng | — |
| POST | `/api/hoa-don/generate-all/{thang}/{nam}` | Tính hóa đơn tất cả phòng của tháng | — |
| GET | `/api/hoa-don/{hoadon_id}/pdf` | Trả về file PDF | — |

### 6.7 Thống Kê — `/api/thong-ke`

| Method | Path | Mô tả |
|--------|------|-------|
| GET | `/api/thong-ke/dashboard` | KPI cards: tổng phòng, doanh thu tháng, phòng trống, chưa đóng |
| GET | `/api/thong-ke/doanh-thu?months=6` | Doanh thu 6 tháng gần nhất (cho Chart.js) |
| GET | `/api/thong-ke/chua-dong/{thang}/{nam}` | Danh sách phòng chưa đóng tiền |

### Response mẫu

```json
// GET /api/phong/grid
{
  "data": [
    {
      "phong_id": 1,
      "so_phong": "101",
      "cap_phong": "cap2",
      "trang_thai": "dang_thue",
      "khach_chinh": "Nguyễn Văn A",
      "ngay_het_han": "2025-06-30",
      "days_remaining": 74
    }
  ]
}

// GET /api/thong-ke/dashboard
{
  "tong_phong": 12,
  "phong_dang_thue": 9,
  "phong_trong": 3,
  "doanh_thu_thang_nay": 27000000,
  "chua_dong_tien": 2,
  "sap_het_han": 1
}
```

---

## 7. Frontend — Đặc Tả Từng Màn Hình

> Tất cả màn hình extends `base.html`.
> Data được fetch qua `fetch('/api/...')` — không dùng Jinja2 render data (trừ template tĩnh).

### 7.0 base.html — Layout Chung

```
┌─────────────────────────────────────────────────────┐
│  NAVBAR TOP: Logo "Nhà Trọ" | Tên trang hiện tại   │
├──────────────┬──────────────────────────────────────┤
│  SIDEBAR     │  MAIN CONTENT AREA                   │
│  (fixed)     │                                      │
│  🏠 Dashboard│                                      │
│  🚪 Phòng   │                                      │
│  👤 Khách   │                                      │
│  📋 Hợp đồng│                                      │
│  💰 Bảng giá│                                      │
│  📊 TT Tháng│                                      │
│  🧾 Hóa đơn │                                      │
│  📈 Thống kê│                                      │
│  ⚙️ Nhà trọ │                                      │
└──────────────┴──────────────────────────────────────┘
```

- Sidebar collapse trên mobile (hamburger menu)
- Active link highlight theo route hiện tại
- Badge đỏ trên "Hợp đồng" nếu có hợp đồng sắp hết hạn

### 7.1 Dashboard

**KPI Cards (hàng 1 — 4 thẻ):**
```
[Tổng Phòng: 12] [Đang Thuê: 9] [Phòng Trống: 3] [Doanh Thu Tháng: 27.000.000đ]
```

**Cảnh báo (hàng 2 — 2 thẻ màu):**
```
[⚠️ 2 phòng chưa đóng tiền tháng này]  [🔔 1 hợp đồng sắp hết hạn]
```
→ Click vào cảnh báo → navigate đến màn hình tương ứng

**Biểu đồ (hàng 3):**
- Bar chart: Doanh thu 6 tháng gần nhất (Chart.js)
- Data từ: `GET /api/thong-ke/doanh-thu?months=6`

### 7.2 Quản Lý Phòng

**Grid View (default):**
```
[+ Thêm Phòng]  [🔍 Tìm kiếm]  [Filter: Tất cả ▼]

┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
│  101   │  │  102   │  │  103   │  │  104   │
│ Cấp 2  │  │ Cấp 1  │  │ Cấp 1  │  │ Cấp 2  │
│🟢Thuê  │  │⚪Trống │  │🟢Thuê  │  │🔴Sửa  │
│Ng.V.An │  │        │  │Trần B  │  │        │
└────────┘  └────────┘  └────────┘  └────────┘
```
- Màu thẻ: xanh lá = đang thuê, xám = trống, đỏ = sửa chữa
- Click thẻ → modal xem chi tiết + nút [Sửa] [Xóa]

**Form Thêm/Sửa (trong modal hoặc trang riêng):**
- Số phòng*, Tầng, Diện tích, Cấp phòng (radio: Cấp 1 / Cấp 2), Ghi chú

### 7.3 Quản Lý Khách Thuê

**Table View:**
```
[+ Thêm Khách]  [🔍 Tìm theo tên/CCCD/số phòng]

| Họ tên | CCCD | SĐT | Phòng hiện tại | Ngày thuê | Hành động |
|--------|------|-----|----------------|-----------|-----------|
| Ng.V.A | 001..| 09..| 101            | 01/01/25  | [Sửa][Xóa]|
```

**Form Thêm/Sửa:** họ tên*, CCCD, ngày sinh, SĐT, địa chỉ, email

### 7.4 Quản Lý Hợp Đồng

**Table View với badge trạng thái:**
```
[+ Tạo HĐ]  [Filter: Tất cả | Hiệu lực | Sắp hết hạn | Hết hạn]

| Phòng | Khách thuê | Bắt đầu | Kết thúc | Còn lại | Trạng thái | Hành động |
|-------|-----------|---------|---------|--------|-----------|-----------|
| 101   | Ng.V.An   | 01/01/25| 30/06/25| 74 ngày|🟢Hiệu lực| [Gia hạn][Kết thúc] |
| 102   | Trần B    | 01/01/25| 30/04/25| 13 ngày|🟡Sắp HH  | [Gia hạn][Kết thúc] |
```

**Form Tạo HĐ:** Chọn phòng (dropdown chỉ hiện phòng Trống), Chọn khách, Ngày bắt đầu, Ngày kết thúc

### 7.5 Bảng Giá

**Layout: chọn tháng/năm → hiển thị form nhập giá**
```
Tháng: [05 ▼]  Năm: [2025 ▼]  [Xem]  [Sao chép từ tháng trước]

┌─────────────────────────────────────────────┐
│  🔒 Bảng giá đã khóa (có hóa đơn)          │  ← hiện nếu is_locked
│  hoặc                                       │
│  ✏️  Chỉnh sửa bảng giá tháng 05/2025      │
├──────────────────┬──────────────────────────┤
│ Giá phòng Cấp 1  │ [    2.500.000    ] đ   │
│ Giá phòng Cấp 2  │ [    3.500.000    ] đ   │
│ Đơn giá điện     │ [        3.500    ] đ/kWh│
│ Đơn giá nước     │ [       15.000    ] đ/m³ │
│ Phí Wifi         │ [      100.000    ] đ    │
│ Phí Vệ sinh      │ [       50.000    ] đ    │
│ Phí Gửi xe       │ [       50.000    ] đ    │
├──────────────────┴──────────────────────────┤
│              [Lưu Bảng Giá]                 │
└─────────────────────────────────────────────┘
```

### 7.6 Thanh Toán Hàng Tháng

**Layout: bảng điểm danh**
```
Tháng: [05 ▼]  Năm: [2025 ▼]  [Tải danh sách]  [Tạo tháng mới]  [Tính tất cả HĐ]

| Phòng | Khách thuê  | Số điện (kWh) | Số nước (m³) | Tổng tạm tính | Trạng thái       |
|-------|------------|--------------|-------------|--------------|-----------------|
| 101   | Ng.V.An    | [  120  ]    | [  4.5  ]   | 3.890.000đ   | [✅ Đã TT]       |
| 102   | Trần B     | [   85  ]    | [  3.0  ]   | 3.155.000đ   | [⬜ Chưa TT]     |
| 103   | Lê C       | [  200  ]    | [  6.0  ]   | 4.490.000đ   | [⬜ Chưa TT]     |
```
- Ô nhập số điện/nước: inline editable, blur → auto-save (PATCH API)
- Cột "Tổng tạm tính": tính realtime trên client khi nhập số, lấy đơn giá từ Bảng giá
- Cột "Trạng thái": button toggle, click → đổi trạng thái + gọi API

### 7.7 Hóa Đơn Tháng

**Danh sách hóa đơn:**
```
Tháng: [05 ▼]  Năm: [2025 ▼]  [Xem]  [Tạo tất cả HĐ tháng này]

| Phòng | Khách | Tiền phòng | Điện | Nước | Dịch vụ | Tổng | Trạng thái | |
|-------|-------|-----------|------|------|---------|------|-----------|---|
| 101   | Ng.A  | 3.500.000 | 420k | 68k  | 200k    | 4.2M | ✅ Đã TT | [PDF] |
```

**Chi tiết hóa đơn (modal):**
```
╔══════════════════════════════════════╗
║   HÓA ĐƠN TIỀN PHÒNG — THÁNG 5/2025║
║   Phòng 101 | Nguyễn Văn An          ║
╠══════════════════════════════════════╣
║ Tiền phòng (Cấp 2):     3.500.000đ  ║
║ Tiền điện (120 kWh):      420.000đ  ║
║ Tiền nước (4.5 m³):        67.500đ  ║
║ Phí dịch vụ:              200.000đ  ║
╠══════════════════════════════════════╣
║ TỔNG CỘNG:              4.187.500đ  ║
╚══════════════════════════════════════╝
[Xuất PDF]  [Đóng]
```

### 7.8 Thống Kê

- **Dropdown chọn năm** → load dữ liệu
- **Bar chart**: Doanh thu 12 tháng (Chart.js)
- **Bảng**: Doanh thu từng tháng + số phòng đã thu / tổng phòng

### 7.9 Thông Tin Nhà Trọ

- Form: Tên nhà trọ, Địa chỉ, SĐT chủ nhà
- Lưu vào bảng `config` (key-value) hoặc file JSON tĩnh

---

## 8. Checklist Tiến Độ

> Cập nhật `[ ]` → `[x]` sau mỗi task hoàn thành.

### Phase 0 — Khởi tạo Dự Án

- [x] Tạo repo git, `.gitignore`, `README.md`
- [x] Tạo virtualenv, cài `requirements.txt` (Flask, SQLAlchemy, Flask-Migrate, WeasyPrint)
- [x] Tạo `config.py`, `run.py`, `app/__init__.py` (app factory)
- [x] Tạo `app/extensions.py` (db, migrate)
- [x] Viết `app/models.py` (6 models đầy đủ)
- [x] Chạy `flask db init && flask db migrate && flask db upgrade`
- [x] Seed data mẫu: 5 phòng, 3 khách, 2 hợp đồng, 1 bảng giá

### Phase 1 — Back-end API

#### Module: Phòng (`app/api/phong.py`)
- [x] GET `/api/phong` — list + filter theo trang_thai
- [x] GET `/api/phong/{id}` — chi tiết
- [x] POST `/api/phong` — tạo mới (validate so_phong unique)
- [x] PUT `/api/phong/{id}` — cập nhật
- [x] DELETE `/api/phong/{id}` — xóa (check không có HĐ hiệu lực)
- [x] GET `/api/phong/grid` — grid data

#### Module: Khách Thuê (`app/api/khach_thue.py`)
- [x] GET `/api/khach-thue` — list + search `?q=`
- [x] GET `/api/khach-thue/{id}`
- [x] POST `/api/khach-thue`
- [x] PUT `/api/khach-thue/{id}`
- [x] DELETE `/api/khach-thue/{id}`

#### Module: Hợp Đồng (`app/api/hop_dong.py`)
- [x] GET `/api/hop-dong` — list + filter
- [x] GET `/api/hop-dong/{id}`
- [x] POST `/api/hop-dong` (tạo HĐ → set phong.trang_thai='dang_thue')
- [x] PUT `/api/hop-dong/{id}` (gia hạn / kết thúc sớm)
- [x] GET `/api/hop-dong/sap-het-han`
- [x] Viết `services/warning_service.py`: auto-update trang_thai HĐ

#### Module: Bảng Giá (`app/api/bang_gia.py`)
- [x] GET `/api/bang-gia`
- [x] GET `/api/bang-gia/{thang}/{nam}`
- [x] POST `/api/bang-gia`
- [x] PUT `/api/bang-gia/{id}` (chặn nếu is_locked → trả 423)
- [x] POST `/api/bang-gia/copy` (copy từ tháng trước)

#### Module: Thanh Toán (`app/api/thanh_toan.py`)
- [x] GET `/api/thanh-toan/{thang}/{nam}`
- [x] POST `/api/thanh-toan/tao-thang` (batch create)
- [x] PUT `/api/thanh-toan/{tt_id}`
- [x] PATCH `/api/thanh-toan/{tt_id}/tick`

#### Module: Hóa Đơn (`app/api/hoa_don.py`)
- [x] Viết `services/invoice_service.py` (Rule 2)
- [x] GET `/api/hoa-don/{thang}/{nam}`
- [x] GET `/api/hoa-don/{hoadon_id}`
- [x] POST `/api/hoa-don/{tt_id}/generate` (+ lock BangGia)
- [x] POST `/api/hoa-don/generate-all/{thang}/{nam}`
- [x] GET `/api/hoa-don/{hoadon_id}/pdf`
- [x] Viết `services/pdf_service.py` (WeasyPrint render `pdf/hoa_don_pdf.html`)

#### Module: Thống Kê (`app/api/thong_ke.py`)
- [x] GET `/api/thong-ke/dashboard`
- [x] GET `/api/thong-ke/doanh-thu`
- [x] GET `/api/thong-ke/chua-dong/{thang}/{nam}`

### Phase 2 — Front-end

#### Layout & Base
- [x] `base.html` — sidebar, navbar, responsive
- [x] `static/css/style.css` — custom styles
- [x] `static/js/main.js` — utility: `formatVND()`, `showToast()`, `fetchAPI()`

#### Từng Màn Hình
- [x] `dashboard.html` + `dashboard.js` (KPI cards, chart, cảnh báo)
- [x] `phong/index.html` + `phong.js` (grid view, modal CRUD)
- [ ] `phong/form.html` (form thêm/sửa nếu dùng trang riêng)
- [x] `khach_thue/index.html` (table, search, modal CRUD)
- [x] `hop_dong/index.html` (table, filter, modal tạo/gia hạn)
- [x] `bang_gia/index.html` (form nhập giá theo tháng, lock indicator)
- [x] `thanh_toan/index.html` + `thanh_toan.js` (bảng inline-edit)
- [x] `hoa_don/index.html` (danh sách + nút tạo batch)
- [ ] `hoa_don/detail.html` (chi tiết 1 hóa đơn + xuất PDF)
- [x] `thong_ke/index.html` + `thong_ke.js` (Chart.js bar chart)
- [ ] `pdf/hoa_don_pdf.html` (template PDF — không có sidebar)

### Phase 3 — Kiểm Thử

- [x] `tests/test_models.py` — unit test models
- [x] `tests/test_api_phong.py` — API test CRUD phòng
- [x] `tests/test_invoice_service.py` — test tính tiền hóa đơn (nhiều case)
- [x] Manual test: luồng happy path (tạo phòng → HĐ → nhập TT → xem hóa đơn)
- [x] Test lock Bảng giá: thử sửa tháng đã có hóa đơn → nhận lỗi 423
- [x] Test responsive: mobile, tablet, desktop

### Phase 4 — Hoàn Thiện

- [ ] Seed data demo đầy đủ (12 phòng, 3 tháng dữ liệu)
- [x] Viết `README.md` hướng dẫn cài đặt và chạy
- [ ] Deploy thử nghiệm (localhost hoặc Railway/Render)
- [ ] Chuẩn bị slide demo

---
> Cập nhật thực tế ngày 17/04/2026:
> - Đã nối app factory với API blueprints và page routes cho các màn hình chính.
> - Đã bổ sung warning_service.py, invoice_service.py, pdf_service.py ở mức đủ để app boot và chạy luồng tối thiểu.
> - Đã thêm HopDong.update_trang_thai() và ThanhToanThang.to_dict().
> - Đã cập nhật seed demo để còn hợp đồng hiệu lực, hợp đồng sắp hết hạn, dữ liệu thanh toán/hóa đơn cho dashboard và list.
> - Đã verify end-to-end core flow ở mức API/test client: phòng → khách → hợp đồng → thanh toán → hóa đơn → dashboard.
> - Đã thêm tests/ với smoke test và core API flow tối thiểu chạy độc lập trên SQLite test DB.
> - Đã sửa cấu hình static trong app factory để browser load đúng CSS/JS từ thư mục gốc `static/`.
> - Đã browser-verify các màn Dashboard, Phòng, Khách thuê, Hợp đồng, Bảng giá, Thanh toán, Hóa đơn, Thống kê ở mức load dữ liệu và thao tác chính.
> - Đã dọn warning chính của suite bằng cách thay `datetime.utcnow()` và `Query.get()`/`get_or_404()` cũ bằng helper hiện đại dựa trên `db.session.get(...)`.
> - Đã verify `POST /api/bang-gia/copy` với cả case thành công, thiếu tháng nguồn và trùng tháng đích.
> - Phase 3 vẫn chưa đủ điều kiện tick thêm ngoài mức regression tối thiểu vì chưa có test models/service riêng và chưa có manual responsive coverage.
---

> Cập nhật thực tế ngày 18/04/2026:
> - Phase 3 đã hoàn tất, gồm test models, test API phòng, test invoice service, manual happy path, lock bảng giá `423` và responsive verification.
> - `README.md` đã được nâng lên mức handoff/demo-ready và đã thêm `HANDOFF_NOTES.md`.
> - Phase 2 vẫn còn đúng 3 mục artifact chưa tick: `phong/form.html`, `hoa_don/detail.html`, `pdf/hoa_don_pdf.html`.
> - Hai mục `phong/form.html` và `hoa_don/detail.html` hiện được thay bằng modal trong trang index tương ứng; không tick bổ sung để tránh over-claim.
> - `app/templates/pdf/hoa_don_pdf.html` đã có trong repo và được `pdf_service.py` dùng khi WeasyPrint khả dụng, nhưng checklist vẫn giữ `[ ]` do artifact này chưa được chốt riêng như một deliverable frontend độc lập và runtime vẫn có fallback PDF tối thiểu.

## 9. Conventions & Code Style

### Python / Flask

```python
# Đặt tên snake_case cho tất cả biến, hàm, file
# Tên class: PascalCase

# Mỗi route trả về JSON nhất quán:
def success_response(data, status=200):
    return jsonify({"data": data, "success": True}), status

def error_response(message, status=400):
    return jsonify({"error": message, "success": False}), status

# Validate input bằng if/else đơn giản (không dùng Marshmallow để giữ đơn giản)
# Ví dụ:
@bp.route('', methods=['POST'])
def create_phong():
    body = request.get_json()
    if not body.get('so_phong'):
        return error_response("Thiếu số phòng", 400)
    # ...
```

### JavaScript (Vanilla ES6+)

```javascript
// Dùng async/await, không dùng .then() chain
// Gọi API qua hàm chung trong main.js:
async function fetchAPI(url, method='GET', body=null) {
    const opts = { method, headers: {'Content-Type': 'application/json'} };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(url, opts);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Lỗi server');
    return data;
}

// Format tiền VNĐ:
function formatVND(amount) {
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount);
}

// Toast notification (Bootstrap 5):
function showToast(message, type='success') { /* ... */ }
```

### HTML / Jinja2

```html
<!-- Không nhúng data vào Jinja2 render — fetch qua JS -->
<!-- Ngoại lệ: các trang tĩnh (thông tin nhà trọ) -->

<!-- Class naming: dùng Bootstrap utilities, tránh CSS tùy chỉnh nếu Bootstrap đã có -->
<!-- Mọi form có novalidate + JS validation trước khi gọi API -->
```

### Git Commit Messages (tiếng Anh)
```
feat: add invoice generation API
fix: prevent editing locked bang_gia
style: responsive sidebar on mobile
test: add invoice_service unit tests
```

---

## 10. Gợi Ý Phân Công Cho AI Tools

> Mỗi AI agent nhận 1 nhiệm vụ cụ thể, đọc phần context liên quan trong file này.

### Cách giao việc cho AI agent

Khi giao task cho bất kỳ AI tool nào, luôn đính kèm lệnh sau:
```
Đọc file PLAN.md (đặc biệt section 4, 5, 6) trước khi bắt đầu.
Dự án: Flask + SQLAlchemy + Bootstrap 5 + Vanilla JS.
Không tự thay đổi tech stack hoặc thêm thư viện ngoài danh sách trong section 2.
Sau khi hoàn thành, cập nhật checkbox tương ứng trong section 8.
```

### Phân công gợi ý theo AI tool

| Tool | Phù hợp với task |
|------|-----------------|
| **Claude Code** | Viết toàn bộ `app/models.py`, `app/api/*.py`, `services/*.py` — cần hiểu context phức tạp |
| **Cursor / Copilot** | Autocomplete từng file, sửa bug nhỏ, refactor |
| **Codex / GPT-4** | Viết unit test (`tests/`), viết SQL queries phức tạp |
| **Claude.ai (chat)** | Thiết kế logic mới, review code, giải thích business rule |
| **v0.dev / Lovable** | Tạo prototype UI nhanh cho 1 màn hình cụ thể (paste vào template sau) |

### Ví dụ prompt giao task cụ thể

```
# Giao cho Claude Code:
"Dựa trên PLAN.md section 4 (models) và section 6.4 (API Bảng giá),
hãy implement file app/api/bang_gia.py đầy đủ theo spec.
Chú ý Rule 1 (section 5): chặn UPDATE khi is_locked=true, trả về HTTP 423."

# Giao cho Codex:
"Dựa trên PLAN.md section 5 (Rule 2 — công thức tính hóa đơn),
viết file tests/test_invoice_service.py với các test case:
1. Phòng Cấp 1, 2. Phòng Cấp 2, 3. Không có bảng giá, 4. Giá 0 đồng."

# Giao cho v0.dev:
"Tạo UI màn hình Thanh toán hàng tháng (PLAN.md section 7.6):
bảng inline-edit số điện/nước, nút toggle trạng thái, tổng tạm tính realtime.
Dùng Bootstrap 5, Vanilla JS. Không dùng React."
```

---

*File này là living document — cập nhật mỗi khi có thay đổi thiết kế hoặc quyết định kỹ thuật mới.*

*Phiên bản: 1.0 | Tạo dựa trên: mo-ta-y-tuong-quan-ly-nha-tro_FINAL_.md*
