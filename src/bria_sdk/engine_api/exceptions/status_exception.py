from bria_sdk.engine_api.schemas.status_api import StatusAPIErrorBody, StatusAPIResponse


class InProgressException(Exception, StatusAPIResponse):
    pass


class StatusAPIException(Exception, StatusAPIErrorBody):
    pass
