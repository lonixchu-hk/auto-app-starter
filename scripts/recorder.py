import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
import pygetwindow as gw
import json
import os
import subprocess
import sys
import time
import appdirs
import psutil
import ctypes
import screeninfo
import tkinter.messagebox as messagebox

class Recorder:
    def __init__(self, root):

        self.proceed = True

        self.root = root
        self.root.title("Auto App Starter")
        self.root.geometry("600x400")

        # Instruction Label
        self.instruction_label = tk.Label(root, text="The selected app will be auto started when PC boots.",
                                          font=("Arial", 10))
        self.instruction_label.pack(pady=5)

        # Listbox to display open windows
        self.listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=50, height=15)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.listbox.bind('<<ListboxSelect>>', self.on_listbox_select)

        # Create a frame for buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=20, fill=tk.X, padx=20)

        # Configure grid in button_frame
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)

        # Refresh button
        self.refresh_button = ttk.Button(button_frame, text="Refresh", command=self.refresh_list)
        self.refresh_button.grid(row=0, column=0, padx=5, pady=5)

        # Record button
        self.record_button = ttk.Button(button_frame, text="Record", command=self.record_positions)
        self.record_button.grid(row=0, column=1, padx=5, pady=5)

        # Open button
        self.open_button = ttk.Button(button_frame, text="Open", command=self.open_selected_applications)
        self.open_button.grid(row=0, column=2, padx=5, pady=5)

        # Label to show the result of recording
        self.result_label = ttk.Label(root, text="", font=("Arial", 10))
        self.result_label.pack(pady=5)

        # File paths
        self.window_positions_file = self.get_data_file_path("window_positions.json")
        self.previous_selections = self.load_saved_positions()

        # Load previous selections and display in the listbox
        self.refresh_window_list()

        if self.proceed:
            # Automatically select saved applications
            self.auto_select_saved_applications()

            # Create backdrop for monitors
            self.create_backdrop()

    def create_backdrop(self):
        """Creates a fullscreen backdrop across all monitors and outlines saved application positions."""

        # First, destroy any existing backdrops to avoid duplication
        if hasattr(self, 'backdrops'):
            for backdrop in self.backdrops:
                backdrop.destroy()
            self.backdrops.clear()  # Clear the list of backdrops

        monitors = screeninfo.get_monitors()
        self.backdrops = []

        selected_indices = self.listbox.curselection()
        selected_titles = [self.listbox.get(i).replace("[Saved] ", "") for i in selected_indices]
        positions = self.get_selected_app_positions(selected_titles)

        # Create and configure the backdrop windows
        for monitor in monitors:
            backdrop = tk.Toplevel(self.root)
            backdrop.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")
            backdrop.attributes("-alpha", 0.7)
            backdrop.overrideredirect(1)  # Removes window decorations
            backdrop.configure(bg='black')
            backdrop.attributes('-topmost', 1)  # Ensure the backdrop is on top

            # Ensure that clicking on the backdrop does not bring it to the front
            backdrop.bind("<Button-1>", lambda e: self.root.lift())

            self.root.lift()  # Bring the main app window to the top
            self.root.attributes('-topmost', 1)  # Ensure it stays on top

            # Create a canvas on the backdrop for drawing outlines
            canvas = tk.Canvas(backdrop, bg='black', highlightthickness=0)
            canvas.pack(fill=tk.BOTH, expand=True)

            # Draw outlines of selected applications
            for title in selected_titles:
                pos = None
                if title in positions:
                    pos = positions[title]
                if title in self.previous_selections:
                    pos = self.previous_selections[title]

                if pos is not None:
                    # Check if the window is on the current monitor
                    if monitor.x <= pos['left'] < monitor.x + monitor.width and monitor.y <= pos['top'] < monitor.y + monitor.height:
                        # Calculate position relative to the monitor
                        x = pos['left'] - monitor.x
                        y = pos['top'] - monitor.y
                        width = pos['width']
                        height = pos['height']

                        # Draw the outline as a rectangle with no fill and a blue border
                        canvas.create_rectangle(x, y, x + width, y + height, outline='blue', width=2)
                        print(
                            f"Drawing outline on monitor {monitor} at position ({x}, {y}) with size ({width}x{height})")

                        # Add a label with the application name inside the outline
                        label = tk.Label(
                            backdrop,
                            text=title,
                            bg='yellow',  # Set a contrasting background color
                            fg='black',  # Set text color to black
                            font=("Arial", 14, "bold"),  # Increase font size and make it bold
                            padx=5,  # Add padding inside the label for better readability
                            pady=5
                        )
                        # Position the label within the outline
                        canvas.create_window(x + 10, y + 10, anchor='nw', window=label)
                        self.root.lift()  # Bring the main app window to the top
                        self.root.attributes('-topmost', 1)  # Ensure it stays on top

            self.backdrops.append(backdrop)

        # Ensure the main window is on top of all backdrops
        self.root.after(100, lambda: self.root.lift())  # Wait 100 milliseconds, then bring the main app to the top
        self.root.after(100, lambda: self.root.attributes('-topmost', 1))


    def on_listbox_select(self, event):
        print("Select App")
        self.create_backdrop()


    def get_data_file_path(self, filename):
        if getattr(sys, 'frozen', False):
            user_data_dir = appdirs.user_data_dir("Auto App Starter")
        else:
            user_data_dir = os.path.join(os.path.dirname(__file__), 'data')

        os.makedirs(user_data_dir, exist_ok=True)
        return os.path.join(user_data_dir, filename)

    def refresh_list(self):
        self.refresh_window_list()
        self.auto_select_saved_applications()

    def load_saved_positions(self):
        filename = self.window_positions_file
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        if not os.path.exists(filename):
            with open(filename, 'w') as file:
                json.dump({}, file)

        with open(filename, 'r') as file:
            return json.load(file)

    def refresh_window_list(self):
        """Refresh the listbox with current open windows and saved ones."""
        self.listbox.delete(0, tk.END)
        windows = gw.getWindowsWithTitle('')
        window_titles = [window.title for window in windows if window.title]

        print("Refreshing window list...")
        print(f"Saved selections: {self.previous_selections}")

        base_names = [self.get_base_name(title) for title in window_titles]
        merged_array = self.merge_arrays(self.previous_selections, base_names)
        if len(merged_array) != len(set(merged_array)):
            messagebox.showerror("Error", "Some applications are open duplicated. Please close them. \n\nActive Applications:\n" + str(merged_array))
            self.root.destroy()
            self.proceed = False
            return

        display_applications = []

        # Add currently opened windows with or without instance number
        for title in window_titles:
            base_name = self.get_base_name(title)  # Get the base name
            display_title = base_name
            if display_title in self.previous_selections:
                display_title = f"[Saved] {display_title}"
            display_applications.append(display_title)

        # Add previously saved but not currently opened windows
        for saved_title in self.previous_selections:
            base_name = self.get_base_name(saved_title)
            if saved_title not in window_titles:
                display_title = f"[Saved] {base_name}"
                print(f"Adding to listbox (Saved but not open): {display_title}")
                if display_title not in self.listbox.get(0, tk.END):
                    display_applications.append(display_title)

        for application_title in display_applications:
            self.listbox.insert(tk.END, application_title)


    def merge_arrays(self, arr1, arr2):
        # Create a result array with all elements from array2
        result = arr2[:]

        # Add only elements from array1 that are not already in array2
        for elem in arr1:
            if elem not in arr2:
                result.append(elem)

        # Sort the final merged array
        result.sort()

        return result

    def get_base_name(self, title):
        """Extract base name from the title (e.g., 'Edge')."""
        if "Edge" in title:
            return "Edge"
        # Add other application base names here if needed
        # elif "Notepad" in title:
        #     return "Notepad"
        else:
            return title.split('-')[0].strip()  # Default: Use the first part of the title

    def get_pid_by_window_title(self, window_title):
        hwnd = ctypes.windll.user32.FindWindowW(None, window_title)
        pid = ctypes.c_ulong()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        return pid.value if pid.value != 0 else None

    def is_application_frame_host(self, path):
        return path.lower() == "c:\\windows\\system32\\applicationframehost.exe"

    def get_uwp_apps(self):
        uwp_apps = {}
        try:
            result = subprocess.check_output(
                ["powershell", "Get-AppxPackage | Select-Object Name, PackageFamilyName | ConvertTo-Json"],
                universal_newlines=True
            )
            apps = eval(result)
            for app in apps:
                uwp_apps[app['Name']] = app['PackageFamilyName']
        except subprocess.CalledProcessError as e:
            print(f"Error retrieving UWP apps: {e}")
        return uwp_apps

    def get_selected_app_positions(self, selected_titles):
        uwp_apps = self.get_uwp_apps()
        positions = {}
        for title in selected_titles:
            windows = gw.getWindowsWithTitle(title)
            if windows:
                window = windows[0]
                exe_path = None
                pfn = None

                pid = self.get_pid_by_window_title(title)
                if pid:
                    try:
                        process = psutil.Process(pid)
                        exe_path = process.exe()

                        if self.is_application_frame_host(exe_path):
                            matched_pfn = None
                            for uwp_title, uwp_pfn in uwp_apps.items():
                                if title.lower() in uwp_title.lower():
                                    matched_pfn = uwp_pfn
                                    break
                            pfn = matched_pfn
                            exe_path = None
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                        print(f"Could not get executable path for {title}: {e}")

                positions[title] = {
                    'left': window.left,
                    'top': window.top,
                    'width': window.width,
                    'height': window.height,
                    'exe_path': exe_path,
                    'pfn': pfn
                }
        return positions

    def record_positions(self):

        selected_indices = self.listbox.curselection()
        selected_titles = [self.listbox.get(i).replace("[Saved] ", "") for i in selected_indices]

        positions = self.get_selected_app_positions(selected_titles)

        filename = self.window_positions_file
        with open(filename, 'w') as file:
            json.dump(positions, file)

        self.result_label.config(text="Window positions recorded successfully!")

        self.listbox.selection_clear(0, tk.END)
        for i in range(self.listbox.size()):
            window_name = self.listbox.get(i)
            if i in selected_indices:
                if not window_name.startswith("[Saved]"):
                    window_name = "[Saved] " + window_name
                    self.listbox.delete(i)
                    self.listbox.insert(i, window_name)
                self.listbox.selection_set(i)
            else:
                if window_name.startswith("[Saved]"):
                    window_name = window_name.replace("[Saved] ", "")
                    self.listbox.delete(i)
                    self.listbox.insert(i, window_name)

        self.previous_selections = self.load_saved_positions()
        self.create_backdrop()

    def auto_select_saved_applications(self):
        saved_titles = [f"[Saved] {title}" for title in self.previous_selections]
        for i in range(self.listbox.size()):
            title = self.listbox.get(i)
            if title in saved_titles:
                self.listbox.selection_set(i)

    def open_selected_applications(self):
        positions = self.load_saved_positions()
        for appTitle, attr in positions.items():
            windows = gw.getWindowsWithTitle(appTitle)
            if not windows:
                command = f'start "shell:AppsFolder\\$(Get-StartApps "{appTitle}" | select -ExpandProperty AppId)"'
                subprocess.Popen(['powershell.exe', '-Command', command], shell=False)
                time.sleep(2)
                windows = gw.getWindowsWithTitle(appTitle)
            window = windows[0]
            window.moveTo(attr['left'], attr['top'])
            window.resizeTo(attr['width'], attr['height'])

def main():
    root = ThemedTk(theme="breeze")
    app = Recorder(root)
    root.mainloop()

if __name__ == "__main__":
    main()