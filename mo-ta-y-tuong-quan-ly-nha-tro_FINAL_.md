# Mô Tả Ý Tưởng: Ứng Dụng Quản Lý Dãy Trọ Bình Dân

---

## 1. Tổng Quan Dự Án

### 1.1 Tên dự án
**Hệ thống Quản lý Dãy Trọ Bình Dân** — Ứng dụng web hỗ trợ chủ nhà trọ quản lý phòng, khách thuê, hợp đồng và thu tiền hằng tháng một cách hiệu quả, thay thế việc ghi chép thủ công bằng sổ sách.

### 1.2 Mục tiêu
- Giúp chủ nhà dễ dàng theo dõi tình trạng phòng trọ (trống / đang thuê)
- Quản lý thông tin khách thuê và hợp đồng
- Tự động tính tiền phòng, điện, nước hàng tháng
- Theo dõi trạng thái thanh toán, cảnh báo nợ tiền
- Thống kê doanh thu theo tháng / năm

### 1.3 Đối tượng sử dụng
- **Chủ nhà trọ**: người dùng chính của hệ thống
- Quy mô hướng đến: nhà trọ vừa và nhỏ từ 5–30 phòng

---

## 2. Phân Tích Nghiệp Vụ

### 2.1 Quản lý Phòng
- Thêm, sửa, xóa thông tin phòng (số phòng, tầng, diện tích)
- Phân loại phòng theo 2 cấp:
  - **Phòng Cấp 1**: Phòng không có tiện nghi (giá rẻ nhất)
  - **Phòng Cấp 2**: Phòng đầy đủ tiện nghi (giá đắt hơn)
- Theo dõi trạng thái phòng: **Trống** / **Đang thuê** / **Đang sửa chữa**
- Xem danh sách phòng dạng lưới (grid), nhận biết nhanh phòng nào còn trống
- Ghi chú tiện nghi theo phòng (có điều hòa, có máy giặt, nóng lạnh, ...)

### 2.2 Quản lý Khách Thuê
- Lưu thông tin cá nhân: họ tên, CCCD/CMND, ngày sinh, số điện thoại, địa chỉ thường trú
- Mỗi phòng có thể có nhiều khách thuê (người thuê chính + người ở cùng)
- Lưu ảnh CCCD (tùy chọn)
- Tìm kiếm khách theo tên, số CCCD, số phòng

### 2.3 Quản lý Hợp Đồng
- Tạo hợp đồng thuê phòng: ngày bắt đầu, ngày kết thúc (không cần cọc, đóng tiền cuối tháng)
- Gia hạn hợp đồng, ghi nhận ngày kết thúc hợp đồng sớm (khách trả phòng)
- Cảnh báo hợp đồng còn bao nhiêu ngày đến hạn
- Trạng thái hợp đồng: **Hiệu lực** / **Sắp hết hạn** / **Hết hạn**

### 2.4 Quản lý Hóa Đơn & Thu Tiền
Hằng tháng tạo hóa đơn cho từng phòng, bao gồm:

| Khoản mục | Cách tính |
|-----------|-----------|
| Tiền phòng | Giá gốc theo loại phòng (Cấp 1 / Cấp 2), lấy từ Bảng giá tháng đó |
| Tiền điện | Số điện (kWh) nhập tay × Đơn giá điện tháng đó |
| Tiền nước | Số nước (m³) nhập tay × Đơn giá nước tháng đó |
| Phí dịch vụ | Wifi + Vệ sinh + Gửi xe (lấy từ Bảng giá tháng đó) |
| **Tổng tiền** | Tiền phòng + Tiền điện + Tiền nước + Phí dịch vụ |

- Hóa đơn được tổng hợp tự động từ dữ liệu **Bảng giá** và **Thanh toán hàng tháng**
- Có thể xuất hóa đơn PDF hoặc in trực tiếp

### 2.5 Bảng Giá Theo Tháng

