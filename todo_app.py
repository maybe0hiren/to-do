import tkinter as tk
import json
import os

TASKS_FILE = "tasks.json"
ANIM_DURATION = 500  # milliseconds
FPS = 30  # frames per second

class TodoWidget:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do Widget")
        self.root.geometry("300x400")  # Size of the widget
        self.root.configure(bg="#1c1c1c")
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.95)

        # Round corners (macOS-like)
        self.root.overrideredirect(True)
        self.root.geometry("+100+100")  # Position it in the corner

        # Shadow effect (needs some creativity with external libraries for perfect shadow)
        self.root.config(bg="#1c1c1c")

        self.tasks = []

        # Dragging functionality
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0

        self.root.bind("<Button-1>", self.start_drag)
        self.root.bind("<B1-Motion>", self.do_drag)
        self.root.bind("<ButtonRelease-1>", self.stop_drag)

        # Input area
        self.input_frame = tk.Frame(self.root, bg="#1c1c1c", pady=5)
        self.input_frame.pack(pady=10)

        self.task_entry = tk.Entry(
            self.input_frame, width=18, fg="#ffffff", bg="#333333",
            insertbackground="white", relief=tk.FLAT, font=("Segoe UI", 11)
        )
        self.task_entry.pack(side=tk.LEFT, padx=(10, 5))

        self.add_button = tk.Button(
            self.input_frame, text="Add", command=self.add_task,
            bg="#444444", fg="white", activebackground="#666666",
            relief=tk.FLAT, padx=10, font=("Segoe UI", 10)
        )
        self.add_button.pack(side=tk.LEFT)

        # Task list area
        self.tasks_frame = tk.Frame(self.root, bg="#1c1c1c", pady=5)
        self.tasks_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # Close button in yellow
        self.close_button = tk.Button(
            self.root, text="X", command=self.close_widget, fg="yellow", bg="#1c1c1c", font=("Segoe UI", 12),
            relief=tk.FLAT, borderwidth=0, activeforeground="white", activebackground="#1c1c1c"
        )
        self.close_button.place(x=270, y=370)  # Placed at the bottom-right corner

        self.load_tasks()

    def add_task(self):
        task_text = self.task_entry.get().strip()
        if task_text:
            self.task_entry.delete(0, tk.END)
            self.create_task_widget(task_text, animate=True)
            self.save_tasks()

    def create_task_widget(self, text, animate=False):
        task_frame = tk.Frame(self.tasks_frame, bg="#2b2b2b", pady=6, padx=8, relief="flat", bd=0)
        task_frame.config(borderwidth=0)
        task_label = tk.Label(
            task_frame, text=text, bg="#2b2b2b", fg="white",
            anchor="w", font=("Segoe UI", 11), padx=10
        )
        task_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        finish_button = tk.Button(
            task_frame, text="○", fg="#bbbbbb", bg="#2b2b2b",
            font=("Segoe UI", 12), relief=tk.FLAT, borderwidth=0,
            activeforeground="white", activebackground="#2b2b2b"
        )
        finish_button.pack(side=tk.RIGHT, padx=10)

        finish_button.config(command=lambda: self.animate_finish(task_frame, text, finish_button))

        self.tasks.append((text, task_frame))

        if animate:
            task_frame.pack_forget()
            task_frame.pack(fill=tk.X, padx=10, pady=5)
            self.fade_in(task_frame)
        else:
            task_frame.pack(fill=tk.X, padx=10, pady=5)

    def fade_in(self, frame):
        steps = FPS // 2
        base_color = 17  # start
        max_color = 34   # end
        delta = (max_color - base_color) // max(1, steps)

        def step(i=0):
            if i <= steps:
                c = base_color + i * delta
                hex_color = f"#{c:02x}{c:02x}{c:02x}"
                frame.config(bg=hex_color)
                for widget in frame.winfo_children():
                    widget.config(bg=hex_color)
                self.root.after(int(ANIM_DURATION / steps), lambda: step(i + 1))

        step()

    def animate_finish(self, frame, text, button):
        # Yellow flash
        button.config(fg="yellow")

        def fade_out(i=0):
            steps = FPS // 2
            max_color = 34
            min_color = 17
            delta = (max_color - min_color) // max(1, steps)

            if i <= steps:
                c = max_color - i * delta
                hex_color = f"#{c:02x}{c:02x}{c:02x}"
                frame.config(bg=hex_color)
                for widget in frame.winfo_children():
                    widget.config(bg=hex_color)
                self.root.after(int(ANIM_DURATION / steps), lambda: fade_out(i + 1))
            else:
                frame.destroy()
                self.tasks = [t for t in self.tasks if t[0] != text]
                self.save_tasks()

        # Start fade after yellow flash
        self.root.after(200, fade_out)

    def save_tasks(self):
        task_texts = [t[0] for t in self.tasks]
        with open(TASKS_FILE, 'w') as f:
            json.dump(task_texts, f)

    def load_tasks(self):
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, 'r') as f:
                try:
                    task_texts = json.load(f)
                    for task in task_texts:
                        self.create_task_widget(task)
                except json.JSONDecodeError:
                    pass

    def close_widget(self):
        self.root.quit()

    def start_drag(self, event):
        self.dragging = True
        self.offset_x = event.x
        self.offset_y = event.y

    def do_drag(self, event):
        if self.dragging:
            dx = event.x - self.offset_x
            dy = event.y - self.offset_y
            x = self.root.winfo_x() + dx
            y = self.root.winfo_y() + dy
            self.root.geometry(f"+{x}+{y}")

    def stop_drag(self, event):
        self.dragging = False

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoWidget(root)
    root.mainloop()
