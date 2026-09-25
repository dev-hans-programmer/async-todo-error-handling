from typing import Any


class AppError(Exception):
    code = "APP_ERROR"
    message = "An application error occurred"

    def __init__(self, details: dict[str,Any] | None = None):
        self.details = details
        super().__init__(self.message)



class UserAlreadyExists(AppError):
    code = "USER_ALREADY_EXISTS"
    message = "A user with this email already exists"


