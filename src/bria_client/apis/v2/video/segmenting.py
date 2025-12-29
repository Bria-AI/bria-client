from bria_client.apis.api import api_endpoint
from bria_client.apis.v2.video.api import VideoAPI
from bria_client.payloads.video_editing_payload import VideoMaskByKeypointsPayload, VideoMaskByPromptPayload
from bria_client.results.video_segmenting import VideoMaskByKeypointsResult, VideoMaskByPromptResult


class VideoSegmentingAPI(VideoAPI):
    path = "segment"

    @api_endpoint("mask_by_prompt")
    def mask_by_prompt(self, payload: VideoMaskByPromptPayload):
        """
        Remove the detected prompt from the video
        """
        response = self.api_engine.post(url=self.url, payload=payload, result_obj=VideoMaskByPromptResult)
        return response

    @api_endpoint("mask_by_key_points")
    def mask_by_key_points(self, payload: VideoMaskByKeypointsPayload):
        """
        Remove the detected key-pointed object from the video
        """
        response = self.api_engine.post(url=self.url, payload=payload, result_obj=VideoMaskByKeypointsResult)
        return response
