from datetime import date, timedelta


def test_monthly_payment_and_invoice_flow(client, current_period):
    month, year = current_period

    room_res = client.post(
        "/api/phong",
        json={
            "so_phong": "T301",
            "tang": 3,
            "dien_tich": 19,
            "cap_phong": "cap1",
            "trang_thai": "trong",
        },
    )
    room_id = room_res.get_json()["data"]["phong_id"]

    tenant_res = client.post(
        "/api/khach-thue",
        json={
            "ho_ten": "Khach Thanh Toan",
            "cccd": "888888888888",
            "ngay_sinh": "2001-02-02",
            "sdt": "0911111111",
            "la_chinh": True,
        },
    )
    tenant_id = tenant_res.get_json()["data"]["khach_id"]

    start = date.today()
    end = start + timedelta(days=45)
    contract_res = client.post(
        "/api/hop-dong",
        json={
            "phong_id": room_id,
            "khach_id": tenant_id,
            "ngay_bat_dau": start.isoformat(),
            "ngay_ket_thuc": end.isoformat(),
        },
    )
    contract_id = contract_res.get_json()["data"]["hopdong_id"]

    price_res = client.post(
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
    )
    assert price_res.status_code == 201
    bangia_id = price_res.get_json()["data"]["bangia_id"]

    create_month = client.post("/api/thanh-toan/tao-thang", json={"thang": month, "nam": year})
    assert create_month.status_code == 201

    payments = client.get(f"/api/thanh-toan/{month}/{year}")
    assert payments.status_code == 200
    payment = next(item for item in payments.get_json()["data"] if item["hopdong_id"] == contract_id)

    updated = client.put(
        f"/api/thanh-toan/{payment['tt_id']}",
        json={"so_dien": 40, "so_nuoc": 2, "trang_thai": "chua_tt"},
    )
    assert updated.status_code == 200
    assert updated.get_json()["data"]["so_dien"] == 40

    generated = client.post(f"/api/hoa-don/{payment['tt_id']}/generate")
    assert generated.status_code == 201
    invoice = generated.get_json()["data"]
    assert invoice["tong_tien"] > 0

    invoice_detail = client.get(f"/api/hoa-don/{invoice['hoadon_id']}")
    assert invoice_detail.status_code == 200
    assert invoice_detail.get_json()["data"]["tt_id"] == payment["tt_id"]

    locked_update = client.put(f"/api/bang-gia/{bangia_id}", json={"gia_phong_cap1": 2600000})
    assert locked_update.status_code == 423
