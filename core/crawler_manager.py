import asyncio
from typing import Any, Dict, Optional
from playwright.async_api import BrowserContext

import config
from media_platform.douyin import DouYinCrawler
from .account_manager import Account
from tools import utils


class CrawlerInstance:
    def __init__(self, account: Account, login_manager=None):
        self.account = account
        self.crawler: Optional[DouYinCrawler] = None
        self.browser_context: Optional[BrowserContext] = None
        self.lock = asyncio.Lock()
        self.login_manager = login_manager

    async def initialize(self) -> bool:
        async with self.lock:
            try:
                self.crawler = DouYinCrawler(
                    login_manager=self.login_manager,
                    account=self.account.to_dict() if hasattr(self.account, 'to_dict') else self.account
                )
                return True
            except Exception as e:
                utils.logger.error(f"[CrawlerInstance] 初始化失败 account={self.account.account_id}: {e}")
                return False

    async def close(self) -> None:
        async with self.lock:
            if self.crawler:
                try:
                    await self.crawler.close()
                except Exception:
                    pass
                self.crawler = None


class MultiAccountCrawlerManager:
    def __init__(self, login_manager=None):
        self.instances: Dict[str, CrawlerInstance] = {}
        self._lock = asyncio.Lock()
        self.login_manager = login_manager

    async def get_or_create_instance(self, account: Account) -> CrawlerInstance:
        async with self._lock:
            if account.account_id not in self.instances:
                instance = CrawlerInstance(account, login_manager=self.login_manager)
                await instance.initialize()
                self.instances[account.account_id] = instance
            return self.instances[account.account_id]

    async def close_instance(self, account_id: str) -> None:
        async with self._lock:
            if account_id in self.instances:
                await self.instances[account_id].close()
                del self.instances[account_id]

    async def close_all(self) -> None:
        for instance in list(self.instances.values()):
            await instance.close()
        self.instances.clear()
