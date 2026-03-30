"""
抖音爬虫入口
支持命令行参数配置
"""

import asyncio
from dotenv import load_dotenv

load_dotenv()

import cmd_arg
from core.crawler_scheduler import crawl_only


async def main():
    args = await cmd_arg.parse_cmd()

    if args.init_db:
        from database import db

        await db.init_db(args.init_db)
        print(f"Database {args.init_db} initialized successfully.")
        return

    creator_ids = []
    if args.type == "creator":
        from config.dy_config import get_creator_id_list

        creator_ids = await get_creator_id_list()

    results = await crawl_only(creator_ids, rounds=1)
    print(f"Crawl results: {results}")


if __name__ == "__main__":
    asyncio.run(main())
