def create_bang_gia(client, thang, nam, cap1=2500000, cap2=3500000):
    return client.post(
        "/api/bang-gia",
        json={
            "thang": thang,
            "nam": nam,
            "gia_phong_cap1": cap1,
            "gia_phong_cap2": cap2,
            "don_gia_dien": 3500,
            "don_gia_nuoc": 15000,
            "phi_wifi": 100000,
            "phi_ve_sinh": 50000,
            "phi_gui_xe": 50000,
        },
    )


def test_copy_bang_gia_success(client):
    created = create_bang_gia(client, 3, 2026, cap1=2400000, cap2=3300000)
    assert created.status_code == 201

    copied = client.post(
        "/api/bang-gia/copy",
        json={"from_thang": 3, "from_nam": 2026, "to_thang": 4, "to_nam": 2026},
    )
    assert copied.status_code == 201
    payload = copied.get_json()["data"]
    assert payload["thang"] == 4
    assert payload["nam"] == 2026
    assert payload["gia_phong_cap1"] == 2400000
    assert payload["gia_phong_cap2"] == 3300000


def test_copy_bang_gia_fails_when_source_missing(client):
    response = client.post(
        "/api/bang-gia/copy",
        json={"from_thang": 1, "from_nam": 2026, "to_thang": 2, "to_nam": 2026},
    )
    assert response.status_code == 404
    assert response.get_json()["success"] is False


def test_copy_bang_gia_fails_when_target_exists(client):
    assert create_bang_gia(client, 5, 2026).status_code == 201
    assert create_bang_gia(client, 6, 2026).status_code == 201

    response = client.post(
        "/api/bang-gia/copy",
        json={"from_thang": 5, "from_nam": 2026, "to_thang": 6, "to_nam": 2026},
    )
    assert response.status_code == 409
    assert response.get_json()["success"] is False
