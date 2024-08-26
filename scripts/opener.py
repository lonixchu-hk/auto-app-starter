import subprocess
import sys
import os
import pygetwindow as gw
import time
import json
import appdirs

def get_data_file_path(filename):
    # Use the path the exe application save the position json
    user_data_dir = appdirs.user_data_dir("Auto App Starter")
    os.makedirs(user_data_dir, exist_ok=True)
    return os.path.join(user_data_dir, filename)

def load_saved_positions():
    """Load previously saved window positions, creating the file if it doesn't exist."""
    filename = get_data_file_path("window_positions.json")
    print(filename)
    os.makedirs(os.path.dirname(filename), exist_ok=True)  # Ensure the directory exists

    # If the file doesn't exist, create an empty JSON file
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            json.dump({}, file)

    with open(filename, 'r') as file:
        return json.load(file)

def open_selected_applications():
    positions = load_saved_positions()
    print(positions)
    for appTitle, attr in positions.items():
        windows = gw.getWindowsWithTitle(appTitle)
        if not windows:
            command = f'start "shell:AppsFolder\\$(Get-StartApps "{appTitle}" | select -ExpandProperty AppId)"'
            print(command)
            subprocess.Popen(['powershell.exe', '-Command', command], shell=False)
            time.sleep(2)  # Wait for the application to open
            windows = gw.getWindowsWithTitle(appTitle)
        window = windows[0]
        window.moveTo(attr['left'], attr['top'])
        window.resizeTo(attr['width'], attr['height'])

if __name__ == "__main__":
    open_selected_applications()
