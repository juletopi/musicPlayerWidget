def test_health_plain(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.data == b"OK"


def test_health_with_vercel_prefix(client):
    r = client.get("/api/spotify/health")
    assert r.status_code == 200 and r.data == b"OK"


def test_health_with_api_prefix(client):
    assert client.get("/api/health").data == b"OK"


def test_prefix_root_goes_to_widget(client):
    # With no service configured the catch-all answers with an SVG
    for path in ("/api/spotify", "/api/spotify/"):
        assert client.get(path).mimetype == "image/svg+xml"


def test_prefix_only_on_segment_boundary(client):
    r = client.get("/apis/health")
    assert r.mimetype == "image/svg+xml"  # not rewritten to /health
