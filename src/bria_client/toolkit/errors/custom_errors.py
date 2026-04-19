from pydantic import Field, model_validator

from bria_client.toolkit.models import BriaError


class EndpointNotFoundError(BriaError):
    url: str = Field(exclude=True, repr=False)

    code: int = 404
    message: str = "Endpoint not found"
    details: str = ""

    @model_validator(mode="before")
    @classmethod
    def set_details(cls, data: dict) -> dict:
        if not data.get("details") and data.get("url"):
            data["details"] = f"The requested endpoint does not exist: {data['url']}"
        return data


class ServerConnectionError(BriaError):
    url: str = Field(exclude=True, repr=False)

    code: int = 503
    message: str = "Connection error"
    details: str = ""

    @model_validator(mode="before")
    @classmethod
    def set_details(cls, data: dict) -> dict:
        if not data.get("details") and data.get("url"):
            data["details"] = f"Failed to connect to the server: {data['url']}"
        return data
