import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional

class TribalStateManager:
    """
    Guardián de la memoria material, hábitos y marginalia.
    Garantiza que los archivos Markdown permanezcan como artefactos 100% inmutables:
    ninguna anotación ni hábito altera los archivos en disco.
    """

    def __init__(self, state_file_path: str):
        self.state_file_path = state_file_path
        self.state: Dict[str, Any] = {
            "version": 2,
            "settings": {
                "circadian_mode": "auto",
                "here_and_now": True,
                "simulated_day": "",       # Vacio = usar reloj real
                "simulated_meal": "",      # Vacio = usar reloj real
                "portion_multiplier": 1.0, # 0.5 (1p), 1.0 (2p), 2.0 (4p), 4.0 (8p Tribu)
                "portion_label": "2 Pareja",
                "season": "invierno",
                "semantic_zoom": "micro"   # "macro", "meso", "micro"
            },
            "patina": {},      # file_key -> { section_id: { seconds: int, visits: int } }
            "habits": {},      # file_key -> { item_id: bool }
            "marginalia": {},  # file_key -> list of { id, section_id, text, timestamp }
            "active_timers": []# list of { id, title, duration_sec, remaining_sec, running: bool, timestamp }
        }
        self.load()
        if not os.path.exists(self.state_file_path):
            self.save()

    def load(self):
        if os.path.exists(self.state_file_path):

            try:
                with open(self.state_file_path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    if isinstance(saved, dict):
                        # Merge saved into defaults
                        for k, v in saved.items():
                            if k == "settings" and isinstance(v, dict):
                                self.state["settings"].update(v)
                            else:
                                self.state[k] = v
            except Exception as e:
                print(f"[TribalStateManager] Error loading state: {e}")

    def save(self):
        try:
            folder = os.path.dirname(self.state_file_path)
            if folder and not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
            with open(self.state_file_path, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[TribalStateManager] Error saving state: {e}")

    @staticmethod
    def compute_file_hash(filepath: str) -> str:
        """Calcula el hash criptográfico SHA-256 del archivo para certificar su inmutabilidad."""
        if not os.path.exists(filepath):
            return "0000000000000000"
        hasher = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return "error_reading_file"

    def record_patina(self, file_key: str, section_id: str, elapsed_seconds: int = 5):
        """Acumula tiempo de lectura y desgaste noble sobre una sección del texto."""
        if file_key not in self.state["patina"]:
            self.state["patina"][file_key] = {}
        file_patina = self.state["patina"][file_key]
        if section_id not in file_patina:
            file_patina[section_id] = {"seconds": 0, "visits": 0}
        file_patina[section_id]["seconds"] += elapsed_seconds
        file_patina[section_id]["visits"] += 1
        self.save()

    def get_patina_level(self, file_key: str, section_id: str) -> float:
        """Devuelve un factor de 0.0 a 1.0 indicando el nivel de pátina / uso de la sección."""
        file_patina = self.state.get("patina", {}).get(file_key, {})
        entry = file_patina.get(section_id, {"seconds": 0, "visits": 0})
        # 300 segundos (5 minutos) de atención acumulada alcanza pátina completa 1.0
        sec_ratio = min(1.0, entry["seconds"] / 300.0)
        visit_ratio = min(1.0, entry["visits"] / 10.0)
        return round(max(sec_ratio, visit_ratio), 2)

    def toggle_habit(self, file_key: str, item_id: str) -> bool:
        """Marca o desmarca un hábito o preparación consumada sin alterar el Markdown."""
        if file_key not in self.state["habits"]:
            self.state["habits"][file_key] = {}
        current = self.state["habits"][file_key].get(item_id, False)
        new_val = not current
        self.state["habits"][file_key][item_id] = new_val
        self.save()
        return new_val

    def is_habit_completed(self, file_key: str, item_id: str) -> bool:
        return self.state.get("habits", {}).get(file_key, {}).get(item_id, False)

    def add_marginalia(self, file_key: str, section_id: str, note_text: str):
        """Guarda una nota al margen estilo pergamino."""
        if file_key not in self.state["marginalia"]:
            self.state["marginalia"][file_key] = []
        note_id = f"note_{datetime.now().strftime('%Y%m%d%H%M%S%f')[:17]}"
        note = {
            "id": note_id,
            "section_id": section_id,
            "text": note_text.strip(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.state["marginalia"][file_key].append(note)
        self.save()
        return note

    def delete_marginalia(self, file_key: str, note_id: str):
        if file_key in self.state["marginalia"]:
            self.state["marginalia"][file_key] = [
                n for n in self.state["marginalia"][file_key] if n.get("id") != note_id
            ]
            self.save()

    def get_marginalia(self, file_key: str) -> List[Dict[str, Any]]:
        return self.state.get("marginalia", {}).get(file_key, [])

    def add_timer(self, title: str, duration_sec: int) -> Dict[str, Any]:
        """Añade un ritual/temporizador de cocción."""
        timer_id = f"timer_{datetime.now().strftime('%Y%m%d%H%M%S%f')[:17]}"
        timer = {
            "id": timer_id,
            "title": title,
            "total_sec": duration_sec,
            "remaining_sec": duration_sec,
            "running": True,
            "created_at": datetime.now().isoformat()
        }
        self.state["active_timers"].append(timer)
        self.save()
        return timer

    def update_timers(self, tick_seconds: int = 1) -> List[Dict[str, Any]]:
        """Avanza los temporizadores activos en curso."""
        completed = []
        for t in self.state["active_timers"]:
            if t.get("running", False) and t["remaining_sec"] > 0:
                t["remaining_sec"] = max(0, t["remaining_sec"] - tick_seconds)
                if t["remaining_sec"] == 0:
                    t["running"] = False
                    completed.append(t)
        if self.state["active_timers"]:
            self.save()
        return completed

    def remove_timer(self, timer_id: str):
        self.state["active_timers"] = [
            t for t in self.state["active_timers"] if t.get("id") != timer_id
        ]
        self.save()
