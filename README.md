
# Global Disaster Monitoring System

A cloud-native disaster monitoring platform that collects earthquake data from the USGS API, processes events through Google Cloud Pub/Sub, stores them in Google Cloud Firestore, and displays them on a live dashboard.

## Project Overview

The Global Disaster Monitoring System is designed to collect, process, store, and visualize disaster-related events in near real time.

The current implementation focuses on earthquake monitoring using data from the United States Geological Survey (USGS).

## Architecture

```text
USGS Earthquake API
        |
        v
Cloud Run: Data Collector
        |
        v
Google Cloud Pub/Sub
        |
        v
Cloud Run: Event Processor
        |
        v
Google Cloud Firestore
        |
        v
Cloud Run: Dashboard
```

## Main Components

### 1. Data Collector

The data collector retrieves earthquake information from the USGS earthquake API.

Responsibilities:

- Fetch earthquake events.
- Calculate event severity.
- Normalize event data.
- Publish events to Google Cloud Pub/Sub.
- Expose health and collection endpoints.

### 2. Google Cloud Pub/Sub

Pub/Sub provides asynchronous communication between the data collector and event processor.

Responsibilities:

- Receive earthquake events from the collector.
- Deliver events to the event processor.
- Decouple data collection from event processing.

### 3. Event Processor

The event processor is a FastAPI service that receives Pub/Sub messages and stores validated events in Firestore.

Responsibilities:

- Decode Pub/Sub messages.
- Validate event data.
- Validate latitude and longitude values.
- Store events in Firestore.
- Provide an API for retrieving stored events.

### 4. Google Cloud Firestore

Firestore stores disaster events in the `disaster_events` collection.

Each event may contain:

- Event ID
- Event type
- Latitude
- Longitude
- Source
- Magnitude
- Severity
- Event timestamp
- Storage timestamp

### 5. Dashboard

The dashboard provides a web-based interface for viewing disaster events.

Responsibilities:

- Display earthquake events.
- Show event locations.
- Display severity information.
- Support event filtering.
- Retrieve event data from the event processor API.

### 6. Cloud Scheduler

Cloud Scheduler triggers the data collector periodically.

Current schedule:

```text
Every 15 minutes
```

### 7. Cloud Monitoring and Logging

Google Cloud Monitoring and Cloud Logging are used to observe the deployed services.

They support:

- Service health monitoring.
- Uptime checks.
- Application log inspection.
- Operational troubleshooting.

## Technologies

- Python
- FastAPI
- Docker
- Google Cloud Run
- Google Cloud Pub/Sub
- Google Cloud Firestore
- Google Cloud Scheduler
- Google Cloud Monitoring
- Google Cloud Logging
- Google Artifact Registry
- HTML
- CSS
- JavaScript
- GitHub

## Google Cloud Configuration

### Project

```text
Project ID: global-disaster-monitoring
```

### Region

```text
europe-north1
```

### Artifact Registry Repository

```text
disaster-monitor-repo
```

### Pub/Sub Topic

```text
disaster-events
```

### Pub/Sub Subscription

```text
disaster-events-sub
```

### Firestore Collection

```text
disaster_events
```

## Cloud Run Services

The project currently uses the following Cloud Run services:

```text
disaster-data-collector
event-processor
disaster-dashboard
```

## API Endpoints

### Data Collector

```text
GET /
GET /health
GET /collect
```

### Event Processor

```text
GET /
GET /health
GET /events
POST /pubsub
```

## Event Processor API

### Get Recent Events

```text
GET /events?limit=10
```

### Filter by Severity

```text
GET /events?severity=HIGH
```

Supported severity values depend on the event data, for example:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

### Filter by Event Type

```text
GET /events?event_type=EARTHQUAKE
```

### Combine Filters

```text
GET /events?limit=20&severity=HIGH&event_type=EARTHQUAKE
```

## Example Event Structure

```json
{
  "event_id": "example-event-001",
  "type": "EARTHQUAKE",
  "latitude": 59.3293,
  "longitude": 18.0686,
  "source": "USGS",
  "magnitude": 5.2,
  "severity": "HIGH"
}
```

## Local Development

### Clone the Repository

```powershell
git clone https://github.com/Gihchathur/global-disaster-monitor.git
cd global-disaster-monitor
```

### Create a Python Virtual Environment

```powershell
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### Install Dependencies

Install the dependencies for the relevant service:

```powershell
pip install -r requirements.txt
```

### Run a FastAPI Service Locally

From the service directory:

```powershell
uvicorn app.main:app --reload
```

## Running Tests

Run tests from the relevant service directory:

```powershell
python -m pytest -q
```

The project includes tests for:

- Severity calculation.
- Event validation.
- Latitude validation.
- Longitude validation.
- Health endpoints.
- Root endpoints.
- Invalid Pub/Sub messages.

## Docker Development

### Build a Docker Image

Example:

```powershell
docker build -t disaster-monitor-service .
```

### Run a Docker Container

```powershell
docker run -p 8080:8080 disaster-monitor-service
```

## Deployment

The services are deployed to Google Cloud Run.

Container images are stored in Google Artifact Registry.

Example Artifact Registry image format:

```text
europe-north1-docker.pkg.dev/global-disaster-monitoring/disaster-monitor-repo/SERVICE_NAME:VERSION
```

Example Cloud Run deployment command:

```powershell
gcloud run deploy SERVICE_NAME `
  --image=IMAGE_URL `
  --region=europe-north1 `
  --project=global-disaster-monitoring
```

## Security

The project uses dedicated service accounts for its cloud services:

- Data collector service account
- Event processor service account
- Cloud Scheduler service account

The service accounts are granted only the permissions required for their respective tasks.

The current architecture should be further improved by introducing a separate public read-only API for dashboard access while keeping the Pub/Sub event-processing endpoint private.

## Monitoring and Operations

Useful commands for inspecting deployed services:

### List Cloud Run Services

```powershell
gcloud run services list `
  --region=europe-north1 `
  --project=global-disaster-monitoring
```

### View Cloud Run Logs

```powershell
gcloud logging read `
  'resource.type="cloud_run_revision"' `
  --limit=20 `
  --project=global-disaster-monitoring
```

### List Cloud Scheduler Jobs

```powershell
gcloud scheduler jobs list `
  --location=europe-west1 `
  --project=global-disaster-monitoring
```

## Project Structure

```text
global-disaster-monitor/
│
├── services/
│   ├── data-collector/
│   │   ├── app/
│   │   │   └── main.py
│   │   ├── tests/
│   │   │   └── test_main.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── event-processor/
│       ├── app/
│       │   └── main.py
│       ├── tests/
│       │   └── test_main.py
│       ├── Dockerfile
│       └── requirements.txt
│
├── dashboard/
│   ├── index.html
│   └── ...
│
├── README.md
└── .gitignore
```

## Future Improvements

- Add a separate public read-only API for the dashboard.
- Add authentication and authorization.
- Add automated CI/CD with GitHub Actions or Cloud Build.
- Add more disaster data sources.
- Add flood, wildfire, storm, and volcanic activity monitoring.
- Add email and messaging notifications.
- Add historical event analytics.
- Add event trend visualizations.
- Add automated integration tests.
- Add infrastructure as code using Terraform.
- Add better dashboard filtering and search.
- Add a production database indexing strategy.
- Improve error handling and retry logic.
- Add structured JSON logging.
- Add performance and load testing.

## Author

**Gihan Chathuranga**

GitHub:  
https://github.com/Gihchathur/global-disaster-monitor