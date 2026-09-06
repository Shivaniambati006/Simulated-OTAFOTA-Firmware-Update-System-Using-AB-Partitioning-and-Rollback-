"""
ota_gui.py - Simple OTA/FOTA Dashboard (Optional GUI, Section 12 of SRS)

What this does:
- Shows the current active partition (A or B) and which firmware is running
- "Start OTA Update" button installs the valid V2 firmware, verifies it,
  and switches the active slot if verification passes
- "Simulate Failure" button installs the corrupted firmware, which fails
  verification, and shows rollback in action
- A log box at the bottom shows every step as it happens (like a mini
  version of logs/update_log.txt, but live in the window)

Run it with:
    python ota_gui.py

Requirements:
- Must be run from inside the vending_ota_project folder (same place as
  active_slot.txt, firmware/, slots/, ota_incoming/, logs/)
- gcc must be available in your terminal PATH (same as before)
"""

import tkinter as tk
from tkinter import ttk
import hashlib
import subprocess
import threading
import os
from datetime import datetime

# ---------------------------------------------------------------------------
# CONFIGURATION
# These are the same values we used from the command line earlier.
# If you regenerate V2's checksum later, update KNOWN_GOOD_CHECKSUM here.
# ---------------------------------------------------------------------------
ACTIVE_SLOT_FILE = "active_slot.txt"
LOG_FILE = "logs/update_log.txt"

SOURCE_VALID = "firmware/vending_v2_valid.c"
SOURCE_CORRUPTED = "ota_incoming/vending_v2_corrupted.c"

KNOWN_GOOD_CHECKSUM = "aa0ea4fd8ac1d2d77cf26bffa6e79bddb34ef68798beed3efd8f40c7b322bca6"

GCC_FLAGS = ["-Wl,--no-insert-timestamp"]  # keeps checksums consistent every build


# ---------------------------------------------------------------------------
# HELPER FUNCTIONS (same logic as ota_manager.py, reused here)
# ---------------------------------------------------------------------------
def get_active_slot():
    if not os.path.exists(ACTIVE_SLOT_FILE):
        return "A"
    with open(ACTIVE_SLOT_FILE, "r") as f:
        return f.read().strip()

def set_active_slot(slot):
    with open(ACTIVE_SLOT_FILE, "w") as f:
        f.write(slot)

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


