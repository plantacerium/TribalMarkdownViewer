import re
import unicodedata
from typing import Dict, Any, List, Tuple

ELEMENT_LEXICON = {
    "fuego": {
        "name": "Fuego Metabólico",
        "icon": "🔥",
        "color": "#ef4444",
        "keywords": [
            "fuego", "caliente", "asado", "estofado", "osobuco", "jengibre",
            "cúrcuma", "curcuma", "pimienta", "horno", "chili", "curry",
            "cocción", "coccion", "calor", "salteado", "dorado", "canela"
        ]
    },
    "tierra": {
        "name": "Tierra & Densidad Mineral",
        "icon": "🌍",
        "color": "#d97706",
        "keywords": [
            "tierra", "raíz", "raiz", "raíces", "raices", "tubérculos", "tuberculos",
            "huesos", "minerales", "camote", "nabo", "tuétano", "tuetano",
            "lentejas", "remolacha", "zanahoria", "enraizamiento", "densidad"
        ]
    },
    "agua": {
        "name": "Agua & Esencia Marina",
        "icon": "💧",
        "color": "#06b6d4",
        "keywords": [
            "agua", "caldo", "sopa", "mar", "pescado", "salmón", "salmon",
            "algas", "infusión", "infusion", "té", "te", "dashi", "hidratación",
            "hidratacion", "kéfir", "kefir", "líquido", "liquido", "mariscos"
        ]
    },
    "eter": {
        "name": "Éter & Geometría Fractal",
        "icon": "🌀",
        "color": "#8b5cf6",
        "keywords": [
            "geometría", "geometria", "fractal", "romanesco", "espiral",
            "círculos", "circulos", "patrones", "hongos", "fungi", "red",
            "vida", "fermento", "alquimia", "sagrada", "divino", "orden"
        ]
    }
}

class FractalEngine:
    """Motor de geometría fractal, balance de elementos y red de micelio."""

    @staticmethod
    def slugify(text: str) -> str:
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
        text = re.sub(r'[^\w\s-]', '', text).strip().lower()
        return re.sub(r'[-\s]+', '-', text)

    @staticmethod
    def extract_header_tree(md_text: str) -> List[Dict[str, Any]]:
        """Extrae el árbol de encabezados (#, ##, ###) para navegación en micelio."""
        headers = []
        pattern = re.compile(r'^(#{1,3})\s+(.+)$', re.MULTILINE)
        idx = 0
        for match in pattern.finditer(md_text):
            level = len(match.group(1))
            title = match.group(2).strip()
            # Eliminar posibles negritas o cursivas del título
            clean_title = re.sub(r'[*_`]', '', title)
            slug = f"sec-{idx}-{FractalEngine.slugify(clean_title)}"
            headers.append({
                "id": slug,
                "index": idx,
                "level": level,
                "title": clean_title,
                "raw": match.group(0)
            })
            idx += 1
        return headers

    @staticmethod
    def build_mycelium_graph(headers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Construye los nodos y filamentos de la red de micelio."""
        nodes = []
        links = []
        last_at_level = {1: None, 2: None, 3: None}

        for h in headers:
            lvl = h["level"]
            node_id = h["id"]
            nodes.append({
                "id": node_id,
                "label": h["title"],
                "level": lvl,
                "radius": 18 if lvl == 1 else (13 if lvl == 2 else 9)
            })

            # Vincular al padre jerárquico más cercano
            parent = None
            if lvl == 2:
                parent = last_at_level[1]
            elif lvl == 3:
                parent = last_at_level[2] or last_at_level[1]

            if parent:
                links.append({"source": parent, "target": node_id})

            last_at_level[lvl] = node_id
            # Reset sublevels
            for deeper in range(lvl + 1, 4):
                last_at_level[deeper] = None

        return {"nodes": nodes, "links": links}

    @staticmethod
    def calculate_elemental_harmony(md_text: str) -> Dict[str, Any]:
        """Analiza la proporción de los 4 elementos primordiales en el texto."""
        text_lower = md_text.lower()
        scores = {}
        total = 0

        for elem_key, info in ELEMENT_LEXICON.items():
            count = 0
            for kw in info["keywords"]:
                count += len(re.findall(r'\b' + re.escape(kw) + r'\b', text_lower))
            scores[elem_key] = max(1, count)
            total += scores[elem_key]

        proportions = {}
        for elem_key, count in scores.items():
            pct = round((count / total) * 100, 1)
            info = ELEMENT_LEXICON[elem_key]
            proportions[elem_key] = {
                "name": info["name"],
                "icon": info["icon"],
                "color": info["color"],
                "percentage": pct,
                "score": count
            }

        return proportions

    @staticmethod
    def apply_semantic_zoom(md_text: str, zoom_level: str) -> str:
        """
        Destilación semántica no destructiva del Markdown:
        - 'macro': Solo la Semilla Sagrada (filosofía, aforismos, pilares, sin tablas detalladas).
        - 'meso': Las Ramas (encabezados, enfoques y resúmenes semanales).
        - 'micro': El Tejido Completo (todo el texto, tablas y recetas).
        """
        if zoom_level == "micro" or not zoom_level:
            return md_text

        lines = md_text.split("\n")
        filtered_lines = []
        in_table = False

        for line in lines:
            stripped = line.strip()

            # Detectar tablas markdown
            if stripped.startswith("|") and stripped.endswith("|"):
                in_table = True
                if zoom_level == "macro":
                    continue # Ocultar tablas en vista macro
                elif zoom_level == "meso":
                    # En vista meso, mostrar solo los días principales o fila de cabecera
                    if ":---" in stripped or "Día" in stripped:
                        filtered_lines.append(line)
                    elif "**Lunes**" in stripped or "**Domingo**" in stripped:
                        filtered_lines.append(line)
                    continue
            else:
                if in_table and stripped == "":
                    in_table = False

            if zoom_level == "macro":
                # Mantener encabezados, citas, listas y párrafos filosóficos
                if stripped.startswith("#") or stripped.startswith(">") or (stripped and not stripped.startswith("|")):
                    # Si menciona "Semana X:" en macro, solo mostramos el título
                    filtered_lines.append(line)
            elif zoom_level == "meso":
                filtered_lines.append(line)

        return "\n".join(filtered_lines)
