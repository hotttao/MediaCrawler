import asyncio
from typing import Any, Dict, Optional, Callable

import config
from tools import utils
from .account_manager import AccountManager, Account
from .crawler_manager import MultiAccountCrawlerManager, CrawlerInstance
from .login_manager import LoginManager
from .notifier.manager import NotificationManager


class TaskDispatcher:
    def __init__(
        self,
        account_manager: AccountManager,
        notifier_manager: NotificationManager,
    ):
        self.account_manager = account_manager
        self.notifier_manager = notifier_manager
        self.login_manager = LoginManager(notifier_manager=self.notifier_manager)
        self.crawler_manager = MultiAccountCrawlerManager(
            login_manager=self.login_manager
        )
        self.running = False
        self.stats = {"success": 0, "failed": 0}
        self._tasks: asyncio.Queue = asyncio.Queue()

    async def start(self) -> None:
        self.running = True
        stats = await self.account_manager.get_account_stats()
        await self.notifier_manager.notify_crawler_start(stats["total"])
        utils.logger.info(f"[TaskDispatcher] 爬虫启动，共 {stats['total']} 个账户")

    async def stop(self) -> None:
        self.running = False
        await self.crawler_manager.close_all()
        await self.notifier_manager.notify_crawler_stop(self.stats)
        utils.logger.info(
            f"[TaskDispatcher] 爬虫停止，成功: {self.stats['success']}, 失败: {self.stats['failed']}"
        )

    async def submit_task(self, task_func: Callable, *args, **kwargs) -> bool:
        await self._tasks.put((task_func, args, kwargs))

    async def _execute_with_account(self, task_func: Callable, args, kwargs) -> bool:
        account = await self.account_manager.get_available_account()
        if not account:
            utils.logger.warning("[TaskDispatcher] 没有可用的账户")
            await self.notifier_manager.notify_error("没有可用的账户")
            return False

        instance: Optional[CrawlerInstance] = None
        try:
            account.mark_used()
            instance = await self.crawler_manager.get_or_create_instance(account)

            if not instance.crawler:
                utils.logger.error(
                    f"[TaskDispatcher] Crawler实例未初始化 account={account.account_id}"
                )
                return False

            utils.logger.info(
                f"[TaskDispatcher] 使用账户 {account.account_id} 执行任务"
            )
            await task_func(instance.crawler, *args, **kwargs)
            self.stats["success"] += 1
            return True

        except Exception as e:
            utils.logger.error(f"[TaskDispatcher] 任务执行失败: {e}")
            account.record_error()
            if account.should_ban():
                await self.account_manager.ban_account(account, str(e))
                await self.notifier_manager.notify_account_banned(
                    account.account_id, str(e)
                )
            self.stats["failed"] += 1
            return False

        finally:
            if instance:
                await self.crawler_manager.close_instance(account.account_id)
            await self.account_manager.release_account(account)

    async def run_creator_crawl(self, crawler: Any, user_ids: list) -> None:
        from config.dy_config import get_creator_id_list

        if not user_ids:
            user_ids = await get_creator_id_list()

        for user_id in user_ids:
            try:
                await crawler.dy_client.get_user_info(user_id)
                await asyncio.sleep(config.CRAWLER_MAX_SLEEP_SEC)
            except Exception as e:
                utils.logger.error(f"[TaskDispatcher] 抓取用户 {user_id} 失败: {e}")

    async def run_forever(
        self, task_func: Callable, user_ids: Optional[list] = None
    ) -> None:
        await self.start()
        try:
            while self.running:
                success = await self._execute_with_account(
                    self.run_creator_crawl, (), {"user_ids": user_ids}
                )
                if not success:
                    await asyncio.sleep(5)
        finally:
            await self.stop()
