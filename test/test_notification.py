"""
飞书通知测试脚本
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.notifier.manager import NotificationManager


async def test_feishu():
    notifier_manager = NotificationManager()
    await notifier_manager.start()

    await notifier_manager.send("🔔 测试通知", "这是一条测试消息")
    await notifier_manager.send_image("🖼️ 测试图片", "qrcode_images/test_notification.png")

    await notifier_manager.shutdown()
    print("测试完成")


if __name__ == "__main__":
    asyncio.run(test_feishu())
