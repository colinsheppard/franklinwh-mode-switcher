import config
import logging

# Start strictly with config


# Mock logging to avoid clutter
logging.disable(logging.CRITICAL)

# Extract the known modes from main.py by inspecting the code or simply hardcoding the expectation 
# since we can't easily import the inner function scope map without refactoring.
# However, we can inspect 'Mode' usage or just define what we KNOW are valid modes based on our reading of main.py.
# In main.py:
# mode_factories = {
#     "time_of_use": Mode.time_of_use,
#     "emergency_backup": Mode.emergency_backup,
#     "self_consumption": Mode.self_consumption,
# }

VALID_MODES = {"time_of_use", "emergency_backup", "self_consumption"}

def verify():
    print("Verifying config.SCHEDULE...")
    valid = True
    for item in config.SCHEDULE:
        mode = item["mode"]
        if mode not in VALID_MODES:
            print(f"❌ INVALID MODE FOUND: '{mode}'")
            valid = False
        else:
            print(f"✅ Mode '{mode}' is valid.")
    
    if valid:
        print("\nSUCCESS: All configured modes are valid.")
    else:
        print("\nFAILURE: Invalid modes detected in config.py.")
        exit(1)

if __name__ == "__main__":
    verify()
