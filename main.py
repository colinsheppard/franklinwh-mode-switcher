import os
import datetime
import pytz
import logging
from google.cloud import secretmanager
import functions_framework
from franklinwh import Client, Mode
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
            # Map string to Mode factory
            mode_factories = {
                "time_of_use": Mode.time_of_use,
                "emergency_backup": Mode.emergency_backup,
                "self_consumption": Mode.self_consumption,
            }
            
            if target_mode not in mode_factories:
                logger.error(f"Unknown target mode in config: {target_mode}")
                return f"Configuration error: unknown mode {target_mode}", 500

            # Create the Mode object
            # Use default SOCs for now, or we could add SOC to config later
            target_mode_obj = mode_factories[target_mode]()

            # Check current mode
            try:
                # get_mode returns (mode_name, soc)
                current_mode_tuple = client.get_mode()
                current_mode_name = current_mode_tuple[0]
                logger.info(f"Current mode is: {current_mode_name} (full info: {current_mode_tuple})")
            except (KeyError, RuntimeError) as e:
                # If we hit the 18513 error or similar, client.get_mode will likely raise KeyError or RuntimeError
                # In this case, we don't know the current mode, so we should attempt to switch anyway to be safe.
                logger.warning(f"Failed to determine current mode (likely unknown mode ID): {e}. Proceeding to switch.")
                current_mode_name = None

            if current_mode_name != target_mode:
                client.set_mode(target_mode_obj)
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
