import os
import re
import json
import markdown
from typing import Dict, Any, List
from .state_manager import TribalStateManager
from .circadian import CircadianClock, SEASONS_INFO
from .alchemy import AlchemyEngine, TIME_PATTERNS
from .fractal import FractalEngine
from .themes import generate_theme_css

class TribalRenderer:
    """
    Renderizador Alquímico: fusiona el artefacto inmutable de Markdown
    con la reactividad viva circadiana, el escalado somático y la pátina del tiempo.
    """

    def __init__(self, state_manager: TribalStateManager):
        self.state_manager = state_manager

    def render(self, md_text: str, filepath: str) -> str:
        file_hash = self.state_manager.compute_file_hash(filepath)
        filename = os.path.basename(filepath)
        settings = self.state_manager.state.get("settings", {})

        # 1. Configuración activa
        circadian_mode = settings.get("circadian_mode", "auto")
        here_and_now = settings.get("here_and_now", True)
        sim_day = settings.get("simulated_day", "")
        sim_meal = settings.get("simulated_meal", "")
        portion_mult = settings.get("portion_multiplier", 1.0)
        season_key = settings.get("season", "invierno")
        zoom_level = settings.get("semantic_zoom", "micro")

        # 2. Información del momento
        now_info = CircadianClock.get_current_moment(sim_day, sim_meal)
        current_day = now_info["day"]
        current_meal = now_info["meal"]
        phase_key = now_info["circadian_phase"] if circadian_mode == "auto" else circadian_mode

        # 3. Zoom Semántico en Markdown
        zoomed_md = FractalEngine.apply_semantic_zoom(md_text, zoom_level)

        # 4. Escalado de porciones previo a conversión HTML
        if portion_mult != 1.0:
            zoomed_md = AlchemyEngine.scale_quantities_in_text(zoomed_md, portion_mult)

        # 5. Conversión base a HTML
        raw_html = markdown.markdown(
            zoomed_md,
            extensions=['extra', 'tables', 'fenced_code']
        )

        # 6. Enriquecimiento Alquímico y Reactivo del HTML
        enriched_html = self._enrich_html(
            raw_html, file_hash, current_day, current_meal,
            here_and_now, season_key, portion_mult
        )

        # 7. CSS y Paleta
        css = generate_theme_css(phase_key)

        # 8. Sello de Inmutabilidad Sagrada
        season_info = SEASONS_INFO.get(season_key, SEASONS_INFO["invierno"])
        seal_html = f"""
        <div class="immutable-seal-badge">
            <div>
                <span class="seal-icon">🛡️</span>
                <strong>Artefacto Inmutable:</strong> {filename}
                <span style="opacity: 0.7; margin-left: 10px;">(SHA-256: {file_hash[:12]}... Pura e Intacta)</span>
            </div>
            <div>
                <span>{season_info['icon']} Estación: {season_info['name']}</span>
                <span style="margin-left: 12px;">{now_info['moon_icon']} {now_info['moon_phase']}</span>
                <span style="margin-left: 12px; font-weight: bold; color: var(--circuit-gold);">
                    Porciones: {settings.get('portion_label', '2 Pareja')} (x{portion_mult})
                </span>
            </div>
        </div>
        """

        # 9. Script interactivo y puente con Web Audio API
        js_runtime = self._generate_client_script(file_hash, current_day, current_meal, here_and_now)

        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <title>{filename}</title>
    <style>{css}</style>
</head>
<body>
    {seal_html}
    <div id="tribal-content">
        {enriched_html}
    </div>
    {js_runtime}
