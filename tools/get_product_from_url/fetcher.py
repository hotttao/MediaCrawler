# -*- coding: utf-8 -*-
"""
使用项目已有的 DouYinCrawler 获取视频商品信息
"""
import asyncio
import json
import os
import re
import sys
from typing import Optional

# 添加项目根目录到路径
sys.path.insert(0, '.')

import config
from media_platform.douyin.client import DouYinClient
from media_platform.douyin.login import DouYinLogin
from playwright.async_api import async_playwright
from tools import utils
from tools.get_product_from_url.extractor import extract_aweme_id, extract_product_info


async def get_product_from_url(url: str) -> dict:
    """
    从抖音视频链接获取商品信息

    Args:
        url: 抖音视频链接

    Returns:
        包含商品信息的字典
    """
    aweme_id = extract_aweme_id(url)
    if not aweme_id:
        return {"error": f"无法从链接中提取视频 ID: {url}"}

    browser_context = None
    context_page = None
    cleanup_done = False

    async def cleanup():
        nonlocal cleanup_done
        if cleanup_done:
            return
        cleanup_done = True
        if context_page:
            try:
                await context_page.close()
            except Exception:
                pass
        if browser_context:
            try:
                await browser_context.close()
            except Exception:
                pass
        await asyncio.sleep(1)

    try:
        async with async_playwright() as playwright:
            user_data_dir = os.path.join(os.getcwd(), "browser_data", "dy_user_data_dir", "get_product_tool")
            os.makedirs(user_data_dir, exist_ok=True)

            chromium = playwright.chromium
            browser_context = await chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=config.HEADLESS,
                proxy=None,
                viewport={"width": 1920, "height": 1080},
                accept_downloads=True,
            )
            context_page = browser_context.pages[0] if browser_context.pages else await browser_context.new_page()

            if not context_page.url or context_page.url == 'about:blank':
                await context_page.goto("https://www.douyin.com", timeout=300000)
                await asyncio.sleep(3)

            cookie_str, cookie_dict = utils.convert_cookies(await browser_context.cookies())

            dy_client = DouYinClient(
                proxy=None,
                headers={
                    "User-Agent": await context_page.evaluate("() => navigator.userAgent"),
                    "Cookie": cookie_str,
                    "Host": "www.douyin.com",
                    "Origin": "https://www.douyin.com/",
                    "Referer": "https://www.douyin.com/",
                    "Content-Type": "application/json;charset=UTF-8",
                },
                playwright_page=context_page,
                cookie_dict=cookie_dict,
            )

            login_success = await dy_client.pong(browser_context=browser_context)
            if not login_success:
                print("检测到未登录状态，请在打开的浏览器中扫码登录...", file=sys.stderr)
                login_start_time = asyncio.get_event_loop().time()
                max_wait_seconds = 300
                check_interval = 3
                while (asyncio.get_event_loop().time() - login_start_time) < max_wait_seconds:
                    await asyncio.sleep(check_interval)
                    if await dy_client.pong(browser_context=browser_context):
                        print("登录成功！", file=sys.stderr)
                        await dy_client.update_cookies(browser_context)
                        await context_page.reload()
                        await asyncio.sleep(2)
                        break
                else:
                    print("登录超时，已退出", file=sys.stderr)
                    await cleanup()
                    return {"error": "登录超时，请重试"}

            print(f"正在获取视频 {aweme_id} 的详情...", file=sys.stderr)
            aweme_detail = await dy_client.get_video_by_id(aweme_id)

            if not aweme_detail:
                await cleanup()
                return {"error": f"无法获取视频详情，视频 ID: {aweme_id}"}

            product = extract_product_info(aweme_detail)

            if not product:
                await cleanup()
                return {
                    "aweme_id": aweme_id,
                    "has_product": False,
                    "message": "该视频没有关联商品"
                }

            product["aweme_id"] = aweme_id
            product["has_product"] = True

            try:
                from .db_helper import insert_product, build_product_record
                record = build_product_record(product, aweme_id)
                success = insert_product(record)
                product["db_inserted"] = success
            except Exception as e:
                product["db_inserted"] = False
                product["db_error"] = str(e)

            await cleanup()
            return product
    except Exception as e:
        await cleanup()
        raise


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python fetcher.py <抖音视频链接>")
        sys.exit(1)

    url = sys.argv[1]
    result = asyncio.run(get_product_from_url(url))
    print(json.dumps(result, ensure_ascii=False, indent=2))
