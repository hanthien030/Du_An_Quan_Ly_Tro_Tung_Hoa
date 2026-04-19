# Cấu Trúc Thư Mục Repo

Tài liệu này mô tả cấu trúc thư mục hiện tại của repo `DuAnQuanLyTro`, dựa trên trạng thái filesystem đang có.

Lưu ý:
- Có liệt kê cả các thư mục phát sinh như `venv`, `__pycache__`, `tests/.runtime`, `pytest-cache-files-*`.
- Không bung chi tiết toàn bộ bên trong các thư mục cache/runtime rất lớn vì đó là file sinh tự động, không phải mã nguồn chính.

## Cây thư mục tổng quan

```text
DuAnQuanLyTro/
|-- app/
|   |-- __init__.py
|   |-- extensions.py
|   |-- models.py
|   |-- utils.py
|   |-- web.py
|   |-- api/
|   |   |-- __init__.py
|   |   |-- bang_gia.py
|   |   |-- hoa_don.py
|   |   |-- hop_dong.py
|   |   |-- khach_thue.py
|   |   |-- phong.py
|   |   |-- thanh_toan.py
|   |   `-- thong_ke.py
|   |-- services/
|   |   |-- __init__.py
|   |   |-- invoice_service.py
|   |   |-- pdf_service.py
|   |   `-- warning_service.py
|   `-- templates/
|       |-- base.html
|       |-- dashboard.html
|       |-- bang_gia/
|       |   `-- index.html
|       |-- hoa_don/
|       |   |-- detail.html
|       |   `-- index.html
|       |-- hop_dong/
|       |   `-- index.html
|       |-- khach_thue/
|       |   `-- index.html
|       |-- pdf/
|       |   `-- hoa_don_pdf.html
|       |-- phong/
|       |   |-- form.html
|       |   `-- index.html
|       |-- thanh_toan/
|       |   `-- index.html
|       `-- thong_ke/
|           `-- index.html
|-- migrations/
|   |-- README
|   |-- alembic.ini
|   |-- env.py
|   |-- script.py.mako
|   `-- versions/
|       `-- f8f98cfc925e_init_models.py
|-- static/
|   |-- css/
|   |   `-- style.css
|   |-- img/
|   |   `-- (chưa thấy file đáng chú ý trong lần quét hiện tại)
|   |-- js/
|   |   |-- dashboard.js
|   |   |-- main.js
|   |   |-- phong.js
|   |   |-- thanh_toan.js
|   |   `-- thong_ke.js
|   `-- runtime/
|       `-- (thư mục runtime/phát sinh khi chạy)
|-- tests/
|   |-- conftest.py
|   |-- test_api_phong.py
|   |-- test_bang_gia_copy.py
|   |-- test_contract_flow.py
|   |-- test_invoice_edges.py
|   |-- test_invoice_service.py
|   |-- test_models.py
|   |-- test_payment_invoice_flow.py
|   |-- test_smoke.py
|   |-- test_statistics.py
|   |-- .runtime/
|   |   `-- nhiều file/thư mục runtime sinh ra khi verify UI/browser và test
|   |-- pytest-cache-files-0gxr340r/
|   |-- pytest-cache-files-f3fuy8ef/
|   `-- __pycache__/
|-- venv/
|   `-- môi trường ảo Python của dự án
|-- __pycache__/
|   `-- cache Python ở root
|-- pytest-cache-files-78k2o0z3/
|-- pytest-cache-files-af1l8d6o/
|-- pytest-cache-files-gidz2uzh/
|-- pytest-cache-files-pq5r26mo/
|-- pytest-cache-files-w5vuhjtn/
|-- pytest-cache-files-whg5z4ui/
|-- .gitignore
|-- config.py
|-- HANDOFF_NOTES.md
|-- mo-ta-y-tuong-quan-ly-nha-tro_FINAL_.md
|-- nhatrobinhdan.png
|-- nha_tro.db
|-- nha_tro.dbml
|-- PLAN.md
|-- pytest.ini
|-- README.md
|-- requirements.txt
|-- run.bat
|-- run.py
|-- schema.sql
|-- seed.py
`-- setup.bat
```

## Vai trò các khu vực chính

- `app/`: mã nguồn chính của ứng dụng Flask.
- `app/api/`: các API/blueprint theo từng nghiệp vụ như phòng, khách thuê, hợp đồng, thanh toán, hóa đơn, thống kê, bảng giá.
- `app/services/`: business logic tách riêng khỏi route/controller.
- `app/templates/`: giao diện Jinja2 theo từng màn hình.
- `migrations/`: cấu hình Flask-Migrate/Alembic và migration tạo schema.
- `static/`: tài nguyên tĩnh như CSS, JavaScript, ảnh và file runtime.
- `tests/`: bộ test pytest, kèm thư mục `.runtime` dùng cho verify/browser runtime.
- `venv/`: môi trường Python cục bộ của máy hiện tại.

## Nhóm file ở root

- `config.py`: cấu hình ứng dụng, bao gồm chuỗi kết nối database.
- `run.py`, `run.bat`, `setup.bat`: script chạy/cài nhanh.
- `seed.py`: reset và nạp dữ liệu mẫu.
- `nha_tro.db`: file SQLite hiện tại của dự án.
- `nha_tro.dbml`: sơ đồ DBML để dán vào dbdiagram.io.
- `schema.sql`: schema SQL đã tạo từ cấu trúc hiện tại.
- `README.md`, `PLAN.md`, `HANDOFF_NOTES.md`: tài liệu hướng dẫn, kế hoạch và handoff.
- `requirements.txt`: dependency Python.
- `pytest.ini`: cấu hình pytest.
- `mo-ta-y-tuong-quan-ly-nha-tro_FINAL_.md`: tài liệu mô tả ý tưởng/bài toán.
- `nhatrobinhdan.png`: ảnh minh họa/tài nguyên đi kèm ở root.

## Ghi chú thêm

- Repo hiện chứa cả mã nguồn và artifact sinh ra trong quá trình test/demo.
- Nếu muốn một bản cấu trúc "sạch để bàn giao", có thể tạo thêm một tài liệu thứ hai chỉ giữ phần source code, bỏ `venv`, cache và runtime.
