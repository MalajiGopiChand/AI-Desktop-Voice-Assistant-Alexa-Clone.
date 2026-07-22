import tkinter as tk
import time
import os

STATE_FILE = "widget_state.txt"

class SiriWidget:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        
        # Windows transparent color trick
        self.root.attributes("-transparentcolor", "black")
        
        # Position at top right or center bottom? Let's do bottom right
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.root.geometry(f"100x100+{screen_width - 150}+{screen_height - 150}")
        self.root.configure(bg="black")
        
        self.canvas = tk.Canvas(root, width=100, height=100, bg="black", highlightthickness=0)
        self.canvas.pack()
        
        self.circle = self.canvas.create_oval(25, 25, 75, 75, fill="#4b5563", outline="")
        
        self.current_state = "idle"
        self.pulse_dir = 1
        self.size = 25
        self.max_size = 35
        self.min_size = 15
        
        self.update_loop()
        
    def update_loop(self):
        try:
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, "r") as f:
                    new_state = f.read().strip()
                    if new_state:
                        self.current_state = new_state
        except:
            pass
            
        color = "#10a37f" # default
        if self.current_state == "idle":
            color = "#4b5563" # grey
            self.max_size = 26
            self.min_size = 24
        elif self.current_state == "listening":
            color = "#3b82f6" # blue
            self.max_size = 35
            self.min_size = 15
        elif self.current_state == "processing":
            color = "#eab308" # yellow
            self.max_size = 30
            self.min_size = 20
        elif self.current_state == "speaking":
            color = "#10a37f" # green (Jarvis aesthetic)
            self.max_size = 40
            self.min_size = 20
            
        self.canvas.itemconfig(self.circle, fill=color)
        
        # Pulse animation
        if self.current_state != "idle":
            self.size += 2 * self.pulse_dir
            if self.size >= self.max_size:
                self.pulse_dir = -1
            elif self.size <= self.min_size:
                self.pulse_dir = 1
        else:
            self.size = 25
            
        # Draw from center (50, 50)
        self.canvas.coords(self.circle, 50 - self.size, 50 - self.size, 50 + self.size, 50 + self.size)
        
        self.root.after(50, self.update_loop)

if __name__ == "__main__":
    with open(STATE_FILE, "w") as f:
        f.write("idle")
    root = tk.Tk()
    app = SiriWidget(root)
    root.mainloop()
