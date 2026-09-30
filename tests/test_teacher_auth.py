import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from src import app as activities_app
from src.teacher_auth import hash_password


class TeacherAuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.credentials_file = Path(self.temp_dir.name) / "teachers.json"
        self.credentials_file.write_text(
            json.dumps({"teachers": {"teacher": hash_password("correct horse")}}),
            encoding="utf-8",
        )
        self.activity_name = "Authentication Test Activity"
        activities_app.activities[self.activity_name] = {
            "description": "Test activity",
            "schedule": "Fridays",
            "max_participants": 2,
            "participants": [],
        }
        self.credentials_patch = patch.object(
            activities_app, "TEACHERS_FILE", self.credentials_file
        )
        self.credentials_patch.start()
        self.client = TestClient(activities_app.app)

    def tearDown(self):
        self.client.close()
        self.credentials_patch.stop()
        activities_app.activities.pop(self.activity_name, None)
        self.temp_dir.cleanup()

    def test_public_activity_list_remains_available_without_login(self):
        response = self.client.get("/activities")

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.activity_name, response.json())

    def test_signup_and_unregister_require_teacher_login(self):
        signup_url = f"/activities/{self.activity_name}/signup"
        unregister_url = f"/activities/{self.activity_name}/unregister"

        self.assertEqual(
            self.client.post(signup_url, params={"email": "student@example.edu"}).status_code,
            401,
        )
        self.assertEqual(
            self.client.delete(unregister_url, params={"email": "student@example.edu"}).status_code,
            401,
        )

        login_response = self.client.post(
            "/auth/login",
            json={"username": "teacher", "password": "correct horse"},
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(
            self.client.post(signup_url, params={"email": "student@example.edu"}).status_code,
            200,
        )
        self.assertEqual(
            self.client.delete(unregister_url, params={"email": "student@example.edu"}).status_code,
            200,
        )

        self.client.post("/auth/logout")
        self.assertEqual(
            self.client.post(signup_url, params={"email": "student@example.edu"}).status_code,
            401,
        )

    def test_invalid_teacher_password_is_rejected(self):
        response = self.client.post(
            "/auth/login",
            json={"username": "teacher", "password": "wrong password"},
        )

        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()