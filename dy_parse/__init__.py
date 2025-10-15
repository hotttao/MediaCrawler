from wxauto import WeChat

# 初始化微信实例
wx = WeChat()
wx.ChatWith(who="贝儿")
# 获取当前聊天窗口消息
msgs = wx.GetAllMessage()
collect = []
for msg in msgs:
    if msg.type == "text":
        collect.append(msg.content)
print(collect)