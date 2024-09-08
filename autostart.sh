#!/bin/bash

# Check if running under X11
if [ "$XDG_SESSION_TYPE" = "x11" ]; then
  setxkbmap -option caps:escape
  xset r rate 210 40
  copyq &
  dunst &
  # /usr/bin/emacs --daemon &
  nm-applet --indicator &
  # /usr/bin/kdeconnectd &
  # kdeconnect-indicator &
  ./.fehbg &
  picom &
  /usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1 &
  dbus-update-activation-environment --all &
  gnome-keyring-daemon --start --components=secrets &
fi

if [ "$XDG_SESSION_TYPE" = "wayland" ]; then
  copyq &
  mako &
  kanshi &
  # /usr/bin/emacs --daemon &
  nm-applet --indicator &
  # /usr/bin/kdeconnectd &
  # kdeconnect-indicator &
  swww-daemon &
  /usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1 &
  dbus-update-activation-environment --all &
  gnome-keyring-daemon --start --components=secrets &
fi
