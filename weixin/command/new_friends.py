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
    wx_auto_svc.add_new_friends()    


if __name__ == "__main__":
    extract_product()
