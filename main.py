import os
import sys
import webbrowser
import urllib.parse

def get_base_path():
    # 1. If running from Program Files, always use the EXE directory
    exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    if "Program Files" in exe_dir:
        return exe_dir

    # 2. If running as a PyInstaller onefile EXE (portable mode)
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS

    # 3. Running from source
    return os.path.dirname(os.path.abspath(__file__))

def main():
    base_path = get_base_path()
    html_path = os.path.join(base_path, "index.html")

    if not os.path.exists(html_path):
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                0,
                f"index.html not found at:\n{html_path}",
                "Meeting Formatter Error",
                0
            )
        except:
            pass
        return

    url = "file:///" + urllib.parse.quote(html_path.replace("\\", "/"))

    try:
        os.startfile(html_path)
    except:
        webbrowser.open(url)

if __name__ == "__main__":
    main()