import unittest
from datetime import timedelta
from fastapi.testclient import TestClient
from backend.main import app
from backend.models.database import init_db
from backend.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

init_db()


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(
            data={"sub": "testuser", "scopes": ["read", "write"]},
            expires_delta=token_expires
        )
        self.headers = {"Authorization": f"bearer {token}"}

    def test_health(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "ok")

    def test_create_research(self):
        resp = self.client.post("/api/research", json={"topic": "AI", "depth": "shallow"}, headers=self.headers)
        self.assertIn(resp.status_code, [200, 201])
        data = resp.json()
        self.assertIn("id", data)
        self.assertEqual(data["topic"], "AI")

    def test_create_research_empty_topic(self):
        resp = self.client.post("/api/research", json={"topic": "", "depth": "medium"}, headers=self.headers)
        self.assertEqual(resp.status_code, 400)

    def test_create_research_invalid_depth(self):
        resp = self.client.post("/api/research", json={"topic": "AI", "depth": "invalid"}, headers=self.headers)
        self.assertEqual(resp.status_code, 400)

    def test_list_research(self):
        self.client.post("/api/research", json={"topic": "Test", "depth": "shallow"}, headers=self.headers)
        resp = self.client.get("/api/research", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json(), list)

    def test_get_research_not_found(self):
        resp = self.client.get("/api/research/nonexistent-id", headers=self.headers)
        self.assertEqual(resp.status_code, 404)

    def test_get_research_success(self):
        create_resp = self.client.post("/api/research", json={"topic": "Python", "depth": "shallow"}, headers=self.headers)
        task_id = create_resp.json()["id"]
        resp = self.client.get(f"/api/research/{task_id}", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("task", data)
        self.assertIn("sources", data)

    def test_delete_research_not_found(self):
        resp = self.client.delete("/api/research/nonexistent-id", headers=self.headers)
        self.assertEqual(resp.status_code, 404)

    def test_delete_research_success(self):
        create_resp = self.client.post("/api/research", json={"topic": "Delete Me", "depth": "shallow"}, headers=self.headers)
        task_id = create_resp.json()["id"]
        resp = self.client.delete(f"/api/research/{task_id}", headers=self.headers)
        self.assertEqual(resp.status_code, 200)

    def test_get_report_not_found(self):
        resp = self.client.get("/api/research/nonexistent-id/report", headers=self.headers)
        self.assertEqual(resp.status_code, 404)

    def test_get_stats(self):
        resp = self.client.get("/api/research/stats", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("total_tasks", data)

    def test_export_report_not_found(self):
        resp = self.client.get("/api/research/nonexistent-id/report/export", headers=self.headers)
        self.assertEqual(resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()
