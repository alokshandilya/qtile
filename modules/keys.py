from libqtile.config import Key, KeyChord
from libqtile.lazy import lazy
from .settings import MOD, TERMINAL, GPU_PREFIX, SCRIPTS_PATH, IS_WAYLAND

keys = [
    Key([MOD], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([MOD], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([MOD], "j", lazy.layout.down(), desc="Move focus down"),
    Key([MOD], "k", lazy.layout.up(), desc="Move focus up"),
    Key([MOD], "period", lazy.next_screen(), desc="Move focus to next screen"),
    Key([MOD], "comma", lazy.prev_screen(), desc="Move focus to prev screen"),
    Key([MOD], "space", lazy.layout.next()),
    Key([MOD], "r", lazy.spawncmd()),
    Key([MOD, "shift"], "h", lazy.layout.swap_left()),
    Key([MOD, "shift"], "l", lazy.layout.shuffle_right()),
    Key([MOD, "shift"], "j", lazy.layout.shuffle_down()),
    Key([MOD, "shift"], "k", lazy.layout.shuffle_up()),
    Key([MOD], "i", lazy.layout.grow()),
    Key([MOD], "m", lazy.layout.shrink()),
    Key([MOD], "n", lazy.layout.reset()),
    Key([MOD, "shift"], "n", lazy.layout.normalize()),
    Key([MOD], "o", lazy.layout.maximize()),
    Key([MOD, "shift"], "space", lazy.layout.flip()),
    Key([MOD, "shift"], "Return", lazy.layout.toggle_split()),
    Key([MOD], "Return", lazy.spawn(TERMINAL), desc="Launch terminal"),
    Key(
        [MOD, "shift"],
        "Return",
        lazy.spawn(f"env {GPU_PREFIX} {TERMINAL}"),
        desc="Launch GPU terminal",
    ),
    Key(
        [MOD],
        "w",
        lazy.spawn(f"env {GPU_PREFIX} zen-browser"),
        desc="Launch Zen Browser",
    ),
    Key([MOD, "shift"], "t", lazy.spawn(f"{TERMINAL} -e bpytop"), desc="Launch Bpytop"),
    Key([MOD], "d", lazy.spawn("rofi -show drun")),
    Key(
        [MOD],
        "c",
        lazy.spawn(f"python3 {SCRIPTS_PATH / 'clip.py'}"),
        desc="Clipboard Manager",
    ),
    Key([MOD], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([MOD, "shift"], "q", lazy.window.kill(), desc="Kill focused window"),
    Key([MOD, "control"], "l", lazy.spawn("brightnessctl s 3%+")),
    Key([MOD, "control"], "h", lazy.spawn("brightnessctl s 3%-")),
    Key([MOD, "control"], "k", lazy.spawn("amixer -q set Master 2%+")),
    Key([MOD, "control"], "j", lazy.spawn("amixer -q set Master 2%-")),
    Key([MOD], "Right", lazy.screen.next_group(), desc="Move to next workspace"),
    Key([MOD], "Left", lazy.screen.prev_group(), desc="Move to previous workspace"),
    Key([MOD], "f", lazy.window.toggle_fullscreen()),
    Key([MOD], "t", lazy.window.toggle_floating()),
    Key(
        [MOD, "shift"],
        "s",
        lazy.spawn(
            "sh -c 'export XDG_CURRENT_DESKTOP=qtile XDG_SESSION_TYPE=wayland && dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP XDG_SESSION_TYPE && systemctl --user import-environment WAYLAND_DISPLAY XDG_CURRENT_DESKTOP XDG_SESSION_TYPE && systemctl --user restart xdg-desktop-portal-wlr xdg-desktop-portal'"
        )
        if IS_WAYLAND
        else lazy.spawn("flameshot gui"),
        desc="Screen sharing fix or screenshot",
    ),
    KeyChord(
        [MOD],
        "x",
        [
            Key([], "r", lazy.reload_config()),
            Key([], "x", lazy.shutdown()),
            Key([], "p", lazy.spawn("shutdown -h now")),
        ],
    ),
    KeyChord([MOD], "b", [Key([], "m", lazy.spawn("blueman-manager"))]),
    KeyChord(
        [MOD],
        "e",
        [
            Key([], "f", lazy.spawn("thunar")),
        ],
    ),
    KeyChord(
        [MOD],
        "v",
        [
            Key([], "c", lazy.spawn(f"env {GPU_PREFIX} code")),
            Key([], "v", lazy.spawn("pavucontrol")),
        ],
    ),
]

if IS_WAYLAND:
    keys.append(
        Key([], "print", lazy.spawn("sh -c 'grim -g \"$(slurp)\" - | wl-copy'"))
    )
else:
    keys.append(Key([], "print", lazy.spawn("flameshot gui")))
