import random
import time
from typing import List
from weixin.internal.wx_auto.type import WxAccount
from weixin.internal.wx_auto.biz import WxAuto
from weixin.internal.product.biz import ProductBiz
from weixin.internal.chat.biz import ChatBiz
from weixin.agent.node.merchant import extract_merchant_info
from weixin.agent.node.role import extract_role
from weixin.biz.db.mysql import get_db


class WeixinAutoService:
    def __init__(self, wx_chat, llm, engine):
        self.wx_auto = WxAuto(wx_chat)
        self.llm = llm
        self.biz_chat = ChatBiz.new(engine)
        self.biz_product = ProductBiz.new(engine)
    
    def get_friends(self, prefix="", max_num=None, tag=None) -> List[WxAccount]:
        return self.wx_auto.get_friends(prefix=prefix, n=max_num, tag=tag)

    def get_new_friends(self):
        return self.wx_auto.get_new_friends()
    
    def extrac_merchant(self, account: WxAccount):

        chat_info = self.wx_auto.get_chat_msg(account)
        # chat_info = CHAT_INFO
        if self.biz_chat.is_chat_cached(account.wx_id, chat_info.last_id):
            print(f'{chat_info["nickname"]} 最近消息已处理')
            return
        chat_content = chat_info.llm_content
        # chat_content = CHAT_EXAMPLE
        merchant_info = extract_merchant_info(llm=self.llm, wx_msg=chat_content)
        products = merchant_info.get("products", [])
        with get_db() as session:
            self.biz_product.save_from_llm(
                session, account.nickname, products
            )
            c = {
                "nickname": chat_info.account.nickname, 
                "last_msg": chat_info.last_msg, 
                "last_id": chat_info.last_id
            }
            self.biz_chat.save(session, c)

    def add_new_friends(self):
        new_reqs = self.get_new_friends()
        collect = []
        for i in new_reqs:
            req_parse = extract_role(self.llm, new_req=i.req_msg, nickname=i.nickname)
            print(req_parse, i.wx_id)
            i.wx_op.accept(remark=req_parse.remark, tags=[req_parse.role])
            collect.append(req_parse)
            time.sleep(random.uniform(3, 5))
            # msg = "宝子，你好，我们账号目前不会自己投流，后续如果需要会 dd，谢谢！"
        
        for req_parse in collect:
            if req_parse.role == "商家":
                msg = f"宝子，我们最近在广州学习，加晚了，请见谅！\n" \
                        "抖音号: 现在定位在<个护家清>，其他品暂时就不会带了。\n" \
                        "视频号: 只要是投流品都拍。\n" \
                        "团队人少，如果回复慢了，也请见谅！"
                self.wx_auto.chat(msg=msg, who=req_parse.remark)

    def add_tag(self, wx_accounts: List[WxAccount], tags):
        for i in wx_accounts:
            self.wx_auto.add_tag([i], tags)