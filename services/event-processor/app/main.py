import base64
import json
import logging
from typing import Any

from fastapi import FastAPI, Request, Response


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("event-processor")


app = FastAPI(
    title="Global Disaster Monitoring - Event Processor",
    version="0.1.0",
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "event-processor",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "healthy",
    }


@app.post("/pubsub")
async def process_pubsub_message(request: Request) -> Response:
    envelope: dict[str, Any] = await request.json()

    message = envelope.get("message", {})
    encoded_data = message.get("data")

    if not encoded_data:
        logger.warning("Received Pub/Sub message without data")
        return Response(status_code=400)

    try:
        decoded_data = base64.b64decode(encoded_data)
        event = json.loads(decoded_data.decode("utf-8"))

        validate_event(event)

        logger.info(
            "Disaster event processed: event_id=%s type=%s severity=%s",
            event.get("event_id"),
            event.get("type"),
            event.get("severity"),
        )

        return Response(status_code=204)

    except ValueError as error:
        logger.error("Invalid disaster event: %s", error)
        return Response(status_code=400)

    except Exception:
        logger.exception("Unexpected error while processing Pub/Sub message")
        return Response(status_code=500)


def validate_event(event: dict[str, Any]) -> None:
    required_fields = [
        "event_id",
        "type",
        "latitude",
        "longitude",
        "source",
    ]

    missing_fields = [
        field
        for field in required_fields
        if field not in event or event[field] is None
    ]

    if missing_fields:
        raise ValueError(
            f"Missing required fields: {', '.join(missing_fields)}"
        )

    if not isinstance(event["latitude"], (int, float)):
        raise ValueError("latitude must be a number")

    if not isinstance(event["longitude"], (int, float)):
        raise ValueError("longitude must be a number")

    if not -90 <= event["latitude"] <= 90:
        raise ValueError("latitude must be between -90 and 90")

    if not -180 <= event["longitude"] <= 180:
        raise ValueError("longitude must be between -180 and 180")