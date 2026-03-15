"""
抖音创作者配置管理命令
支持通过命令行添加user_id到dy_crawler_creator表，并自动从dy_creator表更新nickname
"""

import argparse
import asyncio
import sys
import time
from dotenv import load_dotenv

load_dotenv()

import config
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from database.db_session import get_async_engine
from database.models import DyCrawlerCreator, DyCreator
from sqlalchemy.orm import sessionmaker


async def get_mysql_session() -> AsyncSession:
    """获取MySQL会话"""
    engine = get_async_engine("mysql")
    AsyncSessionFactory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    session = AsyncSessionFactory()
    return session


async def add_creator(user_id: str) -> bool:
    """添加创作者到dy_crawler_creator表"""
    session = await get_mysql_session()
    try:
        # 检查是否已存在
        stmt = select(DyCrawlerCreator).where(DyCrawlerCreator.user_id == user_id)
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            if existing.is_enabled == 0:
                # 用户之前被删除，恢复启用状态
                stmt_update = (
                    update(DyCrawlerCreator)
                    .where(DyCrawlerCreator.user_id == user_id)
                    .values(is_enabled=1, add_ts=int(time.time()))
                )
                await session.execute(stmt_update)
                await session.commit()
                print(f"已恢复用户 {user_id} 到待抓取列表")
                return True
            else:
                print(f"用户 {user_id} 已存在")
                return False

        # 添加新记录
        creator = DyCrawlerCreator(
            user_id=user_id, nickname=None, add_ts=int(time.time()), is_enabled=1
        )
        session.add(creator)
        await session.commit()
        print(f"已添加用户 {user_id} 到待抓取列表")
        return True
    finally:
        await session.close()


async def remove_creator(user_id: str) -> bool:
    """从抓取配置中删除创作者（将is_enabled设置为0）"""
    session = await get_mysql_session()
    try:
        # 检查是否存在
        stmt = select(DyCrawlerCreator).where(DyCrawlerCreator.user_id == user_id)
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()

        if not existing:
            print(f"用户 {user_id} 不存在")
            return False

        # 将 is_enabled 设置为 0
        stmt_update = (
            update(DyCrawlerCreator)
            .where(DyCrawlerCreator.user_id == user_id)
            .values(is_enabled=0)
        )
        await session.execute(stmt_update)
        await session.commit()
        print(f"已将用户 {user_id} 从抓取配置中删除")
        return True
    finally:
        await session.close()


async def update_nicknames() -> int:
    """更新dy_crawler_creator表中nickname为空的记录"""
    updated_count = 0

    session = await get_mysql_session()
    try:
        # 查找nickname为空或中文字符串的记录
        stmt = select(DyCrawlerCreator).where(
            (DyCrawlerCreator.nickname == None)
            | (DyCrawlerCreator.nickname == "")
            | (DyCrawlerCreator.nickname.like("%\u4e00-%\u9fff%"))  # 包含中文
        )
        result = await session.execute(stmt)
        creators = result.scalars().all()

        print(f"找到 {len(creators)} 条需要更新nickname的记录")

        for creator in creators:
            # 从dy_creator表查找nickname
            stmt_creator = select(DyCreator).where(DyCreator.user_id == creator.user_id)
            result_creator = await session.execute(stmt_creator)
            dy_creator = result_creator.scalar_one_or_none()

            if dy_creator and dy_creator.nickname:
                # 更新nickname
                stmt_update = (
                    update(DyCrawlerCreator)
                    .where(DyCrawlerCreator.id == creator.id)
                    .values(nickname=dy_creator.nickname)
                )
                await session.execute(stmt_update)
                updated_count += 1
                print(f"更新 user_id={creator.user_id}, nickname={dy_creator.nickname}")
            else:
                print(f"未找到 user_id={creator.user_id} 在dy_creator表中的记录")

        await session.commit()
    finally:
        await session.close()

    return updated_count


async def main():
    parser = argparse.ArgumentParser(description="抖音创作者配置管理工具")
    parser.add_argument("--user_id", type=str, help="抖音用户ID")
    parser.add_argument(
        "--update_nickname", action="store_true", help="更新所有nickname为空的记录"
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        help="从抓取配置中删除指定user_id（将is_enabled设置为0）",
    )

    args = parser.parse_args()

    if args.remove and args.user_id:
        # 删除用户
        await remove_creator(args.user_id)
    elif args.user_id:
        # 添加用户
        await add_creator(args.user_id)

    # 无论是否添加用户，都可以执行更新nickname操作
    if args.update_nickname:
        count = await update_nicknames()
        print(f"共更新了 {count} 条记录的nickname")

    # 如果没有提供参数，显示帮助
    if not args.user_id and not args.update_nickname:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
