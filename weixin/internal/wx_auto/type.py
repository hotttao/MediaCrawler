import io
from pydantic import BaseModel
from typing import Optional, List, Any

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

    def to_text(self, split="\n"):
        if self.type != "text":
                return ""
        if self.is_self:
            return f"我: {self.msg}{split}"
        else:
            nickname = self.account.remark or self.account.nickname
            return f"{nickname}: {self.msg}{split}"


class ChatInfo(BaseModel):
    account: WxAccount
    content: List[ChatMsg]
    last_id: int
    self_last_msg: Optional[str] = None
    self_last_id: Optional[int] = None
    friend_last_msg: Optional[str] = None
    friend_last_id: Optional[int] = None

    def to_dict(self):
        c = self.model_dump()
        c["account"] = self.account.remark
        del c["content"]
        return c

    @property
    def last_msg(self):
        return self.friend_last_msg \
            if self.last_id == self.friend_last_id else self.self_last_msg

    @property
    def llm_content_csv(self):
        buffer = io.StringIO()
        for s in self.content:
            buffer.write(s.to_text(split="\n\n"))
        return buffer.getvalue()

    @property
    def llm_content(self):
        buffer = io.StringIO()
        for s in self.content:
            buffer.write(s.to_text())
        return buffer.getvalue()

class FriendReq(BaseModel):
    wx_id: str
    nickname: str
    req_msg: str
    wx_op: Any


class GroupChatMsg(BaseModel):
    nickname: str
    msg: str
    type: str


class GroupChatInfo(BaseModel):
    group: str # 群名称
    content: List[GroupChatMsg]
    last_id: int
    last_msg: str

    @property
    def llm_content(self):
        buffer = io.StringIO()
        for s in self.content:
            buffer.write(f"{s.nickname}: {s.msg}\n")
        return buffer.getvalue()
