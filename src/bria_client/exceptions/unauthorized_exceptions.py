from bria_client.exceptions.bria_exception import BriaException


class MissingAuthenticationException(BriaException):
    code = 401
    message = "Missing authentication"
    details = "Either enter api_token to client, or provide BRIA_API_TOKEN environment variable"

    def __init__(self):
        super().__init__(message=self.message, details=self.details)
