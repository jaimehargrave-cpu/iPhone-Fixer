# iPhone Fixer

A small, read-only command-line utility to identify connected iPhones, iPads,
and iPod touches. It uses `libimobiledevice` and does not modify the device.

## Supported devices

This initial version supports iPhone, iPad, and iPod touch devices that can be
seen by `libimobiledevice`. Classic iPods and iPod nanos do not run iOS and use
different protocols, so they are not supported by this version.

## Requirements

- Python 3.8 or newer
- `libimobiledevice`, including `idevice_id` and `ideviceinfo`
- A USB connection; unlock the device and accept the trust prompt when asked

Install `libimobiledevice` with your operating system's package manager. On
macOS it is available through Homebrew (`brew install libimobiledevice`). On
Linux, use your distribution's package manager.

## Run

From the repository root, the quick-detect script produces a report for every
connected iOS device:

```bash
chmod +x iphone-fixer-detect.sh
./iphone-fixer-detect.sh
```

Use the full CLI to get JSON output for automation:

```bash
./bin/iphone-fixer report --json
./bin/iphone-fixer info --udid DEVICE_UDID --json
```

The report includes serial number, device/hardware identifiers, SIM status,
carrier and cellular technology when iOS exposes them. It reports Wi-Fi state
only when the device exposes a recognized status field; it deliberately does
not include SSIDs, phone numbers, SIM identifiers, or Wi-Fi MAC/BSSID values.
RAM size is not consistently exposed by `ideviceinfo`, so the report returns
`null` for `ram_bytes` rather than guessing. Other unavailable fields are also
`null` in JSON. Serial numbers and device IDs are sensitive identifiers; avoid
sharing reports publicly without reviewing them.

To report only one of several connected devices, pass its device ID:

```bash
./iphone-fixer-detect.sh --udid DEVICE_UDID
```

The full CLI is also available:

```bash
./bin/iphone-fixer --help
./bin/iphone-fixer list-devices
./bin/iphone-fixer status
./bin/iphone-fixer info
./bin/iphone-fixer report
```

You can also run the Python CLI directly:

```bash
python3 iphone_fixer/cli.py report --json
```

Battery and storage values are read from iOS information domains. Some iOS
versions or device states may not expose every field; unavailable values are
shown as `Unavailable` in text and `null` in JSON. Storage is reported in
decimal GB. Commands only read information; this project does not perform
restores, jailbreaks, downgrades, or other device modifications.

## Example JSON

```json
[
  {
    "device_id": "DEVICE_UDID",
    "status": "Connected",
    "device_name": "Kellen’s iPhone",
    "device_class": "iPhone",
    "product_type": "iPhone13,2",
    "ios_version": "26.4.2",
    "build": "23E261",
    "serial_number": "Unavailable",
    "hardware_model": "Unavailable",
    "cpu_architecture": "arm64",
    "ram_bytes": null,
    "sim_status": null,
    "sim_connected": null,
    "carrier": null,
    "cellular_technology": null,
    "wifi_status": null,
    "battery_percent": 74,
    "charging": true,
    "external_power": true,
    "storage_total_bytes": 128000000000,
    "storage_available_bytes": 73200000000
  }
]
```

With multiple devices, text output separates reports with a blank line. With
no device connected, text output says so and exits with status 2; JSON report
mode outputs an empty array. Device/tool errors appear in stderr in text mode
and as JSON errors in JSON mode.

## Project layout

```text
iPhone-Fixer/
├── bin/
│   └── iphone-fixer       # Bash wrapper
├── iphone_fixer/
│   ├── __init__.py
│   ├── cli.py             # CLI commands and output
│   └── device.py          # libimobiledevice detection and queries
├── iphone-fixer-detect.sh # All-device report shortcut
├── LICENSE
└── README.md
```

## License

See [LICENSE](LICENSE).
