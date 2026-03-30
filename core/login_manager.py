import asyncio
import functools
import os
import time
from io import BytesIO
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw

import config
from core.notifier.manager import NotificationManager
from tools import utils


QRCODE_LOCAL_WAIT_SEC = 30
QRCODE_TOTAL_TIMEOUT_SEC = 300


class LoginManager:
    def __init__(self, notifier_manager: Optional[NotificationManager] = None):
        self.notifier_manager = notifier_manager
        self.qrcode_save_dir = Path("qrcode_images")
        self.qrcode_save_dir.mkdir(exist_ok=True)

    async def wait_for_qrcode_scan(
        self,
        context_page,
        browser_context,
        account_id: str,
        base64_qrcode_img: str,
        nickname: str = "",
        phone: str = "",
    ) -> bool:
        qrcode_path = await self._save_qrcode_image(base64_qrcode_img, account_id)
        utils.logger.info(f"[LoginManager] QR code saved to {qrcode_path}")

        utils.show_qrcode(base64_qrcode_img)

        if self.notifier_manager and (nickname or phone):
            await self.notifier_manager.notify_login_required(
                account_id=account_id,
                nickname=nickname,
                phone=phone,
                qrcode_path=qrcode_path,
            )

        start_time = time.time()
        local_wait_done = False

        while True:
            elapsed = time.time() - start_time

            if not local_wait_done and elapsed >= QRCODE_LOCAL_WAIT_SEC:
                local_wait_done = True
                utils.logger.info(
                    f"[LoginManager] Local wait expired, sending QR code via notification"
                )
                if self.notifier_manager:
                    await self.notifier_manager.notify_qrcode_timeout(
                        qrcode_path=qrcode_path,
                        account_id=account_id,
                        nickname=nickname,
                        phone=phone,
                    )

            if elapsed >= QRCODE_TOTAL_TIMEOUT_SEC:
                utils.logger.error(
                    f"[LoginManager] QR code timeout after {QRCODE_TOTAL_TIMEOUT_SEC}s"
                )
                if self.notifier_manager:
                    await self.notifier_manager.notify_qrcode_expired(
                        account_id=account_id,
                        nickname=nickname,
                        phone=phone,
                    )
                return False

            login_success = await self._check_login_status(
                context_page, browser_context
            )
            if login_success:
                utils.logger.info(
                    f"[LoginManager] QR code scanned and login successful"
                )
                return True

            await asyncio.sleep(1)

    async def _save_qrcode_image(self, base64_qrcode: str, account_id: str) -> str:
        import base64

        if "," in base64_qrcode:
            base64_qrcode = base64_qrcode.split(",")[1]
        qrcode_data = base64.b64decode(base64_qrcode)
        image = Image.open(BytesIO(qrcode_data))

        width, height = image.size
        new_image = Image.new("RGB", (width + 20, height + 20), color=(255, 255, 255))
        new_image.paste(image, (10, 10))
        draw = ImageDraw.Draw(new_image)
        draw.rectangle((0, 0, width + 19, height + 19), outline=(0, 0, 0), width=1)

        file_path = self.qrcode_save_dir / f"qrcode_{account_id}_{int(time.time())}.png"
        new_image.save(file_path)
        return str(file_path)

    async def _check_login_status(self, context_page, browser_context) -> bool:
        try:
            cookies = await browser_context.cookies()
            cookie_names = [c.get("name") for c in cookies]
            utils.logger.debug(f"[LoginManager] cookie_names={cookie_names}")
            if "sessionid" in cookie_names or "sid_guard" in cookie_names:
                utils.logger.info(
                    "[LoginManager] 检测到登录 cookie (sessionid/sid_guard)，登录成功"
                )
                return True
        except Exception:
            pass

        try:
            local_storage = await context_page.evaluate("() => window.localStorage")
            has_user_login = local_storage.get("HasUserLogin", "")
            utils.logger.debug(f"[LoginManager] HasUserLogin={has_user_login}")
            if has_user_login == "1":
                return True
        except Exception:
            pass

        try:
            current_url = context_page.url
            utils.logger.debug(f"[LoginManager] current_url={current_url}")
            if "douyin.com" in current_url and "/user/" in current_url:
                return True
        except Exception:
            pass

        try:
            login_panel = await context_page.query_selector("#login-panel-new")
            if login_panel is None:
                utils.logger.info("[LoginManager] 登录面板已消失，可能已登录")
                return True
        except Exception:
            pass

        for page in browser_context.pages:
            if page == context_page:
                continue
            try:
                local_storage = await page.evaluate("() => window.localStorage")
                if local_storage.get("HasUserLogin", "") == "1":
                    return True
            except Exception:
                pass

            try:
                current_url = page.url
                if "douyin.com" in current_url and "/user/" in current_url:
                    return True
            except Exception:
                pass

        return False
