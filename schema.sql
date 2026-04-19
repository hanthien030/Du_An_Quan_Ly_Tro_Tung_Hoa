-- Generated from app/models.py and migrations/versions/f8f98cfc925e_init_models.py
-- Target dialect: SQLite-compatible SQL

CREATE TABLE bang_gia (
    bangia_id INTEGER PRIMARY KEY AUTOINCREMENT,
    thang INTEGER NOT NULL,
    nam INTEGER NOT NULL,
    gia_phong_cap1 NUMERIC(12, 0) NOT NULL,
    gia_phong_cap2 NUMERIC(12, 0) NOT NULL,
    don_gia_dien NUMERIC(10, 0) NOT NULL,
    don_gia_nuoc NUMERIC(10, 0) NOT NULL,
    phi_wifi NUMERIC(10, 0),
    phi_ve_sinh NUMERIC(10, 0),
    phi_gui_xe NUMERIC(10, 0),
    is_locked BOOLEAN,
    created_at DATETIME,
    CONSTRAINT uq_bang_gia_thang_nam UNIQUE (thang, nam)
);

CREATE TABLE khach_thue (
    khach_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ho_ten VARCHAR(100) NOT NULL,
    cccd VARCHAR(20) UNIQUE,
    ngay_sinh DATE,
    sdt VARCHAR(15),
    dia_chi TEXT,
    email VARCHAR(100),
    la_chinh BOOLEAN,
    created_at DATETIME
);

CREATE TABLE phong (
    phong_id INTEGER PRIMARY KEY AUTOINCREMENT,
    so_phong VARCHAR(10) NOT NULL UNIQUE,
    tang INTEGER,
    dien_tich FLOAT,
    cap_phong VARCHAR(10),
    trang_thai VARCHAR(20),
    mo_ta TEXT,
    created_at DATETIME
);

CREATE TABLE hop_dong (
    hopdong_id INTEGER PRIMARY KEY AUTOINCREMENT,
    phong_id INTEGER NOT NULL,
    khach_id INTEGER NOT NULL,
    ngay_bat_dau DATE NOT NULL,
    ngay_ket_thuc DATE,
    trang_thai VARCHAR(20),
    ghi_chu TEXT,
    created_at DATETIME,
    CONSTRAINT fk_hop_dong_phong FOREIGN KEY (phong_id) REFERENCES phong (phong_id),
    CONSTRAINT fk_hop_dong_khach_thue FOREIGN KEY (khach_id) REFERENCES khach_thue (khach_id)
);

CREATE TABLE thanh_toan_thang (
    tt_id INTEGER PRIMARY KEY AUTOINCREMENT,
    hopdong_id INTEGER NOT NULL,
    thang INTEGER NOT NULL,
    nam INTEGER NOT NULL,
    so_dien FLOAT,
    so_nuoc FLOAT,
    trang_thai VARCHAR(20),
    ngay_thanh_toan DATE,
    ghi_chu TEXT,
    created_at DATETIME,
    CONSTRAINT fk_thanh_toan_thang_hop_dong FOREIGN KEY (hopdong_id) REFERENCES hop_dong (hopdong_id),
    CONSTRAINT uq_thanh_toan_thang_hopdong_thang_nam UNIQUE (hopdong_id, thang, nam)
);

CREATE TABLE hoa_don (
    hoadon_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tt_id INTEGER NOT NULL UNIQUE,
    tien_phong NUMERIC(12, 0) NOT NULL,
    tien_dien NUMERIC(12, 0) NOT NULL,
    tien_nuoc NUMERIC(12, 0) NOT NULL,
    phi_dich_vu NUMERIC(12, 0),
    tong_tien NUMERIC(12, 0) NOT NULL,
    ngay_tao DATE,
    snapshot_don_gia_dien NUMERIC(10, 0),
    snapshot_don_gia_nuoc NUMERIC(10, 0),
    snapshot_gia_phong NUMERIC(12, 0),
    CONSTRAINT fk_hoa_don_thanh_toan_thang FOREIGN KEY (tt_id) REFERENCES thanh_toan_thang (tt_id)
);
