from libqtile.config import DropDown, Group, Key, ScratchPad
from libqtile.lazy import lazy

from .keys import keys
from .settings import GROUPS_CONF, IS_WAYLAND, MOD, TERMINAL

groups_1_to_4_on_external = True


def _get_laptop_and_external_screens(qtile):
    if len(qtile.screens) < 2:
        return 0, None

    laptop_screen = 0

    if IS_WAYLAND and hasattr(qtile.core, "outputs"):
        for idx, output in enumerate(qtile.core.outputs):
            name = getattr(output, "name", "").lower()
            if any(token in name for token in ("edp", "lvds", "dsi")):
                if idx < len(qtile.screens):
                    laptop_screen = idx
                break

    external_screen = next(
        (idx for idx in range(len(qtile.screens)) if idx != laptop_screen),
        None,
    )
    return laptop_screen, external_screen


def _set_laptop_groupbox_visibility(qtile):
    laptop_screen, _ = _get_laptop_and_external_screens(qtile)

    if laptop_screen >= len(qtile.screens):
        return

    screen = qtile.screens[laptop_screen]
    if not getattr(screen, "top", None):
        return

    visible_groups = ["5", "6", "7", "8"] if groups_1_to_4_on_external else None

    for wid in screen.top.widgets:
        if wid.__class__.__name__ == "GroupBox":
            wid.visible_groups = visible_groups
            wid.bar.draw()
            break


def get_groups(num_monitors):
    global groups_1_to_4_on_external
    groups_1_to_4_on_external = num_monitors > 1

    groups = [
        Group(
            name=name,
            label=label,
            screen_affinity=1 if (i < 4 and num_monitors > 1) else 0,
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
                    "firefox -new-window 'https://chatgpt.com'",
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
        laptop_screen, external_screen = _get_laptop_and_external_screens(qtile)
        target_screen = laptop_screen

        if name in "1234" and groups_1_to_4_on_external and external_screen is not None:
            target_screen = external_screen

        qtile.to_screen(target_screen)
        qtile.groups_map[name].toscreen()

    return _inner


def go_to_group_and_move_window(name):
    def _inner(qtile):
        if not qtile.current_window:
            return

        laptop_screen, external_screen = _get_laptop_and_external_screens(qtile)
        target_screen = laptop_screen

        if name in "1234" and groups_1_to_4_on_external and external_screen is not None:
            target_screen = external_screen

        qtile.current_window.togroup(name, switch_group=False)
        qtile.to_screen(target_screen)
        qtile.groups_map[name].toscreen()

    return _inner


def set_workspace_1_to_4_screen(one_to_four_screen):
    def _inner(qtile):
        global groups_1_to_4_on_external

        laptop_screen, external_screen = _get_laptop_and_external_screens(qtile)

        if external_screen is None:
            groups_1_to_4_on_external = False
            for name in "12345678":
                if name in qtile.groups_map:
                    qtile.groups_map[name].toscreen(laptop_screen)
            _set_laptop_groupbox_visibility(qtile)
            qtile.to_screen(laptop_screen)
            qtile.groups_map["1"].toscreen(laptop_screen)
            return

        groups_1_to_4_on_external = one_to_four_screen == 1
        one_to_four_target = (
            external_screen if groups_1_to_4_on_external else laptop_screen
        )

        for name in "1234":
            if name in qtile.groups_map:
                qtile.groups_map[name].toscreen(one_to_four_target)

        for name in "5678":
            if name in qtile.groups_map:
                qtile.groups_map[name].toscreen(laptop_screen)

        _set_laptop_groupbox_visibility(qtile)
        qtile.to_screen(one_to_four_target)
        qtile.groups_map["1"].toscreen(one_to_four_target)

    return _inner


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
                lazy.function(set_workspace_1_to_4_screen(0)),
                # Use when external monitor is connected but unavailable (e.g. power cut): keep all workspaces on laptop.
                desc="Move workspaces 1-8 to laptop screen",
            ),
            Key(
                [MOD, "control"],
                "2",
                lazy.function(set_workspace_1_to_4_screen(1)),
                # Use when external monitor is back: move workspaces 1-4 back to external monitor.
                desc="Move workspaces 1-4 to external screen",
            ),
        ]
    )
