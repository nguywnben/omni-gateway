"""
é€ç”¨ç„HTTPå®¢æˆ·ç«¯æ¨¡å—
ä¸ºæ‰€æœ‰éœ€è¦ä½¿ç”¨httpxç„æ¨¡å—æä¾›ç»Ÿä¸€ç„å®¢æˆ·ç«¯é…ç½®å’Œæ–¹æ³•
ä¿æŒé€ç”¨æ€§ï¼Œä¸ä¸ç‰¹å®ä¸å¡é€»è¾‘è€¦åˆ
"""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, Optional

import httpx

from config import get_proxy_config
from log import log


class HttpxClientManager:
    """é€ç”¨HTTPå®¢æˆ·ç«¯ç®¡ç†å™¨"""

    async def get_client_kwargs(self, timeout: float = 30.0, **kwargs) -> Dict[str, Any]:
        """è·å–httpxå®¢æˆ·ç«¯ç„é€ç”¨é…ç½®å‚æ•°"""
        client_kwargs = {"timeout": timeout, **kwargs}

        # å¨æ€è¯»å–ä»£ç†é…ç½®ï¼Œæ”¯æŒçƒ­æ›´æ–°
        current_proxy_config = await get_proxy_config()
        if current_proxy_config:
            client_kwargs["proxy"] = current_proxy_config

        return client_kwargs

    @asynccontextmanager
    async def get_client(
        self, timeout: float = 30.0, **kwargs
    ) -> AsyncGenerator[httpx.AsyncClient, None]:
        """è·å–é…ç½®å¥½ç„å¼‚æ­¥HTTPå®¢æˆ·ç«¯"""
        client_kwargs = await self.get_client_kwargs(timeout=timeout, **kwargs)

        async with httpx.AsyncClient(**client_kwargs) as client:
            yield client

    @asynccontextmanager
    async def get_streaming_client(
        self, timeout: float = None, **kwargs
    ) -> AsyncGenerator[httpx.AsyncClient, None]:
        """è·å–ç”¨äºæµå¼è¯·æ±‚ç„HTTPå®¢æˆ·ç«¯ï¼ˆæ— è¶…æ—¶é™åˆ¶ï¼‰"""
        client_kwargs = await self.get_client_kwargs(timeout=timeout, **kwargs)

        # åˆ›å»ºç‹¬ç«‹ç„å®¢æˆ·ç«¯å®ä¾‹ç”¨äºæµå¼å¤„ç†
        client = httpx.AsyncClient(**client_kwargs)
        try:
            yield client
        finally:
            # ç¡®ä¿æ— è®ºå‘ç”Ÿä»€ä¹ˆéƒ½å…³é—­å®¢æˆ·ç«¯
            try:
                await client.aclose()
            except Exception as e:
                log.warning(f"Error closing streaming client: {e}")


# å…¨å±€HTTPå®¢æˆ·ç«¯ç®¡ç†å™¨å®ä¾‹
http_client = HttpxClientManager()


# é€ç”¨ç„å¼‚æ­¥æ–¹æ³•
async def get_async(
    url: str, headers: Optional[Dict[str, str]] = None, timeout: float = 30.0, **kwargs
) -> httpx.Response:
    """é€ç”¨å¼‚æ­¥GETè¯·æ±‚"""
    async with http_client.get_client(timeout=timeout, **kwargs) as client:
        return await client.get(url, headers=headers)


async def post_async(
    url: str,
    data: Any = None,
    json: Any = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: float = 900.0,
    **kwargs,
) -> httpx.Response:
    """é€ç”¨å¼‚æ­¥POSTè¯·æ±‚"""
    async with http_client.get_client(timeout=timeout, **kwargs) as client:
        return await client.post(url, data=data, json=json, headers=headers)


# è°ƒè¯•ç”¨ï¼è®¾ä¸º True æ—¶æ‰€æœ‰æµå¼è¯·æ±‚éƒ½è¿”å› 429
_MOCK_STREAM_429 = False

async def stream_post_async(
    url: str,
    body: Dict[str, Any],
    native: bool = False,
    headers: Optional[Dict[str, str]] = None,
    **kwargs,
):
    """æµå¼å¼‚æ­¥POSTè¯·æ±‚"""
    if _MOCK_STREAM_429:
        from fastapi import Response
        import json
        log.warning(f"[MOCK] stream_post_async: returning simulated 429 error")
        yield Response(
            content=json.dumps({"error": {"code": 429, "message": "mock rate limit", "status": "RESOURCE_EXHAUSTED"}}),
            status_code=429,
        )
        return

    async with http_client.get_streaming_client(**kwargs) as client:
        async with client.stream("POST", url, json=body, headers=headers) as r:
            # é”™è¯¯ç›´æ¥è¿”å›
            if r.status_code != 200:
                from fastapi import Response
                yield Response(await r.aread(), r.status_code, dict(r.headers))
                return

            # å¦‚æœnative=Trueï¼Œç›´æ¥è¿”å›bytesæµ
            if native:
                async for chunk in r.aiter_bytes():
                    yield chunk
            else:
                # é€è¿‡aiter_linesè½¬åŒ–æˆstræµè¿”å›
                async for line in r.aiter_lines():
                    yield line
