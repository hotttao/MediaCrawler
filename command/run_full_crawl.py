"""
抖音数据日增计算入口
爬取完成后计算视频日增播放量
"""

import argparse
import asyncio
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

import config

config.PLATFORM = "dy"
config.LOGIN_TYPE = "qrcode"
config.ENABLE_GET_COMMENTS = False
config.ENABLE_GET_SUB_COMMENTS = False
config.SAVE_DATA_OPTION = "db"


async def main():
    parser = argparse.ArgumentParser(description="抖音爬取+日增计算")
    parser.add_argument("-t", "--target_date", type=str, help="目标日期 YYYY-MM-DD")
    parser.add_argument("-d", "--days", type=int, default=15, help="往前推天数")
    parser.add_argument("-r", "--rounds", type=int, default=1, help="轮询次数")
    args = parser.parse_args()

    if args.target_date is None:
        args.target_date = datetime.today().strftime("%Y-%m-%d")

    from core.crawler_scheduler import crawl_and_calc_incr

    results = await crawl_and_calc_incr(args.target_date, args.days, args.rounds)
    print(f"Results: {results}")


if __name__ == "__main__":
    asyncio.run(main())
