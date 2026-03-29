import asyncio
import subprocess
from libqtile import hook, qtile
from .settings import QTILE_CONF, IS_WAYLAND


@hook.subscribe.startup_once
def autostart():
    autostart_sh = QTILE_CONF / "autostart.sh"
    if autostart_sh.exists():
        subprocess.Popen([str(autostart_sh)])


@hook.subscribe.startup_complete
def focus_first_workspace():
    if "1" in qtile.groups_map:
        group = qtile.groups_map["1"]
        group.cmd_toscreen()
        screen = qtile.current_screen
        qtile.core.warp_pointer(
            screen.x + screen.width // 2,
            screen.y + screen.height // 2,
        )


_reload_task = None


@hook.subscribe.screen_change
def screen_change(event):
    global _reload_task
    if _reload_task:
        _reload_task.cancel()

    async def reload_config():
        await asyncio.sleep(1.0)
        if not IS_WAYLAND:
            proc = await asyncio.create_subprocess_exec("xrandr", "--auto")
            await proc.wait()
        qtile.cmd_reload_config()

    _reload_task = asyncio.create_task(reload_config())
