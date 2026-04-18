"""
推送热点视频脚本
从 douyin_aweme_day 中过滤热点视频，通过配置的通知渠道发送
"""

import argparse
import asyncio
from datetime import datetime, timedelta
from typing import List

from dotenv import load_dotenv

load_dotenv()

import config

config.SAVE_DATA_OPTION = "db"

from core.notifier.manager import NotificationManager
from database.db_session import get_session
from database.models import DouyinAwemeDay
from sqlalchemy import select, and_
from tools import utils


async def push_hot_videos(
    calc_date: str,
    start_date: str,
    filter_field: str,
    min_value: int,
    first_cnames: List[str] = None,
) -> List[DouyinAwemeDay]:
    """
    从数据库查询热点视频并发送通知

    Args:
        calc_date: 数据日期，格式 YYYY-MM-DD
        start_date: 视频发布起始时间，格式 YYYY-MM-DD
        filter_field: X轴字段，用于最小值过滤
        min_value: 最小值过滤
        first_cnames: 商品一级分类过滤列表，默认["水饮冲调", "酒类"]

    Returns:
        热点视频列表
    """
    if first_cnames is None:
        first_cnames = ["水饮冲调", "酒类"]

    utils.logger.info(
        f"[HotVideos] 查询热点视频: calc_date={calc_date}, start_date={start_date}, "
        f"filter_field={filter_field}, min_value={min_value}, first_cnames={first_cnames}"
    )

    async with get_session() as session:
        stmt = select(DouyinAwemeDay).where(
            and_(
                DouyinAwemeDay.data_date == calc_date,
                DouyinAwemeDay.create_time
                >= int(datetime.strptime(start_date, "%Y-%m-%d").timestamp()),
                getattr(DouyinAwemeDay, filter_field) >= min_value,
                DouyinAwemeDay.first_cname.in_(first_cnames),
            )
        )
        result = await session.execute(stmt)
        hot_videos = list(result.scalars().all())

    utils.logger.info(f"[HotVideos] 查询到 {len(hot_videos)} 条热点视频")
    return hot_videos


def format_video_message(video: DouyinAwemeDay) -> str:
    """格式化单条视频消息"""
    publish_time = ""
    if video.create_time:
        from datetime import datetime

        publish_time = datetime.fromtimestamp(video.create_time).strftime(
            "%Y-%m-%d %H:%M"
        )
    return (
        f"**{video.elastic_title or '无标题'}**\n"
        f"👤 {video.nickname or '未知'} | 🕐 {publish_time}\n"
        f"👍 点赞: {video.digg_tt} (+{video.digg_count})\n"
        f"⭐ 收藏: {video.collect_tt} (+{video.collect_count})\n"
        f"🔄 分享: {video.share_tt} (+{video.share_count})\n"
        f"💬 评论: {video.comment_count}\n"
        f"🔗 {video.aweme_url or '无链接'}\n"
    )


async def send_hot_videos_notification(
    notifier: NotificationManager,
    videos: List[DouyinAwemeDay],
    calc_date: str,
    filter_field: str,
    min_value: int,
) -> None:
    """发送热点视频通知"""
    if not videos:
        await notifier.send(
            "🔥 热点视频推送",
            f"📅 {calc_date} 暂无满足条件的热点视频\n"
            f"筛选条件: {filter_field} >= {min_value}",
        )
        return

    header = (
        f"📅 {calc_date} 热点视频推送\n"
        f"共 {len(videos)} 条 | 筛选条件: {filter_field} >= {min_value}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
    )

    body = "\n".join(format_video_message(v) for v in videos)

    footer = f"\n━━━━━━━━━━━━━━━━━━━━\n数据来源: 抖音日增数据"

    full_message = header + body + footer
    await notifier.send("🔥 热点视频推送", full_message)


async def main():
    parser = argparse.ArgumentParser(description="推送热点视频")
    parser.add_argument(
        "-t",
        "--target_date",
        type=str,
        default=datetime.today().strftime("%Y-%m-%d"),
        help="数据日期，格式 YYYY-MM-DD，默认为今天",
    )
    parser.add_argument(
        "-s",
        "--start_date",
        type=str,
        default=None,
        help="视频发布起始时间，格式 YYYY-MM-DD，默认为 target_date往前7天",
    )
    parser.add_argument(
        "-f",
        "--filter_field",
        type=str,
        default="digg_count",
        help="X轴字段，用于最小值过滤，默认为 digg_count",
    )
    parser.add_argument(
        "-m",
        "--min_value",
        type=int,
        default=20,
        help="最小值过滤，默认为 20",
    )
    parser.add_argument(
        "-c",
        "--first_cnames",
        type=str,
        nargs="+",
        default=["水饮冲调", "酒类"],
        help="商品一级分类过滤列表，默认为 水饮冲调 酒类",
    )
    args = parser.parse_args()

    calc_date = args.target_date
    if args.start_date:
        start_date = args.start_date
    else:
        start_date = (
            datetime.strptime(calc_date, "%Y-%m-%d") - timedelta(days=7)
        ).strftime("%Y-%m-%d")

    utils.logger.info(
        f"[HotVideos] 开始推送热点视频: date={calc_date}, start={start_date}"
    )

    notifier = NotificationManager()
    await notifier.start()

    try:
        hot_videos = await push_hot_videos(
            calc_date, start_date, args.filter_field, args.min_value, args.first_cnames
        )
        await send_hot_videos_notification(
            notifier, hot_videos, calc_date, args.filter_field, args.min_value
        )
        utils.logger.info(f"[HotVideos] 推送完成，共 {len(hot_videos)} 条")
    finally:
        await notifier.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
