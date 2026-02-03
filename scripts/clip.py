import subprocess
import os

CACHE_DIR = os.path.expanduser("~/.cache/cliphist/thumbs")
ROFI_THEME = """
    * { font: "JetBrainsMono Nerd Font 10"; }
    element-icon { size: 6ch; }
    element-text { vertical-align: 0.5; }
"""

def main():
    # Fix xkbcommon locale error
    env = os.environ.copy()
    env["LC_ALL"] = "en_IN.UTF-8"
    
    os.makedirs(CACHE_DIR, exist_ok=True)

    # 1. Get clipboard history
    try:
        ps = subprocess.run(["cliphist", "list"], capture_output=True, env=env)
        lines = ps.stdout.decode("utf-8", errors="ignore").strip().splitlines()
    except Exception:
        return

    if not lines:
        return

    # 2. Process items for Rofi
    rofi_lines = []
    for line in lines:
        parts = line.split("\t", 1)
        if len(parts) < 2:
            continue
        
        clip_id, text = parts
        
        # Check for image content
        if "[[ binary data" in text and any(ext in text for ext in ["png", "jpg", "jpeg"]):
            thumb_path = os.path.join(CACHE_DIR, f"{clip_id}.png")
            
            # Generate thumbnail if missing
            if not os.path.exists(thumb_path):
                with open(thumb_path, "wb") as f:
                    subprocess.run(["cliphist", "decode", clip_id], stdout=f, env=env)
            
            # Append icon metadata for Rofi
            rofi_lines.append(f"{line}\0icon\x1f{thumb_path}")
        else:
            rofi_lines.append(line)

    # 3. Show Rofi selection menu
    rofi_input = "\n".join(rofi_lines).encode("utf-8")
    
    try:
        p_rofi = subprocess.Popen(
            ["rofi", "-dmenu", "-p", "Clipboard", "-show-icons", "-theme-str", ROFI_THEME],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            env=env
        )
        selected, _ = p_rofi.communicate(input=rofi_input)
    except Exception:
        return

    # 4. Decode and copy selection
    if selected:
        try:
            # Extract ID from the selected line (format: ID\tText...)
            selected_text = selected.decode("utf-8").strip()
            clip_id = selected_text.split("\t")[0]
            
            p_decode = subprocess.Popen(["cliphist", "decode", clip_id], stdout=subprocess.PIPE, env=env)
            decoded_data, _ = p_decode.communicate()
            
            subprocess.run(["wl-copy"], input=decoded_data)
        except Exception:
            pass

if __name__ == "__main__":
    main()