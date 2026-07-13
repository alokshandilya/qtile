#!/bin/bash

echo "AUTOSTART SCRIPT STARTED" >> /tmp/qtile-autostart.log 2>&1

# Check if running under X11
if [ "$XDG_SESSION_TYPE" = "x11" ]; then
  setxkbmap -option caps:escape &
  xset r rate 210 40 &
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
  conky -c ~/.config/conky/gruvbox-material.conkyrc &
fi

if [ "$XDG_SESSION_TYPE" = "wayland" ]; then
  # Stale docked-mode flag from a previous session would make get_monitors()
  # report 1 monitor even though a fresh compositor enables all outputs.
  rm -f /tmp/qtile-docked-mode

  # 1. Essential Environment Setup
  # XDG_CURRENT_DESKTOP is set in config.py (qtile's own env) and inherited here;
  # push it plus WAYLAND_DISPLAY to DBus/systemd activation environments
  dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP
  
  systemctl --user import-environment WAYLAND_DISPLAY XDG_CURRENT_DESKTOP
  systemctl --user restart xdg-desktop-portal-wlr
  systemctl --user restart xdg-desktop-portal
  gsettings set org.gnome.desktop.interface color-scheme "prefer-dark"

  # 3. Background Apps
  wl-paste --type text --watch cliphist store &
  wl-paste --type image --watch cliphist store &
  mako &
  kanshi &
  nm-applet --indicator &
  awww-daemon &
  /usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1 &
  gnome-keyring-daemon --start --components=secrets &
fi
