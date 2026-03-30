import os
import shutil
import subprocess

# ------------------------------------------------------------
# Versioning
# ------------------------------------------------------------
VERSION = "1.0"   # <-- update this whenever you release a new build

# Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEV_TOOLS_DIR = os.path.dirname(__file__)
RELEASE_DIR = os.path.join(BASE_DIR, "release")
INSTALLER_TEMP = os.path.join(BASE_DIR, "installer_temp")

APP_EXE = os.path.join(RELEASE_DIR, "meeting-formatter.exe")
INSTALLER_GUI = os.path.join(DEV_TOOLS_DIR, "installer_gui.py")

# Output installer filename now includes version
OUTPUT_INSTALLER = os.path.join(RELEASE_DIR, f"meeting_formatter-installer_v{VERSION}.exe")

# Custom installer icon
INSTALLER_ICON = os.path.join(BASE_DIR, "installer-icon.ico")

# Files to include inside installer
FILES_TO_PACKAGE = [
    APP_EXE,
    os.path.join(BASE_DIR, "index.html"),
    os.path.join(BASE_DIR, "style.css"),
    os.path.join(BASE_DIR, "script.js"),
    os.path.join(BASE_DIR, "icon.ico"),
]

def prepare_temp_folder():
    shutil.rmtree(INSTALLER_TEMP, ignore_errors=True)
    os.makedirs(INSTALLER_TEMP, exist_ok=True)

    for file in FILES_TO_PACKAGE:
        if not os.path.exists(file):
            raise FileNotFoundError(f"Missing file for installer: {file}")
        shutil.copy(file, INSTALLER_TEMP)

    print("Prepared installer temp folder.")

def build_installer():
    print("Building installer...")

    subprocess.run([
        "python",
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--icon", INSTALLER_ICON,
        f"--add-data={INSTALLER_TEMP}{os.pathsep}data",
        INSTALLER_GUI
    ], cwd=BASE_DIR, check=True)

    built_path = os.path.join(BASE_DIR, "dist", "installer_gui.exe")

    if not os.path.exists(built_path):
        raise FileNotFoundError(f"Installer EXE not found at: {built_path}")

    shutil.move(built_path, OUTPUT_INSTALLER)
    print(f"Installer built at: {OUTPUT_INSTALLER}")

def clean_up():
    shutil.rmtree(os.path.join(BASE_DIR, "build"), ignore_errors=True)
    shutil.rmtree(os.path.join(BASE_DIR, "dist"), ignore_errors=True)
    shutil.rmtree(INSTALLER_TEMP, ignore_errors=True)
    print("Cleaned temporary files.")

def main():
    prepare_temp_folder()
    build_installer()
    clean_up()
    print("Installer builder finished successfully.")

if __name__ == "__main__":
    main()
