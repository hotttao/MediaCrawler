import dotenv
dotenv.load_dotenv()

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

import config
import asyncio
from media_platform.douyin import DouYinCrawler


async def crawler():
    config.PLATFORM = "dy"
    config.LOGIN_TYPE = "qrcode"
    config.CRAWLER_TYPE = "creator"
    config.ENABLE_GET_COMMENTS = False
    config.ENABLE_GET_SUB_COMMENTS = False
    config.SAVE_DATA_OPTION = "db"
    
    c = DouYinCrawler()
    await c.start()


def job():
    """定时任务执行的函数"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"任务执行时间: {current_time}")
    asyncio.run(crawler())
    print("定时任务正在执行中...")
    # 这里可以添加你需要执行的具体任务
    print("任务执行完成!")
    print("-" * 40)


def main():
    job()

if __name__ == "__main__":
    main()



