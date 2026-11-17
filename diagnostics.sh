
#!/bin/bash

# =====================================
# iPhone Fixer Alpha
# Diagnostics Launcher
# =====================================

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$PROJECT_DIR"

echo ""
echo "====================================="
echo "       iPhone Fixer Alpha"
echo "          DIAGNOSTICS"
echo "====================================="
echo ""

python3 -c '
from iphone_fixer.device import select_device
from iphone_fixer.diagnostics import print_diagnostics

try:
    udid = select_device()
    raise SystemExit(print_diagnostics(udid))
except Exception as error:
    print("[FAIL] " + str(error))
    raise SystemExit(1)
'
