import pandas

from weixin.config import get_db, engine
from weixin.biz.model import Chat


class ChatData:
    def __init__(self):
        self.cache = self.load_cache()


    def load_cache(self):
        with engine.connect() as con:
            df_chat = pandas.read_sql("select * from chat", con=con)
        cache = {}
        for i in df_chat.to_dict("records"):
            cache[i["nickname"]] = {
                "last_msg": i["last_msg"],
                "last_id": str(i["last_id"])
            }
        return cache

    def is_chat_cached(self, chat_info):
        cache_chat = self.cache
        who = chat_info["nickname"]
        if who in cache_chat and \
            chat_info["last_id"] == cache_chat[who]["last_id"]:
            return True
        return False
    
    def save(self, chat_info):
        with get_db() as db:
            Chat.upsert_by_nickname(db, **chat_info)
