"""Command-line interface for the read-only iPhone Fixer utility."""

import argparse
import json
import sys
from typing import Optional, Sequence

from device import DeviceError, connected_devices, device_info, select_device


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="iphone-fixer",
        description="Read-only detection and basic information for iOS devices.",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("list-devices", help="List connected device IDs")
    subparsers.add_parser("status", help="Show the number of connected devices")

    info_parser = subparsers.add_parser("info", help="Show information for one device")
    info_parser.add_argument("--udid", help="Device ID to query")
    info_parser.add_argument("--json", action="store_true", help="Output JSON")

    report_parser = subparsers.add_parser(
        "report", help="Show information for all connected devices"
    )
    report_parser.add_argument("--udid", help="Show only the device with this ID")
    report_parser.add_argument("--json", action="store_true", help="Output JSON")
    return parser


def _yes_no(value: Optional[str]) -> str:
    if value is None:
        return "Unavailable"
    normalized = value.strip().lower()
    if normalized in ("true", "yes", "1"):
        return "Yes"
    if normalized in ("false", "no", "0"):
        return "No"
    return value


def _storage_summary(info: dict) -> str:
    try:
        total = int(info["Total storage bytes"])
        available = int(info["Available storage bytes"])
        if total <= 0 or available < 0:
            raise ValueError("invalid storage values")
        used = max(0, total - available)
        used_percent = round(100 * used / total)
        return "{:.1f} GB total, {:.1f} GB available ({}% used)".format(
            total / 1_000_000_000,
            available / 1_000_000_000,
            used_percent,
        )
    except (TypeError, ValueError, ZeroDivisionError):
        return "Unavailable"


def _sim_label(value: Optional[bool]) -> str:
    if value is None:
        return "Unavailable"
    return "Yes" if value else "No"


def _report_data(udid: str) -> dict:
    info = device_info(udid)
    return {
        "device_id": udid,
        "status": "Connected",
        "device_name": info["Device"],
        "device_class": info["Device class"],
        "product_type": info["Product type"],
        "ios_version": info["iOS version"],
        "build": info["Build"],
        "serial_number": info["Serial number"],
        "hardware_model": info["Hardware model"],
        "cpu_architecture": info["CPU architecture"],
        "ram_bytes": info["RAM bytes"],
        "sim_status": info["SIM status"],
        "sim_connected": info["SIM connected"],
        "carrier": info["Carrier"],
        "cellular_technology": info["Cellular technology"],
        "wifi_status": info["Wi-Fi status"],
        "battery_percent": _as_int(info["Battery level"]),
        "charging": _as_bool(info["Charging"]),
        "external_power": _as_bool(info["External power"]),
        "storage_total_bytes": _as_int(info["Total storage bytes"]),
        "storage_available_bytes": _as_int(info["Available storage bytes"]),
    }


def _as_int(value: Optional[str]) -> Optional[int]:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _as_bool(value: Optional[str]) -> Optional[bool]:
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in ("true", "yes", "1"):
        return True
    if normalized in ("false", "no", "0"):
        return False
    return None


def print_info(udid: str, include_udid: bool = False) -> None:
    info = device_info(udid)
    if include_udid:
        print("Device ID:      {}".format(udid))
    print("Device:         {}".format(info["Device"] or "Unavailable"))
    print("Device class:   {}".format(info["Device class"] or "Unavailable"))
    print("Product type:   {}".format(info["Product type"] or "Unavailable"))
    print("iOS version:    {}".format(info["iOS version"] or "Unavailable"))
    print("Build:          {}".format(info["Build"] or "Unavailable"))
    print("Serial number:  {}".format(info["Serial number"] or "Unavailable"))
    print("Hardware model: {}".format(info["Hardware model"] or "Unavailable"))
    print("CPU architecture: {}".format(info["CPU architecture"] or "Unavailable"))
    print("RAM:            Unavailable via ideviceinfo")
    print("SIM status:     {}".format(info["SIM status"] or "Unavailable"))
    print("SIM connected:  {}".format(_sim_label(info["SIM connected"])))
    print("Carrier:        {}".format(info["Carrier"] or "Unavailable"))
    print("Cellular:       {}".format(info["Cellular technology"] or "Unavailable"))
    print("Wi-Fi status:   {}".format(_yes_no(info["Wi-Fi status"])))

    battery = info["Battery level"]
    print(
        "Battery:        {}%".format(battery)
        if battery is not None
        else "Battery:        Unavailable"
    )
    print("Charging:       {}".format(_yes_no(info["Charging"])))
    print("External power: {}".format(_yes_no(info["External power"])))
    print("Storage:        {}".format(_storage_summary(info)))
    print("Status:         Connected")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 0

    try:
        if args.command == "list-devices":
            devices = connected_devices()
            if not devices:
                print("No iOS devices detected.")
                return 2
            for udid in devices:
                print(udid)
            return 0

        if args.command == "status":
            devices = connected_devices()
            print("Connected iOS devices: {}".format(len(devices)))
            return 0 if devices else 2

        if args.command == "info":
            udid = select_device(args.udid)
            if args.json:
                print(json.dumps(_report_data(udid), indent=2))
            else:
                print_info(udid)
            return 0

        if args.command == "report":
            devices = connected_devices()
            if args.udid:
                if args.udid not in devices:
                    raise DeviceError("Device not found: {}".format(args.udid))
                devices = [args.udid]
            if not devices:
                if args.json:
                    print("[]")
                else:
                    print("No iOS devices detected.")
                return 2

            results = []
            failed = False
            for udid in devices:
                try:
                    results.append(_report_data(udid))
                except DeviceError as exc:
                    failed = True
                    results.append({"device_id": udid, "status": "Error", "error": str(exc)})

            if args.json:
                print(json.dumps(results, indent=2, ensure_ascii=False))
            else:
                for index, result in enumerate(results):
                    if index:
                        print()
                    if result.get("error"):
                        print("Device ID:      {}".format(result["device_id"]))
                        print("Error:          {}".format(result["error"]))
                        continue
                    print_info(result["device_id"], include_udid=True)
            return 1 if failed else 0
    except DeviceError as exc:
        if getattr(args, "json", False):
            print(json.dumps({"error": str(exc)}))
        else:
            print("Error: {}".format(exc), file=sys.stderr)
        return 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
