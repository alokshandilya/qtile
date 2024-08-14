#!/bin/bash

copyq &

dunst &
/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1 &
conky -c ~/.config/conky/gruvbox-material.conkyrc &
# xfce4-power-manager &
# /usr/bin/emacs --daemon &
nm-applet &
/usr/bin/kdeconnectd &
kdeconnect-indicator &

# for x11
# picom &
# ./.fehbg &

# for wayland
swww-daemon &
