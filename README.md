# Hệ Thống Quản Lý Dãy Trọ Bình Dân

Ứng dụng web Flask quản lý dãy trọ quy mô nhỏ, phục vụ demo và handoff cho bài toán quản lý phòng, khách thuê, hợp đồng, thanh toán tháng, hóa đơn và thống kê doanh thu.

## Trạng thái hiện tại

Phase 0, Phase 1 và Phase 3 đã hoàn tất theo `PLAN.md`.

Phase 2 đã hoàn thành phần lớn giao diện và đã được verify ở mức demo thực tế. Ba mục checklist frontend vẫn để `[ ]` là:

- `phong/form.html`
- `hoa_don/detail.html`
- `pdf/hoa_don_pdf.html`

Lý do cụ thể được ghi trong [HANDOFF_NOTES.md](/main/HANDOFF_NOTES.md). README này không over-claim ba mục đó là đã đóng.

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

Script seed hiện tạo:

- 5 phòng
- 3 khách thuê
- 2 hợp đồng
- 1 bảng giá tháng hiện tại
- 2 bản ghi thanh toán tháng
- 1 hóa đơn mẫu

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

Trạng thái suite tại lúc handoff: `28 passed`.

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
4. Mở `/hop-dong` để xem hợp đồng hiệu lực / sắp hết hạn
5. Mở `/thanh-toan` để xem dữ liệu thanh toán tháng hiện tại
6. Mở `/hoa-don` để xem hóa đơn đã có sẵn và thử xuất PDF

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
