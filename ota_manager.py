"""
ota_manager.py - Simple OTA Update Manager with A/B Rollback

Usage:
    python ota_manager.py <source_c_file> <expected_checksum>
"""

import hashlib
import subprocess
import sys
import os
from datetime import datetime

ACTIVE_SLOT_FILE = "active_slot.txt"
LOG_FILE = "logs/update_log.txt"

def get_active_slot():
    with open(ACTIVE_SLOT_FILE, "r") as f:
        return f.read().strip()

def get_inactive_slot(active):
    return "B" if active == "A" else "A"

def calculate_checksum(filepath):
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def log_event(message):
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def main():
    if len(sys.argv) != 3:
        print("Usage: python ota_manager.py <source_c_file> <expected_checksum>")
        sys.exit(1)

    source_file = sys.argv[1]
    expected_checksum = sys.argv[2]

    active = get_active_slot()
    inactive = get_inactive_slot(active)

    target_bin = f"slots/slot{inactive}/firmware.bin"

    print(f"Current active slot: {active}")
    print(f"Installing new firmware into inactive slot: {inactive}")
    log_event(f"OTA update started. Active={active}, Target={inactive}, Source={source_file}")

    result = subprocess.run(["gcc", source_file, "-o", target_bin, "-Wl,--no-insert-timestamp"])
    if result.returncode != 0:
        print("Compilation failed. Aborting update.")
        log_event("Compilation FAILED. Update aborted. No changes made.")
        sys.exit(1)

    actual_checksum = calculate_checksum(target_bin)
    print(f"Expected checksum: {expected_checksum}")
    print(f"Actual checksum:   {actual_checksum}")

    if actual_checksum == expected_checksum:
        with open(ACTIVE_SLOT_FILE, "w") as f:
            f.write(inactive)
        print(f"VERIFICATION PASSED. Switching active slot to {inactive}.")
        log_event(f"Verification PASSED. Active slot switched from {active} to {inactive}.")
    else:
        print(f"VERIFICATION FAILED. Rolling back. Active slot remains {active}.")
        log_event(f"Verification FAILED. Rollback performed. Active slot remains {active}.")

if __name__ == "__main__":
    main()