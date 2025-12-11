#!/bin/bash

# Deploy the Cloud Function
gcloud functions deploy franklinwh-mode-switcher \
    --gen2 \
    --runtime=python310 \
    --region=us-central1 \
    --source=. \
    --entry-point=mode_switcher \
    --trigger-http \
    --allow-unauthenticated \
    --set-secrets="franklinwh-username=franklinwh-username:latest,franklinwh-password=franklinwh-password:latest,franklinwh-gateway-id=franklinwh-gateway-id:latest" \
    --set-env-vars="GCP_PROJECT=$(gcloud config get-value project)"

# Note: You need to create the secrets first:
# gcloud secrets create franklinwh-username --replication-policy="automatic"
# echo -n "YOUR_USERNAME" | gcloud secrets versions add franklinwh-username --data-file=-
# ... and so on for password and gateway-id.

# To set up the scheduler:
# gcloud scheduler jobs create http franklinwh-mode-switcher-job \
#   --schedule="*/5 * * * *" \
#   --uri="YOUR_FUNCTION_URL" \
#   --http-method=GET
