import gc
import os
from pathlib import Path

# Must be in qtile's own environment so every spawned app inherits it —
# exporting it in autostart.sh only reaches that script's subshell.
os.environ.setdefault("XDG_CURRENT_DESKTOP", "qtile:wlroots")

from libqtile import bar, qtile
from libqtile.config import Key, Screen
from libqtile.lazy import lazy

from modules.groups import ScratchPad, get_groups, init_group_bindings
from modules.layouts import floating_layout, layouts
from modules.keys import keys
from modules.settings import COLORS, IS_WAYLAND, InputConfig
from modules.widgets import init_widgets_list
import modules.hooks  # noqa: F401

# Tune Garbage Collection for lower latency
gc.set_threshold(1500, 15, 15)


# --- Monitor Detection ---
DOCKED_FLAG = Path("/tmp/qtile-docked-mode")


def get_monitors():
    # Docked mode (laptop panel intentionally off via MOD+Ctrl+0): the flag
    # file is the source of truth, because nothing else works from inside a
    # config load: wlr-randr DEADLOCKS (it's a wayland client asking the
    # compositor whose loop is busy executing this file), and the DRM
    # connector count below can't see a disabled-but-connected panel.
    # Reloading with this returning 1 keeps the panel off; with 2 a reload
    # re-enables it — both are what we want for the respective states.
    if DOCKED_FLAG.exists():
        return 1

    try:
        count = sum(
            1
            for s in Path("/sys/class/drm/").glob("card*-*")
            if (s / "status").exists()
            and (s / "status").read_text().strip() == "connected"
        )
        return max(count, 1)
    except Exception:
        return 1


num_monitors = get_monitors()

# --- Groups & Bindings ---
groups = get_groups(num_monitors)
init_group_bindings(groups)
group_names = [g.name for g in groups if not isinstance(g, ScratchPad)]


# --- Screens ---
def create_screen(visible_groups=None, is_primary=True):
    return Screen(
        top=bar.Bar(
            init_widgets_list(visible_groups=visible_groups, is_primary=is_primary),
            24,
            background=COLORS["bg_dark"],
            border_width=[0, 0, 2, 0],
            border_color=COLORS["bg_dark"],
        ),
        left=bar.Gap(10),
        right=bar.Gap(10),
        bottom=bar.Gap(3),
    )


# With one monitor (incl. docked mode) a single screen gets the primary bar
# with all its widgets and every group; with two, the classic 1-4 / 5-8 split.
screens = [
    create_screen(
        visible_groups=group_names[:4] if num_monitors > 1 else None, is_primary=True
    )
]

if num_monitors > 1:
    screens.append(create_screen(visible_groups=group_names[4:], is_primary=False))

# --- General Settings ---
mouse = []
dgroups_key_binder = None
dgroups_app_rules = []
follow_mouse_focus = True
bring_front_click = False
floats_kept_above = True
cursor_warp = False
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True
auto_minimize = True
wmname = "LG3D"

# --- Backend Specific ---
if IS_WAYLAND:
    wl_input_rules = {
        "type:touchpad": InputConfig(
            tap=True,
            natural_scroll=True,
            left_handed=False,
        ),
        "type:pointer": InputConfig(
            accel_profile="flat",
            pointer_accel=-0.15,
            natural_scroll=True,
        ),
        "type:keyboard": InputConfig(
            kb_options="caps:escape,compose:ralt",
            kb_repeat_rate=30,
            kb_repeat_delay=350,
        ),
    }
    wl_xcursor_theme = "Qogir-manjaro-light"
    wl_xcursor_size = 24

# VT Switching for Wayland
for vt in range(1, 8):
    keys.append(
        Key(
            ["control", "mod1"],
            f"f{vt}",
            lazy.core.change_vt(vt).when(func=lambda: IS_WAYLAND),
            desc=f"Switch to VT{vt}",
        )
    )
