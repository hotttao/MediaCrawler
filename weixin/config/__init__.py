import dotenv
dotenv.load_dotenv()

from logging.config import dictConfig

from hydra import initialize, compose
from omegaconf import OmegaConf
from weixin.config.schema import Config

CONFIG = None

def load_config():
    with initialize(config_path="./", version_base="1.3"):
        # config is relative to a module
        cfg:dictConfig = compose(config_name="config.yaml", return_hydra_config=False)
    config_dict = OmegaConf.to_container(cfg, resolve=True)
    CONFIG = Config(**config_dict)
    return CONFIG
