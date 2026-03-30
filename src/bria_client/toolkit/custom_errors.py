from pydantic import Field, field_validator

from bria_client.toolkit import BriaError


class EndpointNotFoundError(BriaError):
    url: str = Field(exclude=True)

    code: int = 404
    message: str = "Endpoint not found"
    details: str = "The requested endpoint does not exist"

    @field_validator("details", mode="before")
    @classmethod
    def set_details(cls, v, info):
        if not v and info.data.get("url"):
            return f"The requested endpoint does not exist: {info.data['url']}"
        return v
