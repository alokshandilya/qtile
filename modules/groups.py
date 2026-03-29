from libqtile.config import DropDown, Group, Key, ScratchPad
from libqtile.lazy import lazy

from .keys import keys
from .settings import GROUPS_CONF, MOD, TERMINAL


def get_groups(num_monitors):
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
        if len(qtile.screens) == 1:
            qtile.groups_map[name].toscreen()
            return

        target_screen = 1 if name in "1234" else 0
        qtile.to_screen(target_screen)
        qtile.groups_map[name].toscreen()

    return _inner


def go_to_group_and_move_window(name):
    def _inner(qtile):
        if not qtile.current_window:
            return

        if len(qtile.screens) == 1:
            qtile.current_window.togroup(name, switch_group=True)
            return

        target_screen = 1 if name in "1234" else 0
        qtile.current_window.togroup(name, switch_group=False)
        qtile.to_screen(target_screen)
        qtile.groups_map[name].toscreen()

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
        ]
    )
