from contextvars import ContextVar

source_keyword_var: ContextVar[str] = ContextVar("source_keyword_var", default="")
crawler_type_var: ContextVar[str] = ContextVar("crawler_type_var", default="")
request_keyword_var: ContextVar[str] = ContextVar("request_keyword_var", default="")
