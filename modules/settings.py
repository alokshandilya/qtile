from pathlib import Path
from typing import Any

from libqtile import qtile

MOD = "mod4"
TERMINAL = "kitty"
GPU_PREFIX = "prime-run"
HOME = Path.home()
QTILE_CONF = HOME / ".config" / "qtile"
SCRIPTS_PATH = QTILE_CONF / "scripts"
IS_WAYLAND = qtile.core.name == "wayland"

# Which monitor hosts workspaces 1-4. That monitor is the MAIN display: it
# gets the full widget bar; the other one gets workspaces 5-8 and a minimal
# bar (workspaces + clock). Set to "external" or "internal" and reload
# (MOD+X, R) to swap — or press MOD+Ctrl+3 to swap on the fly.
WORKSPACES_1_TO_4_ON = "external"

# MOD+Ctrl+3 (groups.py) writes the override here and reloads; it wins over
# the default above until reboot (/tmp is wiped on boot).
_MAIN_DISPLAY_OVERRIDE = Path("/tmp/qtile-main-display")
if _MAIN_DISPLAY_OVERRIDE.exists():
    _override = _MAIN_DISPLAY_OVERRIDE.read_text().strip()
    if _override in ("external", "internal"):
        WORKSPACES_1_TO_4_ON = _override

# Workspaces config
GROUPS_CONF = [
    ("1", "󰎤"),
    ("2", "󰎧"),
    ("3", "󰎪"),
    ("4", "󰎭"),
    ("5", "󰎱"),
    ("6", "󰎳"),
    ("7", "󰎶"),
    ("8", "󰎹"),
]

COLORS = {
    "active": "#689d6a",
    "inactive": "#282828",
    "bg_lighter": "#504945",
    "red": "#fb4934",
    "green": "#98971a",
    "yellow": "#d79921",
    "blue": "#83a598",
    "magenta": "#b16286",
    "cyan": "#8ec07c",
    "white": "#ebdbb2",
    "grey": "#928374",
    "orange": "#d65d0e",
    "super_cyan": "#689d6a",
    "super_blue": "#458588",
    "bg_dark": "#1d2021",
}

if IS_WAYLAND:
    from libqtile.backend.wayland.inputs import InputConfig
else:

    class InputConfig:  # type: ignore
        def __init__(self, **kwargs: Any) -> None:
            pass
