from typing import Optional
from sqlalchemy import Column, Integer, VARCHAR, Text, DateTime, func, Float
from sqlalchemy.orm import Session
from sqlalchemy.schema import UniqueConstraint
from weixin.biz.db import Base


class Chat(Base):
    __tablename__ = 'chat'

    id = Column(Integer, primary_key=True, autoincrement=True)
    remark = Column(VARCHAR(255), nullable=False)  # 原 who 字段
    last_msg = Column(Text(), nullable=True)
    last_id = Column(VARCHAR(255), nullable=False)
    
    # 新增的四个字段
    self_last_msg = Column(Text, nullable=True)
    self_last_id = Column(Integer, nullable=True)
    friend_last_msg = Column(Text, nullable=True)
    friend_last_id = Column(Integer, nullable=True)

    # 联合唯一键：(remark, last_id)
    __table_args__ = (UniqueConstraint('remark', name='uix_remark'),)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Chat(remark='{self.remark}', last_msg='{self.last_msg}', last_id={self.last_id})>"

    @classmethod
    def upsert_by_remark(cls, db: Session, remark: str, last_msg: str, last_id: int,
                        self_last_msg: Optional[str] = None,
                        self_last_id: Optional[int] = None,
                        friend_last_msg: Optional[str] = None,
                        friend_last_id: Optional[int] = None):
        """
        基于 remark 的 upsert 操作：
        - 如果该 remark 已存在记录，则更新所有字段
        - 否则插入新记录

        :param db: SQLAlchemy Session
        :param remark: 用户昵称
        :param last_msg: 最后消息内容
        :param last_id: 消息 ID
        :param self_last_msg: 自己发的最后一条消息内容
        :param self_last_id: 自己发的最后一条消息 ID
        :param friend_last_msg: 对方发的最后一条消息内容
        :param friend_last_id: 对方发的最后一条消息 ID
        :return: 更新或插入后的 Chat 实例
        """
        # 查询是否存在该 remark 的记录
        existing = db.query(cls).filter(cls.remark == remark).first()

        if existing:
            # 更新已有记录的所有字段
            existing.last_msg = last_msg
            existing.last_id = last_id
            existing.self_last_msg = self_last_msg
            existing.self_last_id = self_last_id
            existing.friend_last_msg = friend_last_msg
            existing.friend_last_id = friend_last_id
            db.add(existing)
            db.flush()  # 确保更新立即生效（非必须，commit 时会处理）
            print(f"[Chat.upsert] Updated record for remark='{remark}'")
            return existing
        else:
            # 创建新记录，包含所有字段
            new_chat = cls(
                remark=remark, 
                last_msg=last_msg, 
                last_id=last_id,
                self_last_msg=self_last_msg,
                self_last_id=self_last_id,
                friend_last_msg=friend_last_msg,
                friend_last_id=friend_last_id
            )
            db.add(new_chat)
            db.flush()  # 获取新记录的 id
            print(f"[Chat.upsert] Inserted new record for remark='{remark}'")
            return new_chat



class Merchant(Base):
    __tablename__ = 'merchant'

    id = Column(Integer, primary_key=True, autoincrement=True)
    remark = Column(VARCHAR(255), nullable=False, index=True)  # 用作唯一键，加索引
    wx_id = Column(VARCHAR(255), nullable=True)
    nickname = Column(VARCHAR(255), nullable=True)
    shop = Column(VARCHAR(255), nullable=True)
    brand = Column(VARCHAR(255), nullable=True)
    category = Column(VARCHAR(255), nullable=True)

    sample_count = Column(Integer, default=0, nullable=False)        # 寄样总数
    ad_spend_total = Column(Float, default=0.0, nullable=False)      # 投流总金额
    scheduling_count = Column(Integer, default=0, nullable=False)    # 排片数量

    evaluation = Column(Text, nullable=True)  # 评价

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 添加唯一约束：remark 唯一
    __table_args__ = (
        UniqueConstraint('remark', name='uix_merchant_remark'),
    )

    def __repr__(self):
        return f"<Merchant(id={self.id}, remark='{self.remark}', brand='{self.brand}', shop='{self.shop}')>"

    @classmethod
    def create(cls, db: Session, **kwargs):
        """
        创建新商户。
        """
        if 'remark' not in kwargs:
            raise ValueError("Field 'remark' is required to create a merchant.")

        merchant = cls(**kwargs)
        db.add(merchant)
        db.flush()
        print(f"[Merchant.create] Created merchant: {merchant}")
        return merchant

    @classmethod
    def upsert_by_remark(cls, db: Session, **kwargs):
        """
        根据 'remark' 字段执行 upsert 操作：
        - 如果存在，则更新传入的非 None 字段
        - 如果不存在，则创建新记录

        :param db: SQLAlchemy Session
        :param kwargs: Merchant 字段（必须包含 'remark'）
        :return: (Merchant 实例, is_created: bool)
        """
        remark = kwargs.get('remark')
        if not remark:
            raise ValueError("Field 'remark' is required for upsert_by_remark.")

        # 查询是否已存在
        merchant = db.query(cls).filter(cls.remark == remark).first()

        is_created = False

        if merchant:
            # 更新已有记录：仅更新非 None 值
            updated_fields = []
            for key, value in kwargs.items():
                if value is not None and getattr(merchant, key, None) != value:
                    setattr(merchant, key, value)
                    updated_fields.append(key)
            if updated_fields:
                # 显式设置 updated_at，确保触发更新
                merchant.updated_at = func.now()
                print(f"[Merchant.upsert_by_remark] Updated merchant '{remark}': {updated_fields}")
        else:
            # 创建新商户
            merchant = cls(**kwargs)
            db.add(merchant)
            db.flush()  # 获取 id
            is_created = True
            print(f"[Merchant.upsert_by_remark] Created new merchant: {merchant}")

        db.flush()  # 确保写入数据库
        return merchant, is_created

    @classmethod
    def get_by_remark(cls, db: Session, remark: str):
        """根据 remark 查询商户"""
        return db.query(cls).filter(cls.remark == remark).first()

    @classmethod
    def get_by_wx_id(cls, db: Session, wx_id: str):
        """根据 wx_id 查询商户"""
        return db.query(cls).filter(cls.wx_id == wx_id).first()