from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

# 数据库连接（使用 SQLite 示例）
# database.py
import os
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus


def create_mysql_engine():
    """
    从环境变量中读取 MySQL 配置，创建并返回 SQLAlchemy engine。
    环境变量：
        MYSQL_DB_USER: 用户名
        MYSQL_DB_PWD: 密码
        MYSQL_DB_HOST: 主机地址
        MYSQL_DB_PORT: 端口
        MYSQL_DB_NAME: 数据库名
    """
    # 读取环境变量
    user = os.getenv("MYSQL_DB_USER")
    password = os.getenv("MYSQL_DB_PWD")
    host = os.getenv("MYSQL_DB_HOST")
    port = os.getenv("MYSQL_DB_PORT")
    db_name = os.getenv("MYSQL_DB_NAME")

    # 检查是否所有环境变量都已设置
    if not all([user, password, host, port, db_name]):
        missing = [key for key, value in {
            'MYSQL_DB_USER': user,
            'MYSQL_DB_PWD': password,
            'MYSQL_DB_HOST': host,
            'MYSQL_DB_PORT': port,
            'MYSQL_DB_NAME': db_name
        }.items() if not value]
        raise EnvironmentError(f"缺少必要的环境变量: {', '.join(missing)}")

    # 对密码进行 URL 编码，防止特殊字符导致解析错误
    encoded_password = quote_plus(password)

    # 构造数据库连接 URL
    DATABASE_URL = (
        f"mysql+pymysql://{user}:{encoded_password}"
        f"@{host}:{port}/{db_name}"
        f"?charset=utf8mb4&collation=utf8mb4_unicode_ci"
    )

    # 创建 engine
    engine = create_engine(
        DATABASE_URL,
        echo=False,           # 生产环境建议设为 False，或通过环境变量控制
        pool_pre_ping=True,   # 每次连接前检查有效性
        pool_recycle=3600,    # 避免 MySQL 的 wait_timeout 导致断连
        pool_size=10,
        max_overflow=20
    )
    return engine

engine = create_mysql_engine()
SessionLocal = sessionmaker(bind=engine)

# 创建表
# Base.metadata.create_all(bind=engine)


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init(config):
    pass
