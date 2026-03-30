import httpx
import base64
from typing import Any, Dict

from ..base import BaseNotifier


class WechatNotifier(BaseNotifier):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.webhook_url = config.get("webhook_url", "")

    async def send(self, title: str, content: str, **kwargs) -> bool:
        if not self.enabled:
            return False

        message = {
            "msgtype": "text",
            "text": {
                "content": f"{title}\n{content}"
            }
        }
        return await self._send_request(message)

    async def send_markdown(self, title: str, content: str, **kwargs) -> bool:
        if not self.enabled:
            return False

        message = {
            "msgtype": "markdown",
            "markdown": {
                "content": f"**{title}**\n{content}"
            }
        }
        return await self._send_request(message)

    async def send_image(self, title: str, image_path: str, **kwargs) -> bool:
        if not self.enabled:
            return False

        try:
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()
        except Exception:
            return False

        message = {
            "msgtype": "image",
            "image": {
                "base64": image_data,
                "md5": ""
            }
        }
        return await self._send_request(message)

    async def _send_request(self, message: Dict[str, Any]) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(self.webhook_url, json=message)
                if resp.status_code == 200:
                    result = resp.json()
                    return result.get("errcode", 0) == 0
                return False
        except Exception:
            return False