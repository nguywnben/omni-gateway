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
    model_to_dict,
)
from core.protocol_contract import list_protocol_conversions
from core.provider_registry import INFERENCE_PROTOCOLS
from core.router.primary.responses import responses_to_chat_request

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "protocol-contract-corpus-v1.json"
REQUEST_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "protocol-request-golden-v1.json"


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


class ProtocolRequestGoldenTests(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(REQUEST_FIXTURE_PATH.read_text(encoding="utf-8"))

    async def test_openai_chat_and_vertex_openai_translate_the_golden_request(self):
        from core.converter.openai_to_gemini import convert_openai_to_gemini_request

        case = self.fixture["openai_chat"]
        request = OpenAIChatCompletionRequest.model_validate(case["request"])
        with patch("config.get_compatibility_mode_enabled", new=AsyncMock(return_value=False)):
            translated = await convert_openai_to_gemini_request(model_to_dict(request))

        expected = case["expected"]
        self.assertEqual(
            translated["systemInstruction"]["parts"][0]["text"], expected["system_text"]
        )
        self.assertEqual(translated["contents"][0]["parts"][0]["text"], expected["user_text"])
        inline_data = translated["contents"][0]["parts"][1]["inlineData"]
        self.assertEqual(inline_data["mimeType"], expected["image_mime_type"])
        self.assertEqual(inline_data["data"], expected["image_data"])
        self.assertEqual(
            translated["generationConfig"]["maxOutputTokens"], expected["max_output_tokens"]
        )
        self.assertEqual(
            translated["generationConfig"]["responseMimeType"],
            expected["response_mime_type"],
        )
        self.assertEqual(
            translated["tools"][0]["functionDeclarations"][0]["name"],
            expected["tool_name"],
        )

    def test_openai_responses_translates_the_golden_request_without_loss(self):
        case = self.fixture["openai_responses"]
        request = OpenAIResponsesRequest.model_validate(case["request"])
        translated = model_to_dict(responses_to_chat_request(request))
        expected = case["expected"]

        self.assertEqual(
            [item["role"] for item in translated["messages"]], expected["message_roles"]
        )
        self.assertEqual(translated["tools"][0]["function"]["name"], expected["tool_name"])
        self.assertEqual(translated["response_format"]["type"], expected["response_format_type"])
        self.assertEqual(
            translated["response_format"]["json_schema"]["name"],
            expected["response_format_name"],
        )

    async def test_anthropic_translates_the_golden_request_without_loss(self):
        from core.converter.anthropic_to_gemini import anthropic_to_gemini_request

        case = self.fixture["anthropic"]
        request = ClaudeRequest.model_validate(case["request"])
        with patch("config.get_compatibility_mode_enabled", new=AsyncMock(return_value=False)):
            translated = await anthropic_to_gemini_request(model_to_dict(request))

        expected = case["expected"]
        self.assertEqual(
            translated["systemInstruction"]["parts"][0]["text"], expected["system_text"]
        )
        thinking_part = next(
            part
            for content in translated["contents"]
            for part in content["parts"]
            if part.get("thought") is True
        )
        self.assertEqual(thinking_part["text"], expected["thinking_text"])
        self.assertEqual(thinking_part["thoughtSignature"], expected["thinking_signature"])
        self.assertEqual(
            translated["generationConfig"]["thinkingConfig"]["thinkingBudget"],
            expected["thinking_budget"],
        )
        self.assertEqual(
            translated["generationConfig"]["responseMimeType"],
            expected["response_mime_type"],
        )
        self.assertEqual(
            translated["tools"][0]["functionDeclarations"][0]["name"],
            expected["tool_name"],
        )

    def test_gemini_and_vertex_gemini_preserve_the_native_golden_request(self):
        from core.anthropic import gemini_request_to_anthropic

        request = self.fixture["gemini"]["request"]
        self.assertEqual(model_to_dict(GeminiRequest.model_validate(request)), request)
        translated = gemini_request_to_anthropic(request, "fixture-model", False)
        self.assertEqual(
            translated["output_config"]["format"],
            {
                "type": "json_schema",
                "schema": request["generationConfig"]["responseSchema"],
            },
        )

    def test_unsupported_or_unknown_semantics_fail_closed(self):
        cases = (
            (
                OpenAIChatCompletionRequest,
                {
                    "model": "fixture-model",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "reasoning_effort": "high",
                },
            ),
            (
                OpenAIChatCompletionRequest,
                {
                    "model": "fixture-model",
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"type": "unknown_part", "value": "lost"}],
                        }
                    ],
                },
            ),
            (
                OpenAIResponsesRequest,
                {"model": "fixture-model", "input": "Hello", "reasoning": {"effort": "high"}},
            ),
            (
                OpenAIResponsesRequest,
                {
                    "model": "fixture-model",
                    "input": [{"type": "unknown_item", "value": "lost"}],
                },
            ),
            (
                ClaudeRequest,
                {
                    "model": "fixture-model",
                    "max_tokens": 32,
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"type": "unknown_block", "value": "lost"}],
                        }
                    ],
                },
            ),
        )

        for model, payload in cases:
            with self.subTest(model=model.__name__), self.assertRaises(ValidationError):
                model.model_validate(payload)


if __name__ == "__main__":
    unittest.main()
