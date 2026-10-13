import math
from datetime import datetime
from typing import Dict, Any, Tuple, List

SPANISH_DAYS = [
    "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"
]

SEASONS_INFO = {
    "invierno": {
        "name": "Invierno",
        "icon": "❄️",
        "principle": "Enraizamiento, conservación del fuego interno y densidad mineral",
        "color": "#38bdf8",
        "keywords": [
            "caldo", "huesos", "raíces", "raices", "tubérculos", "tuberculos",
            "osobuco", "miso", "jengibre", "romanesco", "tuétano", "tuetano",
            "estofado", "cúrcuma", "curcuma", "sopa", "colágeno", "colageno"
        ]
    },
    "primavera": {
        "name": "Primavera",
        "icon": "🌱",
        "principle": "Brote verde, drenaje hepático y expansión sutil",
        "color": "#4ade80",
        "keywords": [
            "brotes", "fermentos", "algas", "kéfir", "kefir", "espinacas",
            "té verde", "te verde", "germinados", "diente de león", "limón", "limon"
        ]
    },
    "verano": {
        "name": "Verano",
        "icon": "☀️",
        "principle": "Vitalidad solar, alta hidratación celular y ligereza",
        "color": "#facc15",
        "keywords": [
            "aguacate", "sardinas", "frutas", "frescas", "hidratación", "hidratacion",
            "coco", "pepino", "ceviche", "menta", "pescado", "mariscos"
        ]
    },
    "otoño": {
        "name": "Otoño",
        "icon": "🍂",
        "principle": "Cosecha, reposo de las ramas y calor de especias",
        "color": "#fb923c",
        "keywords": [
            "hongos", "calabaza", "nueces", "manzana", "canela", "lentejas",
            "miel", "semillas", "chía", "chia", "camote", "castañas"
        ]
    }
}

CIRCADIAN_PHASES = {
    "sunrise": {
        "name": "Amanecer Dorado",
        "subtitle": "Luz de la Aurora • Despertar Metabólico",
        "icon": "🌅",
        "bg_type": "parchment_gold",
        "blue_light": "Mínima / Luz Cálida"
    },
    "zenith": {
        "name": "Cenit Solar",
        "subtitle": "Piedra y Alta Agudeza • Foco Claro",
        "icon": "☀️",
        "bg_type": "slate_clean",
        "blue_light": "Plena / Claridad de Día"
    },
    "sunset": {
        "name": "Atardecer de Arcilla",
        "subtitle": "Cobre y Terracota • Integración y Cierre",
        "icon": "🌇",
        "bg_type": "terracotta_copper",
        "blue_light": "Atenuada / Cero Espectro Azul"
    },
    "night": {
        "name": "Fuego Sagrado & Obsidiana",
        "subtitle": "Noche Tribal • Melatonina Pura (Cero Luz Azul)",
        "icon": "🌌",
        "bg_type": "obsidian_ember",
        "blue_light": "Cero Absoluto / Fuego Ambar"
    },
    "bioluminescent_stone": {
        "name": "Piedra Rúnica Bioluminiscente",
        "subtitle": "Basalto y Circuitos Grabados • Resplandor Fósforo",
        "icon": "🗿",
        "bg_type": "carved_stone_cyan",
        "blue_light": "Bioluminiscencia Esmeralda/Cian"
    }
}


class CircadianClock:
    """Calculador de alineación biológica, rítmica y cósmica."""

    @staticmethod
    def get_current_moment(simulated_day: str = "", simulated_meal: str = "") -> Dict[str, Any]:
        now = datetime.now()
        day_name = simulated_day if simulated_day else SPANISH_DAYS[now.weekday()]
        hour = now.hour
        minute = now.minute
        time_str = f"{hour:02d}:{minute:02d}"

        # Determinación de momento de la comida
        if simulated_meal:
            meal = simulated_meal
        else:
            if 6 <= hour < 12:
                meal = "Desayuno"
            elif 12 <= hour < 17:
                meal = "Almuerzo"
            elif 17 <= hour < 20:
                meal = "Bebida Medicina"
            elif 20 <= hour < 23:
                meal = "Cena"
            else:
                meal = "Bebida Medicina"

        # Fase circadiana automática según hora
        if 6 <= hour < 10:
            phase = "sunrise"
        elif 10 <= hour < 18:
            phase = "zenith"
        elif 18 <= hour < 21:
            phase = "sunset"
        else:
            phase = "night"

        moon_phase, moon_icon = CircadianClock.calculate_moon_phase(now)

        return {
            "day": day_name,
            "hour": hour,
            "minute": minute,
            "time_str": time_str,
            "meal": meal,
            "circadian_phase": phase,
            "phase_info": CIRCADIAN_PHASES.get(phase, CIRCADIAN_PHASES["night"]),
            "moon_phase": moon_phase,
            "moon_icon": moon_icon
        }

    @staticmethod
    def calculate_moon_phase(date: datetime) -> Tuple[str, str]:
        """Calcula aproximadamente la fase lunar sin dependencias pesadas."""
        # Ciclo sinódico promedio ~ 29.53058867 días
        # Luna nueva de referencia: 2000-01-06 18:14 UTC
        diff = date - datetime(2000, 1, 6, 18, 14)
        days = diff.total_seconds() / 86400.0
        cycle = (days % 29.53058867) / 29.53058867

        if cycle < 0.125:
            return "Luna Nueva", "🌑"
        elif cycle < 0.375:
            return "Cuarto Creciente", "🌓"
        elif cycle < 0.625:
            return "Luna Llena", "🌕"
        elif cycle < 0.875:
            return "Cuarto Menguante", "🌗"
        else:
            return "Luna Nueva", "🌑"
