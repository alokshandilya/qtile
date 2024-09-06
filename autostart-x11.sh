#!/bin/bash

# clipboard
copyq &

# desktop notification
dunst &

# /usr/bin/emacs --daemon &

# nm-applet
nm-applet --indicator &
# /usr/bin/kdeconnectd &
# kdeconnect-indicator &

# wallpaper
./.fehbg &
picom &

# gnome polkit
/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1 &

# gnome keyring
dbus-update-activation-environment --all &
gnome-keyring-daemon --start --components=secrets &
