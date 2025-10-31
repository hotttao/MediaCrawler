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
    # account = WxAccount(wx_id="zzcc565511", nickname="木木", remark="z_白杨树卷纸投流品")
    # wx_auto_svc.extrac_merchant(account)
    # accounts = wx_auto_svc.get_friends(prefix="z_", max_num=None)
    # df = pandas.DataFrame([i.model_dump() for i in accounts])
    # df.to_csv("z_.csv", index=False)
    # df = pandas.read_csv("z_.csv")
    # accounts = [WxAccount
    # 
    # (**i) for i in df.to_dict("records")]
    # print(accounts)
    # wx_auto_svc.add_tag(accounts, ["商家"])
    # print(wx_auto_svc.get_friends(tag="z"))
    wx_auto_svc.get_group_msg("爆单🈺9班投流群（爆单10🈷️）")

if __name__ == "__main__":
    extract_product()
