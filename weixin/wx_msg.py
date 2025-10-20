from wxautox import WeChat
from weixin.internal.wx_auto.biz import WxAuto
# 初始化微信实例
wx = WeChat()
wx_auto = WxAuto(wx)

        
if __name__ == "__main__":
    # print(get_chat_msg("贝儿"))
    print(wx_auto.get_friends())