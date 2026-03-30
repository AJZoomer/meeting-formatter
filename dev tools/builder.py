import os
import shutil
import subprocess

# Get the project root (one folder up from dev tools)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEV_TOOLS_DIR = os.path.dirname(__file__)

# Paths
RELEASE_DIR = os.path.join(BASE_DIR, "release")
MAIN_SCRIPT = os.path.join(BASE_DIR, "main.py")
ICON_PATH = os.path.join(BASE_DIR, "icon1.ico")
OUTPUT_EXE_NAME = "meeting-formatter.exe"

def clean_build_folders():
    shutil.rmtree(os.path.join(BASE_DIR, "build"), ignore_errors=True)
    shutil.rmtree(os.path.join(BASE_DIR, "dist"), ignore_errors=True)
    print("Cleaned old build folders.")

def build_exe():
    print("Building launcher (silent)...")

    html_path = os.path.join(BASE_DIR, "index.html")
    css_path = os.path.join(BASE_DIR, "style.css")
    js_path = os.path.join(BASE_DIR, "script.js")
    ico_path = os.path.join(BASE_DIR, "icon.ico")

    sep = os.pathsep

    cmd = [
        "python",
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",              # silent launcher should be onefile
        "--windowed",             # <-- NO CONSOLE WINDOW
        "--paths=.",
        "--exclude-module=tkinter",
        "--exclude-module=_tkinter",
        "--exclude-module=installer_gui",
        "--exclude-module=pygame",
        "--exclude-module=pygame._sdl2",
        "--exclude-module=pygame.base",
        "--exclude-module=pygame.display",
        "--exclude-module=pygame.mixer",
        f"--icon={ico_path}",

        f"--add-data={html_path}{sep}.",
        f"--add-data={css_path}{sep}.",
        f"--add-data={js_path}{sep}.",
        f"--add-data={ico_path}{sep}.",

        "main.py"
    ]

    subprocess.run(cmd, cwd=BASE_DIR, check=True)
    print("Launcher build complete.")

def move_output():
    os.makedirs(RELEASE_DIR, exist_ok=True)

    src = os.path.join(BASE_DIR, "dist", "main.exe")
    dst = os.path.join(RELEASE_DIR, OUTPUT_EXE_NAME)

    if not os.path.exists(src):
        raise FileNotFoundError(f"Expected EXE not found at: {src}")

    shutil.copy(src, dst)
    print(f"Copied launcher to {dst}")

def main():
    clean_build_folders()
    build_exe()
    move_output()
    print("Launcher builder finished successfully.")

if __name__ == "__main__":
    main()
