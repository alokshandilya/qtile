#!/bin/bash

copyq &

dunst &
/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1 &
dbus-update-activation-environment --all &
# conky -c ~/.config/conky/gruvbox-material.conkyrc &
# /usr/bin/emacs --daemon &
nm-applet &
/usr/bin/kdeconnectd &
kdeconnect-indicator &

swww-daemon &
