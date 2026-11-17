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

From the repository root:

```bash
chmod +x bin/iphone-fixer
./bin/iphone-fixer --help
./bin/iphone-fixer list-devices
./bin/iphone-fixer status
./bin/iphone-fixer info
./bin/iphone-fixer info --udid DEVICE_UDID
```

You can also run the Python CLI directly:

```bash
python3 iphone_fixer/cli.py info
```

If multiple devices are connected, `info` asks you to provide `--udid`.
Commands only read information; this project does not perform restores,
jailbreaks, downgrades, or other device modifications.

## Example output

```text
$ ./bin/iphone-fixer status
Connected iOS devices: 1

$ ./bin/iphone-fixer info
Device:       Alex's iPhone
Product type: iPhone15,2
iOS version:  17.5.1
Build:        21F90
Status:       Connected
```

Output depends on the connected device and installed `libimobiledevice`
version. With no device connected, `status` prints `Connected iOS devices: 0`
and exits with status 2. Device/tool errors are printed to stderr.

## Project layout

```text
iPhone-Fixer/
├── bin/
│   └── iphone-fixer       # Bash wrapper
├── iphone_fixer/
│   ├── __init__.py
│   ├── cli.py             # CLI commands and output
│   └── device.py          # libimobiledevice detection and queries
├── LICENSE
└── README.md
```

## License

See [LICENSE](LICENSE).
