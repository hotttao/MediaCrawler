"""

"""
import pandas
from weixin.biz.db.mysql import engine
from weixin.biz.db.wx import WX
from weixin.agent.init import llm
from weixin.biz.service.wx_auto import WeixinAutoService
from weixin.internal.wx_auto.type import WxAccount


def extract_product():
    wx_auto_svc = WeixinAutoService(
        llm=llm,
        wx_chat=WX,
        engine=engine
    )

    # 1. 缓存所有商家的微信昵称
    # wx_auto_svc.cache_merchant()

    # 2. 缓存所有商家的聊天记录
    friends = wx_auto_svc.load_merchant_cache()
    wx_auto_svc.cache_chat(friends)
    # account = WxAccount(wx_id="zzcc565511", nickname="木木", remark="z_白杨树卷纸投流品")
    # wx_auto_svc.extrac_merchant(account)
    
    # df = pandas.read_csv("z_.csv")
    # accounts = [WxAccount
    # 
    # (**i) for i in df.to_dict("records")]
    # print(accounts)
    # wx_auto_svc.add_tag(accounts, ["商家"])
    # print(wx_auto_svc.get_friends(tag="z"))
    # wx_auto_svc.get_group_msg("爆单🈺9班投流群（爆单10🈷️）")

if __name__ == "__main__":
    extract_product()