> **Mô tả:** Bảng dùng để nhập các mức giá áp dụng cho từng tháng. Dựa vào bảng này, chủ nhà có thể điều chỉnh giá (tăng/giảm) cho các tháng sắp tới.

Các mục cần nhập trong Bảng giá:

| Mục giá | Đơn vị |
|---------|--------|
| Giá phòng Cấp 1 | VNĐ / tháng |
| Giá phòng Cấp 2 | VNĐ / tháng |
| Đơn giá điện | VNĐ / kWh |
| Đơn giá nước | VNĐ / m³ |
| Phí wifi | VNĐ / tháng |
| Phí vệ sinh | VNĐ / tháng |
| Phí gửi xe | VNĐ / tháng |

> ⚠️ **Lưu ý quan trọng:** Bảng giá chỉ có thể áp dụng cho tháng hiện tại trở đi. Các tháng đã có hóa đơn thanh toán **không được phép chỉnh sửa** — nếu sửa sẽ làm sai toàn bộ dữ liệu hóa đơn đã ghi nhận.

### 2.6 Thanh Toán Hàng Tháng

> **Mô tả:** Bảng dùng để nhập dữ liệu tiêu thụ và xác nhận trạng thái thanh toán cuối tháng cho từng phòng — tương tự bảng điểm danh sinh viên, nhập dữ liệu trong kỳ và tick xác nhận khi hoàn tất.

Các cột trong bảng Thanh toán hàng tháng:

| Cột | Mô tả |
|-----|-------|
| Số phòng | Mã phòng |
| Số điện (kWh) | Nhập tay tổng số điện tiêu thụ trong tháng |
| Số nước (m³) | Nhập tay tổng số nước tiêu thụ trong tháng |
| Trạng thái thanh toán | Bấm chọn: **Đã thanh toán** / **Chưa thanh toán** |

### 2.7 Thống Kê & Báo Cáo
- Tổng doanh thu theo tháng / quý / năm
- Số phòng đang trống, số phòng đang cho thuê
- Danh sách phòng chưa đóng tiền trong tháng
- Biểu đồ doanh thu theo tháng

---

## 3. Thiết Kế Giao Diện (Front-end)

### 3.1 Công nghệ
- **HTML5 + CSS3 + JavaScript** (Vanilla hoặc Bootstrap 5)
- Giao diện responsive (tương thích máy tính và điện thoại)
- Sử dụng **Chart.js** để vẽ biểu đồ thống kê

### 3.2 Các Màn Hình Chính

| STT | Màn hình | Chức năng chính |
|-----|----------|-----------------|
| 1 | Dashboard / Trang chủ | Tổng quan: số phòng, doanh thu, cảnh báo |
| 2 | Quản lý Phòng | Danh sách phòng dạng grid + CRUD |
| 3 | Quản lý Khách thuê | Bảng danh sách + tìm kiếm + CRUD |
| 4 | Quản lý Hợp đồng | Danh sách hợp đồng, lọc theo trạng thái |
| 5 | Bảng giá | Nhập giá phòng / điện / nước / dịch vụ theo tháng |
| 6 | Thanh toán hàng tháng | Nhập số điện, số nước, xác nhận trạng thái thanh toán |
| 7 | Hóa đơn tháng | Xem chi tiết hóa đơn, xuất PDF |
| 8 | Thống kê | Biểu đồ doanh thu, báo cáo theo tháng / năm |
| 9 | Thông tin nhà trọ | Hiển thị và chỉnh sửa thông tin chung của dãy trọ |

### 3.3 Dashboard (Trang Chủ)
Hiển thị nhanh các thông tin quan trọng nhất:
- **Thẻ KPI**: Tổng số phòng | Phòng đang thuê | Phòng trống | Doanh thu tháng này
- **Cảnh báo**: Phòng chưa đóng tiền tháng này | Hợp đồng sắp hết hạn
- **Biểu đồ**: Doanh thu 6 tháng gần nhất

---

