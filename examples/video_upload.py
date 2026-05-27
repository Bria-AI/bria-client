import logging

from dotenv import load_dotenv

from bria_client import BriaSyncClient

load_dotenv()

logging.basicConfig(level=logging.ERROR)
logging.getLogger("bria_client").setLevel(logging.DEBUG)

VIDEO_PATH = "path/to/video.mp4"


def video_upload():
    with BriaSyncClient() as client:
        file_url = client.upload(VIDEO_PATH, media_type="video/mp4")

        response = client.submit(
            endpoint="video/edit/remove_background",
            payload={"video": file_url},
        )

        result = client.poll(response, timeout=300)
        return result


result = video_upload()
print(result)
