"""Contract tests for OpenAI Responses API compatibility."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.models import OpenAIResponsesRequest
from core.router.primary.responses import (
    _iter_chat_events,
    chat_to_responses_response,
    create_response,
    responses_to_chat_request,
)


class OpenAIResponsesTests(unittest.IsolatedAsyncioTestCase):
    def test_string_input_and_instructions_translate_to_chat_messages(self):
        request = OpenAIResponsesRequest(
            model="gemini-2.5-flash",
            instructions="Be concise.",
            input="Hello",
            max_output_tokens=100,
        )

        chat = responses_to_chat_request(request)

        self.assertEqual(chat.messages[0].role, "system")
        self.assertEqual(chat.messages[1].role, "user")
        self.assertEqual(chat.max_tokens, 100)

    def test_chat_completion_translates_to_response_output_and_usage(self):
        request = OpenAIResponsesRequest(model="gemini-2.5-flash", input="Hello")
        chat = {
            "id": "chatcmpl-123",
            "created": 100,
            "choices": [{"message": {"role": "assistant", "content": "Hi"}}],
            "usage": {
                "prompt_tokens": 4,
                "completion_tokens": 2,
                "total_tokens": 6,
            },
        }

        response = chat_to_responses_response(chat, request)

        self.assertEqual(response["object"], "response")
        self.assertEqual(response["status"], "completed")
        self.assertEqual(response["output"][0]["content"][0]["text"], "Hi")
        self.assertEqual(response["usage"]["input_tokens"], 4)
        self.assertEqual(response["usage"]["output_tokens"], 2)

    async def test_chat_sse_parser_handles_frames_split_across_chunks(self):
        async def chunks():
            yield b'data: {"choices":[{"delta":{"content":"Hel'
            yield b'lo"}}]}\n\ndata: [DONE]\n\n'

        events = [event async for event in _iter_chat_events(chunks())]

        self.assertEqual(events[0]["choices"][0]["delta"]["content"], "Hello")

    def test_non_function_tools_fail_explicitly(self):
        request = OpenAIResponsesRequest(
            model="gemini-2.5-flash",
            input="Search",
            tools=[{"type": "web_search"}],
        )

        with self.assertRaisesRegex(Exception, "Only function tools"):
            responses_to_chat_request(request)

    def test_function_call_history_translates_to_assistant_and_tool_messages(self):
        request = OpenAIResponsesRequest(
            model="gemini-2.5-flash",
            input=[
                {
                    "type": "function_call",
                    "call_id": "call_1",
                    "name": "lookup",
                    "arguments": '{"id":1}',
                },
                {
                    "type": "function_call_output",
                    "call_id": "call_1",
                    "output": "found",
                },
            ],
        )

        chat = responses_to_chat_request(request)

        self.assertEqual(chat.messages[0].role, "assistant")
        self.assertEqual(chat.messages[0].tool_calls[0].id, "call_1")
        self.assertEqual(chat.messages[1].role, "tool")

    async def test_store_true_is_rejected_instead_of_claiming_persistence(self):
        request = OpenAIResponsesRequest(
            model="gemini-2.5-flash",
            input="Hello",
            store=True,
        )

        with self.assertRaisesRegex(Exception, "Stored responses"):
            await create_response(request, token="test")


if __name__ == "__main__":
    unittest.main()
