from libqtile import layout
from libqtile.config import Match

from .settings import COLORS

layouts = [
    layout.MonadTall(
        border_focus=COLORS["super_cyan"],
        border_normal=COLORS["bg_lighter"],
        border_width=2,
        single_border_width=2,
        margin=7,
        single_margin=7,
        ratio=0.55,
        new_client_position="top",
        flip=True,
    ),
    layout.Max(
        margin=7,
        border_focus=COLORS["cyan"],
        border_normal=COLORS["bg_lighter"],
        border_width=2,
    ),
]

floating_layout = layout.Floating(
    float_rules=[
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
    ],
    border_focus=COLORS["cyan"],
    border_normal=COLORS["bg_lighter"],
    border_width=2,
)
