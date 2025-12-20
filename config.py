# Configuration for FranklinWH Mode Switcher

# Schedule for mode switching
# Format: {"time": "HH:MM", "mode": "MODE_NAME"}
# Modes: "emergency_backup" (Emergency Backup), "time_of_use" (Time of Use), "self_consumption" (Self Use)
# Times are in 24-hour format.

SCHEDULE = [
    {"time": "00:00", "mode": "emergency_backup"},
    {"time": "15:00", "mode": "time_of_use"},
]

# Timezone for the schedule
TIMEZONE = "America/Los_Angeles" # Defaulting to user's likely timezone, can be changed
