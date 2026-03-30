"""
Flash WLS Sensor App — entry point.

Two buttons: flash U1 (0x78, 12 pads) and U2 (0x77, 8 pads).
Hex files are read directly from the Microchip Studio Debug output folders:
    WaterLevel_u1_driver/.../Debug/WaterLevel_u1_driver.hex
    WaterLevel_u2_driver/.../Debug/WaterLevel_u2_driver.hex

Run from repo root or via launch.sh:
    python flash_wls_sensor_app/app.py
"""
import os
import sys
import queue
import threading
import subprocess

_APP_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_APP_DIR)
sys.path.insert(0, _APP_DIR)

import customtkinter as ctk
from PIL import Image, ImageTk

# ── Constants ──────────────────────────────────────────────────────────────────
WINDOW_W  = 800
WINDOW_H  = 480
HEADER_H  = 64
ICONS_DIR = os.path.join(_APP_DIR, "icons")

HEX_U1 = os.path.join(_REPO_ROOT, "WaterLevel_u1_driver", "WaterLevel_u1_driver", "WaterLevel_u1_driver", "Debug", "WaterLevel_u1_driver.hex")  # 0x78, 12 pads
HEX_U2 = os.path.join(_REPO_ROOT, "WaterLevel_u2_driver", "WaterLevel_u2_driver", "WaterLevel_u2_driver", "Debug", "WaterLevel_u2_driver.hex")  # 0x77, 8 pads

DEVICE = "attiny1616"


def _find_updi_port() -> str | None:
    """Return the first available USB serial port, or None if none found."""
    import serial.tools.list_ports
    ports = list(serial.tools.list_ports.comports())
    # Prefer ports with a USB description (filters out Bluetooth etc.)
    usb_ports = [p for p in ports if p.hwid and "USB" in p.hwid.upper()]
    candidates = usb_ports if usb_ports else ports
    return candidates[0].device if candidates else None

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme(os.path.join(_APP_DIR, "magnotherm_green.json"))


# ── Flash worker ───────────────────────────────────────────────────────────────

def _flash(hex_path: str, q: "queue.Queue"):
    """Run pymcuprog in a background thread; push status messages to q."""
    if not os.path.exists(hex_path):
        q.put(("error", f"Hex file not found:\n{os.path.basename(hex_path)}"))
        q.put(("done", False))
        return

    port = _find_updi_port()
    if port is None:
        q.put(("error", "No serial port found — is the UPDI adapter connected?"))
        q.put(("done", False))
        return

    cmd = [
        sys.executable, "-m", "pymcuprog",
        "write",
        "-t", "uart",
        "-u", port,
        "-d", DEVICE,
        "--erase",
        "--verify",
        "-f", hex_path,
    ]

    q.put(("status", "Connecting…"))
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        for raw in iter(proc.stdout.readline, b""):
            line = raw.decode("utf-8", errors="replace").strip()
            if line:
                if "Writing" in line:
                    q.put(("status", "Writing flash…"))
                elif "Verifying" in line:
                    q.put(("status", "Verifying…"))
                elif "ERROR" in line or "Error" in line:
                    q.put(("error", line))
        proc.wait()
    except Exception as exc:
        q.put(("error", str(exc)))
        q.put(("done", False))
        return

    if proc.returncode == 0:
        q.put(("done", True))
    else:
        q.put(("done", False))


# ── Main window ───────────────────────────────────────────────────────────────

