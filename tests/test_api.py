from unittest import TestCase

from fastapi.testclient import TestClient

from app.main import app


class TestAPI(TestCase):
    client: TestClient

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    def test_health(self):
        response = self.client.get("/health")
        expect = {"status": "OK", "details": None}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expect)