## 4. Thiết Kế Cơ Sở Dữ Liệu (Back-end)

### 4.1 Công nghệ đề xuất
- **Ngôn ngữ xử lý nghiệp vụ**: Python (Flask) hoặc PHP hoặc Node.js (Express)
- **Hệ quản trị CSDL**: MySQL / SQLite / PostgreSQL
- **Giao tiếp**: REST API (JSON) giữa front-end và back-end

### 4.2 Sơ Đồ Các Bảng Dữ Liệu (6 bảng chính)

#### Bảng `PHONG` (Rooms)
| Cột | Kiểu dữ liệu | Mô tả |
|-----|-------------|-------|
| phong_id | INT (PK) | Mã phòng |
| so_phong | VARCHAR(10) | Số hiệu phòng (101, 102, ...) |
| tang | INT | Tầng |
| dien_tich | FLOAT | Diện tích (m²) |
| cap_phong | ENUM | Cấp 1 / Cấp 2 |
| trang_thai | ENUM | Trống / Đang thuê / Sửa chữa |
| mo_ta | TEXT | Ghi chú tiện nghi |

#### Bảng `KHACH_THUE` (Tenants)
| Cột | Kiểu dữ liệu | Mô tả |
|-----|-------------|-------|
| khach_id | INT (PK) | Mã khách thuê |
| ho_ten | VARCHAR(100) | Họ và tên |
| cccd | VARCHAR(20) | Số CCCD / CMND |
| ngay_sinh | DATE | Ngày sinh |
| sdt | VARCHAR(15) | Số điện thoại |
| dia_chi | TEXT | Địa chỉ thường trú |
| email | VARCHAR(100) | Email liên hệ (tùy chọn) |

#### Bảng `HOP_DONG` (Contracts)
| Cột | Kiểu dữ liệu | Mô tả |
|-----|-------------|-------|
| hopdong_id | INT (PK) | Mã hợp đồng |
| phong_id | INT (FK) | Phòng thuê |
| khach_id | INT (FK) | Khách thuê chính |
| ngay_bat_dau | DATE | Ngày bắt đầu thuê |
| ngay_ket_thuc | DATE | Ngày dự kiến kết thúc |
| trang_thai | ENUM | Hiệu lực / Sắp hết hạn / Hết hạn |
| ghi_chu | TEXT | Ghi chú thêm |

#### Bảng `BANG_GIA` (Price Table)
| Cột | Kiểu dữ liệu | Mô tả |
|-----|-------------|-------|
| bangia_id | INT (PK) | Mã bảng giá |
| thang | INT | Tháng áp dụng |
| nam | INT | Năm áp dụng |
| gia_phong_cap1 | DECIMAL | Giá phòng Cấp 1 (VNĐ/tháng) |
| gia_phong_cap2 | DECIMAL | Giá phòng Cấp 2 (VNĐ/tháng) |
| don_gia_dien | DECIMAL | Đơn giá điện (VNĐ/kWh) |
| don_gia_nuoc | DECIMAL | Đơn giá nước (VNĐ/m³) |
| phi_wifi | DECIMAL | Phí wifi (VNĐ/tháng) |
| phi_ve_sinh | DECIMAL | Phí vệ sinh (VNĐ/tháng) |
| phi_gui_xe | DECIMAL | Phí gửi xe (VNĐ/tháng) |

> Ràng buộc: Mỗi cặp `(thang, nam)` là duy nhất. Không cho phép sửa bảng giá của tháng đã có hóa đơn.

#### Bảng `THANH_TOAN_THANG` (Monthly Payment Input)
| Cột | Kiểu dữ liệu | Mô tả |
|-----|-------------|-------|
| tt_id | INT (PK) | Mã bản ghi |
| hopdong_id | INT (FK) | Hợp đồng liên quan |
| thang | INT | Tháng |
| nam | INT | Năm |
| so_dien | FLOAT | Số điện tiêu thụ (kWh) |
| so_nuoc | FLOAT | Số nước tiêu thụ (m³) |
| trang_thai | ENUM | Đã thanh toán / Chưa thanh toán |
| ngay_thanh_toan | DATE | Ngày thanh toán thực tế (nếu đã TT) |

