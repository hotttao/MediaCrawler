from typing import List
from wxautox import WeChat
from weixin.internal.wx_auto.type import (
    ChatMsg,
    ChatInfo,
    FriendReq,
    Friend
)


class WxAuto:
    def __init__(self, wx_chat: WeChat):
        self.wx = wx_chat

    def get_chat_msg(self, nickname) -> ChatInfo:
        wx = self.wx
        wx.ChatWith(who=nickname)
        # 获取当前聊天窗口消息
        msgs = wx.GetAllMessage()
        chat_msgs = []
        chat_info = ChatInfo(
            nickname=nickname,
            content=[],
            last_id=-1,
            self_last_id=-1,
            self_last_msg="",
            friend_last_id=-1,
            friend_last_msg=""
        )
        
        for msg in msgs:
            if msg.attr not in ("self", "friend"):
                continue
            is_self = msg.attr == "self"
            chat_msg = ChatMsg(
                nickname="我" if is_self else nickname,
                type=msg.type,
                msg=msg.content,
                is_self=is_self
            )
            chat_info.content.append(chat_msg)
            chat_info.last_id = msg.id
            if is_self:
                chat_info.self_last_id = msg.id
                chat_info.self_last_msg = msg.content
            else:
                chat_info.friend_last_id = msg.id
                chat_info.friend_last_msg = msg.content
        return chat_info
    
    def get_friends(self, prefix="z_", n=None):
        friends = self.wx.GetFriendDetails(n=n)
        collect = []
        for i in friends:
            f = Friend(wx_id=i["微信号"], nickname=i["昵称"], remark=i["备注"])
            collect.append(f)
        return collect

    def get_new_friends(self) -> List[FriendReq]:
        wx = self.wx
        newfriends = wx.GetNewFriends(acceptable=True)
        new_req = []
        for friend in newfriends:
            req = FriendReq(
                wx_id=friend.info["id"],
                nickname=friend.info["name"],
                req_msg=friend.info["msg"]
                )
            new_req.append(req)
        return new_req
