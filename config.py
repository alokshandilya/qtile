import os
import subprocess
from libqtile import bar, hook, layout, qtile
from libqtile.backend.wayland.inputs import InputConfig
from libqtile.config import (
    Click,
    Drag,
    DropDown,
    Group,
    Key,
    KeyChord,
    Match,
    ScratchPad,
    Screen,
)
from libqtile.lazy import lazy
from qtile_extras import widget
from qtile_extras.widget.decorations import BorderDecoration

mod = "mod4"
terminal = "kitty"
gpu = "DRI_PRIME=pci-0000_01_00_0 __VK_LAYER_NV_optimus=NVIDIA_only __GLX_VENDOR_LIBRARY_NAME=nvidia"
gpu_term = "alacritty"


@hook.subscribe.startup_once
def autostart():
    home = os.path.expanduser("~/.config/qtile/autostart.sh")
    subprocess.Popen([home])


emacs_run = "emacsclient -c -a 'emacs' --eval '(dashboard-refresh-buffer)'"

keys = [
    Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    Key([mod], "space", lazy.layout.next()),
    Key([mod], "r", lazy.spawncmd()),
    Key([], "print", lazy.spawn("grim")),
    Key([mod], "h", lazy.layout.left()),
    Key([mod], "l", lazy.layout.right()),
    Key([mod], "j", lazy.layout.down()),
    Key([mod], "k", lazy.layout.up()),
    Key([mod, "shift"], "h", lazy.layout.swap_left()),
    Key([mod, "shift"], "l", lazy.layout.swap_right()),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down()),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up()),
    Key([mod], "i", lazy.layout.grow()),
    Key([mod], "m", lazy.layout.shrink()),
    Key([mod], "n", lazy.layout.reset()),
    Key([mod, "shift"], "n", lazy.layout.normalize()),
    Key([mod], "o", lazy.layout.maximize()),
    Key([mod, "shift"], "space", lazy.layout.flip()),
    Key([mod, "shift"], "h", lazy.layout.shuffle_left()),
    Key([mod, "shift"], "l", lazy.layout.shuffle_right()),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down()),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up()),
    Key([mod, "shift"], "Return", lazy.layout.toggle_split()),
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    Key(
        [mod, "shift"],
        "Return",
        lazy.spawn(f"env {gpu} {gpu_term}"),
        desc="Launch terminal",
    ),
    Key([mod], "w", lazy.spawn("librewolf"), desc="Launch Librewolf"),
    Key([mod], "grave", lazy.group["scratchpad"].dropdown_toggle("term")),
    Key([mod], "q", lazy.group["scratchpad"].dropdown_toggle("chatgpt")),
    Key([mod], "d", lazy.spawn("rofi -show drun")),
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod, "shift"], "q", lazy.window.kill(), desc="Kill focused window"),
    Key([mod, "control"], "l", lazy.spawn("brightnessctl s 1%+")),
    Key([mod, "control"], "h", lazy.spawn("brightnessctl s 1%-")),
    Key([mod, "control"], "k", lazy.spawn("amixer -q set Master 2%+")),
    Key([mod, "control"], "j", lazy.spawn("amixer -q set Master 2%-")),
    Key([mod], "f", lazy.window.toggle_fullscreen()),
    Key([mod], "t", lazy.window.toggle_floating()),
    KeyChord(
        [mod], "x", [Key([], "r", lazy.reload_config()), Key([], "x", lazy.shutdown())]
    ),
    KeyChord([mod], "b", [Key([], "m", lazy.spawn("blueman-manager"))]),
    KeyChord(
        [mod],
        "e",
        [
            Key([], "f", lazy.group["scratchpad"].dropdown_toggle("file_manager")),
            Key([], "f", lazy.spawn("thunar")),
            Key([], "e", lazy.spawn(f"{emacs_run}")),
        ],
    ),
    KeyChord(
        [mod],
        "v",
        [
            # Key([], "c", lazy.spawn(f"env {gpu} code")),
            # Key([], "c", lazy.spawn(f"env {gpu} zeditor")),
            Key([], "c", lazy.spawn("zeditor")),
            Key([], "v", lazy.spawn("pavucontrol")),
        ],
    ),
]

for vt in range(1, 8):
    keys.append(
        Key(
            ["control", "mod1"],
            f"f{vt}",
            lazy.core.change_vt(vt).when(func=lambda: qtile.core.name == "wayland"),
            desc=f"Switch to VT{vt}",
        )
    )


groups = []
group_names = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

