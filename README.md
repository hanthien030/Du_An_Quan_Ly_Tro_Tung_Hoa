# Hệ Thống Quản Lý Dãy Trọ Bình Dân

Ứng dụng web Flask quản lý dãy trọ quy mô nhỏ, phục vụ demo và handoff cho bài toán quản lý phòng, khách thuê, hợp đồng, thanh toán tháng, hóa đơn và thống kê doanh thu.

## Trạng thái hiện tại

Phase 0, Phase 1 và Phase 3 đã hoàn tất theo `PLAN.md`.

Phase 4 đã hoàn tất mục seed demo: bộ dữ liệu mẫu hiện có `12 phòng` và `3 tháng dữ liệu` để phục vụ dashboard, thanh toán, hóa đơn và thống kê.

Phase 2 hiện chỉ còn giữ `[ ]` cho `pdf/hoa_don_pdf.html` theo strict mode, vì runtime dev vẫn đang dùng fallback PDF khi WeasyPrint thiếu native library để render HTML -> PDF đầy đủ.

Chi tiết handoff và known limitations được ghi trong [HANDOFF_NOTES.md](</c:/Users/Admin/Desktop/DuAnQuanLyTro/HANDOFF_NOTES.md:1>).

## Stack công nghệ

- Backend: Python 3.10+ / Flask 3
- ORM: Flask-SQLAlchemy / SQLAlchemy 2
- Migration: Flask-Migrate
- Database: SQLite mặc định, có thể đổi qua `DATABASE_URL`
- Frontend: Jinja2 templates + Bootstrap 5 + Vanilla JS
- PDF: WeasyPrint, có fallback PDF tối thiểu nếu render HTML -> PDF không khả dụng
- Test: pytest

## Cấu trúc thư mục chính

```text
app/
  __init__.py          App factory
  models.py            SQLAlchemy models
  api/                 REST API blueprints
  services/            Business logic (invoice, warning, pdf)
  templates/           Jinja templates cho các màn hình
static/
  css/style.css        CSS giao diện
  js/                  JS cho dashboard, phòng, thanh_toan, thong_ke
tests/                 Pytest suite
seed.py                Tạo dữ liệu demo
run.py                 Entry point chạy Flask app
PLAN.md                Checklist và mô tả dự án
HANDOFF_NOTES.md       Ghi chú handoff/demo cuối
nha_tro.dbml           DBML để dán vào dbdiagram.io
schema.sql             SQL schema tham chiếu theo cấu trúc hiện tại
Cấu Trúc Thư Mục.md    Mô tả cây thư mục repo
```

## Cài đặt môi trường

### 1. Tạo virtualenv

```powershell
python -m venv venv
```

### 2. Kích hoạt virtualenv

```powershell
.\venv\Scripts\Activate.ps1
```

Nếu PowerShell chặn script, có thể dùng:

```powershell
.\venv\Scripts\python.exe --version
```

và gọi trực tiếp Python trong `venv` cho các lệnh bên dưới.

### 3. Cài dependencies

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Cấu hình và database

Mặc định app dùng SQLite file `nha_tro.db` tại root repo.

Có thể override bằng biến môi trường:

```powershell
$env:DATABASE_URL = "sqlite:///custom.db"
```

Nếu muốn khởi tạo schema rỗng qua Flask-Migrate:

```powershell
.\venv\Scripts\python.exe -m flask db upgrade
```

Trong demo thông thường, chỉ cần chạy seed là đủ vì `seed.py` sẽ `drop_all()` + `create_all()` trước khi nạp dữ liệu mẫu.

## Seed dữ liệu demo

```powershell
.\venv\Scripts\python.exe seed.py
```

Script seed hiện tạo bộ demo có chủ đích:

- 12 phòng trên 3 tầng
- 9 khách thuê
- 9 hợp đồng với đủ trạng thái `hieu_luc`, `sap_het_han`, `het_han`
- 3 bảng giá liên tiếp: tháng hiện tại, tháng trước, và 2 tháng trước
- 22 bản ghi thanh toán tháng
- 22 hóa đơn

Bộ seed được thiết kế để khi mở app có thể demo được ngay:

- dashboard có KPI, doanh thu tháng hiện tại, phòng chưa đóng tiền và hợp đồng sắp hết hạn
- màn phòng có đủ `trong`, `dang_thue`, `sua_chua`
- màn hợp đồng có đủ active / sắp hết hạn / hết hạn
- màn thanh toán có cả `da_tt` và `chua_tt`
- màn hóa đơn và thống kê có dữ liệu trải trên nhiều tháng

