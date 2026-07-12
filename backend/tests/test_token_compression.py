"""Behavior tests for token-aware conversation compression."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.token_compression import CompressionSettings, compress_gemini_request
from core.token_estimator import estimate_input_tokens


def text_content(role: str, text: str):
    return {"role": role, "parts": [{"text": text}]}


class TokenCompressionTests(unittest.TestCase):
    def test_request_below_threshold_is_preserved(self):
        payload = {
            "systemInstruction": {"parts": [{"text": "Keep this instruction."}]},
            "contents": [text_content("user", "short request")],
        }
        settings = CompressionSettings(
            enabled=True,
            threshold_tokens=1000,
            target_tokens=800,
            min_recent_turns=2,
        )

        result = compress_gemini_request(payload, settings)

        self.assertFalse(result.applied)
        self.assertEqual(result.request, payload)
        self.assertEqual(result.estimated_tokens_saved, 0)

    def test_oversized_history_keeps_system_instruction_and_recent_turns(self):
        contents = []
        for index in range(5):
            contents.append(text_content("user", f"user-{index}-" + "u" * 160))
            contents.append(text_content("model", f"model-{index}-" + "m" * 160))
        payload = {
            "systemInstruction": {"parts": [{"text": "Never remove this."}]},
            "contents": contents,
            "tools": [{"functionDeclarations": [{"name": "lookup"}]}],
        }
        settings = CompressionSettings(
            enabled=True,
            threshold_tokens=300,
            target_tokens=220,
            min_recent_turns=2,
        )

        result = compress_gemini_request(payload, settings)

        self.assertTrue(result.applied)
        self.assertEqual(result.request["systemInstruction"], payload["systemInstruction"])
        self.assertEqual(result.request["tools"], payload["tools"])
        self.assertEqual(result.request["contents"], contents[-4:])
        self.assertEqual(result.removed_contents, 6)
        self.assertGreater(result.estimated_tokens_saved, 0)

    def test_compression_never_starts_with_an_orphaned_tool_result(self):
        contents = [
            text_content("user", "old request " + "x" * 300),
            {
                "role": "model",
                "parts": [{"functionCall": {"name": "lookup", "args": {}}}],
            },
            {
                "role": "user",
                "parts": [{"functionResponse": {"name": "lookup", "response": {}}}],
            },
            text_content("model", "tool response " + "y" * 200),
            text_content("user", "latest request " + "z" * 120),
            text_content("model", "latest response " + "q" * 120),
        ]
        payload = {"contents": contents}
        settings = CompressionSettings(
            enabled=True,
            threshold_tokens=180,
            target_tokens=120,
            min_recent_turns=1,
        )

        result = compress_gemini_request(payload, settings)

        first_part = result.request["contents"][0]["parts"][0]
        self.assertNotIn("functionResponse", first_part)
        self.assertEqual(result.request["contents"], contents[-2:])

    def test_estimator_accounts_for_structured_payload_overhead(self):
        plain = {"contents": [text_content("user", "a" * 40)]}
        structured = {
            **plain,
            "tools": [
                {
                    "functionDeclarations": [
                        {
                            "name": "read_file",
                            "description": "Read a file from the workspace.",
                            "parameters": {"type": "object", "properties": {}},
                        }
                    ]
                }
            ],
        }

        self.assertGreater(estimate_input_tokens(structured), estimate_input_tokens(plain))


if __name__ == "__main__":
    unittest.main()
