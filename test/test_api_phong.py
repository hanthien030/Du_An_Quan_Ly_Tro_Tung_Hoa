from datetime import date, timedelta


def create_room(client, so_phong="P101", **overrides):
    payload = {
        "so_phong": so_phong,
        "tang": 1,
        "dien_tich": 20,
        "cap_phong": "cap1",
        "trang_thai": "trong",
        "mo_ta": "Phong test",
    }
    payload.update(overrides)
    return client.post("/api/phong", json=payload)


def create_tenant(client, cccd="999999999999", **overrides):
    payload = {
        "ho_ten": "Khach test",
        "cccd": cccd,
        "ngay_sinh": "2000-01-01",
        "sdt": "0901234567",
        "la_chinh": True,
    }
    payload.update(overrides)
    return client.post("/api/khach-thue", json=payload)


def create_contract(client, phong_id, khach_id, *, start_offset_days=0, duration_days=45):
    start = date.today() + timedelta(days=start_offset_days)
    end = start + timedelta(days=duration_days)
    return client.post(
        "/api/hop-dong",
        json={
            "phong_id": phong_id,
            "khach_id": khach_id,
            "ngay_bat_dau": start.isoformat(),
            "ngay_ket_thuc": end.isoformat(),
        },
    )


def test_room_crud_flow(client):
    created = create_room(client, "P101")
    assert created.status_code == 201
    room = created.get_json()["data"]

    listing = client.get("/api/phong")
    assert listing.status_code == 200
    assert [item["so_phong"] for item in listing.get_json()["data"]] == ["P101"]

    fetched = client.get(f"/api/phong/{room['phong_id']}")
    assert fetched.status_code == 200
    assert fetched.get_json()["data"]["so_phong"] == "P101"

    updated = client.put(
        f"/api/phong/{room['phong_id']}",
        json={
            "so_phong": "P102",
            "dien_tich": 22,
            "cap_phong": "cap2",
            "mo_ta": "Da cap nhat",
        },
    )
    assert updated.status_code == 200
    updated_room = updated.get_json()["data"]
    assert updated_room["so_phong"] == "P102"
    assert updated_room["dien_tich"] == 22
    assert updated_room["cap_phong"] == "cap2"
    assert updated_room["mo_ta"] == "Da cap nhat"

    deleted = client.delete(f"/api/phong/{room['phong_id']}")
    assert deleted.status_code == 200
    assert deleted.get_json()["data"]["deleted"] == room["phong_id"]

    missing = client.get(f"/api/phong/{room['phong_id']}")
    assert missing.status_code == 404


def test_create_room_validates_required_and_unique_so_phong(client):
    missing_number = client.post("/api/phong", json={"tang": 2})
    assert missing_number.status_code == 400
    assert "thiếu số phòng" in missing_number.get_json()["error"].lower()

    assert create_room(client, "P201").status_code == 201

    duplicate = create_room(client, "P201")
    assert duplicate.status_code == 409
    assert "đã tồn tại" in duplicate.get_json()["error"].lower()


def test_update_room_rejects_duplicate_so_phong(client):
    room_a = create_room(client, "P301").get_json()["data"]
    room_b = create_room(client, "P302").get_json()["data"]

    duplicate = client.put(
        f"/api/phong/{room_b['phong_id']}",
        json={"so_phong": room_a["so_phong"]},
    )

    assert duplicate.status_code == 409
    assert "đã tồn tại" in duplicate.get_json()["error"].lower()


def test_list_and_grid_filter_rooms_by_status(client):
    create_room(client, "P401", trang_thai="trong")
    create_room(client, "P402", trang_thai="dang_thue")
    create_room(client, "P403", trang_thai="sua_chua")

    listed = client.get("/api/phong?trang_thai=dang_thue")
    assert listed.status_code == 200
    assert [item["so_phong"] for item in listed.get_json()["data"]] == ["P402"]

    grid = client.get("/api/phong/grid?trang_thai=trong")
    assert grid.status_code == 200
    grid_data = grid.get_json()["data"]
    assert [item["so_phong"] for item in grid_data] == ["P401"]
    assert grid_data[0]["khach_chinh"] is None
    assert grid_data[0]["hopdong_id"] is None


def test_grid_includes_active_contract_summary(client):
    room = create_room(client, "P501").get_json()["data"]
    tenant = create_tenant(client, "999999999501", ho_ten="Khach Grid").get_json()["data"]
    contract = create_contract(client, room["phong_id"], tenant["khach_id"], duration_days=15)
    assert contract.status_code == 201

    grid = client.get("/api/phong/grid")
    assert grid.status_code == 200
    room_data = next(item for item in grid.get_json()["data"] if item["phong_id"] == room["phong_id"])

    assert room_data["so_phong"] == "P501"
    assert room_data["khach_chinh"] == "Khach Grid"
    assert room_data["hopdong_id"] == contract.get_json()["data"]["hopdong_id"]
    assert room_data["days_remaining"] is not None
    assert room_data["ngay_het_han"] is not None


def test_delete_room_rejects_active_contract_and_historical_contract(client):
    active_room = create_room(client, "P601").get_json()["data"]
    active_tenant = create_tenant(client, "999999999601").get_json()["data"]
    assert create_contract(client, active_room["phong_id"], active_tenant["khach_id"], duration_days=20).status_code == 201

    active_delete = client.delete(f"/api/phong/{active_room['phong_id']}")
    assert active_delete.status_code == 400
    assert "hợp đồng hiệu lực" in active_delete.get_json()["error"].lower()

    history_room = create_room(client, "P602").get_json()["data"]
    history_tenant = create_tenant(client, "999999999602").get_json()["data"]
    assert create_contract(
        client,
        history_room["phong_id"],
        history_tenant["khach_id"],
        start_offset_days=-60,
        duration_days=30,
    ).status_code == 201

    historical_delete = client.delete(f"/api/phong/{history_room['phong_id']}")
    assert historical_delete.status_code == 400
    assert "lịch sử hợp đồng" in historical_delete.get_json()["error"].lower()
