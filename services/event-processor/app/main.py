import base64
import json
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request, Response
from google.cloud import firestore


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("event-processor")

app = FastAPI(
    title="Global Disaster Monitoring - Event Processor",
    version="0.2.0",
)

db = firestore.Client()
events_collection = db.collection("disaster_events")


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "event-processor",
        "version": "0.2.0",
        "status": "running",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}

@app.get("/events")
def get_events(
    limit: int = Query(default=20, ge=1, le=100),
    severity: str | None = None,
    event_type: str | None = None,
) -> dict[str, Any]:
    query = events_collection

    if severity:
        query = query.where("severity", "==", severity.upper())

    if event_type:
        query = query.where("type", "==", event_type.upper())

    query = query.limit(limit)

    documents = query.stream()

    events = []

    for document in documents:
        event = document.to_dict()
        event["document_id"] = document.id

        for key, value in event.items():
            if isinstance(value, datetime):
                event[key] = value.isoformat()

        events.append(event)

    return {
        "count": len(events),
        "filters": {
            "severity": severity,
            "event_type": event_type,
        },
        "events": events,
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
        save_event(event)

        logger.info(
            "Disaster event stored: event_id=%s type=%s severity=%s",
            event.get("event_id"),
            event.get("type"),
            event.get("severity"),
        )

        return Response(status_code=204)

    except ValueError as error:
        logger.error("Invalid disaster event: %s", error)
        return Response(status_code=400)

    except Exception:
        logger.exception("Unexpected error while processing event")
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


def save_event(event: dict[str, Any]) -> None:
    event_id = str(event["event_id"])

    event_to_store = dict(event)
    event_to_store["stored_at"] = datetime.now(timezone.utc)

    events_collection.document(event_id).set(
        event_to_store,
        merge=True,
    )