"""A daily project timer using only Python's standard library."""

import json
import os
from datetime import datetime, time, timedelta
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


PROJECTS = (
    "Project A - Security",
    "Project B - AI",
    "Training",
    "Travel",
    "Other / Misc.",
)
DATA_FILE = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "ProjectTimer" / "time_data.json"


def duration(seconds, show_seconds=False):
    seconds = max(0, int(seconds))
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    result = f"{hours:02d}:{minutes:02d}"
    return f"{result}:{seconds:02d}" if show_seconds else result


class Timer:
    def __init__(self):
        self.days = {}
        self.active = None
        self.last = None

    def account(self, now=None):
        now = now or datetime.now()
        if self.active is not None and self.last is not None and now > self.last:
            cursor = self.last
            while cursor < now:
                midnight = datetime.combine(cursor.date() + timedelta(days=1), time.min)
                end = min(midnight, now)
                totals = self.days.setdefault(cursor.date().isoformat(), {})
                totals[self.active] = totals.get(self.active, 0.0) + (end - cursor).total_seconds()
                cursor = end
        self.last = now

    def select(self, project, now=None):
        self.account(now)
        self.active = project

    def export(self):
        return "\n".join(
            f"{project} - {duration(totals.get(project, 0))} - {day}"
            for day, totals in sorted(self.days.items())
            for project in PROJECTS
        ) + "\n"


class App:
    def __init__(self, root):
        self.root = root
        self.timer = Timer()
        self.storage_ok = True
        root.title("Project Timer")
        root.attributes("-topmost", True)
        root.geometry("660x540")
        root.minsize(590, 470)
        root.protocol("WM_DELETE_WINDOW", self.close)
        ttk.Style().theme_use("clam")

        frame = ttk.Frame(root, padding=20)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Project Timer", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Select a project to switch timers. Totals are saved automatically.").pack(anchor="w", pady=(4, 12))
        self.status = tk.StringVar(value="Stopped")
        ttk.Label(frame, textvariable=self.status, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 10))

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x")
        self.buttons = {}
        for index, project in enumerate(PROJECTS):
            button = ttk.Button(buttons, command=lambda p=project: self.select(p))
            button.grid(row=index // 2, column=index % 2, sticky="ew", padx=4, pady=4, ipady=12)
            self.buttons[project] = button
        buttons.columnconfigure((0, 1), weight=1)

        actions = ttk.Frame(frame)
        actions.pack(fill="x", pady=12)
        ttk.Button(actions, text="Stop All", command=lambda: self.select(None)).pack(side="left")
        ttk.Button(actions, text="Save…", command=self.save_text).pack(side="right")
        ttk.Label(frame, text="Daily totals (HH:MM:SS)", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 6))
        table_frame = ttk.Frame(frame)
        table_frame.pack(fill="both", expand=True)
        self.table = ttk.Treeview(table_frame, columns=("date", "project", "total"), show="headings", height=7)
        for column, heading, width in (("date", "Date", 100), ("project", "Project", 270), ("total", "Time", 100)):
            self.table.heading(column, text=heading)
            self.table.column(column, width=width, anchor="w")
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.table.pack(side="left", fill="both", expand=True)
        self.note = tk.StringVar(value="Save exports all dates as Project - HH:MM - YYYY-MM-DD.")
        ttk.Label(frame, textvariable=self.note, wraplength=600).pack(anchor="w", pady=(10, 0))
        self.load()
        self.refresh()
        self.tick()

    def load(self):
        if not DATA_FILE.exists():
            return
        try:
            data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("Expected daily totals")
            for day, totals in data.items():
                datetime.strptime(day, "%Y-%m-%d")
                if not isinstance(totals, dict):
                    raise ValueError("Invalid totals")
                for project, seconds in totals.items():
                    if project not in PROJECTS or not isinstance(seconds, (int, float)) or not 0 <= seconds < float("inf"):
                        raise ValueError("Invalid project or elapsed time")
            self.timer.days = data
        except (OSError, ValueError, TypeError) as exc:
            self.storage_ok = False
            messagebox.showerror("Could not load saved time", f"{exc}\n\nThe existing data file will be preserved. You can still export this session with Save.", parent=self.root)

    def persist(self):
        if not self.storage_ok:
            return
        try:
            DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
            temporary = DATA_FILE.with_suffix(".tmp")
            temporary.write_text(json.dumps(self.timer.days, indent=2), encoding="utf-8")
            temporary.replace(DATA_FILE)
        except OSError as exc:
            self.storage_ok = False
            messagebox.showerror("Automatic saving failed", f"{exc}\n\nUse Save to export your recorded time before closing.", parent=self.root)

    def refresh(self):
        today = datetime.now().date().isoformat()
        self.timer.days.setdefault(today, {})
        self.status.set(f"Running: {self.timer.active}" if self.timer.active else "Stopped")
        for project, button in self.buttons.items():
            elapsed = self.timer.days[today].get(project, 0)
            prefix = "▶ " if project == self.timer.active else ""
            button.configure(text=f"{prefix}{project}\nToday: {duration(elapsed, True)}")
        # Update existing rows in place so scrolling and selection stay stable.
        position = 0
        for day in sorted(self.timer.days, reverse=True):
            for index, project in enumerate(PROJECTS):
                row_id = f"{day}-{index}"
                values = (day, project, duration(self.timer.days[day].get(project, 0), True))
                if self.table.exists(row_id):
                    self.table.item(row_id, values=values)
                else:
                    self.table.insert("", position, iid=row_id, values=values)
                position += 1

    def select(self, project):
        self.timer.select(project)
        self.refresh()
        self.persist()

    def tick(self):
        self.timer.account()
        self.refresh()
        self.persist()
        self.root.after(1000, self.tick)

    def save_text(self):
        path = filedialog.asksaveasfilename(parent=self.root, title="Save daily project totals", defaultextension=".txt", initialfile="project_time.txt", filetypes=[("Text files", "*.txt")])
        if not path:
            return
        self.timer.account()
        self.refresh()
        self.persist()
        try:
            Path(path).write_text(self.timer.export(), encoding="utf-8")
        except OSError as exc:
            messagebox.showerror("Could not save", str(exc), parent=self.root)
            return
        self.note.set(f"Saved {Path(path).name} at {datetime.now():%H:%M:%S}. Timers continue running.")

    def close(self):
        if not messagebox.askyesno("Close Project Timer?", "Stop tracking and close application", parent=self.root,):
            return
        self.timer.select(None)
        self.persist()
        if not self.storage_ok and not messagebox.askyesno("Close without automatic saving?", "Automatic saving is unavailable. Have you exported your time with Save?\n\nClose anyway?", parent=self.root):
            self.refresh()
            return
        self.root.destroy()


if __name__ == "__main__":
    App(tk.Tk()).root.mainloop()
