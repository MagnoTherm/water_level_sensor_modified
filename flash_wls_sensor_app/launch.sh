#!/usr/bin/env bash
# Launch the Flash WLS Sensor app from the repo root, using the project venv.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$REPO_ROOT"

PYTHON="$REPO_ROOT/.venv/bin/python"

if [ ! -f "$PYTHON" ]; then
    x-terminal-emulator -e bash -c "
        python3 -m venv $REPO_ROOT/.venv
        $PYTHON -m pip install -r $REPO_ROOT/flash_wls_sensor_app/requirements.txt
        read -p 'Done. Press Enter to close...'
    "
elif ! $PYTHON -c "import customtkinter" 2>/dev/null; then
    x-terminal-emulator -e bash -c "
        $PYTHON -m pip install -r $REPO_ROOT/flash_wls_sensor_app/requirements.txt
        read -p 'Done. Press Enter to close...'
    "
fi

$PYTHON flash_wls_sensor_app/app.py