# group_labels = ["1", "2", "3", "4", "5", "6", "7", "8", "9",]
# group_labels = ["DEV", "WWW", "SYS", "DOC", "VBOX", "CHAT", "MUS", "VID", "GFX",]
# static const char *tags[] = { "󰎦", "󰎩", "󰎬", "󰎮", "󰎰", "󰎵", "󰎸" , "󰎻", "󰎾" };
# static const char *alttags[] = { "", "", };
group_labels = ["󰎤", "󰎧", "󰎪", "󰎭", "󰎱", "󰎳", "󰎶", "󰎹", "󰎼"]
# group_layouts = ["monadtall", "monadtall", "tile", "tile", "monadtall", "monadtall", "monadtall", "monadtall", "monadtall"]

for i in range(len(group_names)):
    groups.append(
        Group(
            name=group_names[i],
            # layout=group_layouts[i].lower(),
            label=group_labels[i],
        )
    )
# scratchpads
groups.append(
    ScratchPad(
        "scratchpad",
        [
            DropDown(
                "term",
                f"{terminal}",
                x=0.1,
                y=0.015,
                opacity=1.0,
                width=0.80,
                height=0.6,
                on_focus_lost_hide=False,
            ),
            DropDown(
                "chatgpt",
                "librewolf -new-window 'https://chatgpt.com'",
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

for i in groups:
    keys.extend(
        [
            # mod + group number = switch to group
            Key(
                [mod],
                i.name,
                lazy.group[i.name].toscreen(),
                desc="Switch to group {}".format(i.name),
            ),
            # mod + shift + group number = switch to & move focused window to group
            # Key(
            #     [mod, "shift"],
            #     i.name,
            #     lazy.window.togroup(i.name, switch_group=True),
            #     desc="Switch to & move focused window to group {}".format(i.name),
            # ),
            # Or, use below if you prefer not to switch to that group.
            # mod + shift + group number = move focused window to group
            Key(
                [mod, "shift"],
                i.name,
                lazy.window.togroup(i.name),
                desc="move focused window to group {}".format(i.name),
            ),
        ]
    )

colors = [
    ["#689d6a", "#689d6a"],  # ACTIVE WORKSPACES 0
    ["#282828", "#282828"],  # INACTIVE WORKSPACES 1
    ["#504945", "#504945"],  # background lighter 2
    ["#fb4934", "#fb4934"],  # red 3
    ["#98971a", "#98971a"],  # green 4
    ["#d79921", "#d79921"],  # yellow 5
    ["#83a598", "#83a598"],  # blue 6
    ["#b16286", "#b16286"],  # magenta 7
    ["#8ec07c", "#8ec07c"],  # cyan 8
    ["#ebdbb2", "#ebdbb2"],  # white 9
    ["#928374", "#928374"],  # grey 10
    ["#d65d0e", "#d65d0e"],  # orange 11
    ["#689d6a", "#689d6a"],  # super cyan12
    ["#458588", "#458588"],  # super blue 13
    ["#1d2021", "#1d2021"],  # super dark background 14
]

layouts = [
    # layout.Columns(border_focus_stack=["#d75f5f", "#8f3d3d"], border_width=2, margin=4),
    layout.MonadTall(
        border_focus=colors[12],
        border_normal=colors[2],
        border_width=2,
        single_border_width=2,
        margin=8,
        single_margin=12,
        ratio=0.55,
        new_client_position="top",
        flip=True,
    ),
    layout.Max(),
    # Try more layouts by unleashing below layouts.
    # layout.Stack(num_stacks=2),
    # layout.Bsp(),
    # layout.Matrix(),
    # layout.MonadWide(),
    # layout.RatioTile(),
    # layout.Tile(),
    # layout.TreeTab(),
    layout.TreeTab(
        font="FiraCode Nerd Font Bold",
        fontsize=13,
        border_width=0,
        bg_color=colors[14],
        active_bg=colors[0],
        active_fg=colors[2],
        inactive_bg=colors[1],
        inactive_fg=colors[0],
        padding_left=8,
        padding_x=8,
        padding_y=6,
        sections=["ONE", "TWO", "THREE"],
        section_fontsize=10,
        section_fg=colors[7],
        section_top=15,
        section_bottom=15,
        level_shift=8,
        vspace=3,
        panel_width=240,
    ),
    # layout.VerticalTile(),
    # layout.Zoomy(),
]

widget_defaults = dict(
    font="JetBrainsMono Nerd Font Bold", fontsize=13, padding=0, background=colors[14]
)

extension_defaults = widget_defaults.copy()

screens = [
    Screen(
        top=bar.Bar(
            [
                widget.Image(
                    filename="~/.config/doom/me-gruv-circle.png",
                    scale="False",
                    mouse_callbacks={"Button1": lambda: qtile.cmd_spawn(terminal)},
                    margin_x=11,
                    margin_y=1,
                ),
                widget.GroupBox(
                    hide_unused=True,
                    font="JetBrainsMono Nerd Font",
                    fontsize=19,
                    margin_y=4,
                    margin_x=0,
                    padding_y=0,
                    padding_x=4,
                    borderwidth=2,
                    active=colors[8],
                    inactive=colors[1],
                    rounded=False,
                    highlight_color=colors[2],
                    highlight_method="line",
                    this_current_screen_border=colors[7],
                    this_screen_border=colors[4],
                    other_current_screen_border=colors[7],
                    other_screen_border=colors[4],
                    disable_drag=True,
                ),
                widget.Spacer(length=8),
                widget.CurrentLayoutIcon(
                    foreground=colors[9],
                    padding=4,
                    scale=0.75,
                ),
                widget.Prompt(
                    font="FiraCode Nerd Font Mono Bold",
                    foreground=colors[13],
                    fontsize=13,
                ),
                widget.CurrentLayout(
                    fontsize=13,
                    foreground=colors[9],
                    padding=5,
                ),
                widget.TextBox("|", name="sep"),
                widget.Spacer(length=4),
                widget.WindowName(
                    fontsize=14,
                    foreground=colors[8],
                    max_chars=40,
                ),
                widget.Net(
                    # format='🔻{down:.0f}{down_suffix} 🔺{up:.0f}{up_suffix}',
                    format=" {down:.0f}{down_suffix}  {up:.0f}{up_suffix}",
                    interface="wlan0",
                    padding=0,
                    margin=0,
                    foreground=colors[13],
                    decorations=[
                        BorderDecoration(
                            border_width=[0, 0, 2, 0],
                            colour=colors[13],
                        )
                    ],
                ),
                widget.Spacer(length=8),
                widget.Memory(
                    # format="🖥 {MemUsed:.0f}{mm}/{MemTotal:.0f}{mm}",
                    format="  {MemUsed:.0f}{mm}/{MemTotal:.0f}{mm}",
                    foreground=colors[7],
                    decorations=[
                        BorderDecoration(
                            border_width=[0, 0, 2, 0],
                            colour=colors[7],
                        )
                    ],
                ),
                widget.Spacer(length=8),
                widget.CPU(
                    # format="🗳️ {load_percent}%",
                    format="  {load_percent}%",
                    foreground=colors[11],
                    decorations=[
                        BorderDecoration(
                            border_width=[0, 0, 2, 0],
                            colour=colors[11],
                        )
                    ],
                ),
                widget.Spacer(length=8),
                widget.Battery(
                    # format="🔋 {percent:2.0%}", notify_below=97,
                    format="  {percent:2.0%}",
                    notify_below=10,
                    foreground=colors[12],
                    decorations=[
                        BorderDecoration(
                            border_width=[0, 0, 2, 0],
                            colour=colors[12],
                        )
                    ],
                ),
                widget.Spacer(length=8),
                widget.Volume(
                    # fmt="🔊 {}",
                    fmt="  {}",
                    foreground=colors[5],
                    decorations=[
                        BorderDecoration(
                            border_width=[0, 0, 2, 0],
                            colour=colors[5],
                        )
                    ],
                ),
                widget.Spacer(length=8),
                widget.Clock(
                    # format="📅 %a, %B %d %l:%M%p",
                    format="  %a, %B %d %l:%M%p",
                    foreground=colors[4],
                    decorations=[
                        BorderDecoration(
                            border_width=[0, 0, 2, 0],
                            colour=colors[4],
                        )
                    ],
                ),
                widget.Spacer(length=8),
                # Systray is incompatible with Wayland, consider using StatusNotifier instead
                # widget.Systray(),
                widget.StatusNotifier(),
            ],
            28,
            # border_width=[3, 0, 3, 0],  # Draw top and bottom borders
            # border_color=["ff00ff", "000000", "ff00ff", "000000"]  # Borders are magenta
        ),
        # You can uncomment this variable if you see that on X11 floating resize/moving is laggy
        # By default we handle these events delayed to already improve performance, however your system might still be struggling
        # This variable is set to None (no cap) by default, but you can set it to 60 to indicate that you limit it to 60 events per second
        # x11_drag_polling_rate = 60,
    ),
]

# Drag floating layouts.
mouse = [
    Drag(
        [mod],
        "Button1",
        lazy.window.set_position_floating(),
        start=lazy.window.get_position(),
    ),
    Drag(
        [mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()
    ),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
floats_kept_above = True
cursor_warp = False
floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
    ]
)
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = {
    "type:touchpad": InputConfig(tap=True, natural_scroll=True, left_handed=False),
    # "*": InputConfig(left_handed=False),
    "type:keyboard": InputConfig(
        kb_options="caps:escape,compose:ralt",
        kb_repeat_rate=40,
        kb_repeat_delay=210,
    ),
}

# xcursor theme (string or None) and size (integer) for Wayland backend
wl_xcursor_theme = "Qogir-manjaro-light"
wl_xcursor_size = 24

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
