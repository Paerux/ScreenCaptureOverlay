import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
import pyautogui
from pynput import mouse
import threading

class RegionWindow:
    def __init__(self, master, x, y, w, h, update_interval=100):
        self.window = tk.Toplevel(master)
        self.window.title("Captured Region")
        self.window.overrideredirect(1)  # Hide window decorations
        self.window.attributes('-topmost', 1)  # Make window always on top
        self.canvas = tk.Canvas(self.window, width=w, height=h)
        self.canvas.pack()
        self.update_interval = update_interval
        self.region = (x, y, w, h)
        self.captured_region = None
        self.capture_screen()

        # Make window draggable
        self.window.bind('<ButtonPress-1>', self.StartMove)
        self.window.bind('<ButtonRelease-1>', self.StopMove)
        self.window.bind('<B1-Motion>', self.OnMotion)
        self.window.bind('<Button-3>', self.close_window)  # Bind right click to close the window

        # Position window in the middle of the region
        window_x = x + (w // 2)
        window_y = y + (h // 2)
        self.window.geometry(f"+{window_x}+{window_y}")


    def StartMove(self, event):
        self.x = event.x
        self.y = event.y

    def StopMove(self, event):
        self.x = None
        self.y = None

    def OnMotion(self,event):
        dx = event.x - self.x
        dy = event.y - self.y
        x = self.window.winfo_x() + dx
        y = self.window.winfo_y() + dy
        self.window.geometry(f"+{x}+{y}")

    def close_window(self, event):
        self.window.destroy()

    def capture_screen(self):
        screenshot = pyautogui.screenshot(region=self.region)
        self.captured_region = ImageTk.PhotoImage(screenshot)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.captured_region)
        self.window.after(self.update_interval, self.capture_screen)

class ScreenCaptureApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Screen Capture")
        self.master.geometry("300x200")  # Set the size of the main window

        self.select_button = tk.Button(self.master, text="Select Region", command=self.start_selection)
        self.select_button.pack()

        self.transparency_scale = tk.Scale(self.master, from_=0, to=1, resolution=0.01, orient=tk.HORIZONTAL, label="Transparency", command=self.update_transparency)
        self.transparency_scale.set(1)  # Set initial value to max
        self.transparency_scale.pack()

        self.selection_started = False
        self.capture_started = False
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None

        self.windows = []

    def start_selection(self):
        self.selection_started = True
        self.sel_win = tk.Toplevel(self.master)
        self.sel_win.attributes('-fullscreen', True, '-alpha', 0.3)
        self.sel_win.bind("<Button-1>", self.on_click)
        self.sel_win.bind("<B1-Motion>", self.on_drag)
        self.sel_win.bind("<ButtonRelease-1>", self.on_release)
        self.sel_canvas = tk.Canvas(self.sel_win)
        self.sel_canvas.pack(fill=tk.BOTH, expand=True)

    def on_click(self, event):
        self.start_x, self.start_y = event.x, event.y

    def on_drag(self, event):
        self.end_x, self.end_y = event.x, event.y
        self.sel_canvas.delete("all")
        self.sel_canvas.create_rectangle(self.start_x, self.start_y, self.end_x, self.end_y, outline='red')

    def on_release(self, event):
        self.end_x, self.end_y = event.x, event.y
        self.selection_started = False
        self.sel_win.destroy()
        x, y = min(self.start_x, self.end_x), min(self.start_y, self.end_y)
        w, h = abs(self.end_x - self.start_x), abs(self.end_y - self.start_y)
        if w > 0 and h > 0:
            win = RegionWindow(self.master, x, y, w, h)
            self.windows.append(win)

    def update_transparency(self, _=None):  # Add _=None to handle the argument passed by the command
        transparency = self.transparency_scale.get()  # Subtract from 1 to invert the scale
        for win in self.windows:
            win.window.attributes('-alpha', transparency)

def main():
    root = tk.Tk()
    app = ScreenCaptureApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
