"""
抖音数据日增计算入口
爬取完成后计算视频日增播放量，并推送热点视频
"""

import argparse
import asyncio
from datetime import datetime, timedelta

from dotenv import load_dotenv

load_dotenv()

from tools import utils

import config

config.PLATFORM = "dy"
config.LOGIN_TYPE = "qrcode"
config.ENABLE_GET_COMMENTS = False
config.ENABLE_GET_SUB_COMMENTS = False
config.SAVE_DATA_OPTION = "db"


async def main():
    parser = argparse.ArgumentParser(description="抖音爬取+日增计算+热点推送")
    parser.add_argument("-t", "--target_date", type=str, help="目标日期 YYYY-MM-DD")
    parser.add_argument("-d", "--days", type=int, default=15, help="往前推天数")
    parser.add_argument("-r", "--rounds", type=int, default=1, help="轮询次数")
    args = parser.parse_args()

    if args.target_date is None:
        args.target_date = datetime.today().strftime("%Y-%m-%d")

    from core.crawler_scheduler import crawl_and_calc_incr

    results = await crawl_and_calc_incr(args.target_date, args.days, args.rounds)

    utils.logger.info(f"[Ops] 爬取完成，开始推送热点视频 ({args.target_date})...")

    try:
        from core.notifier.manager import NotificationManager
        from command.push_hot_videos import (
            push_hot_videos,
            send_hot_videos_notification,
        )

        notifier = NotificationManager()
        await notifier.start()

        start_date = (
            datetime.strptime(args.target_date, "%Y-%m-%d") - timedelta(days=7)
        ).strftime("%Y-%m-%d")

        hot_videos = await push_hot_videos(
            args.target_date, start_date, "digg_count", 20
        )
        await send_hot_videos_notification(
            notifier, hot_videos, args.target_date, "digg_count", 20
        )

        results["hot_videos"] = len(hot_videos)
        await notifier.shutdown()
    except Exception as e:
        utils.logger.error(f"[Ops] 热点视频推送失败: {e}")

    print(f"Results: {results}")


if __name__ == "__main__":
    asyncio.run(main())
