#!/usr/bin/env bash
# Run once after cloning to install the desktop shortcut for the current user.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$SCRIPT_DIR/flash_wls_sensor_app"
DESKTOP_FILE="$HOME/Desktop/FlashWLSSensor.desktop"

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=FlashWLSSensor
Comment=Flash Grove Water Level Sensor firmware
Exec=$APP_DIR/launch.sh
Icon=$APP_DIR/icons/Magnotherm_Logo.png
Terminal=false
Categories=Utility;
EOF

chmod +x "$DESKTOP_FILE"
chmod +x "$APP_DIR/launch.sh"

echo "Shortcut installed to $DESKTOP_FILE"
