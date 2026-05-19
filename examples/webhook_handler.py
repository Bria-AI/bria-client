"""
Bria Webhook Handler Example
=============================
Demonstrates how to:
  1. Submit an async job with a webhook_url so Bria POSTs results on completion.
  2. Receive and verify the signed Bria webhook in a FastAPI endpoint.
  3. (Optional) Use pyngrok to expose localhost for local development.

Requirements:
    pip install fastapi uvicorn bria-client
    pip install pyngrok          # only needed for local dev tunnel

Usage (local dev):
    python examples/webhook_handler.py

    The script starts a FastAPI server on port 8080, opens an ngrok tunnel,
    submits a job with the tunnel URL as the webhook, then waits.
    When Bria finishes the job it will POST to your local server.
"""

import asyncio
import json
import logging
import os

import uvicorn
from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request

try:
    from pyngrok import ngrok as _ngrok
except ImportError:
    _ngrok = None

from bria_client import BriaAsyncClient, verify_webhook_signature

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


# ---------------------------------------------------------------------------
# Webhook receiver endpoint
# ---------------------------------------------------------------------------

@app.post("/webhook")
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    bria_webhook_id: str = Header(...),
    bria_webhook_timestamp: str = Header(...),
    bria_webhook_signature: str = Header(...),
):
    """
    Receive a Bria webhook delivery.

    Bria signs every request with HMAC-SHA256. Always verify before processing.
    Respond with 2xx within 10 seconds; defer heavy work to a background task.
    """
    api_token = os.environ["BRIA_API_TOKEN"]
    body = await request.body()

    if not verify_webhook_signature(
        payload=body,
        webhook_id=bria_webhook_id,
        timestamp=bria_webhook_timestamp,
        signature_header=bria_webhook_signature,
        api_token=api_token,
    ):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    data = json.loads(body)
    logger.info("Webhook received", extra={"request_id": data.get("request_id"), "status": data.get("status")})

    # Defer any slow processing so the 2xx response is sent within 10s
    background_tasks.add_task(process_result, data)

    return {"ok": True}


async def process_result(data: dict):
    """Handle the completed job result."""
    logger.info("Processing result for request_id=%s status=%s", data.get("request_id"), data.get("status"))
    # Your processing logic here


# ---------------------------------------------------------------------------
# Submit a job with a webhook_url
# ---------------------------------------------------------------------------

async def submit_with_webhook(webhook_url: str):
    await asyncio.sleep(1)  # wait for uvicorn to finish starting
    async with BriaAsyncClient() as client:
        response = await client.submit(
            endpoint="image/edit/remove_background",
            payload={
                "image": "https://bria-test-images.s3.us-east-1.amazonaws.com/sun-example.png",
            },
            webhook_url=webhook_url,
        )
        logger.info("Job submitted, request_id=%s — waiting for webhook delivery", response.request_id)


# ---------------------------------------------------------------------------
# Local dev entrypoint: starts ngrok tunnel + uvicorn + submits a job
# ---------------------------------------------------------------------------

async def main():
    if _ngrok is not None:
        tunnel = _ngrok.connect(8080)
        public_url = tunnel.public_url
        logger.info("ngrok tunnel: %s", public_url)
    else:
        public_url = os.environ.get("WEBHOOK_URL")
        if not public_url:
            raise RuntimeError(
                "pyngrok is not installed and WEBHOOK_URL is not set. "
                "Either `pip install pyngrok` or set WEBHOOK_URL to a publicly reachable URL."
            )
        logger.info("Using WEBHOOK_URL: %s", public_url)

    webhook_url = f"{public_url}/webhook"

    config = uvicorn.Config(app, host="0.0.0.0", port=8080, log_level="info")
    server = uvicorn.Server(config)
    await asyncio.gather(
        server.serve(),
        submit_with_webhook(webhook_url),
    )


if __name__ == "__main__":
    asyncio.run(main())
