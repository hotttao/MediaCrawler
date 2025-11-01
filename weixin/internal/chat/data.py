import pandas

from weixin.biz.model import Chat


class ChatData:
    def __init__(self, engine):
        self.engine = engine

    def get_all_chat(self):
        with self.engine.connect() as con:
            df_chat = pandas.read_sql("select * from chat", con=con)
        return df_chat
    
    def save(self, session, chat_info):
        Chat.upsert_by_remark(session, **chat_info)