#### Bảng `HOA_DON` (Invoices — sinh từ BANG_GIA + THANH_TOAN_THANG)
| Cột | Kiểu dữ liệu | Mô tả |
|-----|-------------|-------|
| hoadon_id | INT (PK) | Mã hóa đơn |
| tt_id | INT (FK) | Bản ghi thanh toán tháng |
| tien_phong | DECIMAL | Tiền phòng (theo cấp phòng) |
| tien_dien | DECIMAL | Tiền điện = Số điện × Đơn giá điện |
| tien_nuoc | DECIMAL | Tiền nước = Số nước × Đơn giá nước |
| phi_dich_vu | DECIMAL | Tổng phí dịch vụ (wifi + vệ sinh + xe) |
| tong_tien | DECIMAL | Tổng tiền phải nộp |
| ngay_tao | DATE | Ngày lập hóa đơn |

### 4.3 Quan Hệ Giữa Các Bảng

```
PHONG (1) ──────────── (N) HOP_DONG
KHACH_THUE (1) ──────── (N) HOP_DONG
HOP_DONG (1) ──────────── (N) THANH_TOAN_THANG
BANG_GIA (1) ────────────── (N) THANH_TOAN_THANG  [cùng tháng/năm]
THANH_TOAN_THANG (1) ─── (1) HOA_DON
```

### 4.4 Công Thức Tính Tiền Hóa Đơn

```
Tiền phòng  = Giá phòng Cấp 1 hoặc Cấp 2  (theo BANG_GIA tháng đó)
Tiền điện   = so_dien  × don_gia_dien       (theo BANG_GIA tháng đó)
Tiền nước   = so_nuoc  × don_gia_nuoc       (theo BANG_GIA tháng đó)
Phí DV      = phi_wifi + phi_ve_sinh + phi_gui_xe
Tổng tiền   = Tiền phòng + Tiền điện + Tiền nước + Phí DV
```

---

## 5. Kiến Trúc Hệ Thống

```
┌──────────────────────────────────────────────────┐
│               NGƯỜI DÙNG (Browser)              │
└───────────────────────┬──────────────────────────┘
                        │ HTTP Request / Response
┌───────────────────────▼──────────────────────────┐
│            FRONT-END (HTML / CSS / JS)           │
│  - Giao diện người dùng                          │
│  - Gửi request đến API                           │
│  - Hiển thị dữ liệu nhận về                      │
└───────────────────────┬──────────────────────────┘
                        │ REST API (JSON)
┌───────────────────────▼──────────────────────────┐
│          BACK-END (Python Flask / PHP)           │
│  - Xử lý logic nghiệp vụ                        │
│  - Tính toán hóa đơn                             │
│  - Kiểm soát quy tắc khóa bảng giá              │
│  - Xác thực dữ liệu                              │
│  - Cung cấp API cho front-end                    │
└───────────────────────┬──────────────────────────┘
                        │ SQL Query
┌───────────────────────▼──────────────────────────┐
│           DATABASE (MySQL / SQLite)              │
│  - Lưu trữ toàn bộ dữ liệu                      │
│  - 6 bảng quan hệ                                │
└──────────────────────────────────────────────────┘
```

---

## 6. Các Chức Năng Phân Theo Mức Độ Ưu Tiên

### Mức 1 — Bắt buộc (Core Features)
- ✅ CRUD Phòng trọ (phân loại Cấp 1 / Cấp 2)
- ✅ CRUD Khách thuê
- ✅ CRUD Hợp đồng
- ✅ Bảng giá theo tháng (nhập & khóa tháng đã thanh toán)
- ✅ Thanh toán hàng tháng (nhập số điện, nước, tick trạng thái)
- ✅ Tạo và xem hóa đơn tháng (tính tự động)
- ✅ Dashboard tổng quan

