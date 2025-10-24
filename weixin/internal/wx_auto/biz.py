from typing import List
from wxautox import WeChat
from weixin.internal.wx_auto.type import (
    ChatMsg,
    ChatInfo,
    FriendReq,
    WxAccount
)


class WxAuto:
    def __init__(self, wx_chat: WeChat):
        self.wx = wx_chat

    def chat(self, who, msg):
        self.wx.SendMsg(msg, who=who, exact=True)

    def get_chat_msg(self, account: WxAccount) -> ChatInfo:
        wx = self.wx
        wx.ChatWith(who=account.wx_id)
        # 获取当前聊天窗口消息
        msgs = wx.GetAllMessage()
        chat_msgs = []
        chat_info = ChatInfo(
            account=account,
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
                account=account,
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
    
    def get_friends(self, prefix, n=None, tag=None) -> WxAccount:
        friends = self.wx.GetFriendDetails(n=n, tag=tag)
        collect = []
        for i in friends:
            if "微信号" not in i:
                continue
            f = WxAccount(
                wx_id=i["微信号"], 
                nickname=i["昵称"], remark=i.get("备注", "")
            )
            if not prefix:
                collect.append(f)
            if prefix and f.remark.startswith(prefix):
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
                req_msg=friend.info["msg"],
                wx_op=friend
                )
            new_req.append(req)
        return new_req

    def add_tag(self, wx_accounts: List[WxAccount], tags):
        """
        给微信账号添加 tag
        """
        res = []
        for i in wx_accounts:
            self.wx.ChatWith(who=i.wx_id)
            r = self.wx.ManageFriend(tags=tags)
            res.append(r)
        return res