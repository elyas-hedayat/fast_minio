from typing import Optional

import strawberry


@strawberry.type
class Message:
    message: str
    status_code: int
    id: Optional[str] = None


@strawberry.input
class Response:
    status_code: int
    id: str
