from weixin.internal.wx_auto.type import WxAccount
from weixin.internal.wx_auto.biz import WxAuto
from weixin.internal.product.biz import ProductBiz
from weixin.internal.chat.biz import ChatBiz
from weixin.agent.node.merchant import extract_merchant_info
from weixin.biz.db.mysql import get_db


class WeixinAutoService:
    def __init__(self, wx_chat, llm, engine):
        self.wx_auto = WxAuto(wx_chat)
        self.llm = llm
        self.biz_chat = ChatBiz.new(engine)
        self.biz_product = ProductBiz.new(engine)
    
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
