from typing import Optional
from sqlalchemy import Column, Integer, VARCHAR, Text, DateTime, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import UniqueConstraint

Base = declarative_base()

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


# class Merchant(Base):
#     pass
#     # id
#     # remark
#     # wx_id
#     # nickname
#     # shop
#     # brand
#     # category
#     # 寄样总数
#     # 投流总金额
#     # 排片数量
#     # 评价
