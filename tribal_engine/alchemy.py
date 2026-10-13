import re
from typing import Dict, Any, List, Tuple

TIME_PATTERNS = [
    (r'(\d+)\s*(?:horas|hora|hrs|hr|h)\b', lambda m: int(m.group(1)) * 3600, "{val} Horas"),
    (r'(\d+)\s*(?:minutos|minuto|mins|min)\b', lambda m: int(m.group(1)) * 60, "{val} Minutos"),
    (r'la noche anterior', lambda m: 8 * 3600, "8h (Noche Anterior)"),
    (r'(\d+)\s*(?:días|dias|dia|día)\b', lambda m: int(m.group(1)) * 86400, "{val} Días"),
]

# Expresiones de cantidades escalables: "2 huevos", "500g", "1 taza", "2 zanahorias", etc.
QUANTITY_PATTERN = re.compile(
    r'\b(\d+(?:[.,]\d+)?)\s*(kg|kilos|kilo|g|gr|gramos|ml|l|litros|tazas|taza|cucharadas|cucharadita|dientes|huevos|zanahorias|papas|cebollas|rodajas|gajos)\b',
    re.IGNORECASE
)

PORTION_PRESETS = [
    {"label": "1 Solitario/a", "multiplier": 0.5, "icon": "👤"},
    {"label": "2 Pareja", "multiplier": 1.0, "icon": "👥"},
    {"label": "4 Familia", "multiplier": 2.0, "icon": "👨‍👩‍👧‍👦"},
    {"label": "8 Tribu", "multiplier": 4.0, "icon": "🔥"},
]

class AlchemyEngine:
    """Motor de alquimia física, cocciones, rituales y escalado de porciones."""

    @staticmethod
    def extract_time_rituals(text: str) -> List[Dict[str, Any]]:
        """Busca menciones de tiempo de cocción o reposo en un fragmento de texto."""
        rituals = []
        for pattern, calc_sec, label_tmpl in TIME_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                try:
                    seconds = calc_sec(match)
                    val = match.group(1) if match.groups() else ""
                    label = label_tmpl.format(val=val)
                    rituals.append({
                        "raw_match": match.group(0),
                        "seconds": seconds,
                        "label": label,
                        "start": match.start(),
                        "end": match.end()
                    })
                except Exception:
                    continue
        return rituals

    @staticmethod
    def format_duration(seconds: int) -> str:
        """Formatea segundos en formato sagrado y legible (HH:MM:SS o Xh Ym)."""
        if seconds >= 3600:
            h = seconds // 3600
            m = (seconds % 3600) // 60
            s = seconds % 60
            if s > 0:
                return f"{h}h {m}m {s}s"
            return f"{h}h {m}m" if m > 0 else f"{h}h"
        elif seconds >= 60:
            m = seconds // 60
            s = seconds % 60
            return f"{m}m {s}s" if s > 0 else f"{m}m"
        else:
            return f"{seconds}s"

    @staticmethod
    def scale_quantities_in_text(text: str, multiplier: float) -> str:
        """Recalcula visualmente cantidades en un texto según el multiplicador de la tribu."""
        if multiplier == 1.0:
            return text

        def replacer(match):
            raw_num = match.group(1).replace(",", ".")
            unit = match.group(2)
            try:
                num = float(raw_num)
                scaled = num * multiplier
                # Formatear limpiamente (si es entero, sin decimales)
                if scaled.is_integer():
                    formatted = str(int(scaled))
                else:
                    formatted = f"{scaled:.1f}"
                return f'<span class="scaled-quantity" title="Original: {raw_num} {unit}">{formatted} {unit}</span>'
            except Exception:
                return match.group(0)

        return QUANTITY_PATTERN.sub(replacer, text)
