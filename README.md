# He Thong Quan Ly Day Tro Binh Dan

Ung dung web Flask quan ly day tro quy mo nho, phuc vu demo va handoff cho bai toan quan ly phong, khach thue, hop dong, thanh toan thang, hoa don va thong ke doanh thu.

## Trang thai hien tai

Phase 0, Phase 1 va Phase 3 da hoan tat theo `PLAN.md`.

Phase 2 da hoan thanh phan lon giao dien va da duoc verify o muc demo thuc te. Ba muc checklist frontend van de `[ ]` la:

- `phong/form.html`
- `hoa_don/detail.html`
- `pdf/hoa_don_pdf.html`

Ly do cu the duoc ghi trong [HANDOFF_NOTES.md](/c:/Users/Admin/Desktop/DuAnQuanLyTro/HANDOFF_NOTES.md:1). README nay khong over-claim ba muc do la da dong.

## Stack cong nghe

- Backend: Python 3.10+ / Flask 3
- ORM: Flask-SQLAlchemy / SQLAlchemy 2
- Migration: Flask-Migrate
- Database: SQLite mac dinh, co the doi qua `DATABASE_URL`
- Frontend: Jinja2 templates + Bootstrap 5 + Vanilla JS
- PDF: WeasyPrint, co fallback PDF toi thieu neu render HTML -> PDF khong kha dung
- Test: pytest

## Cau truc thu muc chinh

```text
app/
  __init__.py          App factory
  models.py            SQLAlchemy models
  api/                 REST API blueprints
  services/            Business logic (invoice, warning, pdf)
  templates/           Jinja templates cho cac man hinh
static/
  css/style.css        CSS giao dien
  js/                  JS cho dashboard, phong, thanh_toan, thong_ke
tests/                 Pytest suite
seed.py                Tao du lieu demo
run.py                 Entry point chay Flask app
PLAN.md                Checklist va mo ta du an
HANDOFF_NOTES.md       Ghi chu handoff/demo cuoi
```

## Cai dat moi truong

### 1. Tao virtualenv

```powershell
python -m venv venv
```

### 2. Kich hoat virtualenv

```powershell
.\venv\Scripts\Activate.ps1
```

Neu PowerShell chan script, co the dung:

```powershell
.\venv\Scripts\python.exe --version
```

va goi truc tiep Python trong `venv` cho cac lenh ben duoi.

### 3. Cai dependencies

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Cau hinh va database

Mac dinh app dung SQLite file `nha_tro.db` tai root repo.

Co the override bang bien moi truong:

```powershell
$env:DATABASE_URL = "sqlite:///custom.db"
```

Neu muon khoi tao schema rong qua Flask-Migrate:

```powershell
.\venv\Scripts\python.exe -m flask db upgrade
```

Trong demo thong thuong, chi can chay seed la du vi `seed.py` se `drop_all()` + `create_all()` truoc khi nap du lieu mau.

## Seed du lieu demo

```powershell
.\venv\Scripts\python.exe seed.py
```

Script seed hien tao:

- 5 phong
- 3 khach thue
- 2 hop dong
- 1 bang gia thang hien tai
- 2 ban ghi thanh toan thang
- 1 hoa don mau

Seed se reset lai DB hien tai, vi vay khong nen chay tren du lieu can giu.

## Chay app

Co hai cach don gian:

```powershell
.\venv\Scripts\python.exe run.py
```

Hoac:

```powershell
$env:FLASK_APP = "run.py"
.\venv\Scripts\python.exe -m flask run
```

App mac dinh chay tai `http://127.0.0.1:5000`.

## Chay test

```powershell
.\venv\Scripts\python.exe -m pytest -q
```

Trang thai suite tai luc handoff: `28 passed`.

## Cac URL chinh

Page routes:

- `/` hoac `/dashboard`
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

Neu muon demo nhanh bang du lieu seed:

1. Chay `seed.py`
2. Mo `/dashboard` de xem KPI, canh bao va doanh thu
3. Mo `/phong` de xem tinh trang tung phong
4. Mo `/hop-dong` de xem hop dong hieu luc / sap het han
5. Mo `/thanh-toan` de xem du lieu thanh toan thang hien tai
6. Mo `/hoa-don` de xem hoa don da co san va thu xuat PDF

Neu muon demo luong nghiep vu tay trong 5 phut:

1. Vao `/phong` va tao phong moi
2. Vao `/khach-thue` va tao khach moi
3. Vao `/hop-dong` va tao hop dong cho phong vua tao
4. Vao `/bang-gia` dam bao thang hien tai co bang gia
5. Vao `/thanh-toan`, bam `Tao thang moi`, nhap so dien/nuoc va danh dau da thanh toan neu can
6. Vao `/hoa-don`, bam `Tinh tat ca hoa don` hoac generate theo flow da co
7. Quay lai `/dashboard` de xac nhan KPI va doanh thu cap nhat

## Luu y ve PDF / WeasyPrint

App uu tien render hoa don PDF bang template HTML `app/templates/pdf/hoa_don_pdf.html` thong qua WeasyPrint.

Trong mot so may Windows, WeasyPrint co the can them native libraries hoac environment phu tro. Neu WeasyPrint khong khoi tao duoc, `pdf_service.py` se fallback sang mot PDF toi thieu sinh truc tiep bang bytes de:

- endpoint PDF van tra `application/pdf`
- luong demo khong bi block
- nguoi nhan van co mot file PDF co noi dung co ban

Neu muon su dung HTML PDF day du, hay kiem tra cai dat WeasyPrint va cac thu vien native lien quan tren may demo.

## Tai lieu handoff them

- [PLAN.md](/c:/Users/Admin/Desktop/DuAnQuanLyTro/PLAN.md:1): source of truth ve checklist va pham vi du an
- [HANDOFF_NOTES.md](/c:/Users/Admin/Desktop/DuAnQuanLyTro/HANDOFF_NOTES.md:1): tom tat tinh trang handoff/demo cuoi, cac muc con treo va known limitations
