#!/bin/bash
# Simple deployment script for GCP Cloud Run

set -e

PROJECT_ID=${1:-${GOOGLE_CLOUD_PROJECT_ID}}
REGION=${2:-"us-central1"}
SERVICE_NAME="smarteventadder-api"

if [ -z "$PROJECT_ID" ]; then
    echo "Error: PROJECT_ID required. Usage: ./deploy.sh [PROJECT_ID] [REGION]"
    exit 1
fi

echo "🚀 Deploying SmartEventAdder API to Cloud Run"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"

# Enable required APIs
echo "📋 Enabling required Google Cloud APIs..."
gcloud services enable run.googleapis.com --project $PROJECT_ID
gcloud services enable cloudbuild.googleapis.com --project $PROJECT_ID
gcloud services enable artifactregistry.googleapis.com --project $PROJECT_ID
gcloud services enable aiplatform.googleapis.com --project $PROJECT_ID
gcloud services enable calendar-json.googleapis.com --project $PROJECT_ID
gcloud services enable gmail.googleapis.com --project $PROJECT_ID

# Build and deploy using Cloud Run source deployment
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --no-allow-unauthenticated \
    --memory 512Mi \
    --cpu 0.17 \
    --max-instances 3 \
    --min-instances 0 \
    --concurrency 1 \
    --timeout 180 \
    --set-env-vars "ENVIRONMENT=production,GOOGLE_CLOUD_PROJECT_ID=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=$REGION" \
    --project $PROJECT_ID

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format "value(status.url)" --project $PROJECT_ID)

echo "✅ Deployment completed!"
echo "Service URL: $SERVICE_URL"
echo "Health check: $SERVICE_URL/api/health"
echo "API docs: $SERVICE_URL/docs"