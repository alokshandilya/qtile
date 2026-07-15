#!/bin/bash
#
# Positions outputs so the MAIN display (the one hosting workspaces 1-4)
# sits on the LEFT. Main display resolution: /tmp/qtile-main-display
# override (written by MOD+Ctrl+3), else "external" — keep that default in
# sync with WORKSPACES_1_TO_4_ON in modules/settings.py.

MAIN="external"
if [ -f /tmp/qtile-main-display ]; then
  value=$(cat /tmp/qtile-main-display)
  case "$value" in
  external | internal) MAIN="$value" ;;
  esac
fi

if [ "$MAIN" = "internal" ]; then
  LEFT="eDP-1" RIGHT="HDMI-A-1"
else
  LEFT="HDMI-A-1" RIGHT="eDP-1"
fi

wlr-randr --output "$LEFT" --pos 0,0 --output "$RIGHT" --pos 1920,0
