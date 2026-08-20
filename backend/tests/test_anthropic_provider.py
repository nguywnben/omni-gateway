"""Tests for Claude Code and Claude Platform provider contracts."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch
from urllib.parse import parse_qs, urlparse

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.anthropic import (
    ANTHROPIC_REDIRECT_URI,
    _oauth_flows,
    anthropic_response_to_gemini,
    anthropic_stream_line_to_gemini,
    build_anthropic_headers,
    create_claude_oauth_url,
    gemini_request_to_anthropic,
    parse_anthropic_model_ids,
)


class AnthropicProviderTests(unittest.IsolatedAsyncioTestCase):
    def tearDown(self):
        _oauth_flows.clear()

    def test_model_parser_is_bounded_and_deduplicated(self):
        payload = {
            "data": [
                {"id": "claude-sonnet-4-6"},
                {"id": "claude-sonnet-4-6"},
                {"id": "invalid\u0000"},
                *({"id": f"claude-test-{index}"} for index in range(600)),
            ]
        }
        models = parse_anthropic_model_ids(payload)
        self.assertEqual(models[0], "claude-sonnet-4-6")
        self.assertEqual(len(models), 500)
        self.assertNotIn("invalid\u0000", models)

    def test_headers_distinguish_oauth_and_api_key_credentials(self):
        oauth = build_anthropic_headers(
            {"credential_type": "oauth", "access_token": "oauth-secret"},
            user_agent="claude-cli/test",
        )
        platform = build_anthropic_headers(
            {"credential_type": "api_key", "api_key": "api-secret"},
            user_agent="omni-gateway/test",
        )
        self.assertEqual(oauth["Authorization"], "Bearer oauth-secret")
        self.assertNotIn("x-api-key", oauth)
        self.assertEqual(platform["x-api-key"], "api-secret")
        self.assertNotIn("Authorization", platform)
        self.assertEqual(oauth["anthropic-version"], "2023-06-01")

    async def test_oauth_authorization_uses_pkce_and_loopback_callback(self):
        with patch(
            "core.anthropic.get_claude_client_id",
            AsyncMock(return_value="public-client-id"),
        ):
            result = await create_claude_oauth_url()
        query = parse_qs(urlparse(result["auth_url"]).query)
        self.assertEqual(result["redirect_uri"], ANTHROPIC_REDIRECT_URI)
        self.assertEqual(query["client_id"], ["public-client-id"])
        self.assertEqual(query["redirect_uri"], [ANTHROPIC_REDIRECT_URI])
        self.assertEqual(query["code_challenge_method"], ["S256"])
        self.assertEqual(query["code"], ["true"])
        self.assertEqual(query["state"], [result["state"]])

    def test_request_translation_preserves_system_tools_and_generation_options(self):
        payload = gemini_request_to_anthropic(
            {
                "systemInstruction": {"parts": [{"text": "Be concise."}]},
                "contents": [
                    {"role": "user", "parts": [{"text": "Check the build."}]},
                    {
                        "role": "model",
                        "parts": [
                            {
                                "functionCall": {
                                    "id": "call-1",
                                    "name": "run_tests",
                                    "args": {"scope": "unit"},
                                }
                            }
                        ],
                    },
                ],
                "tools": [
                    {
                        "functionDeclarations": [
                            {
                                "name": "run_tests",
                                "description": "Run tests.",
                                "parameters": {"type": "object"},
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "maxOutputTokens": 128,
                    "temperature": 0.2,
                    "stopSequences": ["STOP"],
                },
            },
            "claude-sonnet-4-6",
            streaming=True,
        )
        self.assertEqual(payload["model"], "claude-sonnet-4-6")
        self.assertTrue(payload["stream"])
        self.assertEqual(payload["system"], "Be concise.")
        self.assertEqual(payload["max_tokens"], 128)
        self.assertEqual(payload["tools"][0]["name"], "run_tests")
        self.assertEqual(payload["messages"][1]["content"][0]["type"], "tool_use")

    def test_response_and_stream_translation_preserve_text_tools_and_usage(self):
        response = anthropic_response_to_gemini(
            {
                "model": "claude-sonnet-4-6",
                "content": [
                    {"type": "text", "text": "Done"},
                    {
                        "type": "tool_use",
                        "id": "call-1",
                        "name": "run_tests",
                        "input": {"scope": "unit"},
                    },
                ],
                "stop_reason": "tool_use",
                "usage": {"input_tokens": 10, "output_tokens": 4},
            }
        )
        stream = anthropic_stream_line_to_gemini(
            'data: {"type":"content_block_delta","delta":{"type":"text_delta","text":"Done"}}'
        )
        parts = response["candidates"][0]["content"]["parts"]
        self.assertEqual(parts[0], {"text": "Done"})
        self.assertEqual(parts[1]["functionCall"]["name"], "run_tests")
        self.assertEqual(response["usageMetadata"]["totalTokenCount"], 14)
        self.assertTrue(stream.startswith("data: "))
        self.assertEqual(
            json.loads(stream.removeprefix("data: ").strip())["candidates"][0]["content"]["parts"][
                0
            ]["text"],
            "Done",
        )


if __name__ == "__main__":
    unittest.main()
