"""Read-only iOS device discovery via libimobiledevice."""

import shutil
import subprocess
import sys
from typing import Dict, List, Optional


class DeviceError(Exception):
    """Raised when device discovery or information lookup fails."""


def require_tool(name: str) -> None:
    if shutil.which(name) is None:
        raise DeviceError(
            "Required command {!r} was not found. Install libimobiledevice "
            "and ensure it is on PATH.".format(name)
        )


def run_command(args: List[str]) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=10,
            check=False,
        )
    except subprocess.TimeoutExpired:
        raise DeviceError("Command timed out: {}".format(args[0]))
    except OSError as exc:
        raise DeviceError("Could not run {}: {}".format(args[0], exc))


def connected_devices() -> List[str]:
    """Return USB-connected iOS device identifiers."""
    require_tool("idevice_id")
    result = run_command(["idevice_id", "-l"])
    if result.returncode != 0:
        detail = result.stderr.strip() or "device query failed"
        raise DeviceError(detail)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def device_info(udid: str) -> Dict[str, Optional[str]]:
    """Read basic device fields; unavailable fields are returned as None."""
    require_tool("ideviceinfo")
    fields = {
        "Device": "DeviceName",
        "Product type": "ProductType",
        "iOS version": "ProductVersion",
        "Build": "BuildVersion",
    }
    info = {}
    for label, key in fields.items():
        result = run_command(["ideviceinfo", "-u", udid, "-k", key])
        value = result.stdout.strip() if result.returncode == 0 else ""
        info[label] = value or None
    if not any(info.values()):
        raise DeviceError(
            "Could not read device information. Unlock the device and accept "
            "the Trust This Computer prompt, then try again."
        )
    return info


def select_device(requested_udid: Optional[str] = None) -> str:
    devices = connected_devices()
    if requested_udid:
        if requested_udid not in devices:
            raise DeviceError("Device not found: {}".format(requested_udid))
        return requested_udid
    if not devices:
        raise DeviceError(
            "No iOS devices detected. Check the USB connection, unlock the "
            "device, and accept the trust prompt if shown."
        )
    if len(devices) > 1:
        raise DeviceError(
            "Multiple devices are connected. Select one with --udid."
        )
    return devices[0]


def report_error(error: Exception) -> int:
    print("Error: {}".format(error), file=sys.stderr)
    return 1
