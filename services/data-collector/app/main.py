import json
import os
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from google.cloud import pubsub_v1


app = FastAPI(
    title="Global Disaster Monitoring - Data Collector",
    version="0.2.0",
)


USGS_EARTHQUAKE_URL = (
    "https://earthquake.usgs.gov/earthquakes/feed/v1.0/"
    "summary/all_day.geojson"
)

PROJECT_ID = os.getenv(
    "GOOGLE_CLOUD_PROJECT",
    "global-disaster-monitoring",
)

PUBSUB_TOPIC = os.getenv(
    "PUBSUB_TOPIC",
    "disaster-events",
)


publisher = pubsub_v1.PublisherClient()

topic_path = publisher.topic_path(
    PROJECT_ID,
    PUBSUB_TOPIC,
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "disaster-data-collector",
        "version": "0.2.0",
        "status": "running",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "healthy",
    }


@app.get("/earthquakes")
async def get_earthquakes() -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(USGS_EARTHQUAKE_URL)
            response.raise_for_status()

        source_data = response.json()
        earthquakes = []

        for feature in source_data.get("features", []):
            properties = feature.get("properties", {})
            geometry = feature.get("geometry", {})
            coordinates = geometry.get("coordinates", [])

            if len(coordinates) < 2:
                continue

            longitude = coordinates[0]
            latitude = coordinates[1]
            depth = coordinates[2] if len(coordinates) > 2 else None

            magnitude = properties.get("mag")
            event_time = properties.get("time")

            occurred_at = None

            if event_time is not None:
                occurred_at = datetime.fromtimestamp(
                    event_time / 1000,
                    tz=timezone.utc,
                ).isoformat()

            event = {
                "event_id": feature.get("id"),
                "type": "EARTHQUAKE",
                "title": properties.get("title"),
                "magnitude": magnitude,
                "severity": calculate_severity(magnitude),
                "latitude": latitude,
                "longitude": longitude,
                "depth_km": depth,
                "place": properties.get("place"),
                "occurred_at": occurred_at,
                "source": "USGS",
                "source_url": properties.get("url"),
            }

            message_id = publish_event(event)
            event["message_id"] = message_id

            earthquakes.append(event)

        return {
            "source": "USGS",
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "count": len(earthquakes),
            "events": earthquakes,
        }

    except httpx.HTTPError as error:
        raise HTTPException(
            status_code=502,
            detail=f"Unable to retrieve earthquake data: {error}",
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to process earthquake data: {error}",
        ) from error


def publish_event(event: dict[str, Any]) -> str:
    message_data = json.dumps(event).encode("utf-8")

    future = publisher.publish(
        topic_path,
        message_data,
        event_type=event["type"],
        source=event["source"],
    )

    return future.result(timeout=15)


def calculate_severity(magnitude: float | None) -> str:
    if magnitude is None:
        return "UNKNOWN"

    if magnitude >= 6.0:
        return "CRITICAL"

    if magnitude >= 5.0:
        return "HIGH"

    if magnitude >= 4.0:
        return "MEDIUM"

    return "LOW"