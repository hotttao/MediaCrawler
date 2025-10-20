import copy
import yaml
import pandas

from weixin.config import get_db, engine
from weixin.biz.model import Product


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


class ProductData:
    def __init__(self):
        self.cache = self.load_cache()

    def load_cache(self):
        with engine.connect() as con:
            df_product = pandas.read_sql("select * from product", con=con)
        cache = {}
        for nickname, df_product in df_product.groupby(by="nickname"):
            cache[nickname]["products"] = set(df_product["product_url"].tolist())
        return cache
    
    def filter_exists_product(self, nickname, df_product):
        df_product["nickname"] = nickname
        cache = self.cache.get(nickname, {})
        exists_product = cache.get("products", {})
        df_new = df_product[-df_product["product_url"].isin(exists_product)]
        return df_new
    
    def save(self, df):
        if df.empty:
            return
        with get_db() as db:
            for i in df.to_dict("records"):
                Product.create(db, **i)
