import subprocess
from pathlib import Path

from libqtile.config import DropDown, Group, Key, ScratchPad
from libqtile.lazy import lazy

from .keys import keys
from .settings import (
    GROUPS_CONF,
    IS_WAYLAND,
    MOD,
    QTILE_CONF,
    TERMINAL,
    WORKSPACES_1_TO_4_ON,
)

ONE_TO_FOUR_ON_EXTERNAL = WORKSPACES_1_TO_4_ON == "external"

# Whether the dual-monitor split (1-4 on main, 5-8 on the other) is applied.
groups_split_active = True


def _get_laptop_and_external_screens(qtile):
    if len(qtile.screens) < 2:
        return 0, None

    laptop_screen = 0

    # qtile's C wayland backend (0.36+) exposes outputs via get_output_info();
    # match the laptop panel's port name to a screen by layout coordinates.
    if IS_WAYLAND and hasattr(qtile.core, "get_output_info"):
        try:
            outputs = qtile.core.get_output_info()
        except Exception:
            outputs = []
        for out in outputs:
            port = (getattr(out, "port", "") or "").lower()
            if any(token in port for token in ("edp", "lvds", "dsi")):
                for idx, scr in enumerate(qtile.screens):
                    if (scr.x, scr.y) == (out.rect.x, out.rect.y):
                        laptop_screen = idx
                break

    external_screen = next(
        (idx for idx in range(len(qtile.screens)) if idx != laptop_screen),
        None,
    )
    return laptop_screen, external_screen


def _get_split_screens(qtile):
    """(screen hosting groups 1-4, screen hosting groups 5-8) per the setting."""
    laptop_screen, external_screen = _get_laptop_and_external_screens(qtile)
    if external_screen is None:
        return laptop_screen, laptop_screen
    if ONE_TO_FOUR_ON_EXTERNAL:
        return external_screen, laptop_screen
    return laptop_screen, external_screen


def _set_groupbox_visibility(qtile):
    laptop_screen, external_screen = _get_laptop_and_external_screens(qtile)

    def set_bar(screen_idx, visible):
        if screen_idx is None or screen_idx >= len(qtile.screens):
            return
        screen = qtile.screens[screen_idx]
        if not getattr(screen, "top", None):
            return
        for wid in screen.top.widgets:
            if wid.__class__.__name__ == "GroupBox":
                wid.visible_groups = visible
                wid.bar.draw()
                break

    if groups_split_active and external_screen is not None:
        main_screen, other_screen = _get_split_screens(qtile)
        set_bar(main_screen, ["1", "2", "3", "4"])
        set_bar(other_screen, ["5", "6", "7", "8"])
    else:
        set_bar(laptop_screen, None)


def get_groups(num_monitors):
    global groups_split_active
    groups_split_active = num_monitors > 1

    # Screen 0 is the laptop panel on this machine (it enumerates first);
    # runtime placement is re-asserted by output identity in hooks.py anyway.
    one_to_four_idx = 1 if ONE_TO_FOUR_ON_EXTERNAL else 0

    groups = [
        Group(
            name=name,
            label=label,
            screen_affinity=(one_to_four_idx if i < 4 else 1 - one_to_four_idx)
            if num_monitors > 1
            else 0,
        )
        for i, (name, label) in enumerate(GROUPS_CONF)
    ]

    # scratchpads
    groups.append(
        ScratchPad(
            "9",
            [
                DropDown(
                    "term",
                    TERMINAL,
                    x=0.1,
                    y=0.015,
                    opacity=1.0,
                    width=0.80,
                    height=0.6,
                    on_focus_lost_hide=False,
                ),
                DropDown(
                    "chatgpt",
                    "zen-browser --new-window 'https://chatgpt.com'",
                    x=0.2825,
                    y=0.015,
                    width=0.435,
                    height=0.80,
                    opacity=1.0,
                    on_focus_lost_hide=False,
                ),
            ],
        )
    )
    return groups


def go_to_group(name):
    def _inner(qtile):
        if groups_split_active:
            main_screen, other_screen = _get_split_screens(qtile)
            target_screen = main_screen if name in "1234" else other_screen
        else:
            target_screen, _ = _get_laptop_and_external_screens(qtile)

        qtile.to_screen(target_screen)
        qtile.groups_map[name].toscreen()

    return _inner


