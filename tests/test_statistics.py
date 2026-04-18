from datetime import date, timedelta


def create_demo_data(client, month, year):
    room = client.post(
        "/api/phong",
        json={
            "so_phong": "S101",
            "tang": 1,
            "dien_tich": 20,
            "cap_phong": "cap1",
            "trang_thai": "trong",
        },
    ).get_json()["data"]

    tenant = client.post(
        "/api/khach-thue",
        json={
            "ho_ten": "Khach Thong Ke",
            "cccd": "771234567890",
            "ngay_sinh": "2001-01-01",
            "sdt": "0900000009",
            "la_chinh": True,
        },
    ).get_json()["data"]

    contract = client.post(
        "/api/hop-dong",
        json={
            "phong_id": room["phong_id"],
            "khach_id": tenant["khach_id"],
            "ngay_bat_dau": date.today().isoformat(),
            "ngay_ket_thuc": (date.today() + timedelta(days=20)).isoformat(),
        },
    ).get_json()["data"]

    assert client.post(
        "/api/bang-gia",
        json={
            "thang": month,
            "nam": year,
            "gia_phong_cap1": 2500000,
            "gia_phong_cap2": 3500000,
            "don_gia_dien": 3500,
            "don_gia_nuoc": 15000,
            "phi_wifi": 100000,
            "phi_ve_sinh": 50000,
            "phi_gui_xe": 50000,
        },
    ).status_code == 201

    assert client.post("/api/thanh-toan/tao-thang", json={"thang": month, "nam": year}).status_code == 201
    payment = next(
        item
        for item in client.get(f"/api/thanh-toan/{month}/{year}").get_json()["data"]
        if item["hopdong_id"] == contract["hopdong_id"]
    )
    assert client.put(
        f"/api/thanh-toan/{payment['tt_id']}",
        json={"so_dien": 30, "so_nuoc": 2, "trang_thai": "chua_tt"},
    ).status_code == 200
    assert client.post(f"/api/hoa-don/{payment['tt_id']}/generate").status_code == 201


def test_statistics_endpoints_return_sane_data(client, current_period):
    month, year = current_period
    create_demo_data(client, month, year)

    dashboard = client.get("/api/thong-ke/dashboard")
    assert dashboard.status_code == 200
    dashboard_data = dashboard.get_json()["data"]
    for key in ["tong_phong", "phong_dang_thue", "phong_trong", "doanh_thu_thang_nay", "chua_dong_tien", "sap_het_han"]:
        assert key in dashboard_data

    revenue = client.get("/api/thong-ke/doanh-thu?months=6")
    assert revenue.status_code == 200
    revenue_rows = revenue.get_json()["data"]
    assert len(revenue_rows) == 6
    assert all(row["doanh_thu"] >= 0 for row in revenue_rows)

    unpaid = client.get(f"/api/thong-ke/chua-dong/{month}/{year}")
    assert unpaid.status_code == 200
    unpaid_rows = unpaid.get_json()["data"]
    assert isinstance(unpaid_rows, list)
    assert unpaid_rows
    assert {"tt_id", "so_phong", "ho_ten", "thang", "nam"}.issubset(unpaid_rows[0].keys())
