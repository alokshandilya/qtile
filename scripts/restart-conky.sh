#!/bin/bash
#
# Show conky on every active monitor.
#
# Conky's Wayland backend has no output-selection option; qtile places a new
# layer surface on the currently FOCUSED screen. So: focus each screen in
# turn, launch one conky instance on it, then restore focus. Called from
# qtile hooks (startup_complete and the post-screen_change reload), so
# docking/undocking automatically re-spreads instances across the monitors
# that exist — with MOD+Ctrl+0 docked mode that means the external gets it.

CONF="$HOME/.config/conky/gruvbox-wayland.conkyrc"

# TERM first, then KILL: conky's wayland loop is slow to honor SIGTERM and
# instances pile up across relaunches without the hard fallback.
pkill -x conky
sleep 0.5
pkill -9 -x conky 2>/dev/null
sleep 0.2

NS=$(qtile cmd-obj -o root -f eval -a "len(self.screens)" 2>/dev/null | tr -dc '0-9')
[ -z "$NS" ] && NS=1
CUR=$(qtile cmd-obj -o root -f eval -a "self.screens.index(self.current_screen)" 2>/dev/null | tr -dc '0-9')

for i in $(seq 0 $((NS - 1))); do
  qtile cmd-obj -o root -f eval -a "self.to_screen($i)" >/dev/null 2>&1
  sleep 0.3
  conky -c "$CONF" >/dev/null 2>&1
  sleep 0.7 # let the layer surface map on this output before moving focus
done

[ -n "$CUR" ] && qtile cmd-obj -o root -f eval -a "self.to_screen($CUR)" >/dev/null 2>&1
