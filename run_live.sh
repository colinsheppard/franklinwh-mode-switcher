#!/bin/bash

# Usage: ./run_live.sh <username> <password> <gateway_id>
# Or set env vars directly in this file (be careful not to commit secrets!)

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <username> <password> <gateway_id>"
    echo "Alternatively, edit this script to set defaults (but don't commit it!)."
#   exit 1
fi

export FRANKLINWH_USERNAME="$1"
export FRANKLINWH_PASSWORD="$2"
export FRANKLINWH_GATEWAY_ID="$3"
# Set a dummy GCP_PROJECT to trigger local logic in main.py if needed, 
# although main.py logic for get_secret falls back to env vars if project is set but secret fails, 
# or if project is NOT set.
# main.py: if not project_id: ... logger.warning ... return None. 
# So we actually want GCP_PROJECT to be unset or set to something that causes get_secret to return None 
# but hopefully main.py handles it.
# Let's check main.py again. get_secret returns None if project_id is missing or if secret access fails.
# Then get_franklin_client falls back to os.environ if get_secret returns None.
# So we are good.

# Run the function locally using functions-framework or just python if we had a dedicated runner.
# Since main.py is a cloud function, we can use functions-framework.
# pip install functions-framework (it's in requirements.txt)

echo "Starting functions-framework with provided credentials..."
./.venv/bin/functions-framework --target=mode_switcher --debug
