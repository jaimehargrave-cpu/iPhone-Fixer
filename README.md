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
connected iOS device, including battery and storage details when available:

```bash
chmod +x iphone-fixer-detect.sh
./iphone-fixer-detect.sh
```

If you prefer not to set the executable bit, run it with Bash:

```bash
bash iphone-fixer-detect.sh
```

To report only one of several connected devices, pass its device ID:

```bash
./iphone-fixer-detect.sh --udid DEVICE_UDID
```

The full CLI is also available:

```bash
chmod +x bin/iphone-fixer
./bin/iphone-fixer --help
./bin/iphone-fixer list-devices
./bin/iphone-fixer status
./bin/iphone-fixer info
./bin/iphone-fixer info --udid DEVICE_UDID
./bin/iphone-fixer report
```

You can also run the Python CLI directly:

```bash
python3 iphone_fixer/cli.py report
```

Battery and storage values are read from iOS information domains. Some iOS
versions or device states may not expose every field; unavailable values are
shown as `Unavailable`. Storage is reported in decimal GB. Commands only read
information; this project does not perform restores, jailbreaks, downgrades,
or other device modifications.

## Example output

```text
$ ./iphone-fixer-detect.sh
Device ID:      0edc5b94c4f4a2b89535c7f11b07e5f0594e2bdf
Device:         Kellen’s iPhone
Device class:   iPhone
Product type:   iPhone13,2
iOS version:    26.4.2
Build:          23E261
Battery:        74%
Charging:       Yes
External power: Yes
Storage:        128.0 GB total, 73.2 GB available (43% used)
Status:         Connected
```

With multiple devices, a blank line separates each device report. With no
device connected, the tool says so and exits with status 2. Device/tool errors
are printed to stderr.

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
