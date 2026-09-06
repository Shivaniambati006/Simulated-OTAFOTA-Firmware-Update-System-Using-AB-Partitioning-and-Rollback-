"""
verify.py - Checks firmware integrity before activation

Usage:
    python verify.py <path-to-firmware> <expected-checksum>

What it does:
- Calculates the SHA-256 checksum of the given firmware file
- Compares it to the expected checksum you provide
- Prints PASS if they match, FAIL if they don't
"""

import hashlib
import sys

def calculate_checksum(filepath):
    with open(filepath, "rb") as f:
        file_bytes = f.read()
    return hashlib.sha256(file_bytes).hexdigest()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python verify.py <firmware_path> <expected_checksum>")
        sys.exit(1)

    firmware_path = sys.argv[1]
    expected_checksum = sys.argv[2]

    actual_checksum = calculate_checksum(firmware_path)

    print(f"Firmware file:      {firmware_path}")
    print(f"Expected checksum:  {expected_checksum}")
    print(f"Actual checksum:    {actual_checksum}")

    if actual_checksum == expected_checksum:
        print("VERIFICATION RESULT: PASS")
        sys.exit(0)
    else:
        print("VERIFICATION RESULT: FAIL")
        sys.exit(1)