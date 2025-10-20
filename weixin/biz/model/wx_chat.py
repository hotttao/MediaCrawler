# models.py
from sqlalchemy import (
    Column, Integer, 
    DateTime, func, 
    UniqueConstraint,
    VARCHAR, Text
)
from sqlalchemy.orm import Session
from weixin.biz.db import Base


class Chat(Base):
    __tablename__ = 'chat'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nickname = Column(VARCHAR(255), nullable=False)  # 原 who 字段
    last_msg = Column(Text(), nullable=True)
    last_id = Column(VARCHAR(255), nullable=False)

    # 联合唯一键：(nickname, last_id)
    __table_args__ = (UniqueConstraint('nickname', name='uix_nickname'),)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Chat(nickname='{self.nickname}', last_msg='{self.last_msg}', last_id={self.last_id})>"

    @classmethod
    def upsert_by_nickname(cls, db: Session, nickname: str, last_msg: str, last_id: int):
        """
        基于 nickname 的 upsert 操作：
        - 如果该 nickname 已存在记录，则更新 last_msg 和 last_id
        - 否则插入新记录

        :param db: SQLAlchemy Session
        :param nickname: 用户昵称
        :param last_msg: 最后消息内容
        :param last_id: 消息 ID
        :return: 更新或插入后的 Chat 实例
        """
        # 查询是否存在该 nickname 的记录
        existing = db.query(cls).filter(cls.nickname == nickname).first()

        if existing:
            # 更新已有记录
            existing.last_msg = last_msg
            existing.last_id = last_id
            db.add(existing)
            db.flush()  # 确保更新立即生效（非必须，commit 时会处理）
            print(f"[Chat.upsert] Updated record for nickname='{nickname}'")
            return existing
        else:
            # 创建新记录
            new_chat = cls(nickname=nickname, last_msg=last_msg, last_id=last_id)
            db.add(new_chat)
            db.flush()  # 获取新记录的 id
            print(f"[Chat.upsert] Inserted new record for nickname='{nickname}'")
            return new_chat