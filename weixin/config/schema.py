from pydantic import BaseModel, computed_field
from typing import Optional
from urllib.parse import quote

class MySQLConfig(BaseModel):
    host: str
    port: int = 3306
    user: str
    password: str
    database: str
    charset: str = 'utf8mb4'

    @computed_field
    @property
    def dsn(self) -> str:
        # 对用户名和密码进行 URL 编码
        encoded_user = quote(self.user, safe='')
        encoded_password = quote(self.password, safe='')
        return f"mysql+pymysql://{encoded_user}:{encoded_password}@{self.host}:{self.port}/{self.database}?charset={self.charset}"


class RedisConfig(BaseModel):
    host: str
    port: int = 6379
    password: Optional[str] = None
    db: int = 0
    ssl: bool = False

    @computed_field
    @property
    def dsn(self) -> str:
        scheme = "rediss" if self.ssl else "redis"
        auth_str = ""
        if self.password:
            # 对密码进行 URL 编码
            encoded_password = quote(self.password, safe='')
            auth_str = f":{encoded_password}@"
        return f"{scheme}://{auth_str}{self.host}:{self.port}/{self.db}"


class ElasticsearchConfig(BaseModel):
    hosts: str  # 多个 host 用逗号分隔
    port: int = 9200
    use_ssl: bool = False
    verify_certs: bool = True
    username: Optional[str] = None
    password: Optional[str] = None

    @computed_field
    @property
    def dsn(self) -> str:
        protocol = "https" if self.use_ssl else "http"
        auth_str = ""
        if self.username and self.password:
            # 对用户名和密码进行 URL 编码
            encoded_username = quote(self.username, safe='')
            encoded_password = quote(self.password, safe='')
            auth_str = f"{encoded_username}:{encoded_password}@"
        
        # 处理多个 hosts
        host_list = [f"{host.strip()}:{self.port}" for host in self.hosts.split(',') if host.strip()]
        host_str = ','.join(host_list)
        return f"{protocol}://{auth_str}{host_str}"


class Database(BaseModel):
    mysql: MySQLConfig
    redis: Optional[RedisConfig] = None
    es: Optional[ElasticsearchConfig] = None


class Config(BaseModel):
    database: Database
