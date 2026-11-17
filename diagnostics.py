
"""Read-only diagnostics for iPhone Fixer Alpha."""

from typing import Dict, List, Optional

from device import (
    DeviceError,
    connected_devices,
    device_info,
    require_tool,
)


def run_diagnostics(udid: str) -> List[Dict[str, str]]:
    """Run basic read-only checks on a connected iOS device."""

    results = []

    def add_check(name: str, status: str, message: str) -> None:
        results.append({
            "check": name,
            "status": status,
            "message": message,
        })

    # Check 1: Required utilities
    try:
        require_tool("idevice_id")
        require_tool("ideviceinfo")
        add_check(
            "Required utilities",
            "PASS",
            "libimobiledevice utilities are installed.",
        )
    except DeviceError as exc:
        add_check("Required utilities", "FAIL", str(exc))
        return results

    # Check 2: USB/device detection
    try:
        devices = connected_devices()

        if udid in devices:
            add_check(
                "USB detection",
                "PASS",
                "Device detected successfully.",
            )
        else:
            add_check(
                "USB detection",
                "FAIL",
                "Device is not currently detected.",
            )
            return results

    except DeviceError as exc:
        add_check("USB detection", "FAIL", str(exc))
        return results

    # Check 3: Device communication
    try:
        info = device_info(udid)

        add_check(
            "Device communication",
            "PASS",
            "Successfully retrieved device information.",
        )

    except DeviceError as exc:
        add_check(
            "Device communication",
            "FAIL",
            str(exc),
        )
        return results

    # Check 4: Device identity
    if info.get("Product type") and info.get("iOS version"):
        add_check(
            "Device identity",
            "PASS",
            "Model and iOS version are available.",
        )
    else:
        add_check(
            "Device identity",
            "WARNING",
            "Some device information is unavailable.",
        )

    # Check 5: Battery information
    battery = info.get("Battery level")

    if battery is not None:
        try:
            level = int(battery)

            if 0 <= level <= 100:
                add_check(
                    "Battery information",
                    "PASS",
                    "Battery level: {}%.".format(level),
                )
            else:
                add_check(
                    "Battery information",
                    "WARNING",
                    "Battery value is outside the expected range.",
                )
        except ValueError:
            add_check(
                "Battery information",
                "WARNING",
                "Battery value could not be interpreted.",
            )
    else:
        add_check(
            "Battery information",
            "WARNING",
            "Battery information is unavailable.",
        )

    # Check 6: Charging information
    charging = info.get("Charging")

    if charging is not None:
        add_check(
            "Charging information",
            "PASS",
            "Charging status: {}.".format(charging),
        )
    else:
        add_check(
            "Charging information",
            "WARNING",
            "Charging information is unavailable.",
        )

    return results


def print_diagnostics(udid: str) -> int:
    """Run diagnostics and print a readable report."""

    print("\nIPHONE FIXER ALPHA")
    print("============================")
    print("DEVICE DIAGNOSTICS")
    print("============================\n")

    try:
        results = run_diagnostics(udid)
    except DeviceError as exc:
        print("[FAIL] Diagnostics: {}".format(exc))
        return 1

    for result in results:
        print(
            "[{}] {}: {}".format(
                result["status"],
                result["check"],
                result["message"],
            )
        )

    failures = sum(r["status"] == "FAIL" for r in results)
    warnings = sum(r["status"] == "WARNING" for r in results)

    print("\n============================")

    if failures:
        print("RESULT: CHECKS FAILED")
        return 1
    elif warnings:
        print("RESULT: COMPLETED WITH WARNINGS")
    else:
        print("RESULT: ALL CHECKS PASSED")

    print("============================\n")
    return 0
