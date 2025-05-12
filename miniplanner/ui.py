import tkinter as tk
from tkinter import messagebox, ttk
from models import Task, TaskManager
import time
import threading

class TaskApp:
    def __init__(self):
        self.manager = TaskManager()
        self.root = tk.Tk()
        self.root.title("MiniPlanner")
        self.root.geometry("700x600")
        self.auto_mode = tk.BooleanVar(value=True)
        self.create_widgets()
        self.run_timer()

    def create_widgets(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=("Segoe UI", 11))
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure("TCheckbutton", font=("Segoe UI", 10))
        style.configure("Horizontal.TProgressbar", troughcolor='#e0e0e0', background='#4caf50', thickness=20)

        top = ttk.Frame(self.root, padding=10)
        top.pack()

        ttk.Label(top, text="Nom de la tâche").grid(row=0, column=0, padx=5, pady=5)
        self.title_entry = ttk.Entry(top, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(top, text="Durée").grid(row=1, column=0, padx=5, pady=5)
        self.duration_entry = ttk.Entry(top, width=10)
        self.duration_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(top, text="Unité").grid(row=1, column=2, padx=5)
        self.unit_var = tk.StringVar(value='h')
        self.unit_menu = ttk.Combobox(top, textvariable=self.unit_var, values=['m', 'h', 'd'], width=5)
        self.unit_menu.grid(row=1, column=3, padx=5)

        self.add_btn = ttk.Button(top, text="Ajouter la tâche", command=self.add_task)
        self.add_btn.grid(row=2, column=0, columnspan=4, pady=10)

        self.auto_checkbox = ttk.Checkbutton(self.root, text="Mode auto (actualisation en temps réel)", variable=self.auto_mode)
        self.auto_checkbox.pack(pady=5)

        self.progress_label = ttk.Label(self.root, text="")
        self.progress_label.pack(pady=5)

        self.progress_bar = ttk.Progressbar(self.root, length=600)
        self.progress_bar.pack(pady=10)

        self.tasks_frame = ttk.Frame(self.root, padding=10)
        self.tasks_frame.pack(fill='both', expand=True)
        self.refresh_task_list()

    def add_task(self):
        title = self.title_entry.get()
        try:
            duration = float(self.duration_entry.get())
        except ValueError:
            messagebox.showerror("Erreur", "Durée invalide.")
            return
        unit = self.unit_var.get()
        task = Task(id=len(self.manager.tasks)+1, title=title, duration=duration, unit=unit)
        self.manager.add_task(task)
        self.refresh_task_list()

    def refresh_task_list(self):
        for widget in self.tasks_frame.winfo_children():
            widget.destroy()

        for task in self.manager.get_tasks():
            row = ttk.Frame(self.tasks_frame)
            row.pack(fill='x', pady=3)

            status = "✔️" if task.done else "⏳"
            ttk.Label(row, text=f"{task.title} ({task.duration}{task.unit}) {status}").pack(side="left", padx=10)

            if not task.done:
                ttk.Button(row, text="✔", command=lambda id=task.id: self.mark_done(id)).pack(side="left", padx=5)
            ttk.Button(row, text="🗑", command=lambda id=task.id: self.delete_task(id)).pack(side="left", padx=5)
            ttk.Button(row, text="✏", command=lambda t=task: self.open_edit_window(t)).pack(side="left", padx=5)

        progress, total = self.manager.get_progress()
        percent = int((progress / total) * 100) if total > 0 else 0
        self.progress_label.config(text=f"Avancement global : {percent}%")
        self.progress_bar['value'] = percent

    def mark_done(self, task_id):
        self.manager.mark_task_done(task_id)
        self.refresh_task_list()

    def delete_task(self, task_id):
        self.manager.delete_task(task_id)
        self.refresh_task_list()

    def open_edit_window(self, task):
        # Ouvre une fenêtre de modification pour la tâche sélectionnée
        edit_win = tk.Toplevel(self.root)
        edit_win.title("Modifier la tâche")
        edit_win.geometry("400x200")

        ttk.Label(edit_win, text="Nom").pack(pady=5)
        title_entry = ttk.Entry(edit_win)
        title_entry.insert(0, task.title)
        title_entry.pack(pady=5)

        ttk.Label(edit_win, text="Durée").pack(pady=5)
        duration_entry = ttk.Entry(edit_win)
        duration_entry.insert(0, str(task.duration))
        duration_entry.pack(pady=5)

        ttk.Label(edit_win, text="Unité").pack(pady=5)
        unit_var = tk.StringVar(value=task.unit)
        unit_menu = ttk.Combobox(edit_win, textvariable=unit_var, values=['m', 'h', 'd'])
        unit_menu.pack(pady=5)

        def save_changes():
            try:
                new_title = title_entry.get()
                new_duration = float(duration_entry.get())
                new_unit = unit_var.get()
                self.manager.edit_task(task.id, new_title, new_duration, new_unit)
                edit_win.destroy()
                self.refresh_task_list()
            except ValueError:
                messagebox.showerror("Erreur", "Durée invalide.")

        ttk.Button(edit_win, text="Enregistrer", command=save_changes).pack(pady=10)

    def run_timer(self):
        # Met à jour la progression toutes les secondes si le mode auto est activé
        def check_tasks():
            while True:
                if self.auto_mode.get():
                    self.refresh_task_list()
                time.sleep(1)
        threading.Thread(target=check_tasks, daemon=True).start()

    def run(self):
        self.root.mainloop()
