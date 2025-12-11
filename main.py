import os
import datetime
import pytz
import logging
from google.cloud import secretmanager
import functions_framework
from franklinwh import Client
from franklinwh.client import TokenFetcher

import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_secret(secret_id, project_id=None):
    """
    Retrieve a secret from Google Secret Manager.
    """
    if not project_id:
        project_id = os.environ.get("GCP_PROJECT")
    
    if not project_id:
        # Fallback for local testing if GCP_PROJECT env var is not set
        # You might want to set this in your local environment
        logger.warning("GCP_PROJECT not set, attempting to use default project or fail.")
        return None

    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    
    try:
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        logger.error(f"Failed to access secret {secret_id}: {e}")
        return None

def get_franklin_client():
    """
    Initialize and authenticate the FranklinWH client.
    """
    username = get_secret("franklinwh-username")
    password = get_secret("franklinwh-password")
    gateway_id = get_secret("franklinwh-gateway-id")
    
    # For local testing, allow env vars if secrets fail or are not set up
    if not username:
        username = os.environ.get("FRANKLINWH_USERNAME")
    if not password:
        password = os.environ.get("FRANKLINWH_PASSWORD")
    if not gateway_id:
        gateway_id = os.environ.get("FRANKLINWH_GATEWAY_ID")

    if not username or not password or not gateway_id:
        logger.error("Missing FranklinWH credentials.")
        raise ValueError("Missing FranklinWH credentials")

    try:
        fetcher = TokenFetcher(username, password)
        client = Client(fetcher, gateway_id)
        return client
    except Exception as e:
        logger.error(f"Failed to authenticate with FranklinWH: {e}")
        raise

@functions_framework.http
def mode_switcher(request):
    """
    Cloud Function entry point.
    """
    logger.info("Starting mode_switcher execution.")
    
    try:
        client = get_franklin_client()
    except Exception as e:
        return f"Authentication failed: {e}", 500

    # Get current time in the configured timezone
    tz = pytz.timezone(config.TIMEZONE)
    now = datetime.datetime.now(tz)
    current_time_str = now.strftime("%H:%M")
    
    logger.info(f"Current time: {current_time_str} ({config.TIMEZONE})")

    # Check schedule
    target_mode = None
    for item in config.SCHEDULE:
        if item["time"] == current_time_str:
            target_mode = item["mode"]
            break
            
    if target_mode:
        logger.info(f"Time match found! Switching to mode: {target_mode}")
        try:
            # Check current mode first to avoid unnecessary calls?
            # The library has get_mode()
            current_mode = client.get_mode()
            logger.info(f"Current mode is: {current_mode}")
            
            if current_mode != target_mode:
                client.set_mode(target_mode)
                logger.info(f"Successfully switched to {target_mode}")
                return f"Switched to {target_mode}", 200
            else:
                logger.info(f"Already in {target_mode} mode. No action needed.")
                return f"Already in {target_mode}", 200
                
        except Exception as e:
            logger.error(f"Failed to switch mode: {e}")
            return f"Failed to switch mode: {e}", 500
    else:
        logger.info("No schedule match for current time.")
        return "No action taken", 200
