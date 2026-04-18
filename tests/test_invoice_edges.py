from datetime import date, timedelta


def create_contract_bundle(client, so_phong="I101", cccd="881111111111"):
    room = client.post(
        "/api/phong",
        json={
            "so_phong": so_phong,
            "tang": 1,
            "dien_tich": 18,
            "cap_phong": "cap1",
            "trang_thai": "trong",
        },
    ).get_json()["data"]

    tenant = client.post(
        "/api/khach-thue",
        json={
            "ho_ten": f"Khach {so_phong}",
            "cccd": cccd,
            "ngay_sinh": "2000-01-01",
            "sdt": "0901234567",
            "la_chinh": True,
        },
    ).get_json()["data"]

    start = date.today()
    end = start + timedelta(days=45)
    contract = client.post(
        "/api/hop-dong",
        json={
            "phong_id": room["phong_id"],
            "khach_id": tenant["khach_id"],
            "ngay_bat_dau": start.isoformat(),
            "ngay_ket_thuc": end.isoformat(),
        },
    ).get_json()["data"]
    return room, tenant, contract


def create_bang_gia(client, thang, nam):
    return client.post(
        "/api/bang-gia",
        json={
            "thang": thang,
            "nam": nam,
            "gia_phong_cap1": 2500000,
            "gia_phong_cap2": 3500000,
            "don_gia_dien": 3500,
            "don_gia_nuoc": 15000,
            "phi_wifi": 100000,
            "phi_ve_sinh": 50000,
            "phi_gui_xe": 50000,
        },
    )


def create_payment_for_contract(client, contract_id, month, year):
    response = client.post("/api/thanh-toan/tao-thang", json={"thang": month, "nam": year})
    assert response.status_code == 201

    payments = client.get(f"/api/thanh-toan/{month}/{year}").get_json()["data"]
    payment = next(item for item in payments if item["hopdong_id"] == contract_id)
    updated = client.put(
        f"/api/thanh-toan/{payment['tt_id']}",
        json={"so_dien": 40, "so_nuoc": 2, "trang_thai": "chua_tt"},
    )
    assert updated.status_code == 200
    return payment["tt_id"]


def test_generate_invoice_requires_bang_gia(client, current_period):
    month, year = current_period
    _, _, contract = create_contract_bundle(client, so_phong="I201", cccd="881111111112")
    tt_id = create_payment_for_contract(client, contract["hopdong_id"], month, year)

    response = client.post(f"/api/hoa-don/{tt_id}/generate")
    assert response.status_code == 400
    assert "bang gia" in response.get_json()["error"].lower()


def test_generate_all_and_pdf_fallback(client, current_period, monkeypatch):
    month, year = current_period
    _, _, contract_a = create_contract_bundle(client, so_phong="I301", cccd="881111111113")
    _, _, contract_b = create_contract_bundle(client, so_phong="I302", cccd="881111111114")
    assert create_bang_gia(client, month, year).status_code == 201
    tt_id = create_payment_for_contract(client, contract_a["hopdong_id"], month, year)
    create_payment_for_contract(client, contract_b["hopdong_id"], month, year)

    generated = client.post(f"/api/hoa-don/generate-all/{month}/{year}")
    assert generated.status_code == 200
    payload = generated.get_json()["data"]
    assert len(payload["generated"]) == 2
    assert payload["errors"] == []

    invoice = client.post(f"/api/hoa-don/{tt_id}/generate").get_json()["data"]

    import app.services.pdf_service as pdf_service

    monkeypatch.setattr(pdf_service, "render_template", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("force fallback")))
    pdf_response = client.get(f"/api/hoa-don/{invoice['hoadon_id']}/pdf")
    assert pdf_response.status_code == 200
    assert pdf_response.mimetype == "application/pdf"
    assert pdf_response.data.startswith(b"%PDF")
