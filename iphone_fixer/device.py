"""Read-only iOS device discovery via libimobiledevice."""

import shutil
import subprocess
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


def read_value(udid: str, key: str, domain: Optional[str] = None) -> Optional[str]:
    """Read one device value, returning None when unavailable."""
    command = ["ideviceinfo", "-u", udid]
    if domain:
        command.extend(["-q", domain])
    command.extend(["-k", key])
    result = run_command(command)
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def device_info(udid: str) -> Dict[str, Optional[str]]:
    """Read basic and battery information; unsupported fields are None."""
    require_tool("ideviceinfo")
    info = {
        "Device": read_value(udid, "DeviceName"),
        "Product type": read_value(udid, "ProductType"),
        "iOS version": read_value(udid, "ProductVersion"),
        "Build": read_value(udid, "BuildVersion"),
        "Battery level": read_value(
            udid, "BatteryCurrentCapacity", "com.apple.mobile.battery"
        ),
        "Charging": read_value(
            udid, "BatteryIsCharging", "com.apple.mobile.battery"
        ),
        "External power": read_value(
            udid, "ExternalConnected", "com.apple.mobile.battery"
        ),
    }
    if not any(info[key] for key in ("Device", "Product type", "iOS version", "Build")):
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
