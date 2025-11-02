import copy
import pandas
import secrets
import string
from weixin.biz.model import Product, Merchant


def generate_secure_string(length: int) -> str:
    """
    生成加密安全的随机字符串（适合密码、token 等）。
    """
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


def format_product_info(products):
    c = []
    for p in products:
        commissions = p.pop("commissions", None)
        if not p.get("product_url"):
            p["product_url"] = generate_secure_string(16)
        if not commissions:
            print(f"未解析到佣金信息")
            continue
        if len(commissions) == 1:
            p["is_promoted"] = commissions[0]["is_promoted"]
            p["rate"] = commissions[0]["rate"]
            if "roi" in commissions[0]:
                p["roi"] = commissions[0]["roi"]
                p["roi_desc"] = commissions[0]["roi_desc"]
            c.append(p)
        else:
            for i in commissions:
                d = copy.deepcopy(p)
                d["is_promoted"] = i["is_promoted"]
                d["rate"] = i["rate"]
                if "roi" in i:
                    d["roi"] = i["roi"]
                    d["roi_desc"] = i["roi_desc"]
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
            r = {k: v for k, v in i.items() if not pandas.isna(v)}
            Product.create(session, **r)

    def save_merchant(self, session, remark, sample_count):
        Merchant.upsert_by_remark(db=session, remark=remark, sample_count=sample_count)