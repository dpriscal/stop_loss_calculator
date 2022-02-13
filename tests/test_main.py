from starlette.testclient import TestClient


def test_root_endpoint(testclient: TestClient):
    r = testclient.get("/stocks/fvrr")
    assert r.status_code == 200
