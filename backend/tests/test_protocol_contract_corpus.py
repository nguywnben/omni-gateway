"""Golden contract coverage shared by every advertised inference protocol."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
from pydantic import ValidationError

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import main
from core.models import (
    ClaudeRequest,
    GeminiRequest,
    OpenAIChatCompletionRequest,
    OpenAIResponsesRequest,
)
from core.protocol_contract import list_protocol_conversions
from core.provider_registry import INFERENCE_PROTOCOLS

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "protocol-contract-corpus-v1.json"


class ProtocolContractMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_corpus_covers_every_advertised_family_and_feature(self):
        self.assertEqual(self.fixture["schema_version"], 1)
        self.assertEqual(set(self.fixture["advertised_families"]), set(INFERENCE_PROTOCOLS))

        vocabulary = set(self.fixture["feature_vocabulary"])
        covered_families = set()
        for conversion in self.fixture["conversions"].values():
            covered_families.add(conversion["family"])
            self.assertEqual(set(conversion["features"]), vocabulary)
            self.assertTrue(
                set(conversion["features"].values()) <= {"supported", "translated", "rejected"}
            )
        self.assertEqual(covered_families, set(INFERENCE_PROTOCOLS))

    def test_runtime_contract_matches_the_versioned_corpus(self):
        self.assertEqual(list_protocol_conversions(), self.fixture["conversions"])

    def test_unknown_top_level_fields_fail_closed_for_every_request_family(self):
        cases = (
            (
                OpenAIChatCompletionRequest,
                {
                    "model": "fixture-model",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "silent_semantic_change": True,
                },
            ),
            (
                OpenAIResponsesRequest,
                {
                    "model": "fixture-model",
                    "input": "Hello",
                    "silent_semantic_change": True,
                },
            ),
            (
                ClaudeRequest,
                {
                    "model": "fixture-model",
                    "max_tokens": 32,
                    "messages": [{"role": "user", "content": "Hello"}],
                    "silent_semantic_change": True,
                },
            ),
            (
                GeminiRequest,
                {
                    "contents": [{"role": "user", "parts": [{"text": "Hello"}]}],
                    "silentSemanticChange": True,
                },
            ),
        )

        for model, payload in cases:
            with self.subTest(model=model.__name__), self.assertRaises(ValidationError):
                model.model_validate(payload)

    def test_unknown_nested_gemini_config_field_fails_closed(self):
        with self.assertRaises(ValidationError):
            GeminiRequest.model_validate(
                {
                    "contents": [{"role": "user", "parts": [{"text": "Hello"}]}],
                    "generationConfig": {"silentSemanticChange": True},
                }
            )


class ProtocolContractBoundaryTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.client = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=main.app),
            base_url="http://test",
        )

    async def asyncTearDown(self) -> None:
        await self.client.aclose()

    async def test_unknown_fields_return_native_http_400_for_every_public_family(self):
        cases = (
            (
                "/v1/chat/completions",
                {"Authorization": "Bearer sk-ogw-test-key"},
                {
                    "model": "fixture-model",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "silent_semantic_change": True,
                },
                "invalid_request_error",
            ),
            (
                "/v1/responses",
                {"Authorization": "Bearer sk-ogw-test-key"},
                {
                    "model": "fixture-model",
                    "input": "Hello",
                    "silent_semantic_change": True,
                },
                "invalid_request_error",
            ),
            (
                "/v1/messages",
                {"x-api-key": "sk-ogw-test-key"},
                {
                    "model": "fixture-model",
                    "max_tokens": 32,
                    "messages": [{"role": "user", "content": "Hello"}],
                    "silent_semantic_change": True,
                },
                "invalid_request_error",
            ),
            (
                "/v1beta/models/fixture-model:generateContent",
                {"x-goog-api-key": "sk-ogw-test-key"},
                {
                    "contents": [{"role": "user", "parts": [{"text": "Hello"}]}],
                    "silentSemanticChange": True,
                },
                "INVALID_ARGUMENT",
            ),
            (
                "/vertex/v1beta/models/fixture-model:generateContent",
                {"x-goog-api-key": "sk-ogw-test-key"},
                {
                    "contents": [{"role": "user", "parts": [{"text": "Hello"}]}],
                    "silentSemanticChange": True,
                },
                "INVALID_ARGUMENT",
            ),
        )

        with patch("config.get_api_key", new=AsyncMock(return_value="sk-ogw-test-key")):
            for path, headers, body, expected_error in cases:
                with self.subTest(path=path):
                    response = await self.client.post(path, headers=headers, json=body)
                    payload = response.json()["error"]

                    self.assertEqual(response.status_code, 400)
                    self.assertIn(expected_error, payload.values())
                    self.assertIn("silent", payload["message"].lower())


if __name__ == "__main__":
    unittest.main()
