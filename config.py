# Configuration for FranklinWH Mode Switcher

# Schedule for mode switching
# Format: {"time": "HH:MM", "mode": "MODE_NAME"}
# Modes: "backup" (Emergency Backup), "tou" (Time of Use), "self_use" (Self Use)
# Times are in 24-hour format.

SCHEDULE = [
    {"time": "00:05", "mode": "emergency_backup"},
    {"time": "04:00", "mode": "time_of_use"},
]

# Timezone for the schedule
TIMEZONE = "America/Los_Angeles" # Defaulting to user's likely timezone, can be changed
