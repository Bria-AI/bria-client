from werkzeug.exceptions import HTTPException


class BriaException(HTTPException):
    code = 500
    description = "Internal Server Error"

    def __init__(self, *, status_code: int | None = None, message: str | None = None, details: str | None = None) -> None:
        if status_code is not None:
            self.code = status_code

        self.details = details
        self.message = message
        if message is not None:
            self.description = self.details
        super().__init__()

    @property
    def name(self) -> str:
        return self.message

    @classmethod
    def from_error(cls, code: int, message: str, details: str):
        return cls(
            status_code=code,
            message=message,
            details=details,
        )
