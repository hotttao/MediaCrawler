from wxauto import WeChat

# 初始化微信实例
wx = WeChat()

# 发送消息
wx.SendMsg("你好", who="张三")

# 获取当前聊天窗口消息
msgs = wx.GetAllMessage()
for msg in msgs:
    print(f"消息内容: {msg.content}, 消息类型: {msg.type}")