Seed sẽ reset lại DB hiện tại, vì vậy không nên chạy trên dữ liệu cần giữ.

## Chạy app

Có hai cách đơn giản:

```powershell
.\venv\Scripts\python.exe run.py
```

Hoặc:

```powershell
$env:FLASK_APP = "run.py"
.\venv\Scripts\python.exe -m flask run
```

App mặc định chạy tại `http://127.0.0.1:5000`.

## Chạy test

```powershell
.\venv\Scripts\python.exe -m pytest -q
```

Kết quả cụ thể phụ thuộc trạng thái codebase tại thời điểm chạy; dùng lệnh trên để verify lại nhanh trên máy hiện tại.

## Các URL chính

Page routes:

- `/` hoặc `/dashboard`
- `/phong`
- `/khach-thue`
- `/hop-dong`
- `/bang-gia`
- `/thanh-toan`
- `/hoa-don`
- `/thong-ke`

API routes:

- `/api/phong`
- `/api/khach-thue`
- `/api/hop-dong`
- `/api/bang-gia`
- `/api/thanh-toan`
- `/api/hoa-don`
- `/api/thong-ke`
- `/health`

## Core flow demo

Nếu muốn demo nhanh bằng dữ liệu seed:

1. Chạy `seed.py`
2. Mở `/dashboard` để xem KPI, cảnh báo và doanh thu
3. Mở `/phong` để xem tình trạng từng phòng
4. Mở `/khach-thue` để xem danh sách khách thuê demo
5. Mở `/hop-dong` để xem hợp đồng hiệu lực / sắp hết hạn
6. Mở `/bang-gia` để xem 3 tháng bảng giá đã seed
7. Mở `/thanh-toan` để xem dữ liệu thanh toán tháng hiện tại
8. Mở `/hoa-don` để xem hóa đơn đã có sẵn và thử xuất PDF
9. Mở `/thong-ke` để xem doanh thu 3 tháng đã có số liệu

Nếu muốn demo luồng nghiệp vụ tay trong 5 phút:

1. Vào `/phong` và tạo phòng mới
2. Vào `/khach-thue` và tạo khách mới
3. Vào `/hop-dong` và tạo hợp đồng cho phòng vừa tạo
4. Vào `/bang-gia` đảm bảo tháng hiện tại có bảng giá
5. Vào `/thanh-toan`, bấm `Tạo tháng mới`, nhập số điện/nước và đánh dấu đã thanh toán nếu cần
6. Vào `/hoa-don`, bấm `Tính tất cả hóa đơn` hoặc generate theo flow đã có
7. Quay lại `/dashboard` để xác nhận KPI và doanh thu cập nhật

## Lưu ý về PDF / WeasyPrint

App ưu tiên render hóa đơn PDF bằng template HTML `app/templates/pdf/hoa_don_pdf.html` thông qua WeasyPrint.

Trong một số máy Windows, WeasyPrint có thể cần thêm native libraries hoặc environment phụ trợ. Nếu WeasyPrint không khởi tạo được, `pdf_service.py` sẽ fallback sang một PDF tối thiểu sinh trực tiếp bằng bytes để:

- endpoint PDF vẫn trả `application/pdf`
- luồng demo không bị block
- người nhận vẫn có một file PDF có nội dung cơ bản

Nếu muốn sử dụng HTML PDF đầy đủ, hãy kiểm tra cài đặt WeasyPrint và các thư viện native liên quan trên máy demo.

## Tài liệu handoff thêm

- [PLAN.md](/c:/Users/Admin/Desktop/DuAnQuanLyTro/PLAN.md:1): source of truth về checklist và phạm vi dự án
- [HANDOFF_NOTES.md](/c:/Users/Admin/Desktop/DuAnQuanLyTro/HANDOFF_NOTES.md:1): tóm tắt tình trạng handoff/demo cuối, các mục còn treo và known limitations
- [nha_tro.dbml](</c:/Users/Admin/Desktop/DuAnQuanLyTro/nha_tro.dbml:1>): sơ đồ DBML để dán vào dbdiagram.io
- [schema.sql](</c:/Users/Admin/Desktop/DuAnQuanLyTro/schema.sql:1>): SQL schema tham chiếu từ cấu trúc hiện tại
- [Cấu Trúc Thư Mục.md](</c:/Users/Admin/Desktop/DuAnQuanLyTro/Cấu Trúc Thư Mục.md:1>): cây thư mục repo ở mức handoff
