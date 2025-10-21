# models.py
from sqlalchemy import (
    Column, Integer, Float, 
    Boolean, DateTime, func, 
    UniqueConstraint,
    VARCHAR, Text
)
from sqlalchemy.orm import Session
from weixin.biz.db import Base


class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True, autoincrement=True)
    brand = Column(VARCHAR(255), nullable=False)
    product_name = Column(VARCHAR(255), nullable=False)
    price = Column(Float, nullable=False)
    product_url = Column(VARCHAR(255), nullable=False)
    is_promoted = Column(Boolean, default=False)
    rate = Column(Float, nullable=True)
    nickname = Column(VARCHAR(255), nullable=True)  # 新增字段

    # 联合唯一键：(nickname, product_url)
    __table_args__ = (UniqueConstraint('nickname', 'product_url', name='uix_nickname_product_url'),)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Product(brand='{self.brand}', name='{self.product_name}', price={self.price})>"

    @classmethod
    def create(cls, db: Session, **kwargs):
        """
        封装 insert 操作，创建一个新商品。

        :param db: SQLAlchemy Session
        :param kwargs: Product 模型字段（如 brand, product_name, price 等）
        :return: 创建后的 Product 实例
        """
        # 可以在这里添加参数校验
        if 'brand' not in kwargs or 'product_name' not in kwargs or 'price' not in kwargs or 'product_url' not in kwargs:
            raise ValueError("Missing required fields: brand, product_name, price, product_url")

        product = cls(**kwargs)
        db.add(product)
        db.flush()  # 立即执行插入，获取 id
        print(f"[Product.create] Created product: {product}")
        return product