</body>
</html>"""

    def _enrich_html(
        self, html: str, file_hash: str, current_day: str,
        current_meal: str, here_and_now: bool, season_key: str, portion_mult: float
    ) -> str:
        """Modifica el DOM generado para inyectar interactividad somática y biológica."""
        season_kws = SEASONS_INFO.get(season_key, {}).get("keywords", [])

        # Resaltado Estacional de palabras clave (exclusivamente fuera de etiquetas HTML)
        for kw in season_kws:
            pattern = re.compile(rf'\b({re.escape(kw)})\b(?![^<]*>)', re.IGNORECASE)
            html = pattern.sub(r'<span class="seasonal-highlight" title="Alimento afín con la estación">\1</span>', html)

        # Transformar tiempos de cocción en botones de ritual (exclusivamente fuera de etiquetas HTML)
        for pat, calc_sec, label_tmpl in TIME_PATTERNS:
            def timer_replacer(m):
                sec = calc_sec(m)
                val = m.group(1) if m.groups() else ""
                label = label_tmpl.format(val=val)
                safe_title = f"Cocción: {label}"
                return f'<button class="ritual-timer-btn" onclick="triggerTimer(\'{safe_title}\', {sec})">⏱️ {label} • Iniciar</button>'

            pattern = re.compile(rf'{pat}(?![^<]*>)', re.IGNORECASE)
            html = pattern.sub(timer_replacer, html)

        # Procesamiento de Filas de Tablas (Aquí y Ahora + Hábitos)
        def row_processor(match):
            row_html = match.group(0)
            is_header = "<th>" in row_html

            if is_header:
                return row_html

            # Verificar si la fila corresponde a un día de la semana
            row_day = None
            for d in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]:
                if f"<strong>{d}</strong>" in row_html or f"**{d}**" in row_html or f">{d}<" in row_html:
                    row_day = d
                    break

            classes = ["tribal-row"]
            if row_day:
                classes.append(f"day-{row_day.lower()}")
                if here_and_now:
                    if row_day == current_day:
                        classes.append("here-and-now-active")
                    else:
                        classes.append("here-and-now-dimmed")

            # Inyectar sellos rúnicos de hábitos en cada celda td
            def cell_processor(td_match):
                td_content = td_match.group(1)
                # Si es celda de día (primera columna), no añadir habit seal
                if any(f"<strong>{d}</strong>" in td_content for d in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]):
                    return f"<td>{td_content}</td>"

                # Generar item_id determinista a partir del texto de la celda
                clean_text = re.sub(r'<[^>]+>', '', td_content).strip()
                if len(clean_text) < 4:
                    return f"<td>{td_content}</td>"

                item_id = f"item_{abs(hash(clean_text)) % 1000000}"
                is_done = self.state_manager.is_habit_completed(file_hash, item_id)
                icon = "☀️" if is_done else "⭕"
                done_class = "habit-completed" if is_done else ""

                seal = f'<span class="habit-check-seal" onclick="toggleHabit(\'{item_id}\')" title="Marcar como ritual consumado">{icon}</span>'
                return f'<td class="{done_class}">{seal}{td_content}</td>'

            processed_cells = re.sub(r'<td>(.*?)</td>', cell_processor, row_html, flags=re.DOTALL)
            class_str = " ".join(classes)
            return f'<tr class="{class_str}">{processed_cells[4:]}'

        html = re.sub(r'<tr>(.*?)</tr>', row_processor, html, flags=re.DOTALL)

        # Enriquecer encabezados con IDs para red de micelio y pátina
        h_pattern = re.compile(r'<(h[1-3])(?:\s+[^>]*)?>(.*?)</\1>', re.DOTALL)
        h_idx = 0
        def header_processor(m):
            nonlocal h_idx
            tag = m.group(1)
            inner = m.group(2)
            clean_title = re.sub(r'<[^>]+>', '', inner).strip()
            slug = f"sec-{h_idx}-{FractalEngine.slugify(clean_title)}"
            h_idx += 1


            patina_level = self.state_manager.get_patina_level(file_hash, slug)
            consecrated_badge = '<span class="consecrated-tag" title="Sección consagrada por uso frecuente">✦ Consagrada</span>' if patina_level > 0.6 else ''

            patina_class = "patina-gold" if patina_level > 0.3 else ""
            marginalia_btn = f'<span class="marginalia-marker" onclick="openMarginalia(\'{slug}\', \'{clean_title}\')" title="Añadir nota al margen">✎</span>'

            return f'<{tag} id="{slug}" class="{patina_class}">{inner} {consecrated_badge} {marginalia_btn}</{tag}>'

        html = h_pattern.sub(header_processor, html)

        return html

    def _generate_client_script(self, file_hash: str, current_day: str, current_meal: str, here_and_now: bool) -> str:
        """Código JavaScript embebido para interactividad, audio ceremonial y puente con PySide6."""
        return f"""
