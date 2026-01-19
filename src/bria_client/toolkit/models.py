from typing import Any

from pydantic import BaseModel, model_serializer
from pydantic_core.core_schema import SerializationInfo, SerializerFunctionWrapHandler


class ExcludeNoneBaseModel(BaseModel):
    # noinspection PyUnusedLocal
    @model_serializer(mode="wrap")
    def serialize_model(self, handler: SerializerFunctionWrapHandler, info: SerializationInfo) -> dict[str, Any]:
        result = handler(self)
        # force exclude_none=True over BaseModel
        result = {k: v for k, v in result.items() if v is not None}
        return result
