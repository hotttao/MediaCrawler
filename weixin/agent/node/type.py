from typing import List, Optional
from pydantic import BaseModel, computed_field
import re

class User(BaseModel):
    role: str  # "商家" 或 "投手"
    brand: List[str]
    platform: List[str]
    shop: List[str]
    category: List[str]
    nickname: str  # 需要作为输入字段

    @computed_field
    @property
    def remark(self) -> str:
        """
        根据角色和信息生成用户昵称
        规则：
        - 如果是投手：z_投手_{nickname}
        - 如果是商家：z_{shop/brand}_{nickname}
        """
        # 清理 nickname，只保留安全字符
        safe_nickname = re.sub(r'[^\w\u4e00-\u9fff]', '', self.nickname).replace(" ", "")
        # 清理并生成前缀
        if self.role == "投手":
            prefix = "z_投手"
            remark = f"{prefix}_{safe_nickname}"
        else:  # 商家
            # 优先使用 shop，否则使用 brand
            identifier = self.brand[0] if self.brand else self.shop[0] if self.shop else "商家"
            # 移除特殊字符，只保留中文、英文、数字和下划线
            safe_identifier = re.sub(r'[^\w\u4e00-\u9fff]', '_', identifier)
            if safe_identifier in safe_nickname:
                remark = f"z_{safe_nickname}"
                return remark
            prefix = f"z_{safe_identifier}"
        
        # safe_nickname = ""
        remark = prefix
        if (safe_nickname not in remark) and safe_nickname:
            remark = f"{prefix}_{safe_nickname}"
        return remark