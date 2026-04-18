from app import create_app


def test_app_boot_and_basic_routes(client):
    app = create_app()
    assert app is not None

    health = client.get("/health")
    assert health.status_code == 200
    assert health.get_json()["status"] == "ok"

    page = client.get("/dashboard")
    assert page.status_code == 200

    api = client.get("/api/phong")
    assert api.status_code == 200
    assert api.get_json()["success"] is True
