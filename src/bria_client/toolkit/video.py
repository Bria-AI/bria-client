from typing import TypeAlias

from pydantic import AnyHttpUrl

VideoSource: TypeAlias = AnyHttpUrl | str


class Video:
    def __init__(self, video: VideoSource) -> None:
        raise NotImplementedError
