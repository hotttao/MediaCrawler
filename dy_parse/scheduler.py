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
    
    await DouYinCrawler().start()


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
    """主函数，启动定时任务调度器"""
    scheduler = BlockingScheduler()
    
    # 使用cron表达式设置定时任务
    # 从00:30开始，每隔4小时执行一次
    # 即: 00:30, 04:30, 08:30, 12:30, 16:30, 20:30
    # cron_trigger = CronTrigger(
    #     minute=30,  # 每小时的30分
    #     hour='0,4,8,12,16,20'  # 在0点、4点、8点、12点、16点、20点执行
    # )
    cron_trigger = CronTrigger(
        minute='*'  # 每分钟执行
    )
    
    scheduler.add_job(
        job, cron_trigger, id='periodic_job',
        max_instances=1,  # 最大并发实例数为1，防止任务重叠
        misfire_grace_time=30  # 任务错过执行的宽限时间（秒）
    ) 
    
    print("APScheduler定时任务已启动...")
    print("任务将在每天的 00:30, 04:30, 08:30, 12:30, 16:30, 20:30 执行")
    print("按 Ctrl+C 停止定时任务")
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\n定时任务已停止")

if __name__ == "__main__":
    main()



