"""
JARVIS 3D Robot AI Mascot Companion
Floating, Draggable, Dynamic Face Expressions, Animations, and Speech Bubble.
"""
import tkinter as tk
import time
import os
import math

STATE_FILE = "widget_state.txt"
TEXT_FILE = "widget_text.txt"
COLOR_KEY = "#000001"  # Transparent window background key


class RobotCompanion:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", COLOR_KEY)
        self.root.configure(bg=COLOR_KEY)

        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        
        # Position at bottom right initially
        self.win_w = 340
        self.win_h = 240
        self.x = screen_w - 380
        self.y = screen_h - 280
        self.root.geometry(f"{self.win_w}x{self.win_h}+{self.x}+{self.y}")

        self.canvas = tk.Canvas(
            root, width=self.win_w, height=self.win_h, bg=COLOR_KEY, highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        # Dragging variables
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.do_drag)

        # State & Animation Variables
        self.current_state = "idle"
        self.current_text = ""
        self.anim_tick = 0
        self.bob_offset = 0

        self.update_loop()

    def start_drag(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def do_drag(self, event):
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        self.x += dx
        self.y += dy
        self.root.geometry(f"{self.win_w}x{self.win_h}+{self.x}+{self.y}")

    def draw_robot(self):
        self.canvas.delete("all")
        self.anim_tick += 1
        
        # Sine wave bobbing animation
        self.bob_offset = math.sin(self.anim_tick * 0.1) * 6
        
        # Center of robot
        cx = 100
        cy = 130 + int(self.bob_offset)

        # 1. Shadow underneath
        shadow_w = 40 + int(self.bob_offset * 1.2)
        self.canvas.create_oval(
            cx - shadow_w, 205, cx + shadow_w, 215,
            fill="#111827", outline=""
        )

        # 2. Outer Glow Aura based on state
        glow_color = "#3b82f6"  # blue
        if self.current_state == "idle":
            glow_color = "#0ea5e9"
        elif self.current_state == "listening":
            glow_color = "#3b82f6"
        elif self.current_state == "processing":
            glow_color = "#eab308"
        elif self.current_state == "speaking":
            glow_color = "#10a37f"

        # 3. Metallic 3D Torso
        self.canvas.create_oval(
            cx - 45, cy - 10, cx + 45, cy + 65,
            fill="#e2e8f0", outline="#cbd5e1", width=2
        )
        self.canvas.create_oval(
            cx - 35, cy, cx + 35, cy + 55,
            fill="#f8fafc", outline=""
        )
        # Torso Core Indicator
        self.canvas.create_oval(
            cx - 12, cy + 18, cx + 12, cy + 42,
            fill=glow_color, outline="#ffffff", width=1.5
        )

        # Arms
        arm_angle = math.sin(self.anim_tick * 0.15) * 4
        # Left arm
        self.canvas.create_oval(
            cx - 65, cy + 5 + int(arm_angle), cx - 40, cy + 55 + int(arm_angle),
            fill="#cbd5e1", outline="#94a3b8"
        )
        # Right arm
        self.canvas.create_oval(
            cx + 40, cy + 5 - int(arm_angle), cx + 65, cy + 55 - int(arm_angle),
            fill="#cbd5e1", outline="#94a3b8"
        )

        # 4. Robot Head (3D Metallic Rounded Helmet)
        self.canvas.create_oval(
            cx - 52, cy - 75, cx + 52, cy + 5,
            fill="#f1f5f9", outline="#94a3b8", width=2
        )
        self.canvas.create_oval(
            cx - 48, cy - 72, cx + 48, cy + 2,
            fill="#ffffff", outline=""
        )

        # Ears / Side Antennas
        self.canvas.create_oval(cx - 60, cy - 45, cx - 48, cy - 25, fill=glow_color, outline="#ffffff")
        self.canvas.create_oval(cx + 48, cy - 45, cx + 60, cy - 25, fill=glow_color, outline="#ffffff")

        # 5. Dark Visor Face Screen
        self.canvas.create_rectangle(
            cx - 40, cy - 62, cx + 40, cy - 12,
            fill="#0f172a", outline="#334155", width=2
        )

        # 6. Facial Expressions & Glowing Cyber Eyes
        if self.current_state == "listening":
            # Listening expression [ ⊙ ‿ ⊙ ] with audio bars
            self.canvas.create_oval(cx - 28, cy - 50, cx - 12, cy - 34, fill="#38bdf8", outline="#ffffff")
            self.canvas.create_oval(cx + 12, cy - 50, cx + 28, cy - 34, fill="#38bdf8", outline="#ffffff")
            # Smiling mouth
            self.canvas.create_arc(cx - 12, cy - 36, cx + 12, cy - 22, start=200, extent=140, fill="#38bdf8", outline="")
            # Soundwave equalizer lines
            bar_h1 = abs(math.sin(self.anim_tick * 0.3)) * 12 + 4
            bar_h2 = abs(math.cos(self.anim_tick * 0.3)) * 14 + 4
            self.canvas.create_line(cx - 35, cy - 25, cx - 35, cy - 25 - bar_h1, fill="#38bdf8", width=3)
            self.canvas.create_line(cx + 35, cy - 25, cx + 35, cy - 25 - bar_h2, fill="#38bdf8", width=3)
            state_label = "Listening... 🎧"

        elif self.current_state == "processing":
            # Thinking expression [ > ‿ < ]
            self.canvas.create_line(cx - 28, cy - 48, cx - 14, cy - 40, fill="#eab308", width=4)
            self.canvas.create_line(cx - 28, cy - 32, cx - 14, cy - 40, fill="#eab308", width=4)
            self.canvas.create_line(cx + 28, cy - 48, cx + 14, cy - 40, fill="#eab308", width=4)
            self.canvas.create_line(cx + 28, cy - 32, cx + 14, cy - 40, fill="#eab308", width=4)
            # Mouth
            self.canvas.create_line(cx - 10, cy - 26, cx + 10, cy - 26, fill="#eab308", width=3)
            state_label = "Thinking... ⚙️"

        elif self.current_state == "speaking":
            # Happy Speaking Expression [ ^ ‿ ^ ]
            self.canvas.create_arc(cx - 28, cy - 52, cx - 12, cy - 36, start=0, extent=180, outline="#10a37f", width=4, style="arc")
            self.canvas.create_arc(cx + 12, cy - 52, cx + 28, cy - 36, start=0, extent=180, outline="#10a37f", width=4, style="arc")
            # Animated open mouth
            m_open = int(abs(math.sin(self.anim_tick * 0.4)) * 8) + 4
            self.canvas.create_oval(cx - 12, cy - 32, cx + 12, cy - 32 + m_open, fill="#10a37f", outline="#ffffff")
            state_label = "Speaking... 🗣️"

        else:  # Idle
            # Happy smiling eyes [ ◕ ‿ ◕ ]
            self.canvas.create_oval(cx - 26, cy - 48, cx - 14, cy - 36, fill="#0284c7", outline="#ffffff")
            self.canvas.create_oval(cx + 14, cy - 48, cx + 26, cy - 36, fill="#0284c7", outline="#ffffff")
            self.canvas.create_arc(cx - 14, cy - 38, cx + 14, cy - 24, start=200, extent=140, fill="#0ea5e9", outline="")
            state_label = "Metis AI Ready ⚡"

        # State Tag Pill
        self.canvas.create_rectangle(cx - 50, cy + 72, cx + 50, cy + 90, fill="#1e293b", outline=glow_color, width=1.5)
        self.canvas.create_text(cx, cy + 81, text=state_label, fill="#ffffff", font=("Inter", 8, "bold"))

        # 7. Floating Speech Bubble (Right side)
        if self.current_text or self.current_state == "speaking":
            display_str = self.current_text if self.current_text else "Hello! I am JARVIS AI Companion."
            if len(display_str) > 65:
                display_str = display_str[:62] + "..."

            # Speech bubble container
            bx, by = 165, 30
            bw, bh = 165, 100
            self.canvas.create_rectangle(bx, by, bx + bw, by + bh, fill="#0f172a", outline=glow_color, width=2)
            # Pointer tail
            self.canvas.create_polygon(bx, by + 40, bx - 12, by + 50, bx, by + 60, fill="#0f172a", outline=glow_color)
            self.canvas.create_polygon(bx + 1, by + 42, bx - 9, by + 50, bx + 1, by + 58, fill="#0f172a", outline="")

            # Text wrapper
            self.canvas.create_text(
                bx + 12, by + 12, anchor="nw", width=140,
                text=display_str, fill="#f8fafc", font=("Inter", 9)
            )

    def update_loop(self):
        try:
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    st = f.read().strip()
                    if st:
                        self.current_state = st
            if os.path.exists(TEXT_FILE):
                with open(TEXT_FILE, "r", encoding="utf-8") as f:
                    txt = f.read().strip()
                    if txt:
                        self.current_text = txt
        except Exception:
            pass

        self.draw_robot()
        self.root.after(40, self.update_loop)


if __name__ == "__main__":
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        f.write("idle")
    with open(TEXT_FILE, "w", encoding="utf-8") as f:
        f.write("METIS AI Assistant is active!")

    root = tk.Tk()
    app = RobotCompanion(root)
    root.mainloop()
