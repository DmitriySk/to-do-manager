def test_sso_login_success_path(client):
    resp = client.post(
        "/auth/test-login",
        json={
            "provider": "google",
            "provider_user_id": "google-123",
            "email": "jane@example.com",
            "display_name": "Jane Doe",
            "avatar_url": "https://example.com/avatar.png",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["provider"] == "google"
    assert body["display_name"] == "Jane Doe"
    assert body["email"] == "jane@example.com"

    me = client.get("/auth/me")
    assert me.status_code == 200
    assert me.json()["email"] == "jane@example.com"


def test_me_requires_authentication(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 401


def test_logout_clears_session(auth_client):
    assert auth_client.get("/auth/me").status_code == 200
    resp = auth_client.post("/auth/logout")
    assert resp.status_code == 200
    assert auth_client.get("/auth/me").status_code == 401
