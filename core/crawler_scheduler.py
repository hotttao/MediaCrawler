"""
爬虫调度器
统一管理多账户轮询抓取策略
"""

import asyncio
from typing import List, Optional

import config
from core.account_manager import AccountManager, Account
from core.account_browser_middleware import AccountBrowserMiddleware
from core.login_manager import LoginManager
from core.notifier.manager import NotificationManager
from media_platform.douyin import DouYinCrawler
from tools import utils


class CrawlerScheduler:
    """
    爬虫调度器
    负责：账户管理、创作者分配、轮询策略、爬虫执行
    """

    def __init__(self, notifier_manager: Optional[NotificationManager] = None):
        self.notifier_manager = notifier_manager or NotificationManager()
        self.account_manager = AccountManager()
        self.login_manager = LoginManager(notifier_manager=self.notifier_manager)
        self.browser_middleware = AccountBrowserMiddleware(
            login_manager=self.login_manager
        )
        self.rounds = 1
        self._initialized = False

    async def initialize(self) -> None:
        """初始化调度器"""
        if self._initialized:
            return
        await self.notifier_manager.start()
        await self.account_manager.init_accounts()
        self._initialized = True

    async def shutdown(self) -> None:
        """关闭调度器"""
        await self.browser_middleware.close_all()
        await self.notifier_manager.shutdown()
        self._initialized = False

    def distribute_creators(self, creator_ids: List[str]) -> List[List[str]]:
        """将创作者均匀分配给各账户"""
        return utils.distribute_items_to_groups(
            creator_ids, len(self.available_accounts)
        )

    async def get_creator_ids(self) -> List[str]:
        """获取创作者ID列表"""
        from config.dy_config import get_creator_id_list

        return await get_creator_id_list()

    async def run_single_account(
        self,
        account: Account,
        creator_ids: List[str],
    ) -> bool:
        """
        运行单个账户的爬虫

        Returns:
            bool: 是否成功
        """
        utils.logger.info(
            f"[Scheduler] 启动爬虫 account={account.nickname} creator_count={len(creator_ids)}"
        )
        crawler_error = None
        try:
            browser_context, context_page = (
                await self.browser_middleware.launch_browser_for_account(
                    account.to_dict()
                )
            )
            crawler = DouYinCrawler(
                login_manager=self.login_manager,
                account=account.to_dict(),
                external_browser_context=browser_context,
                external_context_page=context_page,
                creator_ids=creator_ids,
            )
            await crawler.start()
            account.mark_used()
            return True
        except Exception as e:
            crawler_error = e
            import traceback

            utils.logger.error(
                f"[Scheduler] 爬虫执行失败 account={account.nickname}: {e}\n{traceback.format_exc()}"
            )
            account.record_error()
            return False
        finally:
            await self.browser_middleware.close_current_browser()

    async def run(self, creator_ids: List[str], rounds: int = 1) -> dict:
        """
        运行调度器

        Args:
            creator_ids: 创作者ID列表
            rounds: 轮询次数

        Returns:
            dict: 执行结果 {"success": int, "failed": int}
        """
        await self.initialize()

        stats = await self.account_manager.get_account_stats()
        await self.notifier_manager.notify_crawler_start(stats["total"])
        utils.logger.info(
            f"[Scheduler] 爬虫启动，账户数: {stats['total']}, 创作者数: {len(creator_ids)}, 轮询次数: {rounds}"
        )

        self.available_accounts = await self.account_manager.get_available_accounts()
        if not self.available_accounts:
            utils.logger.warning("[Scheduler] 没有可用的账户")
            return {"success": 0, "failed": 0}

        distributed_creators = self.distribute_creators(creator_ids)

        results = {"success": 0, "failed": 0}

        for round_num in range(rounds):
            utils.logger.info(f"[Scheduler] === 第 {round_num + 1} 轮抓取 ===")

            for i, account in enumerate(self.available_accounts):
                creator_ids = distributed_creators[i]
                if not creator_ids:
                    utils.logger.info(
                        f"[Scheduler] 账户 {account.nickname} 无分配创作者，跳过"
                    )
                    continue

                try:
                    success = await self.run_single_account(account, creator_ids)
                    if success:
                        results["success"] += 1
                    else:
                        results["failed"] += 1
                except KeyboardInterrupt:
                    utils.logger.info("[Scheduler] 用户中断")
                    await self.shutdown()
                    return results
                except Exception as e:
                    utils.logger.error(
                        f"[Scheduler] 账户 {account.nickname} 执行异常: {e}"
                    )
                    results["failed"] += 1

        await self.shutdown()
        await self.notifier_manager.notify_crawler_stop(results)
        utils.logger.info(f"[Scheduler] 所有任务完成 {results}")
        return results


async def crawl_only(creator_ids: List[str], rounds: int = 1) -> dict:
    """
    仅爬取，不包含日增计算

    Args:
        creator_ids: 创作者ID列表
        rounds: 轮询次数

    Returns:
        dict: 执行结果
    """
    scheduler = CrawlerScheduler()
    try:
        return await scheduler.run(creator_ids, rounds)
    finally:
        await scheduler.shutdown()


async def crawl_and_calc_incr(
    target_date: str, days: int = 15, rounds: int = 1
) -> dict:
    """
    爬取 + 日增计算

    Args:
        target_date: 目标日期 YYYY-MM-DD
        days: 往前推天数
        rounds: 轮询次数

    Returns:
        dict: 执行结果
    """
    from command.cal_day_incr import cal_day_incr

    scheduler = CrawlerScheduler()
    try:
        await scheduler.initialize()

        creator_ids = await scheduler.get_creator_ids()
        utils.logger.info(f"[Scheduler] 共有 {len(creator_ids)} 个创作者待抓取")

        crawl_results = await scheduler.run(creator_ids, rounds)

        utils.logger.info(
            f"[Scheduler] 爬取完成，开始计算日增数据 ({target_date}, {days}天)..."
        )
        await scheduler.notifier_manager.send(
            "📊 开始计算日增", f"目标日期: {target_date}"
        )

        try:
            result1, result2 = await cal_day_incr(target_date, days)
            await scheduler.notifier_manager.send(
                "✅ 日增计算完成",
                f"日期: {target_date}\n计算了 {len(result1)} 条增量数据",
            )
            crawl_results["day_incr"] = {
                "updated": len(result1),
                "inserted": len(result2),
            }
        except Exception as e:
            utils.logger.error(f"[Scheduler] 日增计算失败: {e}")
            await scheduler.notifier_manager.notify_error(f"日增计算失败: {e}")
            crawl_results["day_incr"] = {"error": str(e)}

        return crawl_results
    finally:
        await scheduler.shutdown()
