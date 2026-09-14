# Global Disaster Monitoring System

A cloud-native disaster monitoring platform that collects earthquake data from the USGS API, processes events through Google Cloud Pub/Sub, stores them in Firestore, and displays them on a live dashboard.

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