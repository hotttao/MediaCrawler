from pydantic import BaseModel
from typing import Optional, List

class WxAccount(BaseModel):
    wx_id: str # 微信号
    nickname: str # 昵称
    remark: str # 备注


class ChatMsg(BaseModel):
    account: WxAccount # 消息来自谁
    msg: str # 消息的内容
    type: str # 消息的类型
    is_self: bool # 是否是自己发送的消息
    # ref: str # 引用的消息

    def to_text(self):
        if self.type != "text":
                return ""
        if self.is_self:
            return f"我: {self.content}"
        else:
            nickname = self.account.remark or self.account.nickname
            return f"{nickname}: {self.content}"


class ChatInfo(BaseModel):
    account: WxAccount
    content: List[ChatMsg]
    last_id: int
    self_last_msg: Optional[str] = None
    self_last_id: Optional[int] = None
    friend_last_msg: Optional[str] = None
    friend_last_id: Optional[int] = None


class FriendReq(BaseModel):
    wx_id: str
    nickname: str
    req_msg: str

