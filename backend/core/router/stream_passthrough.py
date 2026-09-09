from typing import Any, AsyncIterator

from core.router.protocol_errors import (
    ProtocolName,
    adapt_protocol_error_response,
)
from fastapi import Response
from fastapi.responses import StreamingResponse


async def close_async_iterator(iterator: AsyncIterator[Any]) -> None:
    """Close an async iterator when it exposes the standard ``aclose`` hook."""
    close = getattr(iterator, "aclose", None)
    if close is not None:
        await close()


class ManagedStreamingResponse(StreamingResponse):
    """Streaming response that closes its body after completion or disconnect."""

    async def stream_response(self, send) -> None:
        try:
            await super().stream_response(send)
        finally:
            await close_async_iterator(self.body_iterator)


async def prepend_async_item(first_item: Any, iterator: AsyncIterator[Any]):
    """Yield a prefetched item before continuing the original iterator."""
    try:
        yield first_item
        async for item in iterator:
            yield item
    finally:
        await close_async_iterator(iterator)


async def read_first_async_item(iterator: AsyncIterator[Any]) -> Any:
    """Python 3.9-compatible async equivalent of built-in anext()."""
    return await iterator.__anext__()


async def build_streaming_response_or_error(
    iterator: AsyncIterator[Any],
    media_type: str = "text/event-stream",
    error_protocol: ProtocolName | None = None,
):
    """
    Prefetch the first async item so router code can return an upstream error
    response directly before FastAPI commits a 200 streaming response.
    """
    try:
        first_item = await read_first_async_item(iterator)
    except StopAsyncIteration:
        return Response(status_code=204)

    if isinstance(first_item, Response):
        await close_async_iterator(iterator)
        if error_protocol:
            return adapt_protocol_error_response(first_item, error_protocol)
        return first_item

    return ManagedStreamingResponse(
        prepend_async_item(first_item, iterator),
        media_type=media_type,
    )
