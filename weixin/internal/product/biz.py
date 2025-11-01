import pandas
from weixin.internal.product.data import format_product_info
from weixin.internal.product.data import ProductData


class ProductBiz:
    def __init__(self, data: ProductData):
        self.data = data
        self.cache = self.load_cache()
    
    @classmethod
    def new(cls, engine):
        data = ProductData(engine)
        return cls(data)

    def load_cache(self):
        df_product = self.data.load_all_product()    
        cache = {}
        if df_product.empty:
            return cache
        for remark, df_product in df_product.groupby(by="remark"):
            if remark not in cache:
                cache[remark] = {}
            cache[remark]["products"] = set(df_product["product_url"].tolist())
        return cache
    
    def filter_exists_product(self, remark, df_product):
        df_product["remark"] = remark
        cache = self.cache.get(remark, {})
        exists_product = cache.get("products", {})
        df_new = df_product[-df_product["product_url"].isin(exists_product)]
        return df_new

    def save_from_llm(self, session, remark, products):
        products = format_product_info(products)
        df_product = pandas.DataFrame(products)
        df_new = self.filter_exists_product(remark, df_product)
        self.data.save(session, df_new)   

    def save_merchant(self, session, remark, sample_count):
        self.data.save_merchant(session, remark, sample_count)