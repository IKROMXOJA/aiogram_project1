from aiogram import BaseMiddleware
from typing import Any, Awaitable, Callable, Dict
from database import async_session_maker

class DataBaseSession(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any]
    ) -> Any:
        async with async_session_maker() as session:
            data["session"] = session   # 🔥 handlerlarga session yuboriladi
            return await handler(event, data)
