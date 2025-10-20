from wxautox import WeChat
from weixin.internal.wx_auto.biz import WxAuto
from weixin.internal.wx_auto.type import WxAccount
# 初始化微信实例
wx = WeChat()
wx_auto = WxAuto(wx)

        
if __name__ == "__main__":
    account = WxAccount(wx_id="zzcc565511", nickname="木木", remark="z_白杨树卷纸投流品")
    # print(wx_auto.get_chat_msg(account))
    # print(wx_auto.get_friends(n=20))
    # print(wx_auto.get_new_friends())
    wx_auto.add_tag([account], ["商家"])