# ---------------------------------------------------------------------------
# MAIN APPLICATION CLASS
# ---------------------------------------------------------------------------
class OtaDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("OTA/FOTA Vending Machine Dashboard")
        self.root.geometry("560x520")
        self.root.resizable(False, False)

        # ---------- Status Section ----------
        status_frame = tk.LabelFrame(root, text="Device Status", padx=10, pady=10)
        status_frame.pack(fill="x", padx=10, pady=10)

        self.active_slot_label = tk.Label(status_frame, text="", font=("Segoe UI", 12, "bold"))
        self.active_slot_label.pack(anchor="w")

        self.firmware_label = tk.Label(status_frame, text="", font=("Segoe UI", 11))
        self.firmware_label.pack(anchor="w")

        # ---------- Progress Section ----------
        progress_frame = tk.LabelFrame(root, text="Update Progress", padx=10, pady=10)
        progress_frame.pack(fill="x", padx=10, pady=5)

        self.stage_label = tk.Label(progress_frame, text="Idle", font=("Segoe UI", 10, "italic"))
        self.stage_label.pack(anchor="w")

        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal",
                                             length=520, mode="determinate", maximum=4)
        self.progress_bar.pack(pady=5)

        # ---------- Buttons Section ----------
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        self.update_button = tk.Button(button_frame, text="Start OTA Update",
                                        width=20, bg="#2e7d32", fg="white",
                                        command=self.start_valid_update)
        self.update_button.grid(row=0, column=0, padx=5)

        self.fail_button = tk.Button(button_frame, text="Simulate Failure",
                                      width=20, bg="#c62828", fg="white",
                                      command=self.start_failed_update)
        self.fail_button.grid(row=0, column=1, padx=5)

        # ---------- Log Section ----------
        log_frame = tk.LabelFrame(root, text="Update Log / History", padx=10, pady=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.log_box = tk.Text(log_frame, height=15, state="disabled", wrap="word")
        self.log_box.pack(fill="both", expand=True)

        # Load anything already in the log file, then refresh status
        self.load_existing_log()
        self.refresh_status()

    # -----------------------------------------------------------------
    # UI HELPER METHODS
    # -----------------------------------------------------------------
    def append_log(self, text):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def load_existing_log(self):
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                content = f.read()
            self.append_log(content.strip())

    def refresh_status(self):
        active = get_active_slot()
        firmware_name = "Firmware V1 (Baseline)" if active == "A" else "Firmware V2 (Loyalty Discount)"
        self.active_slot_label.config(text=f"Active Partition: {active}")
        self.firmware_label.config(text=f"Running: {firmware_name}")

    def set_stage(self, text, step):
        self.stage_label.config(text=text)
        self.progress_bar["value"] = step
        self.root.update_idletasks()

    def set_buttons_enabled(self, enabled):
        state = "normal" if enabled else "disabled"
        self.update_button.config(state=state)
        self.fail_button.config(state=state)

    # -----------------------------------------------------------------
    # UPDATE LOGIC (runs in a background thread so the window
    # doesn't freeze while gcc compiles or while we pause for effect)
    # -----------------------------------------------------------------
    def start_valid_update(self):
        threading.Thread(target=self.run_update, args=(SOURCE_VALID, "Valid V2 Update")).start()

    def start_failed_update(self):
        threading.Thread(target=self.run_update, args=(SOURCE_CORRUPTED, "Corrupted Update")).start()

    def run_update(self, source_file, label):
        import time
        self.set_buttons_enabled(False)
        self.append_log(f"--- Starting: {label} ---")

        active = get_active_slot()
        inactive = get_inactive_slot(active)
        target_bin = f"slots/slot{inactive}/firmware.bin"

        # Stage 1: Downloading (simulated)
        self.set_stage("Downloading...", 1)
        log_event(f"OTA update started ({label}). Active={active}, Target={inactive}")
        time.sleep(0.8)

        # Stage 2: Installing (compile into inactive slot)
        self.set_stage("Installing...", 2)
        result = subprocess.run(["gcc", source_file, "-o", target_bin] + GCC_FLAGS)
        time.sleep(0.5)

        if result.returncode != 0:
            self.set_stage("Compilation Failed", 4)
            self.append_log("Compilation FAILED. Update aborted.")
            log_event("Compilation FAILED. Update aborted.")
            self.set_buttons_enabled(True)
            return

        # Stage 3: Verifying
        self.set_stage("Verifying...", 3)
        actual_checksum = calculate_checksum(target_bin)
        time.sleep(0.8)

        self.append_log(f"Expected checksum: {KNOWN_GOOD_CHECKSUM}")
        self.append_log(f"Actual checksum:   {actual_checksum}")

        # Stage 4: Switching (or rollback)
        if actual_checksum == KNOWN_GOOD_CHECKSUM:
            set_active_slot(inactive)
            self.set_stage(f"SUCCESS - Switched to Slot {inactive}", 4)
            self.append_log(f"VERIFICATION PASSED. Active slot switched to {inactive}.")
            log_event(f"Verification PASSED. Active slot switched to {inactive}.")
        else:
            self.set_stage(f"FAILED - Rolled back, staying on {active}", 4)
            self.append_log(f"VERIFICATION FAILED. Rollback performed. Active slot remains {active}.")
            log_event(f"Verification FAILED. Rollback performed. Active slot remains {active}.")

        self.refresh_status()
        self.set_buttons_enabled(True)


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = OtaDashboard(root)
    root.mainloop()