"""Command-line interface for the read-only iPhone Fixer utility."""

import argparse
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

    info_parser = subparsers.add_parser(
        "info", help="Show information for one connected device"
    )
    info_parser.add_argument(
        "--udid", help="Device ID to query when multiple devices are connected"
    )

    report_parser = subparsers.add_parser(
        "report", help="Show information for all connected devices"
    )
    report_parser.add_argument(
        "--udid", help="Show only the device with this ID"
    )
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


def print_info(udid: str, include_udid: bool = False) -> None:
    info = device_info(udid)
    if include_udid:
        print("Device ID:    {}".format(udid))
    print("Device:       {}".format(info["Device"] or "Unavailable"))
    print("Product type: {}".format(info["Product type"] or "Unavailable"))
    print("iOS version:  {}".format(info["iOS version"] or "Unavailable"))
    print("Build:        {}".format(info["Build"] or "Unavailable"))

    battery = info["Battery level"]
    charging = info["Charging"]
    external_power = info["External power"]
    print(
        "Battery:      {}%".format(battery)
        if battery is not None
        else "Battery:      Unavailable"
    )
    print("Charging:     {}".format(_yes_no(charging)))
    print("External power: {}".format(_yes_no(external_power)))
    print("Status:       Connected")


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
            print_info(select_device(args.udid))
            return 0

        if args.command == "report":
            devices = connected_devices()
            if args.udid:
                if args.udid not in devices:
                    raise DeviceError("Device not found: {}".format(args.udid))
                devices = [args.udid]
            if not devices:
                print("No iOS devices detected.")
                return 2

            failed = False
            for index, udid in enumerate(devices):
                if index:
                    print()
                try:
                    print_info(udid, include_udid=True)
                except DeviceError as exc:
                    failed = True
                    print("Device ID:    {}".format(udid))
                    print("Error:        {}".format(exc), file=sys.stderr)
            return 1 if failed else 0
    except DeviceError as exc:
        print("Error: {}".format(exc), file=sys.stderr)
        return 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
