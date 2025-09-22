#!/bin/bash
# Simple deployment script for GCP Cloud Run

set -e

PROJECT_ID=${1:-${GOOGLE_CLOUD_PROJECT_ID}}
REGION=${2:-"asia-northeast1"}
SERVICE_NAME="smarteventadder-api"

if [ -z "$PROJECT_ID" ]; then
    echo "Error: PROJECT_ID required. Usage: ./deploy.sh [PROJECT_ID] [REGION]"
    exit 1
fi

echo "🚀 Deploying SmartEventAdder API to Cloud Run"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"

# Build and deploy using Cloud Run source deployment (simpler than Docker)
gcloud run deploy $SERVICE_NAME \
    --source . \
    --dockerfile Dockerfile \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars "ENVIRONMENT=production,GOOGLE_CLOUD_PROJECT_ID=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=$REGION" \
    --project $PROJECT_ID

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format "value(status.url)" --project $PROJECT_ID)

echo "✅ Deployment completed!"
echo "Service URL: $SERVICE_URL"
echo "Health check: $SERVICE_URL/api/health"
echo "API docs: $SERVICE_URL/docs"