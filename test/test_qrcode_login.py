"""
二维码登录测试脚本
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.login_manager import LoginManager
from core.notifier.manager import NotificationManager
from media_platform.douyin import DouYinCrawler
import config


async def test_qrcode_login():
    print("[Test] 初始化通知管理器...")
    notifier_manager = NotificationManager()
    await notifier_manager.start()

    print("[Test] 初始化登录管理器...")
    login_manager = LoginManager(notifier_manager=notifier_manager)

    test_account = {
        "account_id": "account_1",
        "nickname": "橙子Mama",
        "phone": "19156537759",
        "cookies": "",
    }

    print(f"[Test] 启动抖音爬虫 (账户: {test_account['nickname']})...")
    config.LOGIN_TYPE = "qrcode"
    config.PLATFORM = "dy"

    crawler = DouYinCrawler(login_manager=login_manager, account=test_account)
    try:
        await crawler.start()
    except KeyboardInterrupt:
        print("[Test] 用户中断")
    finally:
        await notifier_manager.shutdown()


if __name__ == "__main__":
    asyncio.run(test_qrcode_login())
