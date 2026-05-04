#!/usr/bin/env bash
# Run once after cloning to install the desktop shortcut for the current user.

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APPS_DIR="$HOME/.local/share/applications"
APP_DESKTOP="$APPS_DIR/FlashWLSSensor.desktop"
DESKTOP_LINK="$HOME/Desktop/FlashWLSSensor.desktop"

mkdir -p "$APPS_DIR"

cat > "$APP_DESKTOP" << EOF
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

update-desktop-database "$APPS_DIR" 2>/dev/null || true

ln -sf "$APP_DESKTOP" "$DESKTOP_LINK"

chmod +x "$APP_DIR/launch.sh"

echo "Shortcut installed to $DESKTOP_LINK"
