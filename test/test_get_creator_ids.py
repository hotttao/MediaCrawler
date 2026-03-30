from dotenv import load_dotenv

load_dotenv()

import config

config.SAVE_DATA_OPTION = "db"
print(f"SAVE_DATA_OPTION = {config.SAVE_DATA_OPTION}")
print(f"MYSQL_DB_HOST = {config.MYSQL_DB_HOST}")


async def main():
    from config.dy_config import get_creator_id_list

    ids = await get_creator_id_list()
    print(f"Result IDs: {ids}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
