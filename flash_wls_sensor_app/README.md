# FlashWLSSensor App

GUI app for flashing Grove Water Level Sensor firmware, designed to run on a Raspberry Pi with a touch screen.

## Setup (new Pi)

After cloning the repo to the Pi's desktop, run the setup script once:

```bash
bash ~/Desktop/water_level_sensor_modified/flash_wls_sensor_app/setup_desktop.sh
```

This will:
- Create a `FlashWLSSensor` shortcut directly on the desktop
- Set the correct executable permissions on the shortcut and `launch.sh`

The app will install its Python dependencies automatically on first launch.
