from typing import Any, Dict, List
from .base import BaseNotifier
from .providers import FeishuNotifier, WechatNotifier


class NotificationManager:
    def __init__(self):
        self.notifiers: List[BaseNotifier] = []
        self._load_config()

    def _load_config(self) -> None:
        from config.notification_config import NOTIFICATION_CHANNELS

        for channel_name, channel_config in NOTIFICATION_CHANNELS.items():
            if not channel_config.get("enabled", False):
                continue

            if channel_name == "feishu":
                self.notifiers.append(FeishuNotifier(channel_config))
            elif channel_name == "wechat":
                self.notifiers.append(WechatNotifier(channel_config))

    async def start(self) -> None:
        for notifier in self.notifiers:
            await notifier.startup()

    async def shutdown(self) -> None:
        for notifier in self.notifiers:
            await notifier.shutdown()

    async def send(self, title: str, content: str, **kwargs) -> None:
        for notifier in self.notifiers:
            try:
                await notifier.send(title, content, **kwargs)
            except Exception:
                pass

    async def send_markdown(self, title: str, content: str, **kwargs) -> None:
        for notifier in self.notifiers:
            try:
                await notifier.send_markdown(title, content, **kwargs)
            except Exception:
                pass

    async def send_image(self, title: str, image_path: str, **kwargs) -> None:
        for notifier in self.notifiers:
            try:
                await notifier.send_image(title, image_path, **kwargs)
            except Exception:
                pass

    async def notify_crawler_start(self, account_count: int) -> None:
        await self.send("🚀 爬虫启动", f"MediaCrawler 启动，共 {account_count} 个账户")

    async def notify_crawler_stop(self, stats: Dict[str, int]) -> None:
        await self.send(
            "🛑 爬虫停止",
            f"成功: {stats.get('success', 0)}, 失败: {stats.get('failed', 0)}",
        )

    async def notify_account_banned(self, account_id: str, reason: str) -> None:
        await self.send("⚠️ 账户被封禁", f"账户 {account_id} 被封禁\n原因: {reason}")

    async def notify_error(self, error_msg: str) -> None:
        await self.send("❌ 爬虫异常", error_msg)

    async def notify_login_required(
        self, account_id: str, nickname: str, phone: str = "", qrcode_path: str = ""
    ) -> None:
        content = f"📱 账号信息\n"
        content += f"- 账户ID: {account_id}\n"
        content += f"- 昵称: {nickname}\n"
        if phone:
            content += f"- 手机: {phone}\n"
        content += f"\n请扫码登录！"

        await self.send("🔐 需要登录", content)
        if qrcode_path:
            await self.send_image("📱 请扫码登录抖音", qrcode_path)

    async def notify_qrcode_timeout(
        self, qrcode_path: str, account_id: str, nickname: str = "", phone: str = ""
    ) -> None:
        content = f"⏰ 二维码扫码超时\n"
        content += f"- 账户: {nickname or account_id}\n"
        if phone:
            content += f"- 手机: {phone}\n"
        content += f"\n请扫码登录！"

        await self.send("⏰ 二维码扫码超时", content)
        await self.send_image("📱 请扫码登录抖音", qrcode_path)

    async def notify_qrcode_expired(
        self, account_id: str, nickname: str = "", phone: str = ""
    ) -> None:
        content = f"🚫 二维码已过期\n"
        content += f"- 账户: {nickname or account_id}\n"
        if phone:
            content += f"- 手机: {phone}\n"
        content += f"\n登录超时（5分钟），程序即将停止"

        await self.send("🚫 二维码已过期", content)
