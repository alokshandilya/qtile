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
