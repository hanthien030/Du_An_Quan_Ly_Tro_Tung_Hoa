from datetime import date, timedelta


def test_contract_updates_room_status(client):
    room_res = client.post(
        "/api/phong",
        json={
            "so_phong": "C201",
            "tang": 2,
            "dien_tich": 18,
            "cap_phong": "cap2",
            "trang_thai": "trong",
        },
    )
    room_id = room_res.get_json()["data"]["phong_id"]

    tenant_res = client.post(
        "/api/khach-thue",
        json={
            "ho_ten": "Khach Hop Dong",
            "cccd": "123456789999",
            "ngay_sinh": "2000-01-01",
            "sdt": "0900000000",
            "la_chinh": True,
        },
    )
    tenant_id = tenant_res.get_json()["data"]["khach_id"]

    start = date.today()
    end = start + timedelta(days=60)
    contract_res = client.post(
        "/api/hop-dong",
        json={
            "phong_id": room_id,
            "khach_id": tenant_id,
            "ngay_bat_dau": start.isoformat(),
            "ngay_ket_thuc": end.isoformat(),
            "ghi_chu": "Contract test",
        },
    )
    assert contract_res.status_code == 201
    contract = contract_res.get_json()["data"]
    assert contract["trang_thai"] == "hieu_luc"

    room_after_create = client.get(f"/api/phong/{room_id}")
    assert room_after_create.status_code == 200
    assert room_after_create.get_json()["data"]["trang_thai"] == "dang_thue"

    ended = client.put(f"/api/hop-dong/{contract['hopdong_id']}", json={"ket_thuc_som": True})
    assert ended.status_code == 200
    assert ended.get_json()["data"]["trang_thai"] == "het_han"

    room_after_end = client.get(f"/api/phong/{room_id}")
    assert room_after_end.status_code == 200
    assert room_after_end.get_json()["data"]["trang_thai"] == "trong"
