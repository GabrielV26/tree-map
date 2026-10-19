import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from .models import SaveDetail
from . import views


class TreemapSecurityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="tester", password="Test-password-123!")
        self.client.force_login(self.user)

    def test_limit_must_be_integer(self):
        response = self.client.get("/api/crypto/?limit=abc")
        self.assertEqual(response.status_code, 400)

    def test_limit_must_be_within_allowed_range(self):
        self.assertEqual(self.client.get("/api/crypto/?limit=0").status_code, 400)
        self.assertEqual(self.client.get("/api/crypto/?limit=101").status_code, 400)

    @patch.dict(os.environ, {"COINMARKETCAP_API_KEY": ""})
    def test_api_returns_service_unavailable_without_api_key(self):
        response = self.client.get("/api/crypto/")
        self.assertEqual(response.status_code, 503)

    def test_save_requires_post(self):
        response = self.client.get("/save/")
        self.assertEqual(response.status_code, 405)

    def test_save_and_delete_require_login(self):
        self.client.logout()
        response = self.client.post("/save/", {"text": "private note"})
        self.assertEqual(response.status_code, 302)

        detail = SaveDetail.objects.create(text="note")
        response = self.client.post(f"/delete_data/{detail.id}/")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(SaveDetail.objects.filter(id=detail.id).exists())

    def test_save_returns_record_id(self):
        response = self.client.post("/save/", {"text": "Market note"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["id"])

    def test_previous_data_handles_invalid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text("{not json", encoding="utf-8")
            with patch.object(views, "DATA_FILE", path):
                self.assertEqual(views.load_previous_data(), {})
