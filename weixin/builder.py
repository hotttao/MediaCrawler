import os
import copy
import yaml
import pandas
from weixin.const import PATH_PRODUCT
from weixin.const import CHAT_EXAMPLE, CHAT_INFO
# from weixin.wx_msg import get_chat_msg
from weixin.agent import extract_product_info


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
    def __init__(self, path_product):
        self.path_product = path_product
        
        self.cache = self.load_cache()


    def load_cache(self):
        path_product = self.path_product
        if not os.path.exists(path_product):
            return {}
        
        reader = pandas.ExcelFile(path_product, engine='openpyxl')
        
        df_chat = pandas.read_excel(reader, sheet_name="chat")
        df_product = pandas.read_excel(reader, sheet_name="product")
        cache = {}
        for i in df_chat.to_dict("dict"):
            cache[i["nickname"]] = {
                "last_content": i["last_content"],
                "last_id": i["last_id"]
            }
        for nickname, df_product in df_product.groupby(by="nickname"):
            cache[nickname]["products"] = set(df_product["product_url"].tolist())
        
        return cache

    def is_chat_cached(self, chat_info):
        cache_chat = self.cache
        if chat_info["who"] in cache_chat and \
            chat_info["last_id"] == cache_chat["last_id"]:
            return True
        return False
    
    def filter_exists_product(self, chat_info, df_product):
        df_product["nickname"] = chat_info["who"]
        cache = self.cache.get(chat_info["who"], {})
        exists_product = cache.get("products", {})
        df_new = df_product[-df_product["product_url"].isin(exists_product)]
        return df_new
    
    def save(self, df, chat_info):
        if df.empty:
            return
        path = self.path_product
        is_exist = os.path.exists(path)
        df_chat = pandas.DataFrame([chat_info])
        if is_exist:        
            with pandas.ExcelWriter(path, engine='openpyxl', mode='a') as writer:
                df.to_excel(writer, sheet_name="product", index=False, header=False)
                df_chat.to_excel(writer, sheet_name="chat", index=False, header=False)
        else:
            with pandas.ExcelWriter(path, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name="product")
                df_chat.to_excel(writer, index=False, sheet_name="chat")

def main():
    db = ProductDB(PATH_PRODUCT)

    who = "z_白杨树卷纸投流品"
    # chat_info = get_chat_msg(who)
    chat_info = CHAT_INFO
    if db.is_chat_cached(chat_info):
        print(f'chat_info["who"] 最近消息已处理')
        return 
    product_info = extract_product_info(CHAT_EXAMPLE)
    df_product = format_product_info(product_info)
    
    df_new = db.filter_exists_product(chat_info, df_product)
    print(df_new)
    db.save(df_new, chat_info)
    

if __name__ == "__main__":
    main()