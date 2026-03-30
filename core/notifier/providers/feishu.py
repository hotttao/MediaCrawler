import json
import httpx
from typing import Any, Dict

from ..base import BaseNotifier


class FeishuNotifier(BaseNotifier):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.app_id = config.get("app_id", "")
        self.app_secret = config.get("app_secret", "")
        self.webhook_url = config.get("webhook_url", "")
        self.receive_id = config.get("receive_id", "")
        self._access_token: str = ""
        self._token_expires_at: float = 0

    async def _get_access_token(self) -> str:
        import time

        if self._access_token and time.time() < self._token_expires_at - 60:
            return self._access_token

        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = {"app_id": self.app_id, "app_secret": self.app_secret}

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                result = resp.json()
                if result.get("code") == 0:
                    self._access_token = result.get("tenant_access_token", "")
                    expire = result.get("expire", 7200)
                    self._token_expires_at = time.time() + expire

        return self._access_token

    async def send(self, title: str, content: str, **kwargs) -> bool:
        if not self.enabled:
            return False

        from datetime import datetime

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = {
            "msg_type": "text",
            "content": json.dumps({"text": f"{title}\n{content}\n\n⏰ {timestamp}"}),
        }
        return await self._send_request(message)

    async def send_markdown(self, title: str, content: str, **kwargs) -> bool:
        if not self.enabled:
            return False

        from datetime import datetime

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content_with_time = f"{content}\n\n⏰ {timestamp}"
        message = {
            "msg_type": "post",
            "content": json.dumps(
                {
                    "post": {
                        "zh_cn": {
                            "title": title,
                            "content": [[{"tag": "text", "text": content_with_time}]],
                        }
                    }
                }
            ),
        }
        return await self._send_request(message)

    async def send_image(self, title: str, image_path: str, **kwargs) -> bool:
        if not self.enabled:
            return False

        image_key = await self._upload_image(image_path)
        if not image_key:
            return False

        message = {"msg_type": "image", "content": json.dumps({"image_key": image_key})}
        return await self._send_request(message)

    async def _upload_image(self, image_path: str) -> str:
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()
        except Exception:
            return ""

        url = "https://open.feishu.cn/open-apis/im/v1/images"
        access_token = await self._get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}

        async with httpx.AsyncClient(timeout=30.0) as client:
            files = {"image": (image_path, image_data, "image/png")}
            data = {"image_type": "message"}
            resp = await client.post(url, headers=headers, data=data, files=files)
            if resp.status_code == 200:
                result = resp.json()
                if result.get("code") == 0:
                    return result.get("data", {}).get("image_key", "")
        return ""

    async def _send_request(self, message: Dict[str, Any]) -> bool:
        try:
            access_token = await self._get_access_token()
            if not access_token:
                return False

            receive_id_type = self.config.get("receive_id_type", "chat_id")
            url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type={receive_id_type}"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }
            payload = {
                "receive_id": self.receive_id,
                "msg_type": message.get("msg_type", "text"),
                "content": message.get("content", {}),
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code == 200:
                    result = resp.json()
                    return result.get("code", -1) == 0
                return False
        except Exception:
            return False
