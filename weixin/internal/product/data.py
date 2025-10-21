import copy
import pandas

from weixin.biz.model import Product


def format_product_info(products):
    c = []
    for p in products:
        commissions = p.pop("commissions", None)
        if not commissions:
            print(f"未解析到佣金信息")
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
    return c


class ProductData:
    def __init__(self, engine):
        self.engine = engine
    
    def load_all_product(self):
        with self.engine.connect() as con:
            df_product = pandas.read_sql("select * from product", con=con)
        return df_product
    
    def save(self, session, df):
        if df.empty:
            return
        for i in df.to_dict("records"):
            Product.create(session, **i)
