"""
账户浏览器中间件
负责管理每个账户独立的浏览器会话，实现账户隔离
"""

import asyncio
import os
from typing import Dict, Optional, List, Callable, Awaitable
from dataclasses import dataclass

import config
from tools import utils
from playwright.async_api import async_playwright


@dataclass
class AccountSession:
    """账户会话"""

    account_id: str
    nickname: str
    browser: Optional[any] = None
    browser_context: Optional[any] = None
    context_page: Optional[any] = None
    is_active: bool = False


class AccountBrowserMiddleware:
    """
    账户浏览器中间件
    确保每个账户使用独立的浏览器数据目录，避免账户数据冲突
    """

    def __init__(self, login_manager=None):
        self.login_manager = login_manager
        self.current_session: Optional[AccountSession] = None
        self.sessions: Dict[str, AccountSession] = {}
        self.playwright: Optional[any] = None

    async def initialize(self):
        """初始化 Playwright"""
        if self.playwright is None:
            self.playwright = await async_playwright().start()

    async def launch_browser_for_account(self, account: dict) -> tuple:
        """
        为指定账户启动浏览器
        每个账户使用独立的 user_data_dir 实现完全隔离

        Returns:
            tuple: (browser_context, context_page)
        """
        await self.initialize()

        account_id = account.get("account_id", "default")
        nickname = account.get("nickname", "")
        utils.logger.info(
            f"[AccountBrowser] 为账户 {nickname} ({account_id}) 启动独立浏览器"
        )

        base_dir = os.path.join(
            os.getcwd(), "browser_data", config.USER_DATA_DIR % config.PLATFORM
        )
        user_data_dir = os.path.join(base_dir, nickname)
        utils.logger.info(f"[AccountBrowser] 浏览器数据目录: {user_data_dir}")
        os.makedirs(user_data_dir, exist_ok=True)

        chromium = self.playwright.chromium
        browser = None

        if config.SAVE_LOGIN_STATE:
            utils.logger.info(
                f"[AccountBrowser] 使用持久化上下文启动浏览器, user_data_dir={user_data_dir}"
            )
            browser_context = await chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                accept_downloads=True,
                headless=config.HEADLESS,
                proxy=None,
                viewport={"width": 1920, "height": 1080},
                user_agent=None,
            )
            utils.logger.info(f"[AccountBrowser] 浏览器启动成功")
            context_page = (
                browser_context.pages[0]
                if browser_context.pages
                else await browser_context.new_page()
            )
        else:
            browser = await chromium.launch(headless=config.HEADLESS, proxy=None)
            browser_context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent=None,
            )
            context_page = await browser_context.new_page()

        await browser_context.add_init_script(path="libs/stealth.min.js")
        await context_page.goto("https://www.douyin.com", timeout=300000)

        session = AccountSession(
            account_id=account_id,
            nickname=nickname,
            browser=browser,
            browser_context=browser_context,
            context_page=context_page,
            is_active=True,
        )
        self.sessions[account_id] = session
        self.current_session = session

        utils.logger.info(f"[AccountBrowser] 账户 {nickname} 浏览器启动成功")
        return browser_context, context_page

    async def switch_account(self, account: dict) -> tuple:
        """
        切换到指定账户
        关闭当前浏览器，为新账户启动独立的浏览器

        Returns:
            tuple: (browser_context, context_page)
        """
        account_id = account.get("account_id", "default")

        if self.current_session and self.current_session.account_id == account_id:
            utils.logger.info(
                f"[AccountBrowser] 账户 {account.get('nickname')} 已是当前会话"
            )
            return (
                self.current_session.browser_context,
                self.current_session.context_page,
            )

        utils.logger.info(
            f"[AccountBrowser] 切换账户，从 {self.current_session.nickname if self.current_session else 'None'} 到 {account.get('nickname')}"
        )

        await self.close_current_browser()

        return await self.launch_browser_for_account(account)

    async def close_current_browser(self):
        """关闭当前浏览器"""
        if self.current_session:
            try:
                utils.logger.info(
                    f"[AccountBrowser] 关闭账户 {self.current_session.nickname} 的浏览器"
                )
                if self.current_session.context_page:
                    await self.current_session.context_page.close()
                if self.current_session.browser_context:
                    await self.current_session.browser_context.close()
                if self.current_session.browser:
                    await self.current_session.browser.close()
                await asyncio.sleep(1)
            except Exception as e:
                utils.logger.warning(f"[AccountBrowser] 关闭浏览器时出错: {e}")
            finally:
                self.current_session.is_active = False
                self.current_session.browser = None
                self.current_session.browser_context = None
                self.current_session.context_page = None
                self.current_session = None

    async def close_all(self):
        """关闭所有会话"""
        await self.close_current_browser()
        if self.playwright:
            try:
                await self.playwright.stop()
            except Exception as e:
                utils.logger.warning(f"[AccountBrowser] Playwright stop 失败: {e}")
            self.playwright = None
        await asyncio.sleep(1)
        await self._cleanup_orphan_chrome_processes()

    async def _cleanup_orphan_chrome_processes(self):
        """清理孤立的 chrome 进程"""
        try:
            import subprocess
            result = subprocess.run(
                ["taskkill", "/F", "/IM", "chrome.exe", "/T"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                utils.logger.info("[AccountBrowser] 已清理残留的 chrome 进程")
        except Exception as e:
            utils.logger.warning(f"[AccountBrowser] 清理 chrome 进程失败: {e}")


class AccountScheduler:
    """
    账户调度器
    管理多个账户的任务分配，确保负载均衡
    """

    def __init__(self, accounts: List[dict]):
        self.accounts = accounts
        self.current_index = 0
        self轮询锁 = asyncio.Lock()

    async def get_next_account(self) -> dict:
        """获取下一个待处理的账户（轮询策略）"""
        async with self.轮询锁:
            if not self.accounts:
                raise ValueError("没有可用的账户")

            account = self.accounts[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.accounts)
            return account

    async def get_all_accounts(self) -> List[dict]:
        """获取所有账户"""
        return self.accounts
