#!/usr/bin/env bash
# Launch the Flash WLS Sensor app from the repo root, using the project venv.

REPO_ROOT="/home/lauda/Desktop/water_level_sensor_modified"

cd "$REPO_ROOT"

PYTHON="$REPO_ROOT/.venv/bin/python"

if ! $PYTHON -c "import customtkinter" 2>/dev/null; then
    x-terminal-emulator -e bash -c "
        $PYTHON -m pip install -r $REPO_ROOT/flash_wls_sensor_app/requirements.txt
        read -p 'Done. Press Enter to close...'
    "
fi

$PYTHON flash_wls_sensor_app/app.py
