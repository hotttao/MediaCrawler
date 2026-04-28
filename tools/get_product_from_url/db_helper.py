# -*- coding: utf-8 -*-
"""
数据库插入模块 - 将商品信息插入 media_ai.products 表
"""
import os
from pathlib import Path
from contextlib import contextmanager

# 加载 .env 文件
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus


def get_media_ai_engine():
    """创建 media_ai 数据库的 engine"""
    user = os.getenv("MYSQL_DB_USER", "root")
    password = os.getenv("MYSQL_DB_PWD", "123456")
    host = os.getenv("MYSQL_DB_HOST", "localhost")
    port = os.getenv("MYSQL_DB_PORT", "3306")

    encoded_password = quote_plus(password)
    # 使用 .env 中的配置，但数据库名为 media_ai
    dsn = f"mysql+pymysql://{user}:{encoded_password}@{host}:{port}/media_ai?charset=utf8mb4&collation=utf8mb4_unicode_ci"

    engine = create_engine(
        dsn,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_size=5,
        max_overflow=10
    )
    return engine


def get_session():
    """获取数据库 session"""
    engine = get_media_ai_engine()
    Session = sessionmaker(bind=engine)
    return Session()


@contextmanager
def media_ai_db():
    """media_ai 数据库上下文管理器"""
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def insert_product(record: dict) -> bool:
    """
    插入或更新商品记录

    Args:
        record: 商品信息字典

    Returns:
        bool: 是否插入成功
    """
    sql = text("""
        INSERT INTO products (
            id, user_id, team_id, name, targetAudience, productDetails, display_actions,
            promotion_id, elastic_title, elastic_images_uri,
            FirstCName, SecondCName, ThirdCName, FourthCName,
            price, aweme_id, updated_at
        ) VALUES (
            :id, :user_id, :team_id, :name, :targetAudience, :productDetails, :display_actions,
            :promotion_id, :elastic_title, :elastic_images_uri,
            :FirstCName, :SecondCName, :ThirdCName, :FourthCName,
            :price, :aweme_id, NOW(3)
        )
        ON DUPLICATE KEY UPDATE id=id
    """)

    try:
        with media_ai_db() as session:
            session.execute(sql, record)
        # 插入商品图片
        if record.get('elastic_images_uri'):
            insert_product_image(record['id'], record['elastic_images_uri'])
        return True
    except Exception as e:
        print(f"插入失败: {e}")
        return False


def insert_product_image(product_id: str, url: str) -> bool:
    """
    插入商品图片记录（如果不存在）
    下载图片到本地，数据库保存本地路径

    Args:
        product_id: 商品ID
        url: 图片URL

    Returns:
        bool: 是否插入成功（已存在返回 True，跳过返回 False）
    """
    # 先检查是否已存在
    check_sql = text("SELECT COUNT(1) FROM product_images WHERE product_id = :product_id AND is_main = 1")
    try:
        with media_ai_db() as session:
            result = session.execute(check_sql, {'product_id': product_id})
            count = result.scalar()
            if count > 0:
                print(f"商品图片已存在，跳过: product_id={product_id}")
                return True
    except Exception as e:
        print(f"检查商品图片失败: {e}")
        return False

    # 下载图片到本地
    local_path = download_product_image(product_id, url)
    if not local_path:
        print(f"下载图片失败，跳过: product_id={product_id}")
        return False

    # 插入新记录
    import uuid
    image_id = str(uuid.uuid4())

    insert_sql = text("""
        INSERT INTO product_images (id, product_id, url, is_main, `order`)
        VALUES (:id, :product_id, :url, :is_main, :order_val)
    """)

    try:
        with media_ai_db() as session:
            session.execute(insert_sql, {
                'id': image_id,
                'product_id': product_id,
                'url': f"/uploads/teams/18982144-3d42-4a51-98d8-4d6959332d66/products/{product_id}.jpg",
                'is_main': 1,
                'order_val': 0
            })
        return True
    except Exception as e:
        print(f"插入商品图片失败: {e}")
        return False


def download_product_image(product_id: str, url: str) -> str:
    """
    下载商品图片到本地

    Args:
        product_id: 商品ID（用作文件名）
        url: 图片URL

    Returns:
        str: 本地文件路径，失败返回空字符串
    """
    import urllib.request
    import os

    # 创建保存目录
    save_dir = r"D:\nginx\media_images\uploads\teams\18982144-3d42-4a51-98d8-4d6959332d66\products"
    os.makedirs(save_dir, exist_ok=True)

    # 本地文件路径
    local_path = os.path.join(save_dir, f"{product_id}.jpg")

    try:
        # 下载图片
        urllib.request.urlretrieve(url, local_path)
        print(f"图片已下载: {local_path}")
        return local_path
    except Exception as e:
        print(f"下载图片失败: {e}")
        # 如果下载失败，尝试保存原始URL
        return url

    try:
        with media_ai_db() as session:
            session.execute(sql, record)
            return True
    except Exception as e:
        print(f"插入失败: {e}")
        return False


def build_product_record(product_data: dict, aweme_id: str = "") -> dict:
    """
    从商品数据构建插入记录

    Args:
        product_data: 商品信息字典（来自 extract_product_info）
        aweme_id: 视频ID

    Returns:
        dict: 符合 products 表结构的记录
    """
    # targetAudience 映射
    second_name = product_data.get('SecondCName', '')
    if second_name == '女装':
        target_audience = 'WOMENS'
    elif second_name == '男装':
        target_audience = 'MENS'
    else:
        target_audience = 'KIDS'  # 默认值

    def esc(s):
        if s is None:
            return ''
        return str(s).replace("'", "''")

    return {
        'id': product_data.get('product_id', ''),
        'user_id': 'd359ec83-a39c-4408-aac6-c1c818d08ab8',
        'team_id': '18982144-3d42-4a51-98d8-4d6959332d66',
        'name': product_data.get('title', ''),
        'targetAudience': target_audience,
        'productDetails': '',
        'display_actions': '',
        'promotion_id': product_data.get('promotion_id', ''),
        'elastic_title': product_data.get('elastic_title', ''),
        'elastic_images_uri': product_data.get('elastic_images_uri', ''),
        'FirstCName': product_data.get('FirstCName', ''),
        'SecondCName': product_data.get('SecondCName', ''),
        'ThirdCName': product_data.get('ThirdCName', ''),
        'FourthCName': product_data.get('FourthCName', ''),
        'price': product_data.get('price', 0),
        'aweme_id': aweme_id or product_data.get('aweme_id', ''),
    }
