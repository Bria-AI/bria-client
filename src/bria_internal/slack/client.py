from slack_sdk import WebClient

from bria_internal.common.singleton_meta import SingletonABCMeta


class SlackClient(metaclass=SingletonABCMeta):
    def __init__(self, token: str):
        self._client = WebClient(token=token)

    def post_slack_message(self, channel_id: str, text: str):
        return self._client.chat_postMessage(channel=channel_id, text=text)
