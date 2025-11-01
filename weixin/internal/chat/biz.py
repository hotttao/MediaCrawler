from weixin.internal.chat.data import ChatData

class ChatBiz:
    def __init__(self, data: ChatData):
        self.chat_data = data
        self.cache = self.load_cache()

    @classmethod
    def new(cls, engine):
        data = ChatData(engine)
        return cls(data)

    def load_cache(self):
        df_chat = self.chat_data.get_all_chat()
        cache = {}
        for i in df_chat.to_dict("records"):
            cache[i["remark"]] = {
                "last_msg": i["last_msg"],
                "last_id": str(i["last_id"])
            }
        return cache

    def is_chat_cached(self, remark, last_id):
        cache_chat = self.cache
        who = remark
        if who in cache_chat and last_id == cache_chat[who]["last_id"]:
            return True
        return False
    
    def save(self, session, chat_info):
        self.chat_data.save(session, chat_info)