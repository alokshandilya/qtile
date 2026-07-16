import asyncio
import subprocess

from libqtile import hook, qtile

from .settings import IS_WAYLAND, QTILE_CONF


@hook.subscribe.startup_once
def autostart():
    autostart_sh = QTILE_CONF / "autostart.sh"
    if autostart_sh.exists():
        print(f"Executing autostart script: {autostart_sh}")
        subprocess.Popen([str(autostart_sh)])
    else:
        print(f"Autostart script not found: {autostart_sh}")


@hook.subscribe.startup_complete
def focus_first_workspace():
    # Place groups by actual output identity (laptop panel detected by name),
    # not by static screen_affinity, which assumes a fixed screen order.
    from .groups import set_workspace_split

    set_workspace_split(1)(qtile)
    screen = qtile.current_screen
    qtile.core.warp_pointer(
        screen.x + screen.width // 2,
        screen.y + screen.height // 2,
    )
    # One conky per monitor (script focuses each screen to place the layer
    # surface, then restores focus). Popen: it calls back into qtile via
    # cmd-obj, so it must not block this hook.
    subprocess.Popen([str(QTILE_CONF / "scripts" / "restart-conky.sh")])


_screen_task = None


@hook.subscribe.screen_change
def screen_change(event):
    global _screen_task
    if _screen_task:
        _screen_task.cancel()

    async def reload_after_settle():
        # NOTE: do NOT run set-output-layout.sh (or any wlr-randr call) from
        # this hook. Its apply re-triggers screen_change on this machine's
        # flaky DRM, producing an endless reload loop (config reload every
        # ~2.7s, visible input lag). Positions are asserted only from
        # explicit actions: boot, dock toggle, MOD+Ctrl+2/3.

        # Settle first: this machine's DRM driver retries/rolls back atomic
        # commits, and reloading mid-churn configures bar widgets against
        # dead drawing surfaces.
        await asyncio.sleep(2.5)
        if not IS_WAYLAND:
            proc = await asyncio.create_subprocess_exec("xrandr", "--auto")
            await proc.wait()

        # CRITICAL (Wayland): before reloading, finalize bars of config
        # screens that lost their output. reload_config only finalizes bars
        # of screens still in qtile.screens, so an unbound screen's bar
        # window survives forever as an immortal "zombie" bar covering the
        # real one on the surviving monitor.
        bound = list(qtile.screens)
        for scr in qtile.config.screens:
            if scr not in bound and scr.top and getattr(scr.top, "window", None):
                scr.top.finalize()

        qtile.reload_config()

        # Zombie sweep. Even after the above, a bar window can leak through
        # a reload (widgets_map is keyed by widget NAME, so duplicate-named
        # widgets on the second bar are never finalized; their timers keep
        # drawing, raising the dead bar's window above the real one). Kill
        # every Internal window that is not a current screen's bar.
        bar_wids = set()
        for scr in qtile.screens:
            for gap in (scr.top, scr.bottom, scr.left, scr.right):
                win = getattr(gap, "window", None) if gap else None
                if win:
                    bar_wids.add(win.wid)
        for wid, win in list(qtile.windows_map.items()):
            if win.__class__.__name__ == "Internal" and wid not in bar_wids:
                win.kill()
        for scr in qtile.screens:
            if scr.top:
                scr.top.draw()

        # Re-assert group placement after the reload: screen indices can
        # change with the output layout, so place groups by output identity.
        # Import resolves to the freshly reloaded module, whose state the
        # new keybindings read.
        from .groups import set_workspace_split

        set_workspace_split(1)(qtile)

        # Re-spread conky across the monitors that now exist. Launching layer
        # surfaces does not fire screen_change, so this cannot loop (unlike
        # wlr-randr calls — see the warning above).
        subprocess.Popen([str(QTILE_CONF / "scripts" / "restart-conky.sh")])

    _screen_task = asyncio.create_task(reload_after_settle())
