#!/bin/bash
#
# Docked-mode toggle for qtile (Wayland). Bound to MOD+Ctrl+0.
#
# This laptop's firmware never reports lid events to the OS (verified: ACPI
# lid state, logind LidClosed, DRM connector status and the evdev Lid Switch
# all stay silent on lid close), so automatic lid handling is impossible.
# Press this before closing / after opening the lid instead.
#
# How it works:
#   - The flag file is the source of truth for get_monitors() in config.py
#     (querying the compositor from inside a config reload deadlocks, and the
#     DRM connector count can't see a disabled-but-connected panel).
#   - The DRM driver intermittently rolls output changes back ("Atomic commit
#     failed: Device or resource busy" in qtile's log), sometimes seconds
#     after they first appear to stick. So we re-assert the desired state
#     every second and only declare success once it has held for
#     STABLE_SECONDS consecutive checks.
#   - qtile's screen_change hook then reloads the config (2.5s after the last
#     change), reads the flag, and rebuilds screens/bars for the right layout.

INTERNAL="eDP-1"
FLAG="/tmp/qtile-docked-mode"
STABLE_SECONDS=3
MAX_SECONDS=15

# Single-instance guard: a second press while a toggle is settling would fight it.
LOCK="/tmp/qtile-docked-toggle.lock"
if ! mkdir "$LOCK" 2>/dev/null; then
  exit 0
fi
trap 'rmdir "$LOCK"' EXIT

query() {
  # prints: "<on|off> <count-of-other-enabled-outputs>"
  wlr-randr --json 2>/dev/null | python3 -c "
import json, sys
outs = json.load(sys.stdin)
internal_on = any(o['name'] == '$INTERNAL' and o.get('enabled') for o in outs)
others_on = sum(1 for o in outs if o['name'] != '$INTERNAL' and o.get('enabled'))
print(('on' if internal_on else 'off'), others_on)
"
}

notify() { command -v notify-send >/dev/null && notify-send -t 3000 "Docked mode" "$1"; }

state=$(query)
internal=${state% *}
others=${state#* }

# Decide direction from the flag when present (it is the intended state);
# otherwise from the actual output state.
if [ -f "$FLAG" ]; then
  target="on"    # currently docked -> undock
else
  target="off"   # currently normal -> dock
  if [ "$internal" = "on" ] && [ "${others:-0}" -eq 0 ]; then
    notify "No external monitor — refusing to turn off the only screen"
    exit 1
  fi
fi

# Set intent FIRST so any config reload fired mid-churn already sees it.
if [ "$target" = "off" ]; then
  touch "$FLAG"
else
  rm -f "$FLAG"
fi

stable=0
for i in $(seq 1 "$MAX_SECONDS"); do
  now=$(query)
  if [ "${now% *}" = "$target" ]; then
    stable=$((stable + 1))
    if [ "$stable" -ge "$STABLE_SECONDS" ]; then
      if [ "$target" = "on" ]; then
        # Re-assert layout: the MAIN display (workspaces 1-4) sits on the left.
        "$(dirname "$0")/scripts/set-output-layout.sh"
      fi
      # xdg-desktop-portal-wlr enumerates outputs once at startup, so screen
      # sharing breaks after any output change until it restarts. Restart only
      # the backend: restarting the frontend (xdg-desktop-portal) severs
      # running apps' portal connections until they're relaunched.
      systemctl --user restart xdg-desktop-portal-wlr
      if [ "$target" = "off" ]; then
        notify "Laptop screen OFF — workspaces on external monitor"
      else
        notify "Laptop screen ON — workspaces 5-8 back on internal"
      fi
      exit 0
    fi
  else
    stable=0
    wlr-randr --output "$INTERNAL" "--$target"
  fi
  sleep 1
done

# Could not make it stick: revert intent so config state matches reality.
if [ "$target" = "off" ]; then rm -f "$FLAG"; else touch "$FLAG"; fi
notify "Failed: compositor kept rolling the change back (see qtile log)"
exit 1
