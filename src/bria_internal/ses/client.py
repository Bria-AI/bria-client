from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import IO, List, Tuple

import boto3

from bria_internal.common.singleton_meta import SingletonABCMeta


class SES(metaclass=SingletonABCMeta):
    def __init__(self):
        self.client = boto3.client("ses", region_name="us-east-1")

    def send_text_email(
        self,
        subject: str,
        body: str,
        to_list: List[str],
        sender: str = "Bria <noreply@bria.ai>",
        bcc_list: List[str] | None = None,
        attachments: List[Tuple[IO, str]] | None = None,
    ):
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = sender
        msg["Bcc"] = ",".join(bcc_list or [])
        msg["To"] = ",".join(to_list)

        mime_body = MIMEText(body, "plain")

        msg.attach(mime_body)
        if attachments:
            for file_obj, filename in attachments:
                part = MIMEApplication(file_obj.read())
                part.add_header("Content-Disposition", "attachment", filename=filename)
                msg.attach(part)

        return self.client.send_raw_email(RawMessage={"Data": msg.as_string()})

    def send_html_email(
        self,
        subject: str,
        body: str,
        to_list: List[str],
        sender: str = "Bria <noreply@bria.ai>",
        bcc_list: List[str] | None = None,
        attachments: List[Tuple[IO, str]] | None = None,
    ):
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = sender
        msg["Bcc"] = ",".join(bcc_list or [])
        msg["To"] = ",".join(to_list)

        html = MIMEText(body, "html")
        msg.attach(html)

        if attachments:
            for attachement, filename in attachments:
                part = MIMEApplication(attachement.read())
                part.add_header("Content-Disposition", "attachment", filename=filename)
                msg.attach(part)

        return self.client.send_raw_email(RawMessage={"Data": msg.as_string()})
