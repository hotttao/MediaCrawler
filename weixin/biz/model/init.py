from weixin.biz.db.mysql import engine, Base
Base.metadata.create_all(bind=engine)