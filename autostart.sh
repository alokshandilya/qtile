#!/bin/bash

copyq &

/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1 &
conky -c ~/.config/conky/gruvbox-material.conkyrc &
swww-daemon &
xfce4-power-manager &
/usr/bin/emacs --daemon &
nm-applet &
