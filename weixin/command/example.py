import hydra
from omegaconf import OmegaConf, DictConfig
from weixin.config.schema import Config


@hydra.main(config_path="../config", config_name="config.yaml", version_base="1.3")
def main(cfg: DictConfig) -> None:
    # Step 1: 将 OmegaConf DictConfig 转换为标准 Python 字典，并解析变量引用
    config_dict = OmegaConf.to_container(cfg, resolve=True)
    print(config_dict)
    # Step 2: 使用字典初始化 Pydantic 模型（自动验证）
    try:
        app_config = Config(**config_dict)
    except Exception as e:
        print("配置验证失败:", e)
        raise

    # Step 3: 使用配置
    print("✅ 配置加载成功！")

    print("MySQL DSN:", app_config.database.mysql.dsn)
    if app_config.database.redis:
        print("Redis DSN:", app_config.database.redis.dsn)
    if app_config.database.es:
        print("Elasticsearch DSN:", app_config.database.es.dsn)

if __name__ == "__main__":
    main()