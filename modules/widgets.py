from libqtile import bar, qtile, widget
from qtile_extras import widget as extra_widget
from qtile_extras.widget.decorations import BorderDecoration

from .settings import COLORS, IS_WAYLAND, TERMINAL


def get_sep():
    return widget.TextBox("|", name="sep")


def get_spacer(length=8):
    return widget.Spacer(length=length)


def get_uptime():
    """Pure Python uptime reader. Fast and non-blocking."""
    try:
        with open("/proc/uptime", "r") as f:
            uptime_seconds = float(f.readline().split()[0])
            h, m = divmod(uptime_seconds, 3600)
            m, _ = divmod(m, 60)
            return f"{int(h)}h {int(m)}m"
    except Exception:
        return "N/A"


DECORATIONS = {
    name: [BorderDecoration(border_width=[0, 0, 2, 0], colour=color)]
    for name, color in COLORS.items()
}


widget_defaults = dict(
    font="JetBrainsMono Nerd Font Bold",
    fontsize=13,
    padding=0,
    background=COLORS["bg_dark"],
)


def init_widgets_list(visible_groups=None, is_primary=True):
    widgets = [
        widget.Image(
            filename="~/.config/doom/me-gruv-circle.png",
            scale="False",
            mouse_callbacks={"Button1": lambda: qtile.cmd_spawn(TERMINAL)},
            margin_x=11,
            margin_y=1,
        ),
        widget.GroupBox(
            visible_groups=visible_groups,
            hide_unused=True,
            font="JetBrainsMono Nerd Font",
            fontsize=18,
            margin_y=4,
            margin_x=0,
            padding_y=0,
            padding_x=4,
            borderwidth=3,
            active=COLORS["cyan"],
            inactive=COLORS["grey"],
            rounded=False,
            highlight_color=COLORS["bg_lighter"],
            highlight_method="line",
            this_current_screen_border=COLORS["magenta"],
            this_screen_border=COLORS["green"],
            other_current_screen_border=COLORS["magenta"],
            other_screen_border=COLORS["green"],
            disable_drag=True,
        ),
        get_spacer(),
        extra_widget.CurrentLayoutIcon(
            foreground=COLORS["white"],
            padding=4,
            scale=0.75,
            font=widget_defaults["font"],
        ),
        widget.CurrentLayout(
            fontsize=13,
            foreground=COLORS["white"],
            padding=5,
            font=widget_defaults["font"],
        ),
        widget.TextBox("|", name="sep", font=widget_defaults["font"]),
    ]

    if is_primary:
        widgets.extend(
            [
                get_spacer(5),
                widget.Prompt(
                    font="JetBrainsMono Nerd Font Bold",
                    foreground=COLORS["green"],
                    fontsize=14,
                ),
                get_spacer(4),
                widget.WindowName(
                    fontsize=14,
                    foreground=COLORS["cyan"],
                    max_chars=110,
                    font=widget_defaults["font"],
                ),
                extra_widget.Net(
                    format=" {down:.0f}{down_suffix}  {up:.0f}{up_suffix}",
                    interface="wlan0",
                    foreground=COLORS["super_blue"],
                    decorations=DECORATIONS["super_blue"],
                    update_interval=5,
                    font=widget_defaults["font"],
                ),
                get_spacer(),
                extra_widget.GenPollText(
                    update_interval=60,
                    func=get_uptime,
                    fmt="󱑀 {}",
                    foreground=COLORS["green"],
                    decorations=DECORATIONS["green"],
                    font=widget_defaults["font"],
                ),
                get_spacer(),
                extra_widget.Memory(
                    format="  {MemUsed:.0f}{mm}/{MemTotal:.0f}{mm}",
                    foreground=COLORS["magenta"],
                    decorations=DECORATIONS["magenta"],
                    update_interval=5,
                    font=widget_defaults["font"],
                ),
                get_spacer(),
                extra_widget.CPU(
                    format="  {load_percent}%",
                    foreground=COLORS["orange"],
                    decorations=DECORATIONS["orange"],
                    update_interval=5,
                    font=widget_defaults["font"],
                ),
                get_spacer(),
                extra_widget.Battery(
                    format="  {percent:2.0%}",
                    notify_below=10,
                    foreground=COLORS["super_cyan"],
                    decorations=DECORATIONS["super_cyan"],
                    update_interval=30,
                    font=widget_defaults["font"],
                ),
                get_spacer(),
                extra_widget.Volume(
                    fmt="  {}",
                    foreground=COLORS["yellow"],
                    decorations=DECORATIONS["yellow"],
                    update_interval=1,
                    font=widget_defaults["font"],
                ),
            ]
        )
    else:
        widgets.append(
            widget.WindowName(
                fontsize=14,
                foreground=COLORS["cyan"],
                max_chars=110,
                font=widget_defaults["font"],
                width=bar.STRETCH,
            )
        )

    widgets.extend(
        [
            get_spacer(),
            extra_widget.Clock(
                format="  %a, %B %d %l:%M%p",
                foreground=COLORS["green"],
                decorations=DECORATIONS["green"],
                update_interval=60,
                font=widget_defaults["font"],
            ),
            get_spacer(),
            widget.StatusNotifier() if IS_WAYLAND else widget.Systray(),
        ]
    )
    return widgets
