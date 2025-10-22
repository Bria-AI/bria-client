class InProgressException(Exception):
    def __init__(self, request_id: str, status: str = "IN_PROGRESS"):
        self.request_id = request_id
        self.status = status
        super().__init__()


class StatusAPIException(Exception):
    def __init__(self, code: int, message: str, details: str):
        self.code = code
        self.message = message
        self.details = details
        super().__init__(self.message)
