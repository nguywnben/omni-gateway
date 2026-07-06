"""Internal implementation detail."""
import time
from typing import Any, Dict, List




def is_health_check_request(request_data: dict, format: str = "openai") -> bool:
    """Internal implementation detail."""
    if format == "openai":

        messages = request_data.get("messages", [])
        if len(messages) == 1:
            msg = messages[0]
            if msg.get("role") == "user" and msg.get("content") == "Hi":
                return True

    elif format == "gemini":

        contents = request_data.get("contents", [])
        if len(contents) == 1:
            content = contents[0]
            if (content.get("role") == "user" and
                content.get("parts", [{}])[0].get("text") == "Hi"):
                return True

    elif format == "anthropic":

        messages = request_data.get("messages", [])
        if (len(messages) == 1
            and messages[0].get("role") == "user"
            and messages[0].get("content") == "Hi"):
            return True

    return False


def is_health_check_message(messages: List[Dict[str, Any]]) -> bool:
    """Internal implementation detail."""
    return (
        len(messages) == 1
        and messages[0].get("role") == "user"
        and messages[0].get("content") == "Hi"
    )




def create_health_check_response(format: str = "openai", **kwargs) -> dict:
    """Internal implementation detail."""
    if format == "openai":

        return {
            "id": "healthcheck",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "healthcheck",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "API is working"
                },
                "finish_reason": "stop"
            }]
        }

    elif format == "gemini":

        return {
            "candidates": [{
                "content": {
                    "parts": [{"text": "Router is working"}],
                    "role": "model"
                },
                "finishReason": "STOP",
                "index": 0,
            }]
        }

    elif format == "anthropic":

        model = kwargs.get("model", "claude-unknown")
        message_id = kwargs.get("message_id", "msg_healthcheck")
        return {
            "id": message_id,
            "type": "message",
            "role": "assistant",
            "model": str(model),
            "content": [{"type": "text", "text": "Anthropic Messages route is working"}],
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {"input_tokens": 0, "output_tokens": 0},
        }


    return {}
