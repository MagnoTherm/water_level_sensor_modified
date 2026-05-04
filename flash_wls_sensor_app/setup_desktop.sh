#!/usr/bin/env bash
# Run once after cloning to install the desktop shortcut for the current user.

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
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
gio set "$DESKTOP_FILE" metadata::trusted yes

# Suppress PCManFM's executable confirmation dialog
PCMANFM_CONF="$HOME/.config/pcmanfm/default/pcmanfm.conf"
if [ ! -f "$PCMANFM_CONF" ]; then
    mkdir -p "$(dirname "$PCMANFM_CONF")"
    printf '[config]\nquick_exec=1\n' > "$PCMANFM_CONF"
elif grep -q "^quick_exec=" "$PCMANFM_CONF"; then
    sed -i 's/^quick_exec=.*/quick_exec=1/' "$PCMANFM_CONF"
else
    sed -i '/^\[config\]/a quick_exec=1' "$PCMANFM_CONF"
fi

echo "Shortcut installed to $DESKTOP_FILE"
