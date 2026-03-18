import tkinter as tk
from PIL import Image, ImageTk, ImageGrab
import keyboard
import ctypes
import os
import sys

# --- Windows DPI ---
try:
    if sys.platform == "win32":
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception as e:
    pass
# ---------------------------------------------

class ComboOverlay:
    def __init__(self, image):
        self.overlay = tk.Toplevel()
        self.overlay.overrideredirect(True) 
        self.overlay.attributes("-topmost", True) 
        self.overlay.attributes("-transparentcolor", "#abcdef") 

        self.root_frame = tk.Frame(self.overlay, bg="#abcdef", bd=0)
        self.root_frame.pack()

        # --- Header Bar ---
        self.title_bar = tk.Frame(self.root_frame, bg="#2e2e2e", height=20)
        self.title_bar.pack(fill="x", side="top")
        self.title_bar.pack_propagate(False)

        # Window Close Button
        self.close_label = tk.Label(self.title_bar, text=" X ", bg="#cc0000", fg="white", 
                                    font=("Arial", 10, "bold"), cursor="hand2")
        self.close_label.pack(side="right", padx=2, pady=1)
        self.close_label.bind("<Button-1>", lambda e: self.exit_app())

        self.desc_label = tk.Label(self.title_bar, text="Select again with F8", bg="#2e2e2e", fg="#aaaaaa", font=("Arial", 8))
        self.desc_label.pack(side="left", padx=5)

        # Sliding Window Movement
        self.title_bar.bind("<Button-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)
        self.desc_label.bind("<Button-1>", self.start_move)
        self.desc_label.bind("<B1-Motion>", self.do_move)

        # --- Selection Image ---
        self.tk_img = ImageTk.PhotoImage(image)
        self.image_label = tk.Label(self.root_frame, image=self.tk_img, bg="black", bd=0)
        self.image_label.pack(side="bottom")

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.overlay.winfo_x() + deltax
        y = self.overlay.winfo_y() + deltay
        self.overlay.geometry(f"+{x}+{y}")
        
    def exit_app(self):
        print("Program fully closed.")
        os._exit(0) # Closing

    def close_overlay(self):
        self.overlay.destroy()

class AreaSelector:
    def __init__(self, root, callback):
        self.root = root
        self.callback = callback
        
        self.selector_window = tk.Toplevel(self.root)
        self.selector_window.attributes("-alpha", 0.3) 
        self.selector_window.attributes("-fullscreen", True)
        self.selector_window.attributes("-topmost", True)
        self.selector_window.config(cursor="cross")
        self.selector_window.attributes("-toolwindow", True) 

        self.canvas = tk.Canvas(self.selector_window, cursor="cross", bg="grey", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.start_x = None
        self.start_y = None
        self.rect = None

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.selector_window.bind("<Escape>", lambda e: self.selector_window.destroy())

    def on_button_press(self, event):
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.rect = self.canvas.create_rectangle(event.x, event.y, event.x+1, event.y+1, outline='red', width=2)

    def on_move_press(self, event):
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.canvas.canvasx(self.start_x_rel(event)), 
                          self.canvas.canvasy(self.start_y_rel(event)), cur_x, cur_y)

    def start_x_rel(self, event): return self.start_x - (event.x_root - event.x)
    def start_y_rel(self, event): return self.start_y - (event.y_root - event.y)

    def on_button_release(self, event):
        end_x = event.x_root
        end_y = event.y_root
        self.selector_window.destroy() 
        
        x1, y1 = min(self.start_x, end_x), min(self.start_y, end_y)
        x2, y2 = max(self.start_x, end_x), max(self.start_y, end_y)

        if x2 - x1 < 10 or y2 - y1 < 10:
            return

        try:
            img = ImageGrab.grab(bbox=(x1, y1, x2, y2), all_screens=True)
            self.callback(img)
        except Exception as e:
            print(f"Failed to capture image: {e}")

class MainApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw() 
        self.overlay_instance = None
        
        keyboard.add_hotkey('f8', self.trigger_selection)
        print("Selection mode: Press F8 to select combo area.")
        self.root.mainloop()

    def trigger_selection(self):
        self.root.after(0, self.start_selector)

    def start_selector(self):
        AreaSelector(self.root, self.create_overlay)

    def create_overlay(self, img):
        if self.overlay_instance:
            try:
                self.overlay_instance.close_overlay()
            except: pass
            
        self.overlay_instance = ComboOverlay(img)

if __name__ == "__main__":
    app = MainApp()