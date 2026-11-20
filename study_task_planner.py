"""A small desktop task list for organizing study and school work."""

from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk


APP_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_FILE = APP_DIR / "tasks.json"

COLORS = {
    "ink": "#18324B",
    "muted": "#6C7F91",
    "teal": "#087E8B",
    "teal_dark": "#06646F",
    "mint": "#DDF4EF",
    "canvas": "#F3F7FA",
    "white": "#FFFFFF",
    "line": "#E2EAF0",
    "soft": "#F7FAFC",
    "red": "#B54747",
    "green": "#247A58",
}


def sample_tasks() -> list[dict[str, object]]:
    """Return a few examples for the optional demo view."""
    return [
        {"id": "demo-1", "text": "Finish science homework", "done": False},
        {"id": "demo-2", "text": "Review math notes", "done": True},
        {"id": "demo-3", "text": "Pack school bag", "done": False},
    ]


class StudyTaskPlanner(tk.Tk):
    def __init__(self, data_file: Path, demo: bool = False) -> None:
        super().__init__()
        self.data_file = data_file
        self.tasks = self._load_tasks(demo)
        self.title("Study Task Planner")
        self.geometry("850x760")
        self.minsize(760, 700)
        self.configure(bg=COLORS["canvas"])
        self._configure_styles()
        self._build_layout()
        self._refresh_tasks()

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=COLORS["canvas"])
        style.configure(
            "Treeview",
            background=COLORS["white"],
            fieldbackground=COLORS["white"],
            foreground=COLORS["ink"],
            rowheight=42,
            borderwidth=0,
            font=("Segoe UI", 11),
        )
        style.configure(
            "Treeview.Heading",
            background=COLORS["soft"],
            foreground=COLORS["muted"],
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padding=(12, 10),
        )
        style.map(
            "Treeview",
            background=[("selected", COLORS["mint"])],
            foreground=[("selected", COLORS["ink"])],
        )

    def _build_layout(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        header = tk.Frame(self, bg=COLORS["ink"], height=112)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.columnconfigure(0, weight=1)
        tk.Label(
            header,
            text="Study Task Planner",
            bg=COLORS["ink"],
            fg=COLORS["white"],
            font=("Segoe UI", 23, "bold"),
        ).grid(row=0, column=0, sticky="sw", padx=30, pady=(18, 0))
        tk.Label(
            header,
            text="A clear list for the things you need to get done.",
            bg=COLORS["ink"],
            fg="#C5D5E2",
            font=("Segoe UI", 10),
        ).grid(row=1, column=0, sticky="nw", padx=31, pady=(3, 18))
        tk.Label(
            header,
            text="STUDY ORGANIZER",
            bg=COLORS["ink"],
            fg="#93D9CE",
            font=("Segoe UI", 9, "bold"),
        ).grid(row=0, column=1, rowspan=2, sticky="e", padx=30)

        stats = ttk.Frame(self, padding=(24, 18, 24, 8))
        stats.grid(row=1, column=0, sticky="ew")
        for column in range(3):
            stats.columnconfigure(column, weight=1, uniform="stats")
        self.total_value = self._stat_card(stats, 0, "TOTAL TASKS", "0")
        self.todo_value = self._stat_card(stats, 1, "TO DO", "0")
        self.done_value = self._stat_card(stats, 2, "COMPLETED", "0")

        content = ttk.Frame(self, padding=(24, 10, 24, 12))
        content.grid(row=2, column=0, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(2, weight=1)
        self._build_entry_card(content)
        self._build_task_list(content)

        footer = tk.Frame(self, bg=COLORS["canvas"])
        footer.grid(row=3, column=0, sticky="ew", padx=26, pady=(0, 14))
        footer.columnconfigure(0, weight=1)
        tk.Label(
            footer,
            text="Tasks are saved on this computer.",
            bg=COLORS["canvas"],
            fg=COLORS["muted"],
            font=("Segoe UI", 9),
        ).grid(row=0, column=0, sticky="w")
        self.status_label = tk.Label(
            footer,
            text="Ready",
            bg=COLORS["canvas"],
            fg=COLORS["teal"],
            font=("Segoe UI", 9, "bold"),
        )
        self.status_label.grid(row=0, column=1, sticky="e")

    def _stat_card(self, parent: ttk.Frame, column: int, title: str, initial: str) -> tk.Label:
        card = tk.Frame(parent, bg=COLORS["white"], highlightbackground=COLORS["line"], highlightthickness=1)
        card.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 8, 0 if column == 2 else 8))
        card.grid_columnconfigure(0, weight=1)
        tk.Label(
            card,
            text=title,
            bg=COLORS["white"],
            fg=COLORS["muted"],
            font=("Segoe UI", 8, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 3))
        value = tk.Label(
            card,
            text=initial,
            bg=COLORS["white"],
            fg=COLORS["ink"],
            font=("Segoe UI", 18, "bold"),
        )
        value.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 12))
        return value

    def _build_entry_card(self, parent: ttk.Frame) -> None:
        card = tk.Frame(parent, bg=COLORS["white"], highlightbackground=COLORS["line"], highlightthickness=1)
        card.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        card.columnconfigure(0, weight=1)
        tk.Label(
            card,
            text="Add a task",
            bg=COLORS["white"],
            fg=COLORS["ink"],
            font=("Segoe UI", 13, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=18, pady=(14, 10))

        self.task_var = tk.StringVar()
        self.task_entry = tk.Entry(
            card,
            textvariable=self.task_var,
            bg=COLORS["white"],
            fg=COLORS["ink"],
            insertbackground=COLORS["teal"],
            relief="solid",
            bd=1,
            font=("Segoe UI", 11),
        )
        self.task_entry.grid(row=1, column=0, sticky="ew", padx=(18, 8), pady=(0, 16), ipady=9)
        self.task_entry.bind("<Return>", lambda _event: self.add_task())
        tk.Button(
            card,
            text="+  Add task",
            command=self.add_task,
            bg=COLORS["teal"],
            fg=COLORS["white"],
            activebackground=COLORS["teal_dark"],
            activeforeground=COLORS["white"],
            relief="flat",
            bd=0,
            padx=18,
            pady=10,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
        ).grid(row=1, column=1, sticky="e", padx=(4, 18), pady=(0, 16))

    def _build_task_list(self, parent: ttk.Frame) -> None:
        toolbar = tk.Frame(parent, bg=COLORS["canvas"])
        toolbar.grid(row=1, column=0, sticky="ew", pady=(0, 9))
        toolbar.columnconfigure(0, weight=1)
        tk.Label(
            toolbar,
            text="My tasks",
            bg=COLORS["canvas"],
            fg=COLORS["ink"],
            font=("Segoe UI", 14, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=(1, 0))

        table_card = tk.Frame(parent, bg=COLORS["white"], highlightbackground=COLORS["line"], highlightthickness=1)
        table_card.grid(row=2, column=0, sticky="nsew")
        table_card.columnconfigure(0, weight=1)
        table_card.rowconfigure(0, weight=1)
        self.tree = ttk.Treeview(table_card, columns=("task", "status"), show="headings", selectmode="browse")
        self.tree.heading("task", text="TASK", anchor="w")
        self.tree.heading("status", text="STATUS", anchor="center")
        self.tree.column("task", width=560, minwidth=280, anchor="w", stretch=True)
        self.tree.column("status", width=150, minwidth=130, anchor="center", stretch=False)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(12, 0), pady=12)
        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 10), pady=12)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.tag_configure("done", foreground=COLORS["muted"])
        self.tree.tag_configure("todo", foreground=COLORS["ink"])

        actions = tk.Frame(parent, bg=COLORS["canvas"])
        actions.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        tk.Button(
            actions,
            text="Mark complete / undo",
            command=self.toggle_selected,
            bg=COLORS["mint"],
            fg=COLORS["teal_dark"],
            activebackground="#C7EBE4",
            relief="flat",
            bd=0,
            padx=14,
            pady=8,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
        ).pack(side="left")
        tk.Button(
            actions,
            text="Clear completed",
            command=self.clear_completed,
            bg=COLORS["canvas"],
            fg=COLORS["muted"],
            activebackground=COLORS["canvas"],
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            font=("Segoe UI", 9),
            cursor="hand2",
        ).pack(side="right")
        tk.Button(
            actions,
            text="Delete selected",
            command=self.delete_selected,
            bg=COLORS["canvas"],
            fg=COLORS["red"],
            activebackground=COLORS["canvas"],
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            font=("Segoe UI", 9),
            cursor="hand2",
        ).pack(side="right")

    def _load_tasks(self, demo: bool) -> list[dict[str, object]]:
        if not self.data_file.exists():
            return sample_tasks() if demo else []
        try:
            raw = json.loads(self.data_file.read_text(encoding="utf-8"))
            if not isinstance(raw, list):
                raise ValueError("The saved task file must contain a list.")
            tasks = []
            for item in raw:
                if not isinstance(item, dict) or not str(item.get("text", "")).strip():
                    continue
                tasks.append(
                    {
                        "id": str(item.get("id") or uuid.uuid4()),
                        "text": str(item["text"]).strip(),
                        "done": bool(item.get("done", False)),
                    }
                )
            return tasks
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
            messagebox.showerror("Could not read tasks", f"The saved tasks could not be loaded.\n\n{error}")
            return []

    def _save_tasks(self) -> None:
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        temp_file = self.data_file.with_suffix(self.data_file.suffix + ".tmp")
        temp_file.write_text(json.dumps(self.tasks, indent=2, ensure_ascii=False), encoding="utf-8")
        temp_file.replace(self.data_file)

    def _refresh_tasks(self) -> None:
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)

        completed = 0
        for task in self.tasks:
            done = bool(task["done"])
            completed += int(done)
            self.tree.insert(
                "",
                "end",
                iid=str(task["id"]),
                values=(str(task["text"]), "Completed" if done else "To do"),
                tags=("done" if done else "todo",),
            )

        total = len(self.tasks)
        self.total_value.configure(text=str(total))
        self.done_value.configure(text=str(completed))
        self.todo_value.configure(text=str(total - completed))
        self.status_label.configure(text=f"{total} {'task' if total == 1 else 'tasks'}")

    def add_task(self) -> None:
        text = self.task_var.get().strip()
        if not text:
            messagebox.showinfo("Add a task", "Type a task name first.")
            self.task_entry.focus_set()
            return
        self.tasks.append({"id": str(uuid.uuid4()), "text": text, "done": False})
        self._save_tasks()
        self.task_var.set("")
        self._refresh_tasks()
        self.task_entry.focus_set()

    def _selected_task(self) -> dict[str, object] | None:
        selection = self.tree.selection()
        if not selection:
            return None
        selected_id = selection[0]
        return next((task for task in self.tasks if str(task["id"]) == selected_id), None)

    def toggle_selected(self) -> None:
        task = self._selected_task()
        if task is None:
            messagebox.showinfo("Select a task", "Choose a task before changing its status.")
            return
        task["done"] = not bool(task["done"])
        self._save_tasks()
        self._refresh_tasks()

    def delete_selected(self) -> None:
        task = self._selected_task()
        if task is None:
            messagebox.showinfo("Select a task", "Choose a task before deleting it.")
            return
        self.tasks = [item for item in self.tasks if str(item["id"]) != str(task["id"])]
        self._save_tasks()
        self._refresh_tasks()

    def clear_completed(self) -> None:
        completed_count = sum(bool(task["done"]) for task in self.tasks)
        if not completed_count:
            messagebox.showinfo("No completed tasks", "There are no completed tasks to clear.")
            return
        if not messagebox.askyesno("Clear completed tasks", f"Remove {completed_count} completed task(s)?"):
            return
        self.tasks = [task for task in self.tasks if not bool(task["done"])]
        self._save_tasks()
        self._refresh_tasks()


def main() -> None:
    parser = argparse.ArgumentParser(description="Keep a simple list of study and school tasks.")
    parser.add_argument("--demo", action="store_true", help="Show example tasks when no task file exists.")
    parser.add_argument("--data-file", type=Path, default=DEFAULT_DATA_FILE, help="Choose where tasks are saved.")
    args = parser.parse_args()
    app = StudyTaskPlanner(args.data_file, demo=args.demo)
    app.mainloop()


if __name__ == "__main__":
    main()