class App(ctk.CTk):

    def __init__(self):
        super().__init__()
        self._q: queue.Queue = queue.Queue()
        self._busy = False

        self._setup_window()
        self._build_header()
        self._build_content()

    # ------------------------------------------------------------------
    # Window
    # ------------------------------------------------------------------

    def _setup_window(self):
        self.geometry(f"{WINDOW_W}x{WINDOW_H}")
        self.resizable(False, False)

        if sys.platform == "linux":
            self.overrideredirect(True)
            self.geometry(f"{WINDOW_W}x{WINDOW_H}+0+0")
        else:
            self.title("Flash WLS Sensor")

        ico = os.path.join(ICONS_DIR, "Magnotherm_Logo.ico")
        png = os.path.join(ICONS_DIR, "Magnotherm_Logo.png")
        if sys.platform == "win32" and os.path.exists(ico):
            self.wm_iconbitmap(ico)
        elif os.path.exists(png):
            img = ImageTk.PhotoImage(Image.open(png))
            self.wm_iconphoto(True, img)

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------

    def _build_header(self):
        header = ctk.CTkFrame(
            self, height=HEADER_H, corner_radius=0,
            fg_color=("gray82", "gray18"),
        )
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        header.grid_propagate(False)

        logo_path = os.path.join(ICONS_DIR, "Magnotherm_Full_Logo.png")
        if os.path.exists(logo_path):
            pil = Image.open(logo_path)
            logo_h = 46
            logo_w = int(pil.width * logo_h / pil.height)
            ctk_img = ctk.CTkImage(light_image=pil, dark_image=pil, size=(logo_w, logo_h))
            ctk.CTkLabel(header, image=ctk_img, text="").grid(
                row=0, column=0, padx=12, pady=8, sticky="w"
            )

        ctk.CTkButton(
            header, text="✕", width=36, height=36,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            hover_color=("#c0392b", "#c0392b"),
            command=self.destroy,
        ).grid(row=0, column=1, padx=8, pady=8, sticky="e")

    # ------------------------------------------------------------------
    # Content
    # ------------------------------------------------------------------

    def _build_content(self):
        content = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=0)   # divider
        content.grid_columnconfigure(2, weight=1)
        content.grid_rowconfigure(0, weight=1)

        # Divider
        ctk.CTkFrame(content, width=1, fg_color=("gray70", "gray35")).grid(
            row=0, column=1, sticky="ns", pady=10,
        )

        self._btn_u1 = self._make_flash_panel(
            content, column=0,
            label="U1  —  0x78  (12 pads)",
            hex_path=HEX_U1,
        )
        self._btn_u2 = self._make_flash_panel(
            content, column=2,
            label="U2  —  0x77  (8 pads)",
            hex_path=HEX_U2,
        )

        # Shared status bar at the bottom
        self._status_label = ctk.CTkLabel(
            self,
            text="Select a firmware to flash",
            font=ctk.CTkFont(size=13),
            text_color=("gray40", "gray70"),
        )
        self._status_label.grid(row=2, column=0, pady=(0, 12))

    def _make_flash_panel(self, parent, column: int, label: str, hex_path: str):
        # Outer frame fills the half-panel and centers its content
        outer = ctk.CTkFrame(parent, fg_color="transparent")
        outer.grid(row=0, column=column, sticky="nsew", padx=20, pady=20)
        outer.grid_rowconfigure(0, weight=1)
        outer.grid_columnconfigure(0, weight=1)

        # Inner frame holds label + button grouped together, centered
        inner = ctk.CTkFrame(outer, fg_color="transparent")
        inner.grid(row=0, column=0)
        inner.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            inner, text=label,
            font=ctk.CTkFont(size=15, weight="bold"),
        ).grid(row=0, column=0, pady=(0, 16))

        btn = ctk.CTkButton(
            inner,
            text="Flash",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=180, height=100,
            command=lambda: self._start_flash(hex_path),
        )
        btn.grid(row=1, column=0)
        return btn

    # ------------------------------------------------------------------
    # Flash sequence
    # ------------------------------------------------------------------

    def _start_flash(self, hex_path: str):
        if self._busy:
            return
        self._busy = True
        self._btn_u1.configure(state="disabled")
        self._btn_u2.configure(state="disabled")
        self._set_status("Starting…", "normal")

        threading.Thread(target=_flash, args=(hex_path, self._q), daemon=True).start()
        self._poll()

    def _poll(self):
        try:
            while True:
                msg = self._q.get_nowait()
                kind = msg[0]
                if kind == "status":
                    self._set_status(msg[1], "normal")
                elif kind == "error":
                    self._set_status(msg[1], "error")
                elif kind == "done":
                    success = msg[1]
                    if success:
                        self._set_status("Done ✓", "success")
                    else:
                        self._set_status("Flash failed ✗", "error")
                    self._busy = False
                    self._btn_u1.configure(state="normal")
                    self._btn_u2.configure(state="normal")
                    return
        except queue.Empty:
            pass
        self.after(100, self._poll)

    def _set_status(self, text: str, style: str):
        colors = {
            "normal":  ("gray40", "gray70"),
            "success": ("#2e7d32", "#66bb6a"),
            "error":   ("#c0392b", "#e74c3c"),
        }
        self._status_label.configure(text=text, text_color=colors.get(style, colors["normal"]))


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
