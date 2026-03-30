import os
import shutil
import sys
import json
import zipfile
import tempfile
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import ctypes

APP_NAME = "Meeting Formatter"
INSTALL_DIR = os.path.join(os.environ["ProgramFiles"], APP_NAME)
SETTINGS_FILE = os.path.join(INSTALL_DIR, "settings.json")

# ------------------------------------------------------------
# Elevation helper (UAC)
# ------------------------------------------------------------
def ensure_admin():
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        is_admin = False

    if not is_admin:
        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            sys.executable,
            " ".join(sys.argv),
            None,
            1
        )
        sys.exit()

# ------------------------------------------------------------
# Helper: packaged data path
# ------------------------------------------------------------
def get_data_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, "data")
    else:
        return os.path.join(os.path.dirname(__file__), "data")

# ------------------------------------------------------------
# SETTINGS HANDLING
# ------------------------------------------------------------
def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {
            "create_desktop_shortcut": True,
            "create_start_menu_shortcut": True,
            "auto_launch": False
        }
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_settings(settings):
    os.makedirs(INSTALL_DIR, exist_ok=True)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

# ------------------------------------------------------------
# SHORTCUT CREATION
# ------------------------------------------------------------
def create_shortcut(path, target, icon=None):
    script = f'''
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{path.replace("\\", "\\\\")}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{target.replace("\\", "\\\\")}"
oLink.WorkingDirectory = "{os.path.dirname(target).replace("\\", "\\\\")}"
oLink.IconLocation = "{(icon or target).replace("\\", "\\\\")}"
oLink.Save
'''
    temp_vbs = os.path.join(tempfile.gettempdir(), "mkshortcut.vbs")
    with open(temp_vbs, "w") as f:
        f.write(script)

    subprocess.call(["wscript.exe", temp_vbs])
    os.remove(temp_vbs)

