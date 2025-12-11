# FranklinWH Mode Switcher

This project deploys a Google Cloud Function that automatically switches your FranklinWH battery mode based on a time schedule.

This is an unofficial tool that uses the [franklinwh python package](https://github.com/richo/franklinwh-python) (also an unofficial tool) and interacts with FranklinWH cloud APIs. This is not endorsed, supported, or reviewed by FranklinWH or any related entity.

**Please read the disclaimer at the bottom of this document before using this tool.**

# Getting Started

## Prerequisites

1.  **Google Cloud Platform (GCP) Account**: You need a GCP project with billing enabled.
2.  **FranklinWH Credentials**: Your username, password, and Gateway ID. Your Gateway ID can be found in the FranklinWH app under Settings > Device Info > SN (Serial Number is the Gateway ID).
3.  **Python 3.10+**: For local testing (optional).

## Step 1: Install Google Cloud SDK

If you don't have the `gcloud` command-line tool installed, follow these steps:

**macOS:**
1.  Install using Homebrew:
    ```bash
    brew install --cask google-cloud-sdk
    ```
2.  Initialize the SDK:
    ```bash
    gcloud init
    ```
    Follow the prompts to log in and select your project.

## Step 2: Configure the Project

1.  **Edit Schedule**: Open `config.py` and modify the `SCHEDULE` list to set your desired times and modes.
    ```python
    SCHEDULE = [
        {"time": "00:05", "mode": "emergency_backup"},
        {"time": "04:00", "mode": "time_of_use"},
    ]
    ```
    *   Supported modes: `emergency_backup`, `time_of_use`, `self_consumption`.
    *   Ensure `TIMEZONE` matches your local time.

## Step 3: Set Up Secrets

We use Google Secret Manager to securely store your FranklinWH credentials. Run the following commands in your terminal (replace placeholders with your actual values):

1.  **Enable APIs**:
    ```bash
    gcloud services enable cloudfunctions.googleapis.com \
        cloudbuild.googleapis.com \
        secretmanager.googleapis.com \
        cloudscheduler.googleapis.com \
        run.googleapis.com
    ```

2.  **Create Secrets**:
    ```bash
    # Create secrets
    gcloud secrets create franklinwh-username --replication-policy="automatic"
    gcloud secrets create franklinwh-password --replication-policy="automatic"
    gcloud secrets create franklinwh-gateway-id --replication-policy="automatic"

    # Add secret versions (replace YOUR_... with actual values)
    echo -n "YOUR_USERNAME" | gcloud secrets versions add franklinwh-username --data-file=-
    echo -n "YOUR_PASSWORD" | gcloud secrets versions add franklinwh-password --data-file=-
    echo -n "YOUR_GATEWAY_ID" | gcloud secrets versions add franklinwh-gateway-id --data-file=-
    ```

3.  **Grant Access to Secrets**:
    The Cloud Function needs permission to access these secrets. Run this command to grant the `Secret Manager Secret Accessor` role to your project's default compute service account:
    ```bash
    PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format="value(projectNumber)")
    
    gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
        --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
        --role="roles/secretmanager.secretAccessor"
    ```

## Step 4: Deploy the Function

Run the provided deployment script:

```bash
chmod +x deploy.sh
./deploy.sh
```

This will deploy the function to Google Cloud. It may take a few minutes.

## Step 5: Schedule the Trigger

The function needs to be triggered periodically to check the time. We'll use Cloud Scheduler to run it every 5 minutes.

1.  **Create the Job**:
    Run the following commands to get the function URL and create the scheduler job:
    ```bash
    # Get the function URL
    FUNCTION_URL=$(gcloud functions describe franklinwh-mode-switcher --gen2 --region=us-central1 --format="value(serviceConfig.uri)")

    # Create the scheduler job
    gcloud scheduler jobs create http franklinwh-mode-switcher-job \
      --schedule="*/5 * * * *" \
      --uri="$FUNCTION_URL" \
      --http-method=GET \
      --location=us-central1
    ```

## Verification

Check the logs to ensure it's running correctly:

```bash
gcloud functions logs read franklinwh-mode-switcher --gen2 --region=us-central1 --limit=20
```

# Disclaimer

This software is provided “as is”, without warranty of any kind, express or implied.
It is an unofficial tool that interacts with FranklinWH cloud APIs and is not endorsed, supported, or reviewed by FranklinWH or any related entity.

By using this software, you acknowledge and agree that:

* You assume all risks associated with running it, including but not limited to misconfiguration, loss of stored energy during an actual outage, unexpected system behavior, battery wear, or any operational or financial consequences.
* The author(s) make no guarantees about correctness, reliability, functionality, or fitness for any particular purpose.
* The author(s) are not responsible for any damages, losses, failures, malfunctions, missed backups, incorrect operating modes, or adverse outcomes that may arise from use of this software.
* You are solely responsible for ensuring that your energy system is configured and operated in a manner consistent with local regulations, utility requirements, warranty terms, and safe electrical practice.
* By running this software, you agree to release, indemnify, and hold harmless the author(s) from any and all claims, liabilities, damages, or losses of any kind arising directly or indirectly from its use.

If you do not agree to these terms, **do not use this software**.
