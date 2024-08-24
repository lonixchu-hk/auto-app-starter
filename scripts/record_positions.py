import tkinter as tk
from tkinter import messagebox
import pygetwindow as gw
import json
import os
import subprocess
import sys
import time
import appdirs


class WindowPositionRecorder:
    def __init__(self, root):
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

        # Load previous selections and display in the listbox
        self.previous_selections = self.load_saved_positions()
        self.refresh_window_list()

        # Record button
        self.record_button = tk.Button(root, text="Record", command=self.record_positions)
        self.record_button.pack(pady=10)

        # Open button
        self.open_button = tk.Button(root, text="Open", command=self.open_selected_applications)
        self.open_button.pack(pady=5)

        # Label to show the result of recording
        self.result_label = tk.Label(root, text="", font=("Arial", 10))
        self.result_label.pack(pady=5)

        # Automatically select saved applications
        self.auto_select_saved_applications()

    def get_data_file_path(self, filename):
        if getattr(sys, 'frozen', False):
            # If running in a PyInstaller bundle
            user_data_dir = appdirs.user_data_dir("Auto App Starter")
        else:
            # If running in a normal script
            user_data_dir = os.path.join(os.path.dirname(__file__), 'data')

        os.makedirs(user_data_dir, exist_ok=True)
        return os.path.join(user_data_dir, filename)

    def load_saved_positions(self):
        """Load previously saved window positions, creating the file if it doesn't exist."""
        filename = self.get_data_file_path('window_positions.json')
        print(filename)

        os.makedirs(os.path.dirname(filename), exist_ok=True)  # Ensure the directory exists

        # If the file doesn't exist, create an empty JSON file
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

        # Add currently opened windows
        for title in window_titles:
            if title in self.previous_selections:
                display_title = f"[Saved] {title}"
            else:
                display_title = title

            self.listbox.insert(tk.END, display_title)

        # Add previously saved but not currently opened windows
        for saved_title in self.previous_selections:
            if saved_title not in window_titles:
                display_title = f"[Saved] {saved_title}"
                print(f"Adding to listbox (Saved but not open): {display_title}")
                if display_title not in self.listbox.get(0, tk.END):
                    self.listbox.insert(tk.END, display_title)

    def record_positions(self):
        """Record positions of selected windows."""
        # Save the current selection
        selected_indices = self.listbox.curselection()
        selected_titles = [self.listbox.get(i).replace("[Saved] ", "") for i in selected_indices]

        # if not selected_titles:
        #     messagebox.showwarning("No Selection", "Please select at least one window.")
        #     return

        positions = {}
        for title in selected_titles:
            windows = gw.getWindowsWithTitle(title)
            if windows:
                window = windows[0]
                positions[title] = {
                    'left': window.left,
                    'top': window.top,
                    'width': window.width,
                    'height': window.height
                }

        filename = self.get_data_file_path('window_positions.json')
        with open(filename, 'w') as file:
            json.dump(positions, file)

        self.result_label.config(text="Window positions recorded successfully!")

        # Reapply the previous selection
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


    def auto_select_saved_applications(self):
        """Automatically select saved applications in the listbox."""
        saved_titles = [f"[Saved] {title}" for title in self.previous_selections]
        for i in range(self.listbox.size()):
            title = self.listbox.get(i)
            if title in saved_titles:
                self.listbox.selection_set(i)

    def open_selected_applications(self):
        """Open selected applications in their saved positions."""
        selected_indices = self.listbox.curselection()
        selected_titles = [self.listbox.get(i).replace("[Saved] ", "") for i in selected_indices]

        positions = self.load_saved_positions()

        for title in selected_titles:
            if title in positions:
                windows = gw.getWindowsWithTitle(title)
                if windows:
                    window = windows[0]
                    pos = positions[title]
                    window.moveTo(pos['left'], pos['top'])
                    window.resizeTo(pos['width'], pos['height'])
                else:
                    subprocess.Popen([title])  # Replace with actual application start command
                    time.sleep(2)  # Wait for the application to open
                    windows = gw.getWindowsWithTitle(title)
                    if windows:
                        window = windows[0]
                        pos = positions[title]
                        window.moveTo(pos['left'], pos['top'])
                        window.resizeTo(pos['width'], pos['height'])
            else:
                messagebox.showwarning("Position Not Found", f"No saved position for {title}")


def main():
    root = tk.Tk()
    app = WindowPositionRecorder(root)
    root.mainloop()


if __name__ == "__main__":
    main()
