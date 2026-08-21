"""Tests for Ollama connection, model discovery, and translation contracts."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.ollama import (
    build_ollama_headers,
    gemini_request_to_ollama,
    normalize_ollama_base_url,
    ollama_response_to_gemini,
    ollama_stream_line_to_gemini,
    parse_ollama_model_ids,
)


class OllamaProviderTests(unittest.TestCase):
    def test_base_url_normalization_accepts_local_and_cloud_hosts(self):
        self.assertEqual(
            normalize_ollama_base_url("http://localhost:11434/api/chat"),
            "http://localhost:11434",
        )
        self.assertEqual(
            normalize_ollama_base_url("https://ollama.com/api/tags/"),
            "https://ollama.com",
        )

    def test_base_url_normalization_rejects_credentials_and_unsupported_schemes(self):
        with self.assertRaisesRegex(ValueError, "credentials"):
            normalize_ollama_base_url("http://user:secret@localhost:11434")
        with self.assertRaisesRegex(ValueError, "HTTP or HTTPS"):
            normalize_ollama_base_url("file:///tmp/ollama")

    def test_model_parser_supports_name_and_model_fields(self):
        models = parse_ollama_model_ids(
            {
                "models": [
                    {"name": "qwen3.5:latest"},
                    {"model": "gpt-oss:120b"},
                    {"name": "qwen3.5:latest"},
                    {"name": "invalid\u0000"},
                ]
            }
        )
        self.assertEqual(models, ["qwen3.5:latest", "gpt-oss:120b"])

    def test_optional_api_key_only_adds_bearer_auth_when_present(self):
        self.assertEqual(build_ollama_headers(""), {"Content-Type": "application/json"})
        self.assertEqual(build_ollama_headers("cloud-key")["Authorization"], "Bearer cloud-key")

    def test_request_translation_preserves_messages_tools_and_options(self):
        request = gemini_request_to_ollama(
            {
                "systemInstruction": {"parts": [{"text": "Be concise."}]},
                "contents": [{"role": "user", "parts": [{"text": "Hello"}]}],
                "tools": [
                    {
                        "functionDeclarations": [
                            {
                                "name": "lookup",
                                "description": "Look up a value.",
                                "parameters": {"type": "object"},
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.3,
                    "topP": 0.8,
                    "maxOutputTokens": 64,
                },
            },
            "qwen3.5:latest",
            streaming=True,
        )
        self.assertEqual(request["model"], "qwen3.5:latest")
        self.assertTrue(request["stream"])
        self.assertEqual(request["messages"][0], {"role": "system", "content": "Be concise."})
        self.assertEqual(request["tools"][0]["function"]["name"], "lookup")
        self.assertEqual(request["options"]["num_predict"], 64)

    def test_response_and_ndjson_stream_translation_preserve_usage(self):
        response = ollama_response_to_gemini(
            {
                "model": "qwen3.5:latest",
                "message": {"role": "assistant", "content": "Hello"},
                "done": True,
                "done_reason": "stop",
                "prompt_eval_count": 8,
                "eval_count": 3,
            }
        )
        stream = ollama_stream_line_to_gemini(
            json.dumps(
                {
                    "model": "qwen3.5:latest",
                    "message": {"role": "assistant", "content": "Hi"},
                    "done": False,
                }
            )
        )
        self.assertEqual(response["candidates"][0]["content"]["parts"][0]["text"], "Hello")
        self.assertEqual(response["usageMetadata"]["totalTokenCount"], 11)
        self.assertTrue(stream.startswith("data: "))


if __name__ == "__main__":
    unittest.main()