<script>
// --- MOTOR DE SONIDO CEREMONIAL (Web Audio API) ---
// Sintetizador procedural de cuencos tibetanos y gongs sin archivos externos
const AudioTribal = {{
    ctx: null,
    init: function() {{
        if (!this.ctx) {{
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            if (AudioCtx) this.ctx = new AudioCtx();
        }}
    }},
    playTibetanBowl: function(baseFreq = 432) {{
        try {{
            this.init();
            if (!this.ctx) return;
            const now = this.ctx.currentTime;
            
            // Frecuencias armónicas sagradas: Fundamental 432Hz, 3ª y 5ª
            const freqs = [baseFreq, baseFreq * 1.5, baseFreq * 2.01, baseFreq * 2.76];
            const gains = [0.4, 0.25, 0.15, 0.08];

            freqs.forEach((f, idx) => {{
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();
                osc.type = "sine";
                osc.frequency.setValueAtTime(f, now);
                
                // Golpe suave y larga resonancia reverberante
                gain.gain.setValueAtTime(0, now);
                gain.gain.linearRampToValueAtTime(gains[idx], now + 0.05);
                gain.gain.exponentialRampToValueAtTime(0.0001, now + 3.2);

                osc.connect(gain);
                gain.connect(this.ctx.destination);
                osc.start(now);
                osc.stop(now + 3.3);
            }});
        }} catch(e) {{
            console.error("Audio error:", e);
        }}
    }}
}};

// --- PUENTE CON PYSIDE6 ---
function sendToPython(action, payload = {{}}) {{
    const eventData = {{
        action: action,
        file_hash: "{file_hash}",
        payload: payload,
        timestamp: new Date().toISOString()
    }};
    console.log("TRIBAL_EVENT:" + JSON.stringify(eventData));
}}

// Marcar / desmarcar hábito rúnico
function toggleHabit(itemId) {{
    AudioTribal.playTibetanBowl(528); // 528Hz: Frecuencia de transformación
    sendToPython("toggle_habit", {{ item_id: itemId }});
}}

// Iniciar ritual de cocción
function triggerTimer(title, seconds) {{
    AudioTribal.playTibetanBowl(432); // 432Hz: Frecuencia de enraizamiento
    sendToPython("start_timer", {{ title: title, duration_sec: seconds }});
}}

// Abrir diálogo de nota al margen
function openMarginalia(sectionId, sectionTitle) {{
    sendToPython("open_marginalia", {{ section_id: sectionId, section_title: sectionTitle }});
}}

// Notificar visualización para cálculo de pátina
let dwellTimer = null;
window.addEventListener("scroll", () => {{
    clearTimeout(dwellTimer);
    dwellTimer = setTimeout(() => {{
        const headers = document.querySelectorAll("h1, h2, h3");
        for (let h of headers) {{
            const rect = h.getBoundingClientRect();
            if (rect.top >= 0 && rect.top <= window.innerHeight * 0.4) {{
                sendToPython("record_patina", {{ section_id: h.id, dwell_sec: 5 }});
                break;
            }}
        }}
    }}, 2000);
}});

// Primer golpe de pátina al cargar
setTimeout(() => {{
    const firstH = document.querySelector("h1, h2");
    if (firstH) {{
        sendToPython("record_patina", {{ section_id: firstH.id, dwell_sec: 3 }});
    }}
}}, 3000);
</script>
"""
