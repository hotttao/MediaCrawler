from wxauto import WeChat

# 初始化微信实例
wx = WeChat()

def get_chat_msg(who):
    wx.ChatWith(who=who)
    # 获取当前聊天窗口消息
    msgs = wx.GetAllMessage()
    collect = []
    chat_info = {"nickname": who}
    for msg in msgs:
        if msg.type != "text":
            continue
        if msg.attr == "friend":
            collect.append(f"{who}: {msg.content}")
        elif msg.attr == "self":
            collect.append(f"我: {msg.content}")
    content = "\n".join(collect)
    chat_info["content"] = content
    if collect:
        chat_info["last_msg"] = msg.content
        chat_info["last_id"] = msg.id
    return chat_info

if __name__ == "__main__":
    print(get_chat_msg("贝儿"))