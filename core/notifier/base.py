from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseNotifier(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", False)

    @abstractmethod
    async def send(self, title: str, content: str, **kwargs) -> bool:
        pass

    @abstractmethod
    async def send_markdown(self, title: str, content: str, **kwargs) -> bool:
        pass

    @abstractmethod
    async def send_image(self, title: str, image_path: str, **kwargs) -> bool:
        pass

    async def startup(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass
