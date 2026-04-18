# Handoff Notes

## Tổng quan

Repo hiện ở mức demo-ready cho bài toán quản lý dãy trọ nhỏ. Luồng nghiệp vụ chính đã chạy được, suite test xanh, và browser/manual verification cho Phase 3 đã hoàn tất.

## Trạng thái checklist

### Phase 0

- Hoàn tất

### Phase 1

- Hoàn tất
- Các module API chính đã có: phòng, khách-thuê, hợp-đồng, bảng-giá, thanh-toán, hóa-đơn, thống-kê

### Phase 2

- Đã hoàn thành phần lớn giao diện dùng cho demo thực tế
- Các màn chính đã có và đã được verify: dashboard, phòng, khách-thuê, hợp-đồng, bảng-giá, thanh-toán, hóa-đơn, thống-kê
- Còn 3 mục checklist để `[ ]` trong `PLAN.md`, không tick bổ sung trong handoff này:

`phong/form.html`
File này chưa tồn tại vì màn Phòng đang dùng modal CRUD ngay trong `phong/index.html`, không dùng page form riêng.

`hoa_don/detail.html`
File này chưa tồn tại vì chi tiết hóa đơn hiện đang hiển thị qua modal trong `hoa_don/index.html`, không dùng trang detail riêng.

`pdf/hoa_don_pdf.html`
Template này thực tế đã có trong repo và đang được `pdf_service.py` gọi khi WeasyPrint khả dụng. Tuy nhiên checklist frontend ban đầu vẫn để mở vì artifact này chưa được đóng như một deliverable giao diện riêng trong giai đoạn Front-end, và runtime vẫn có thể rơi vào fallback PDF tối thiểu nếu máy demo thiếu native libs của WeasyPrint. Để tránh over-claim, mục này vẫn giữ `[ ]`.

### Phase 3

- Hoàn tất
- Đã có test models, API phòng, invoice service
- Đã verify happy path thủ công / browser
- Đã verify lock bảng giá `423`
- Đã verify responsive ở mobile, tablet, desktop

### Phase 4

- Mới chỉ hoàn thành phần README/handoff tài liệu
- Các mục còn lại như deploy, slide demo, seed demo dày hơn vẫn chưa đóng

## Cách demo nhanh trong 5 phút

### Cách 1: Demo bằng dữ liệu seed sẵn

1. Chạy `.\venv\Scripts\python.exe seed.py`
2. Chạy app bằng `.\venv\Scripts\python.exe run.py`
3. Mở `/dashboard` để giới thiệu KPI và doanh thu tháng
4. Mở `/phong` để xem phòng đang thuê, phòng trống, phòng sửa chữa
5. Mở `/hop-dong` để chỉ ra hợp đồng hiệu lực và hợp đồng sắp hết hạn
6. Mở `/thanh-toan` để xem bản ghi thanh toán tháng hiện tại
7. Mở `/hoa-don` để xem hóa đơn có sẵn và thử xuất PDF

### Cách 2: Demo luồng nghiệp vụ từ đầu

1. Tạo phòng mới tại `/phong`
2. Tạo khách mới tại `/khach-thue`
3. Tạo hợp đồng tại `/hop-dong`
4. Tạo hoặc kiểm tra bảng giá tháng hiện tại tại `/bang-gia`
5. Vào `/thanh-toan`, bấm `Tạo tháng mới`, nhập điện/nước và toggle trạng thái thanh toán
6. Vào `/hoa-don`, tính hóa đơn và mở chi tiết/PDF
7. Quay lại `/dashboard` để xem KPI và doanh thu thay đổi

## Dữ liệu mẫu

Seed hiện tại tạo sẵn:

- Phòng `101`, `102`, `103`, `104`, `201`
- Khách: `Nguyễn Văn An`, `Trần Thị Bình`, `Lê Văn Cường`
- 2 hợp đồng demo, trong đó có 1 hợp đồng sắp hết hạn
- Bảng giá tháng hiện tại đã khóa
- 2 bản ghi thanh toán, 1 đã thanh toán và 1 chưa thanh toán
- 1 hóa đơn mẫu

## Known limitations nhỏ

- `seed.py` reset lại database hiện tại bằng `drop_all()` + `create_all()`
- Mobile view của bảng `thanh-toan` và `hoa-don` vẫn dựa vào scroll ngang để xem đủ cột
- PDF HTML đẹp phụ thuộc WeasyPrint và native libs trên máy chạy; nếu thiếu, app sẽ trả fallback PDF tối thiểu
- Chưa có page riêng cho form Phòng và detail Hóa đơn vì UI hiện tại ưu tiên modal để phục vụ demo nhanh

## Lệnh hữu ích cho handoff

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe seed.py
.\venv\Scripts\python.exe run.py
.\venv\Scripts\python.exe -m pytest -q
```
