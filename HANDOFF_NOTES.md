# Handoff Notes

## Tong quan

Repo hien o muc demo-ready cho bai toan quan ly day tro nho. Luong nghiep vu chinh da chay duoc, suite test xanh, va browser/manual verification cho Phase 3 da hoan tat.

## Trang thai checklist

### Phase 0

- Hoan tat

### Phase 1

- Hoan tat
- Cac module API chinh da co: phong, khach-thue, hop-dong, bang-gia, thanh-toan, hoa-don, thong-ke

### Phase 2

- Da hoan thanh phan lon giao dien dung cho demo thuc te
- Cac man chinh da co va da duoc verify: dashboard, phong, khach-thue, hop-dong, bang-gia, thanh-toan, hoa-don, thong-ke
- Con 3 muc checklist de `[ ]` trong `PLAN.md`, khong tick bo sung trong handoff nay:

`phong/form.html`
File nay chua ton tai vi man Phong dang dung modal CRUD ngay trong `phong/index.html`, khong dung page form rieng.

`hoa_don/detail.html`
File nay chua ton tai vi chi tiet hoa don hien dang hien thi qua modal trong `hoa_don/index.html`, khong dung trang detail rieng.

`pdf/hoa_don_pdf.html`
Template nay thuc te da co trong repo va dang duoc `pdf_service.py` goi khi WeasyPrint kha dung. Tuy nhien checklist frontend ban dau van de mo vi artifact nay chua duoc dong nhu mot deliverable giao dien rieng trong giai doan Front-end, va runtime van co the roi vao fallback PDF toi thieu neu may demo thieu native libs cua WeasyPrint. De tranh over-claim, muc nay van giu `[ ]`.

### Phase 3

- Hoan tat
- Da co test models, API phong, invoice service
- Da verify happy path thu cong / browser
- Da verify lock bang gia `423`
- Da verify responsive o mobile, tablet, desktop

### Phase 4

- Moi chi hoan thanh phan README/handoff tai lieu
- Cac muc con lai nhu deploy, slide demo, seed demo day hon van chua dong

## Cach demo nhanh trong 5 phut

### Cach 1: Demo bang du lieu seed san

1. Chay `.\venv\Scripts\python.exe seed.py`
2. Chay app bang `.\venv\Scripts\python.exe run.py`
3. Mo `/dashboard` de gioi thieu KPI va doanh thu thang
4. Mo `/phong` de xem phong dang thue, phong trong, phong sua chua
5. Mo `/hop-dong` de chi ra hop dong hieu luc va hop dong sap het han
6. Mo `/thanh-toan` de xem ban ghi thanh toan thang hien tai
7. Mo `/hoa-don` de xem hoa don co san va thu xuat PDF

### Cach 2: Demo luong nghiep vu tu dau

1. Tao phong moi tai `/phong`
2. Tao khach moi tai `/khach-thue`
3. Tao hop dong tai `/hop-dong`
4. Tao hoac kiem tra bang gia thang hien tai tai `/bang-gia`
5. Vao `/thanh-toan`, bam `Tao thang moi`, nhap dien/nuoc va toggle trang thai thanh toan
6. Vao `/hoa-don`, tinh hoa don va mo chi tiet/PDF
7. Quay lai `/dashboard` de xem KPI va doanh thu thay doi

## Du lieu mau

Seed hien tai tao san:

- Phong `101`, `102`, `103`, `104`, `201`
- Khach: `Nguyen Van An`, `Tran Thi Binh`, `Le Van Cuong`
- 2 hop dong demo, trong do co 1 hop dong sap het han
- Bang gia thang hien tai da khoa
- 2 ban ghi thanh toan, 1 da thanh toan va 1 chua thanh toan
- 1 hoa don mau

## Known limitations nho

- `seed.py` reset lai database hien tai bang `drop_all()` + `create_all()`
- Mobile view cua bang `thanh-toan` va `hoa-don` van dua vao scroll ngang de xem du cot
- PDF HTML dep phu thuoc WeasyPrint va native libs tren may chay; neu thieu, app se tra fallback PDF toi thieu
- Chua co page rieng cho form Phong va detail Hoa don vi UI hien tai uu tien modal de phuc vu demo nhanh

## Lenh huu ich cho handoff

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe seed.py
.\venv\Scripts\python.exe run.py
.\venv\Scripts\python.exe -m pytest -q
```
