#!/bin/bash
# Deploy ImmerseAI to Google Cloud Run
# Usage: source set_env.sh && bash deploy.sh

set -e

PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"your-project-id"}
REGION=${GOOGLE_CLOUD_LOCATION:-"us-central1"}
SERVICE_NAME="immerse-ai"
IMAGE="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "🚀 Deploying ImmerseAI to Cloud Run..."
echo "   Project: $PROJECT_ID"
echo "   Region:  $REGION"
echo "   Service: $SERVICE_NAME"

# Build and push Docker image
gcloud builds submit --tag $IMAGE .

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
  --set-env-vars "GOOGLE_CLOUD_LOCATION=$REGION" \
  --set-env-vars "GOOGLE_GENAI_USE_VERTEXAI=true" \
  --set-env-vars "MONGODB_URI=$MONGODB_URI" \
  --set-env-vars "MONGODB_DB=$MONGODB_DB" \
  --set-env-vars "YOUTUBE_API_KEY=$YOUTUBE_API_KEY" \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --port 8080

echo "✅ Deployed! URL:"
gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)"
