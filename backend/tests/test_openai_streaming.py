"""Regression tests for OpenAI-compatible streaming responses."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.converter.openai_to_gemini import convert_gemini_to_openai_stream


def convert_chunk(candidate: dict) -> dict:
    source = {
        "response": {
            "candidates": [candidate],
        }
    }
    converted = convert_gemini_to_openai_stream(
        f"data: {json.dumps(source)}",
        "gemini-2.5-flash",
        "response-id",
    )
    if converted is None:
        raise AssertionError("Expected an OpenAI stream chunk.")
    return json.loads(converted.removeprefix("data: ").strip())


class OpenAIStreamingTests(unittest.TestCase):
    def test_intermediate_chunk_does_not_end_the_stream(self):
        chunk = convert_chunk(
            {
                "index": 0,
                "content": {
                    "role": "model",
                    "parts": [{"text": "I am"}],
                },
            }
        )

        choice = chunk["choices"][0]
        self.assertEqual(choice["delta"]["content"], "I am")
        self.assertIsNone(choice["finish_reason"])

    def test_stop_reason_is_only_emitted_by_the_final_chunk(self):
        chunk = convert_chunk(
            {
                "index": 0,
                "content": {
                    "role": "model",
                    "parts": [{"text": " complete."}],
                },
                "finishReason": "STOP",
            }
        )

        self.assertEqual(chunk["choices"][0]["finish_reason"], "stop")

    def test_token_limit_maps_to_openai_length_reason(self):
        chunk = convert_chunk(
            {
                "index": 0,
                "content": {"role": "model", "parts": []},
                "finishReason": "MAX_TOKENS",
            }
        )

        self.assertEqual(chunk["choices"][0]["finish_reason"], "length")


if __name__ == "__main__":
    unittest.main()
