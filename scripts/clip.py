import os
import subprocess
from pathlib import Path

# --- Constants ---
CACHE_DIR = Path.home() / ".cache" / "cliphist" / "thumbs"
ROFI_THEME = """
    * { font: "JetBrainsMono Nerd Font 10"; }
    listview { lines: 10; }
    element-icon { size: 6ch; }
    element-text { vertical-align: 0.5; }
"""


def run_command(cmd, input_data=None, capture=True, env=None):
    """Helper to run subprocess commands."""
    try:
        if input_data:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE if capture else None,
                stderr=subprocess.PIPE,
                env=env,
            )
            stdout, stderr = proc.communicate(input=input_data)
            return stdout
        else:
            result = subprocess.run(cmd, capture_output=capture, env=env, check=True)
            return result.stdout
    except subprocess.CalledProcessError:
        return None
    except Exception:
        return None


def main():
    # Fix xkbcommon locale error
    env = os.environ.copy()
    env["LC_ALL"] = "en_IN.UTF-8"

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Get clipboard history
    stdout = run_command(["cliphist", "list"], env=env)
    if not stdout:
        return

    lines = stdout.decode("utf-8", errors="ignore").strip().splitlines()
    if not lines:
        return

    # Process only the first 250 items for faster load times
    lines = lines[:250]

    # 2. Process items for Rofi
    rofi_lines = []
    for line in lines:
        parts = line.split("\t", 1)
        if len(parts) < 2:
            continue

        clip_id, text = parts

        # Check for image content
        if "[[ binary data" in text and any(
            ext in text.lower() for ext in ["png", "jpg", "jpeg", "webp"]
        ):
            thumb_path = CACHE_DIR / f"{clip_id}.png"

            # Generate thumbnail if missing
            if not thumb_path.exists():
                data = run_command(["cliphist", "decode", clip_id], env=env)
                if data:
                    thumb_path.write_bytes(data)

            # Append icon metadata for Rofi
            rofi_lines.append(f"{line}\0icon\x1f{thumb_path}")
        else:
            rofi_lines.append(line)

    # 3. Show Rofi selection menu
    rofi_input = "\n".join(rofi_lines).encode("utf-8")
    selected = run_command(
        ["rofi", "-dmenu", "-p", "Clipboard", "-show-icons", "-theme-str", ROFI_THEME],
        input_data=rofi_input,
        env=env,
    )

    # 4. Decode and copy selection
    if selected:
        try:
            selected_text = selected.decode("utf-8").strip()
            clip_id = selected_text.split("\t")[0]

            decoded_data = run_command(["cliphist", "decode", clip_id], env=env)
            if decoded_data:
                # Use wl-copy for Wayland, xclip for X11 fallback if needed
                # But since the user is on Wayland mostly, wl-copy is fine.
                subprocess.run(["wl-copy"], input=decoded_data, check=True)
        except Exception:
            pass


if __name__ == "__main__":
    main()
