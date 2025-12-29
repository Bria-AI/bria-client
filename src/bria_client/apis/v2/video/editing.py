from bria_client.apis.api import api_endpoint
from bria_client.apis.v2.video.api import VideoAPI
from bria_client.payloads.video_editing_payload import VideoEraserPayload, VideoIncreaseResolutionPayload, VideoRemoveBackgroundPayload
from bria_client.results.video_editing import VideoEraserResult, VideoIncreaseResolutionResult, VideoRemoveBackgroundResult


class VideoEditingAPI(VideoAPI):
    path = "edit"

    @api_endpoint("remove_background")
    def remove_background(self, payload: VideoRemoveBackgroundPayload):
        """
        Remove the background of the video
        """
        response = self.api_engine.post(url=self.url, payload=payload, result_obj=VideoRemoveBackgroundResult)
        return response

    @api_endpoint("increase_resolution")
    def increase_video_resolution(self, payload: VideoIncreaseResolutionPayload):
        """
        Increase the resolution of the video
        """
        response = self.api_engine.post(url=self.url, payload=payload, result_obj=VideoIncreaseResolutionResult)
        return response

    @api_endpoint("erase")
    def erase(self, payload: VideoEraserPayload):
        """
        Erase the object from the video using mask video
        """
        response = self.api_engine.post(url=self.url, payload=payload, result_obj=VideoEraserResult)
        return response
