import os
import copy
import yaml
import pandas
from weixin.const import PATH_PRODUCT
from weixin.const import CHAT_EXAMPLE, CHAT_INFO
from weixin.wx_msg import get_chat_msg
from weixin.agent import extract_product_info
from weixin.config import get_db, engine
from weixin.model import Chat, Product

def format_product_info(llm_res):
    try:
        llm_res = llm_res.strip()
        data = yaml.safe_load(llm_res)
    except Exception as e:
        
        print(f"解析异常: \n {e}")
        return []
    c = []
    for p in data:
        commissions = p.pop("commissions", None)
        if not commissions:
            print(f"未解析到佣金信息: \n{llm_res}")
            continue
        if len(commissions) == 1:
            p["is_promoted"] = commissions[0]["is_promoted"]
            p["rate"] = commissions[0]["rate"]
            c.append(p)
        else:
            for i in commissions:
                d = copy.deepcopy(p)
                d["is_promoted"] = i["is_promoted"]
                d["rate"] = i["rate"]
                c.append(d)
    return pandas.DataFrame(c)
    


def is_cached(chat_info, df_product, cache):
    empty = pandas.DataFrame()
    if chat_info["who"] in cache and chat_info["last_id"] == cache["last_id"]:
        return empty
    exists_product = cache.get("products", {})
    df_product = df_product[-df_product["product_url"].isin(exists_product)]
    return df_product


class ProductDB:
    def __init__(self):
        self.cache = self.load_cache()


    def load_cache(self):
        with engine.connect() as con:
            df_chat = pandas.read_sql("select * from chat", con=con)
            df_product = pandas.read_sql("select * from product", con=con)
        cache = {}
        for i in df_chat.to_dict("records"):
            cache[i["nickname"]] = {
                "last_msg": i["last_msg"],
                "last_id": str(i["last_id"])
            }
        for nickname, df_product in df_product.groupby(by="nickname"):
            cache[nickname]["products"] = set(df_product["product_url"].tolist())
        
        return cache

    def is_chat_cached(self, chat_info):
        cache_chat = self.cache
        who = chat_info["nickname"]
        if who in cache_chat and \
            chat_info["last_id"] == cache_chat[who]["last_id"]:
            return True
        return False
    
    def filter_exists_product(self, chat_info, df_product):
        df_product["nickname"] = chat_info["nickname"]
        cache = self.cache.get(chat_info["nickname"], {})
        exists_product = cache.get("products", {})
        df_new = df_product[-df_product["product_url"].isin(exists_product)]
        return df_new
    
    def save(self, df, chat_info):
        if df.empty:
            return
        with get_db() as db:
            Chat.upsert_by_nickname(db, **chat_info)
            for i in df.to_dict("records"):
                Product.create(db, **i)

def main():
    db = ProductDB()

    who = "z_金纺"
    chat_info = get_chat_msg(who)
    # chat_info = CHAT_INFO
    if db.is_chat_cached(chat_info):
        print(f'{chat_info["nickname"]} 最近消息已处理')
        return
    chat_content = chat_info.pop("content")
    # chat_content = CHAT_EXAMPLE
    product_info = extract_product_info(chat_content)
    df_product = format_product_info(product_info)
    
    df_new = db.filter_exists_product(chat_info, df_product)
    db.save(df_new, chat_info)
    

if __name__ == "__main__":
    main()