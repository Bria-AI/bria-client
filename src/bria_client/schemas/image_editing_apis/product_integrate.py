from pydantic import Field

from bria_client.schemas.base_models import ContentModeratedPayloadModel, APIPayloadModel


class ProductCoordinates(APIPayloadModel):
    x: int
    y: int
    width: int
    height: int


class ProductItem(APIPayloadModel):
    image: str
    coordinates: ProductCoordinates


class ProductIntegrateRequestPayload(ContentModeratedPayloadModel):
    scene: str
    products: list[ProductItem] = Field(min_length=1)
    seed: int | None = None
    sync: bool | None = None
