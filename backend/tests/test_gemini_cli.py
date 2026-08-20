import io
import json
import unittest
import zipfile
from unittest.mock import AsyncMock, patch

from config import DEFAULT_GEMINI_CLI_CLIENT_ID
from core.gemini_cli import (
    build_gemini_cli_headers,
    complete_gemini_cli_oauth,
    create_gemini_cli_oauth_flow,
    gemini_cli_user_agent,
    is_gemini_cli_oauth_state,
    normalize_gemini_cli_api_url,
    wrap_gemini_cli_payload,
)
from core.pool_import import (
    classify_pool_credential,
    restore_pool_archive,
)
from core.provider_registry import (
    GEMINI_CLI,
    build_gemini_cli_credential_filename,
    gemini_cli_account_fingerprint,
    get_provider_capabilities,
    normalize_provider_id,
)


class TestGeminiCliCore(unittest.TestCase):
    def test_provider_registry(self):
        self.assertEqual(normalize_provider_id("gemini_cli"), GEMINI_CLI)
        self.assertEqual(normalize_provider_id("gemini-cli"), GEMINI_CLI)
        self.assertEqual(normalize_provider_id("geminicli"), GEMINI_CLI)
        self.assertEqual(normalize_provider_id("gc"), GEMINI_CLI)

        caps = get_provider_capabilities(GEMINI_CLI)
        self.assertIsNotNone(caps)
        self.assertEqual(caps.display_name, "Gemini CLI")
        self.assertIn("oauth", caps.credential_types)

        fp = gemini_cli_account_fingerprint(email="test@gmail.com")
        self.assertEqual(len(fp), 16)

        fn = build_gemini_cli_credential_filename(email="test@gmail.com")
        self.assertTrue(fn.startswith("gemini-cli-"))
        self.assertTrue(fn.endswith(".json"))

    def test_gemini_cli_headers(self):
        headers = build_gemini_cli_headers("test-token", model="gemini-2.5-flash", stream=True)
        self.assertEqual(headers["Authorization"], "Bearer test-token")
        self.assertEqual(headers["Accept"], "text/event-stream")
        self.assertIn("GeminiCLI", headers["User-Agent"])
        self.assertIn("gemini-2.5-flash", headers["User-Agent"])
        self.assertIn("google-genai-sdk", headers["X-Goog-Api-Client"])

    def test_gemini_cli_user_agent(self):
        ua = gemini_cli_user_agent("gemini-2.5-pro")
        self.assertTrue(ua.startswith("GeminiCLI/0.34.0/gemini-2.5-pro"))

    def test_wrap_gemini_cli_payload(self):
        req = {
            "contents": [{"role": "user", "parts": [{"text": "Hello"}]}],
            "generationConfig": {"temperature": 0.7},
        }
        wrapped = wrap_gemini_cli_payload(req, model="gemini-2.5-flash", project_id="proj-123")
        self.assertEqual(wrapped["project"], "proj-123")
        self.assertEqual(wrapped["model"], "gemini-2.5-flash")
        self.assertEqual(wrapped["request"]["contents"], req["contents"])

    def test_normalize_gemini_cli_api_url(self):
        self.assertEqual(
            normalize_gemini_cli_api_url("https://cloudcode-pa.googleapis.com/"),
            "https://cloudcode-pa.googleapis.com",
        )
        with self.assertRaises(ValueError):
            normalize_gemini_cli_api_url("ftp://insecure.com")

    def test_classify_and_restore_credential(self):
        payload = {
            "provider": "gemini_cli",
            "access_token": "ya29.test",
            "refresh_token": "1//test",
            "token_type": "Bearer",
            "scope": "openid email profile",
            "project_id": "test-project",
            "email": "user@example.com",
            "expiry_date": 1800000000000,
        }
        kind = classify_pool_credential(payload)
        self.assertEqual(kind, GEMINI_CLI)