def go_to_group_and_move_window(name):
    def _inner(qtile):
        if not qtile.current_window:
            return

        if groups_split_active:
            main_screen, other_screen = _get_split_screens(qtile)
            target_screen = main_screen if name in "1234" else other_screen
        else:
            target_screen, _ = _get_laptop_and_external_screens(qtile)

        qtile.current_window.togroup(name, switch_group=False)
        qtile.to_screen(target_screen)
        qtile.groups_map[name].toscreen()

    return _inner


def set_workspace_split(enabled):
    def _inner(qtile):
        global groups_split_active

        laptop_screen, external_screen = _get_laptop_and_external_screens(qtile)

        if external_screen is None or not enabled:
            groups_split_active = False
            for name in "12345678":
                if name in qtile.groups_map:
                    qtile.groups_map[name].toscreen(laptop_screen)
            _set_groupbox_visibility(qtile)
            qtile.to_screen(laptop_screen)
            qtile.groups_map["1"].toscreen(laptop_screen)
            return

        groups_split_active = True
        main_screen, other_screen = _get_split_screens(qtile)

        for name in "1234":
            if name in qtile.groups_map:
                qtile.groups_map[name].toscreen(main_screen)

        for name in "5678":
            if name in qtile.groups_map:
                qtile.groups_map[name].toscreen(other_screen)

        _set_groupbox_visibility(qtile)
        qtile.to_screen(main_screen)
        qtile.groups_map["1"].toscreen(main_screen)

    return _inner


def swap_main_display(qtile):
    """Flip which monitor is MAIN (workspaces 1-4 + full bar) on the fly."""
    new_value = "internal" if ONE_TO_FOUR_ON_EXTERNAL else "external"
    Path("/tmp/qtile-main-display").write_text(new_value)

    # Move the new main display to the LEFT. Popen, not run: wlr-randr is a
    # wayland client — waiting on it from inside the compositor's own loop
    # deadlocks. The resulting screen_change reload is idempotent with ours.
    subprocess.Popen([str(QTILE_CONF / "scripts" / "set-output-layout.sh")])

    # Reload picks up the override (settings.py) and rebuilds bars with the
    # swapped roles; then re-place the groups via the freshly loaded module.
    qtile.reload_config()
    import modules.groups as fresh

    fresh.set_workspace_split(1)(qtile)
    subprocess.Popen(["notify-send", "-t", "3000", "Main display",
                      f"Workspaces 1-4 + full bar on {new_value}"])


def init_group_bindings(groups):
    for i in groups:
        if isinstance(i, ScratchPad):
            continue
        keys.extend(
            [
                Key(
                    [MOD],
                    i.name,
                    lazy.function(go_to_group(i.name)),
                    desc=f"Switch to group {i.name}",
                ),
                Key(
                    [MOD, "shift"],
                    i.name,
                    lazy.function(go_to_group_and_move_window(i.name)),
                    desc=f"Move focused window to group {i.name}",
                ),
            ]
        )

    keys.extend(
        [
            Key([MOD], "grave", lazy.group["9"].dropdown_toggle("term")),
            Key([MOD], "q", lazy.group["9"].dropdown_toggle("chatgpt")),
            Key(
                [MOD, "control"],
                "1",
                lazy.function(set_workspace_split(0)),
                # Use when external monitor is connected but unavailable (e.g. power cut): keep all workspaces on laptop.
                desc="Move workspaces 1-8 to laptop screen",
            ),
            Key(
                [MOD, "control"],
                "2",
                lazy.function(set_workspace_split(1)),
                # Use when external monitor is back: restore the 1-4 / 5-8 split.
                desc="Restore workspace split across monitors",
            ),
            Key(
                [MOD, "control"],
                "3",
                lazy.function(swap_main_display),
                desc="Swap main display (workspaces 1-4 + full bar)",
            ),
            Key(
                [MOD, "control"],
                "0",
                # Docked-mode toggle: this laptop's firmware never reports lid
                # events, so press this before closing / after opening the lid.
                lazy.spawn(str(QTILE_CONF / "toggle-internal-screen.sh")),
                desc="Toggle laptop screen (docked mode)",
            ),
        ]
    )
