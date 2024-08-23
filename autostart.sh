#!/bin/bash

# clipboard
copyq &

# desktop notification
mako &

# Outputs
kanshi &

# /usr/bin/emacs --daemon &

# nm-applet
nm-applet --indicator &
/usr/bin/kdeconnectd &
kdeconnect-indicator &

# wallpaper
swww-daemon &

# gnome polkit
/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1 &

# gnome keyring
dbus-update-activation-environment --all &
gnome-keyring-daemon --start --components=secrets &