### Mức 2 — Nên có (Enhanced Features)
- ⭐ Cảnh báo hợp đồng sắp hết hạn
- ⭐ Danh sách phòng chưa đóng tiền tháng này
- ⭐ Thống kê doanh thu theo tháng / quý / năm
- ⭐ Tìm kiếm khách thuê theo tên / CCCD / số phòng

### Mức 3 — Nâng cao (Bonus Features)
- 💡 Xuất hóa đơn PDF
- 💡 Biểu đồ doanh thu (Chart.js)
- 💡 Lọc & tìm kiếm nâng cao
- 💡 Đăng nhập / phân quyền người dùng

---

## 7. Phân Công & Kế Hoạch Thực Hiện

### Gợi ý phân công (nhóm 2–3 người)

| Thành viên | Phần đảm nhận |
|------------|--------------|
| Thành viên 1 | Thiết kế Database + Back-end API: CRUD Phòng, Khách thuê, Bảng giá |
| Thành viên 2 | Back-end API: Hợp đồng, Thanh toán hàng tháng, Hóa đơn (tính tiền tự động) |
| Thành viên 3 | Front-end toàn bộ (HTML / CSS / JS, gọi API, Dashboard, biểu đồ) |

### Kế hoạch (căn theo deadline nộp 18/4)

| Giai đoạn | Nội dung | Thời gian |
|-----------|----------|-----------|
| 1 | Phân tích nghiệp vụ, thiết kế DB, tạo bảng SQL | Ngày 1–2 |
| 2 | Viết API back-end (CRUD cơ bản) | Ngày 3–4 |
| 3 | Xây dựng giao diện front-end | Ngày 5–6 |
| 4 | Kết nối front-end với back-end | Ngày 7 |
| 5 | Kiểm thử, sửa lỗi, viết báo cáo | Ngày 8 |

---

## 8. Công Nghệ Đề Xuất

| Thành phần | Lựa chọn đề xuất | Lý do |
|------------|-----------------|-------|
| Front-end | HTML5 + CSS3 + Bootstrap 5 + JS | Phổ biến, dễ tạo UI đẹp, responsive |
| Back-end | Python + Flask | Đơn giản, ít boilerplate, dễ học |
| Database | MySQL | Phổ biến, dễ cài đặt, nhiều tài liệu |
| Giao tiếp | REST API (JSON) | Tách biệt rõ front-end / back-end |
| Biểu đồ | Chart.js | Nhẹ, dễ tích hợp với HTML / JS |
| ORM | SQLAlchemy (nếu dùng Flask) | Viết truy vấn DB dễ hơn |

> **Thay thế**: Nếu nhóm quen PHP hơn, có thể dùng PHP thuần hoặc Laravel thay Flask. Nếu quen Node.js, dùng Express.js + MySQL.

---

## 9. Tiêu Chí Nghiệm Thu

Theo yêu cầu của giáo viên, sản phẩm cần đạt:

- [ ] Giao diện front-end hoàn chỉnh (HTML, CSS, JavaScript)
- [ ] Kết nối và truy vấn được cơ sở dữ liệu
- [ ] Có ít nhất 1 ngôn ngữ xử lý nghiệp vụ phía back-end
- [ ] Front-end lấy dữ liệu động từ back-end (không hardcode)
- [ ] Bảng giá tháng được khóa đúng quy tắc (không sửa tháng đã có hóa đơn)
- [ ] Hóa đơn tính tự động, chính xác theo Bảng giá và Thanh toán hàng tháng
- [ ] Báo cáo mô tả đầy đủ: sơ đồ DB, mô tả nghiệp vụ, quan hệ bảng
- [ ] Demo được các chức năng khi vấn đáp

---

*Tài liệu này được tạo để làm cơ sở phân tích, thiết kế và phân công trong nhóm trước khi bắt đầu lập trình.*
