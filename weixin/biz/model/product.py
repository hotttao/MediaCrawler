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
    wx_promot = Column(VARCHAR(255), nullable=True, comment="视频号投流方式")
    rate = Column(Float, nullable=True)
    roi = Column(Float, nullable=True, comment="ROI")
    roi_desc = Column(VARCHAR(255), nullable=True, comment="ROI描述")
    remark = Column(VARCHAR(255), nullable=True)  # 新增字段
    sample_send = Column(Boolean, default=False, comment="是否寄样")
    track_num = Column(VARCHAR(255), default="", comment="快递单号")
    # 一级类目
    # 二级类目

    # 联合唯一键：(remark, product_url)
    __table_args__ = (UniqueConstraint('remark', 'product_url', 'is_promoted', name='uix_remark_product_promoted'),)

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
            # raise ValueError("Missing required fields: brand, product_name, price, product_url")
            return

        product = cls(**kwargs)
        db.add(product)
        db.flush()  # 立即执行插入，获取 id
        print(f"[Product.create] Created product: {product}")
        return product

    @classmethod
    def upsert_by_remark_and_url(cls, db: Session, **kwargs):
        """
        基于联合唯一键 (remark, product_url) 执行 upsert 操作：
        - 如果存在 matching 记录，则更新非 None 字段
        - 否则创建新记录

        :param db: SQLAlchemy Session
        :param kwargs: Product 模型字段（必须包含 'remark' 和 'product_url'）
        :return: (Product 实例, is_created: bool)
        """
        remark = kwargs.get('remark')
        product_url = kwargs.get('product_url')

        if not remark:
            raise ValueError("Field 'remark' is required for upsert.")
        if not product_url:
            raise ValueError("Field 'product_url' is required for upsert.")

        # 查询是否存在 (remark, product_url) 匹配的记录
        product = db.query(cls).filter(
            cls.remark == remark,
            cls.product_url == product_url
        ).first()

        is_created = False

        if product:
            # 更新已有记录：仅更新非 None 且值不同的字段
            updated_fields = []
            for key, value in kwargs.items():
                if value is not None:
                    current_value = getattr(product, key, None)
                    if value != current_value:
                        setattr(product, key, value)
                        updated_fields.append(key)
            if updated_fields:
                product.updated_at = func.now()  # 确保触发 updated_at 更新
                print(f"[Product.upsert_by_remark_and_url] Updated product: {product}, fields: {updated_fields}")
        else:
            # 创建新商品
            product = cls(**kwargs)
            db.add(product)
            db.flush()
            is_created = True
            print(f"[Product.upsert_by_remark_and_url] Created new product: {product}")

        return product


# class AdRecord(Base):
#     """
#     投流记录
#     """
#     # product_url
#     # remark
#     # 物流号
#     # 平台
#     # video_url
#     # 投流金额