class TestGeminiCliAsync(unittest.IsolatedAsyncioTestCase):
    async def test_oauth_flow_creation_and_state(self):
        url, state = await create_gemini_cli_oauth_flow("http://127.0.0.1:4283/callback")
        self.assertTrue(url.startswith("https://accounts.google.com/o/oauth2/v2/auth"))
        self.assertIn(f"client_id={DEFAULT_GEMINI_CLI_CLIENT_ID}", url)
        self.assertIn("code_challenge=", url)
        self.assertIn("code_challenge_method=S256", url)
        self.assertTrue(is_gemini_cli_oauth_state(state))
        self.assertFalse(is_gemini_cli_oauth_state("non-existent-state"))

    @patch("core.gemini_cli.post_async")
    @patch("core.gemini_cli.get_async")
    async def test_complete_oauth_and_store(self, mock_get, mock_post):
        url, state = await create_gemini_cli_oauth_flow("http://127.0.0.1:4283/callback")

        # Mock token exchange
        mock_token_resp = unittest.mock.MagicMock()
        mock_token_resp.status_code = 200
        mock_token_resp.json.return_value = {
            "access_token": "mock-access-token",
            "refresh_token": "mock-refresh-token",
            "expires_in": 3600,
            "scope": "https://www.googleapis.com/auth/cloud-platform",
            "token_type": "Bearer",
        }
        mock_post.return_value = mock_token_resp

        # Mock userinfo
        mock_userinfo_resp = unittest.mock.MagicMock()
        mock_userinfo_resp.status_code = 200
        mock_userinfo_resp.json.return_value = {
            "email": "geminitest@gmail.com",
            "id": "123456789",
        }
        mock_get.return_value = mock_userinfo_resp

        with patch("core.gemini_cli.fetch_gemini_cli_project_id", return_value="mock-project"):
            with patch(
                "core.gemini_cli.upsert_credential_by_email",
                new=AsyncMock(return_value={"action": "created", "filename": "gemini-cli-test.json"}),
            ) as mock_upsert:
                result = await complete_gemini_cli_oauth("mock-auth-code", state)
                self.assertTrue(result["success"])
                self.assertEqual(result["user_email"], "geminitest@gmail.com")
                self.assertEqual(result["project_id"], "mock-project")
                mock_upsert.assert_called_once()

    async def test_restore_archive_gemini_cli(self):
        from fastapi import UploadFile

        payload = {
            "provider": "gemini_cli",
            "access_token": "ya29.imported",
            "refresh_token": "1//imported",
            "token_type": "Bearer",
            "project_id": "imported-project",
            "email": "imported@example.com",
            "expiry_date": 1800000000000,
        }
        archive_buffer = io.BytesIO()
        with zipfile.ZipFile(archive_buffer, "w") as zf:
            zf.writestr("gemini_cli_test.json", json.dumps(payload))

        upload = UploadFile(filename="test.zip", file=io.BytesIO(archive_buffer.getvalue()))
        with patch(
            "core.pool_import.credential_manager.add_primary_credential",
            new=AsyncMock(
                return_value={
                    "action": "created",
                    "stored": True,
                    "filename": "gemini-cli-test.json",
                    "email": "imported@example.com",
                    "message": "Credential added to the pool.",
                }
            ),
        ) as add_mock:
            report = await restore_pool_archive(upload)
            self.assertEqual(report["uploaded_count"], 1)
            self.assertEqual(report["error_count"], 0)
            add_mock.assert_called_once()

    async def test_prepare_provider_request_gemini_cli(self):
        from core.api.primary import prepare_provider_request

        cred = {
            "provider": "gemini_cli",
            "access_token": "ya29.test-access-token",
            "project_id": "test-gemini-project",
        }
        body = {
            "model": "gemini-2.5-flash",
            "request": {
                "contents": [{"role": "user", "parts": [{"text": "Hello world"}]}],
            },
        }
        ctx = await prepare_provider_request(cred, body, streaming=True)
        self.assertIn("cloudcode-pa.googleapis.com", ctx.target_url)
        self.assertIn("v1internal:streamGenerateContent?alt=sse", ctx.target_url)
        self.assertEqual(ctx.headers["Authorization"], "Bearer ya29.test-access-token")
        self.assertEqual(ctx.payload["project"], "test-gemini-project")
        self.assertEqual(ctx.payload["model"], "gemini-2.5-flash")

    async def test_gemini_cli_panel_routes(self):
        from core.panel.providers.gemini_cli import (
            get_gemini_cli_config,
            start_gemini_cli_oauth,
        )

        resp = await get_gemini_cli_config()
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.body.decode())
        self.assertIn("gemini_cli_api_url", data["config"])

        oauth_resp = await start_gemini_cli_oauth()
        self.assertEqual(oauth_resp.status_code, 200)
        oauth_data = json.loads(oauth_resp.body.decode())
        self.assertTrue(oauth_data["success"])
        self.assertIn("accounts.google.com", oauth_data["authorization_url"])


if __name__ == "__main__":
    unittest.main()
