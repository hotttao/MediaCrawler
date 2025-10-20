from weixin.internal.product.data import extract_product_info

class IProduct:
    pass

class ProductBiz:
    def __init__(self, db: IProduct):
        pass


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