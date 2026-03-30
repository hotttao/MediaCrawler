import asyncio
from database.db_session import get_async_engine
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker


async def test():
    engine = get_async_engine("db")
    if engine is None:
        print("Engine is None!")
        return
    AsyncSessionFactory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with AsyncSessionFactory() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM dy_crawler_creator"))
        print("dy_crawler_creator count:", result.scalar())
        result2 = await session.execute(text("SELECT COUNT(*) FROM dy_creator"))
        print("dy_creator count:", result2.scalar())


if __name__ == "__main__":
    asyncio.run(test())
