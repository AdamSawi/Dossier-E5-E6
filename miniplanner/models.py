import json
import time

# Classe représentant une tâche avec ses propriétés
class Task:
    def __init__(self, id, title, duration, unit='h', done=False, start_time=None):
        self.id = id
        self.title = title
        self.duration = duration
        self.unit = unit
        self.done = done
        self.start_time = start_time if start_time else time.time()

    def to_dict(self):
        # Convertit l'objet en dictionnaire pour sauvegarde JSON
        return {
            "id": self.id,
            "title": self.title,
            "duration": self.duration,
            "unit": self.unit,
            "done": self.done,
            "start_time": self.start_time
        }

# Classe qui gère la liste des tâches (ajout, suppression, sauvegarde, tri, etc.)
class TaskManager:
    def __init__(self, filepath='data/tasks.json'):
        self.filepath = filepath
        self.tasks = self.load_tasks()

    def load_tasks(self):
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
                return [Task(**t) for t in data]
        except FileNotFoundError:
            return []

    def save_tasks(self):
        with open(self.filepath, 'w') as f:
            json.dump([t.to_dict() for t in self.tasks], f, indent=2)

    def add_task(self, task):
        self.tasks.append(task)
        self.save_tasks()

    def delete_task(self, task_id):
        self.tasks = [t for t in self.tasks if t.id != task_id]
        self.save_tasks()

    def mark_task_done(self, task_id):
        for t in self.tasks:
            if t.id == task_id:
                t.done = True
        self.save_tasks()

    def edit_task(self, task_id, title, duration, unit):
        for t in self.tasks:
            if t.id == task_id:
                t.title = title
                t.duration = duration
                t.unit = unit
        self.save_tasks()

    def get_tasks(self):
        return sorted(self.tasks, key=lambda t: t.done)

    def get_progress(self, mode='time'):
        total = sum(self._convert_to_hours(t.duration, t.unit) for t in self.tasks)
        now = time.time()
        progress = 0
        for t in self.tasks:
            if t.done:
                progress += self._convert_to_hours(t.duration, t.unit)
            else:
                elapsed = (now - t.start_time) / self._unit_to_seconds(t.unit)
                progress += min(elapsed, t.duration) * self._convert_to_hours(1, t.unit)
        return (progress, total)

    def _convert_to_hours(self, duration, unit):
        if unit == 'm':
            return duration / 60
        elif unit == 'd':
            return duration * 24
        return duration

    def _unit_to_seconds(self, unit):
        return {'m': 60, 'h': 3600, 'd': 86400}.get(unit, 3600)
