from httpx import HTTPStatusError


class EngineAPIException(HTTPStatusError):
    def __init__(self, url: str, base_url: str | None = None, http_status_error: HTTPStatusError | None = None, **kwargs):
        self.route = url.replace(base_url, "")
        self.base_url = base_url
        self.kwargs = kwargs

        # Initialize the parent HTTPStatusError with the correct parameters
        if http_status_error is not None:
            super().__init__(
                message=http_status_error.args[0] if http_status_error.args else str(http_status_error),
                request=http_status_error.request,
                response=http_status_error.response,
            )
        else:
            # Fallback if no http_status_error is provided
            super().__init__(message="Engine API Error", request=None, response=None)