# ------------------------------------------------------------
# INSTALL
# ------------------------------------------------------------
def install_app(progress, status):
    data_path = get_data_path()
    settings = load_settings()

    try:
        status.config(text="Creating install directory...")
        progress["value"] = 10

        os.makedirs(INSTALL_DIR, exist_ok=True)

        files = os.listdir(data_path)
        step = 60 / max(len(files), 1)

        for i, file in enumerate(files):
            status.config(text=f"Copying {file}...")
            src = os.path.join(data_path, file)
            dst = os.path.join(INSTALL_DIR, file)
            shutil.copy(src, dst)

            progress["value"] = 10 + (i * step)
            progress.update_idletasks()

        exe_path = os.path.join(INSTALL_DIR, "meeting-formatter.exe")

        if settings.get("create_desktop_shortcut", True):
            status.config(text="Creating desktop shortcut...")
            progress["value"] = 80
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            create_shortcut(os.path.join(desktop, f"{APP_NAME}.lnk"), exe_path)

        if settings.get("create_start_menu_shortcut", True):
            status.config(text="Creating Start Menu shortcut...")
            progress["value"] = 90
            start_menu = os.path.join(
                os.environ["APPDATA"],
                "Microsoft",
                "Windows",
                "Start Menu",
                "Programs"
            )
            create_shortcut(os.path.join(start_menu, f"{APP_NAME}.lnk"), exe_path)

        if settings.get("auto_launch", False):
            subprocess.Popen([exe_path], shell=True)

        progress["value"] = 100
        status.config(text="Install complete!")
        messagebox.showinfo("Success", f"{APP_NAME} has been installed successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"Installation failed:\n{e}")

# ------------------------------------------------------------
# UNINSTALL
# ------------------------------------------------------------
def uninstall_app(progress, status):
    try:
        status.config(text="Checking installation...")
        progress["value"] = 10

        if not os.path.exists(INSTALL_DIR):
            messagebox.showinfo("Not Installed", f"{APP_NAME} is not installed.")
            progress["value"] = 0
            return

        status.config(text="Removing application files...")
        progress["value"] = 40
        shutil.rmtree(INSTALL_DIR, ignore_errors=True)

        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        ds = os.path.join(desktop, f"{APP_NAME}.lnk")
        if os.path.exists(ds):
            os.remove(ds)

        start_menu = os.path.join(
            os.environ["APPDATA"],
            "Microsoft",
            "Windows",
            "Start Menu",
            "Programs"
        )
        sm = os.path.join(start_menu, f"{APP_NAME}.lnk")
        if os.path.exists(sm):
            os.remove(sm)

        progress["value"] = 100
        status.config(text="Uninstall complete!")
        messagebox.showinfo("Uninstalled", f"{APP_NAME} has been removed.")

    except Exception as e:
        messagebox.showerror("Error", f"Uninstall failed:\n{e}")

# ------------------------------------------------------------
# UPDATE
# ------------------------------------------------------------
def run_update(zip_path, progress, status):
    if not os.path.isfile(zip_path):
        messagebox.showerror("Error", "Invalid update.zip file.")
        return

    temp_dir = tempfile.mkdtemp()

    try:
        status.config(text="Extracting update.zip...")
        progress["value"] = 20

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        status.config(text="Copying updated files...")
        progress["value"] = 60

        for root, dirs, files in os.walk(temp_dir):
            rel = os.path.relpath(root, temp_dir)
            dest = os.path.join(INSTALL_DIR, rel)
            os.makedirs(dest, exist_ok=True)

            for file in files:
                shutil.copy2(os.path.join(root, file), os.path.join(dest, file))

        progress["value"] = 100
        status.config(text="Update complete!")
        messagebox.showinfo("Success", "The application has been updated successfully.")

    except Exception as e:
        messagebox.showerror("Update Failed", str(e))

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

# ------------------------------------------------------------
# GUI
# ------------------------------------------------------------
def build_gui():
    root = tk.Tk()
    root.title(f"{APP_NAME} Installer")
    root.geometry("550x420")
    root.resizable(False, False)

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill="both")

    style = ttk.Style()
    style.theme_use("default")
    style.configure("Green.Horizontal.TProgressbar",
                    troughcolor="#ddd",
                    background="#4CAF50",
                    thickness=20)

    install_tab = ttk.Frame(notebook)
    notebook.add(install_tab, text="Install")

    ttk.Label(install_tab, text=f"Install {APP_NAME}", font=("Segoe UI", 14)).pack(pady=10)

    progress_install = ttk.Progressbar(install_tab, style="Green.Horizontal.TProgressbar", length=400)
    progress_install.pack(pady=10)

    status_install = ttk.Label(install_tab, text="Waiting...")
    status_install.pack()

    ttk.Button(
        install_tab,
        text="Install",
        command=lambda: install_app(progress_install, status_install)
    ).pack(pady=10)

    uninstall_tab = ttk.Frame(notebook)
    notebook.add(uninstall_tab, text="Uninstall")

    ttk.Label(uninstall_tab, text=f"Uninstall {APP_NAME}", font=("Segoe UI", 14)).pack(pady=10)

    progress_uninstall = ttk.Progressbar(uninstall_tab, style="Green.Horizontal.TProgressbar", length=400)
    progress_uninstall.pack(pady=10)

    status_uninstall = ttk.Label(uninstall_tab, text="Waiting...")
    status_uninstall.pack()

    ttk.Button(
        uninstall_tab,
        text="Uninstall",
        command=lambda: uninstall_app(progress_uninstall, status_uninstall)
    ).pack(pady=10)

    settings_tab = ttk.Frame(notebook)
    notebook.add(settings_tab, text="Settings")

    settings = load_settings()

    var_desktop = tk.BooleanVar(value=settings.get("create_desktop_shortcut", True))
    var_startmenu = tk.BooleanVar(value=settings.get("create_start_menu_shortcut", True))
    var_autolaunch = tk.BooleanVar(value=settings.get("auto_launch", False))

    ttk.Checkbutton(settings_tab, text="Create Desktop Shortcut", variable=var_desktop).pack(anchor="w", padx=20)
    ttk.Checkbutton(settings_tab, text="Create Start Menu Shortcut", variable=var_startmenu).pack(anchor="w", padx=20)
    ttk.Checkbutton(settings_tab, text="Auto-launch after install", variable=var_autolaunch).pack(anchor="w", padx=20)

    ttk.Button(
        settings_tab,
        text="Save Settings",
        command=lambda: save_settings({
            "create_desktop_shortcut": var_desktop.get(),
            "create_start_menu_shortcut": var_startmenu.get(),
            "auto_launch": var_autolaunch.get()
        })
    ).pack(pady=15)

    updater_tab = ttk.Frame(notebook)
    notebook.add(updater_tab, text="Updater")

    ttk.Label(updater_tab, text="Update using update.zip", font=("Segoe UI", 14)).pack(pady=10)

    update_path = tk.StringVar()

    path_frame = ttk.Frame(updater_tab)
    path_frame.pack(pady=5)

    ttk.Entry(path_frame, textvariable=update_path, width=40).pack(side="left", padx=5)

    ttk.Button(
        path_frame,
        text="Browse",
        command=lambda: update_path.set(
            filedialog.askopenfilename(title="Select update.zip", filetypes=[("ZIP files", "*.zip")])
        )
    ).pack(side="left")

    progress_update = ttk.Progressbar(updater_tab, style="Green.Horizontal.TProgressbar", length=400)
    progress_update.pack(pady=10)

    status_update = ttk.Label(updater_tab, text="Waiting...")
    status_update.pack()

    ttk.Button(
        updater_tab,
        text="Run Update",
        command=lambda: run_update(update_path.get(), progress_update, status_update)
    ).pack(pady=10)

    about_tab = ttk.Frame(notebook)
    notebook.add(about_tab, text="About")

    ttk.Label(about_tab, text=f"{APP_NAME} Installer", font=("Segoe UI", 14)).pack(pady=10)
    ttk.Label(about_tab, text="Created by AJ\nBuilt with Python", font=("Segoe UI", 10)).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    ensure_admin()
    build_gui()
