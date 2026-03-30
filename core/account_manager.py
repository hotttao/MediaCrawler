from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
import asyncio
import time


class AccountStatus(Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    BANNED = "banned"
    ERROR = "error"


@dataclass
class Account:
    account_id: str
    nickname: str = ""
    phone: str = ""
    cookies: Optional[str] = None
    status: AccountStatus = AccountStatus.AVAILABLE
    browser_context: Optional[Any] = None
    use_count: int = 0
    error_count: int = 0
    last_used_time: float = 0
    ban_reason: Optional[str] = None
    consecutive_errors: int = 0
    max_consecutive_errors: int = 3

    def to_dict(self) -> Dict[str, Any]:
        return {
            "account_id": self.account_id,
            "nickname": self.nickname,
            "phone": self.phone,
            "cookies": self.cookies or "",
        }

    def mark_used(self) -> None:
        self.use_count += 1
        self.last_used_time = time.time()
        self.status = AccountStatus.IN_USE

    def mark_available(self) -> None:
        self.status = AccountStatus.AVAILABLE
        self.error_count = 0
        self.consecutive_errors = 0

    def mark_banned(self, reason: str) -> None:
        self.status = AccountStatus.BANNED
        self.ban_reason = reason

    def record_error(self) -> None:
        self.error_count += 1
        self.consecutive_errors += 1
        if self.consecutive_errors >= self.max_consecutive_errors:
            self.mark_banned("连续错误次数过多")

    def should_ban(self) -> bool:
        return self.consecutive_errors >= self.max_consecutive_errors


class AccountManager:
    def __init__(self):
        self.accounts: List[Account] = []
        self._lock = asyncio.Lock()

    async def init_accounts(self) -> None:
        from config.account_config import ACCOUNTS

        for acc in ACCOUNTS:
            account = Account(
                account_id=acc["account_id"],
                nickname=acc.get("nickname", ""),
                phone=acc.get("phone", ""),
                cookies=acc.get("cookies", ""),
            )
            self.accounts.append(account)

    async def get_account_stats(self) -> Dict[str, int]:
        return {
            "total": len(self.accounts),
            "available": len(
                [a for a in self.accounts if a.status == AccountStatus.AVAILABLE]
            ),
        }

    async def get_available_accounts(self) -> List[Account]:
        return [a for a in self.accounts if a.status == AccountStatus.AVAILABLE]

    async def get_available_account(self) -> Optional[Account]:
        available = await self.get_available_accounts()
        return available[0] if available else None

    async def ban_account(self, account: Account, reason: str) -> None:
        account.mark_banned(reason)

    async def release_account(self, account: Account) -> None:
        account.mark_available()
