# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。

# 抖音平台配置
PUBLISH_TIME_TYPE = 0

# 指定DY视频ID列表
DY_SPECIFIED_ID_LIST = [
    "7280854932641664319",
    "7202432992642387233",
    # ........................
]

# 指定DY用户ID列表（仅作为备用，优先从数据库读取）
DY_CREATOR_ID_LIST = [
    # "MS4wLjABAAAA8EoZrCw43AWujry2n4wq63yLNqCxelDngM7hwXT6tY0",
    # "MS4wLjABAAAAU5VHN-LWFR9_jqqpcFeDgP2tzEFT0RYMi8KMTSnA70g",
]


def get_creator_id_list() -> list:
    """
    获取待抓取的抖音创作者ID列表
    1. 先读取dy_config.py中的DY_CREATOR_ID_LIST
    2. 再读取dy_crawler_creator表配置（is_enabled=1的记录）
    3. 合并后去重，返回最终的user_id列表
    """
    from sqlalchemy import select
    from database.models import DyCrawlerCreator
    from database.db_session import get_session
    import time

    # 1. 读取配置文件中的ID列表
    config_ids = list(DY_CREATOR_ID_LIST)

    # 2. 从数据库读取配置（仅读取启用的记录）
    db_ids = []
    try:
        import config

        if config.SAVE_DATA_OPTION in ("mysql", "db", "sqlite"):
            import asyncio
            from database.db_session import get_async_engine

            async def fetch_db_creator_ids():
                engine = get_async_engine(config.SAVE_DATA_OPTION)
                if engine is None:
                    return []
                from sqlalchemy.ext.asyncio import AsyncSession
                from sqlalchemy.orm import sessionmaker

                AsyncSessionFactory = sessionmaker(
                    engine, class_=AsyncSession, expire_on_commit=False
                )
                async with AsyncSessionFactory() as session:
                    stmt = select(DyCrawlerCreator.user_id).where(
                        DyCrawlerCreator.is_enabled == 1
                    )
                    result = await session.execute(stmt)
                    rows = result.scalars().all()
                    return rows

            # 获取事件循环并执行异步函数
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            db_ids = loop.run_until_complete(fetch_db_creator_ids())
    except Exception as e:
        import sys
        from tools import utils

        utils.logger.warning(f"[get_creator_id_list] 从数据库读取创作者ID失败: {e}")

    # 3. 合并并去重
    all_ids = list(set(config_ids + db_ids))

    # 记录日志
    from tools import utils

    utils.logger.info(
        f"[get_creator_id_list] 配置文件ID数量: {len(config_ids)}, 数据库ID数量: {len(db_ids)}, 合并后总数: {len(all_ids)}"
    )

    return all_ids
