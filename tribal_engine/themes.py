"""
Cyber-Tribal Styling & Visual System
Materialidad: Madera Noble, Piedra Rúnica, Circuitos de Oro y Cobre.
"""

# Circuito decorativo SVG codificado en base64 para fondos de textura
CIRCUIT_SVG_PATTERN = """data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 120 120" opacity="0.05"><path d="M10 10 h40 v40 h-40 z M50 30 h30 v60 h-30 M80 50 h30 v30 h-30" fill="none" stroke="%23f59e0b" stroke-width="1.5"/><circle cx="10" cy="10" r="3" fill="%23f59e0b"/><circle cx="50" cy="50" r="3" fill="%23f59e0b"/><circle cx="80" cy="90" r="3" fill="%23f59e0b"/><circle cx="110" cy="80" r="3" fill="%23f59e0b"/></svg>"""

STONE_CIRCUIT_SVG_PATTERN = """data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="140" height="140" viewBox="0 0 140 140" opacity="0.08"><path d="M15 15 h35 v35 h-35 z M50 25 h40 v70 h-40 M90 50 h35 v35 h-35 M30 90 h40 v35 h-40" fill="none" stroke="%2300f5d4" stroke-width="1.8"/><circle cx="15" cy="15" r="3.5" fill="%2300f5d4"/><circle cx="50" cy="95" r="3.5" fill="%2300f5d4"/><circle cx="90" cy="50" r="3.5" fill="%2300f5d4"/><circle cx="125" cy="85" r="3.5" fill="%2300f5d4"/><path d="M0 70 h20 M120 70 h20 M70 0 v20 M70 120 v20" stroke="%2300f5d4" stroke-width="1" stroke-dasharray="2,3"/></svg>"""

THEME_PALETTES = {
    "bioluminescent_stone": {
        "name": "🗿 Piedra Rúnica Bioluminiscente",
        "bg_main": "#070c10",
        "bg_card": "#0d161d",
        "bg_sidebar": "#05080c",
        "border": "#15333d",
        "text_primary": "#e0fbfc",
        "text_secondary": "#7cd5d9",
        "text_accent": "#00f5d4",
        "circuit_gold": "#00e5ff",
        "circuit_glow": "rgba(0, 245, 212, 0.7)",
        "table_header": "#11222c",
        "table_border": "#183642",
        "highlight_row": "#092930",
        "is_bioluminescent": True
    },
    "sunrise": {
        "name": "🌅 Amanecer Dorado (Aurora)",
        "bg_main": "#fdfbf7",
        "bg_card": "#f8f3ea",
        "bg_sidebar": "#efe6d5",
        "border": "#e2ceb1",
        "text_primary": "#3d3224",
        "text_secondary": "#78644e",
        "text_accent": "#b45309",
        "circuit_gold": "#d97706",
        "circuit_glow": "rgba(217, 119, 6, 0.4)",
        "table_header": "#ebdcc4",
        "table_border": "#e4d3b8",
        "highlight_row": "#fef3c7"
    },
    "zenith": {
        "name": "☀️ Cenit Solar (Piedra & Cobre)",
        "bg_main": "#f3f4f6",
        "bg_card": "#ffffff",
        "bg_sidebar": "#e5e7eb",
        "border": "#cbd5e1",
        "text_primary": "#1e293b",
        "text_secondary": "#475569",
        "text_accent": "#0284c7",
        "circuit_gold": "#f59e0b",
        "circuit_glow": "rgba(245, 158, 11, 0.45)",
        "table_header": "#f1f5f9",
        "table_border": "#cbd5e1",
        "highlight_row": "#e0f2fe"
    },
    "sunset": {
        "name": "🌇 Atardecer de Arcilla (Terracota)",
        "bg_main": "#261c18",
        "bg_card": "#33241f",
        "bg_sidebar": "#1f1512",
        "border": "#5c3d31",
        "text_primary": "#fed7aa",
        "text_secondary": "#ca8a04",
        "text_accent": "#fb923c",
        "circuit_gold": "#f97316",
        "circuit_glow": "rgba(249, 115, 22, 0.5)",
        "table_header": "#432b22",
        "table_border": "#5c3d31",
        "highlight_row": "#4a2d21"
    },
    "night": {
        "name": "🌌 Fuego Sagrado & Obsidiana (Noche)",
        "bg_main": "#0f0e13",
        "bg_card": "#17161f",
        "bg_sidebar": "#0b0a0e",
        "border": "#312a3d",
        "text_primary": "#fef08a",
        "text_secondary": "#a8a29e",
        "text_accent": "#fbbf24",
        "circuit_gold": "#f59e0b",
        "circuit_glow": "rgba(245, 158, 11, 0.6)",
        "table_header": "#221f2d",
        "table_border": "#383147",
        "highlight_row": "#2e2316"
    }
}

def generate_theme_css(phase_key: str = "night") -> str:
    palette = THEME_PALETTES.get(phase_key, THEME_PALETTES["night"])
    is_bio = palette.get("is_bioluminescent", False)
    bg_pattern = STONE_CIRCUIT_SVG_PATTERN if is_bio else CIRCUIT_SVG_PATTERN

    bio_glow_rules = ""
    if is_bio:
        bio_glow_rules = """
        body {
            text-shadow: 0 0 2px rgba(0, 245, 212, 0.35);
        }
        h1 {
            text-shadow: 0 0 8px #00f5d4, 0 0 20px rgba(0, 245, 212, 0.75), 0 0 35px rgba(0, 229, 255, 0.4) !important;
        }
        h2 {
            text-shadow: 0 0 6px #00f5d4, 0 0 15px rgba(0, 245, 212, 0.6) !important;
        }
        h3 {
            text-shadow: 0 0 5px #00e5ff, 0 0 12px rgba(0, 229, 255, 0.5) !important;
        }
        p, td {
            text-shadow: 0 0 2px rgba(0, 245, 212, 0.3);
        }
        """

    return f"""
    :root {{
        --bg-main: {palette['bg_main']};
        --bg-card: {palette['bg_card']};
        --bg-sidebar: {palette['bg_sidebar']};
        --border-color: {palette['border']};
        --text-primary: {palette['text_primary']};
        --text-secondary: {palette['text_secondary']};
        --text-accent: {palette['text_accent']};
        --circuit-gold: {palette['circuit_gold']};
        --circuit-glow: {palette['circuit_glow']};
        --table-header: {palette['table_header']};
        --table-border: {palette['table_border']};
        --highlight-row: {palette['highlight_row']};
    }}

    * {{
        box-sizing: border-box;
    }}

    body {{
        font-family: 'Cinzel', 'Trajan Pro', 'Palatino Linotype', 'Book Antiqua', Georgia, serif;
        background-color: var(--bg-main);
        background-image: url('{bg_pattern}');
        color: var(--text-primary);
        line-height: 1.85;
        margin: 0 auto;
        padding: 25px 35px 80px 35px;
        max-width: 1080px;
        width: 100%;
        transition: background-color 0.4s ease, color 0.4s ease;
    }}

    {bio_glow_rules}


    /* Inmutabilidad Header Badge */
    .immutable-seal-badge {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(180, 83, 9, 0.05));
        border: 1px solid var(--circuit-gold);
        border-radius: 8px;
        padding: 10px 18px;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2), inset 0 0 10px var(--circuit-glow);
        font-size: 0.85rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--text-accent);
    }}
    .immutable-seal-badge .seal-icon {{
        font-size: 1.2rem;
        margin-right: 8px;
    }}

    /* Títulos con estética Cyber-Tribal de piedra tallada y circuitos */
    h1 {{
        color: var(--circuit-gold);
        font-size: 2.1rem;
        letter-spacing: 0.05em;
        border-bottom: 2px solid var(--border-color);
        padding-bottom: 15px;
        margin-top: 10px;
        margin-bottom: 25px;
        text-shadow: 0 2px 10px var(--circuit-glow);
        position: relative;
    }}
    h1::after {{
        content: "◆ ❖ ◆";
        position: absolute;
        bottom: -11px;
        right: 20px;
        background-color: var(--bg-main);
        padding: 0 10px;
        color: var(--circuit-gold);
        font-size: 0.8rem;
    }}

    h2 {{
        color: var(--text-accent);
        font-size: 1.5rem;
        margin-top: 40px;
        margin-bottom: 18px;
        border-left: 5px solid var(--circuit-gold);
        padding-left: 15px;
        letter-spacing: 0.03em;
        background: linear-gradient(90deg, rgba(245, 158, 11, 0.08), transparent);
        padding-top: 6px;
        padding-bottom: 6px;
        border-radius: 0 6px 6px 0;
    }}

    h3 {{
        color: var(--circuit-gold);
        font-size: 1.2rem;
        margin-top: 25px;
        margin-bottom: 12px;
        letter-spacing: 0.02em;
    }}

    p {{
        margin-bottom: 18px;
        font-size: 1.02rem;
        color: var(--text-primary);
    }}

    blockquote {{
        margin: 25px 0;
        padding: 16px 24px;
        background-color: var(--bg-card);
        border-left: 4px solid var(--circuit-gold);
        border-radius: 0 8px 8px 0;
        color: var(--text-secondary);
        font-style: italic;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        position: relative;
    }}
    blockquote::before {{
        content: "«";
        font-size: 2.5rem;
        color: var(--circuit-gold);
        opacity: 0.3;
        position: absolute;
        left: 8px;
        top: -8px;
    }}

    /* Tablas de la Tribu */
    table {{
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        margin: 30px 0;
        background-color: var(--bg-card);
        border: 1px solid var(--table-border);
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }}

    th {{
        background-color: var(--table-header);
        color: var(--circuit-gold);
        padding: 14px 16px;
        text-align: left;
        font-weight: 700;
        font-size: 0.95rem;
        letter-spacing: 0.04em;
        border-bottom: 2px solid var(--border-color);
        text-transform: uppercase;
    }}

    td {{
        padding: 14px 16px;
        border-bottom: 1px solid var(--table-border);
        color: var(--text-primary);
        font-size: 0.96rem;
        vertical-align: top;
        transition: background-color 0.3s ease;
    }}

    tr:last-child td {{
        border-bottom: none;
    }}

    tr:hover td {{
        background-color: rgba(245, 158, 11, 0.04);
    }}

    /* Pulso Viviente: Modo Aquí y Ahora */
    .here-and-now-active {{
        background-color: var(--highlight-row) !important;
        position: relative;
        animation: circuitPulse 2.8s infinite ease-in-out;
        border: 2px solid var(--circuit-gold) !important;
    }}

    .here-and-now-active td {{
        color: var(--text-primary) !important;
        font-weight: 600;
    }}

    .here-and-now-dimmed {{
        opacity: 0.38;
        filter: grayscale(40%);
        transition: opacity 0.5s ease, filter 0.5s ease;
    }}
    .here-and-now-dimmed:hover {{
        opacity: 0.85;
        filter: grayscale(0%);
    }}

    @keyframes circuitPulse {{
        0% {{
            box-shadow: 0 0 8px var(--circuit-glow), inset 0 0 12px rgba(245, 158, 11, 0.1);
        }}
        50% {{
            box-shadow: 0 0 25px var(--circuit-glow), inset 0 0 25px rgba(245, 158, 11, 0.25);
        }}
        100% {{
            box-shadow: 0 0 8px var(--circuit-glow), inset 0 0 12px rgba(245, 158, 11, 0.1);
        }}
    }}

    /* Botones de Ritual Alquímico (Cronómetros de Cocción) */
    .ritual-timer-btn {{
        display: inline-flex;
        align-items: center;
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(180, 83, 9, 0.3));
        border: 1px solid var(--circuit-gold);
        color: var(--text-accent);
        padding: 3px 8px;
        margin: 2px 4px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-family: inherit;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.25s ease;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    }}
    .ritual-timer-btn:hover {{
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.4), rgba(180, 83, 9, 0.5));
        transform: translateY(-1px);
        box-shadow: 0 0 10px var(--circuit-glow);
    }}

    /* Checklists de Hábitos y Fermentación */
    .habit-check-seal {{
        cursor: pointer;
        font-size: 1.1rem;
        margin-right: 6px;
        user-select: none;
        transition: transform 0.2s ease;
        display: inline-block;
    }}
    .habit-check-seal:hover {{
        transform: scale(1.25);
    }}
    .habit-completed {{
        text-decoration: line-through;
        opacity: 0.65;
        color: var(--text-secondary);
    }}

    /* Escalado de Porciones */
    .scaled-quantity {{
        color: var(--circuit-gold);
        font-weight: 700;
        border-bottom: 1px dotted var(--circuit-gold);
        padding: 0 2px;
    }}

    /* Resaltado Estacional */
    .seasonal-highlight {{
        background: linear-gradient(120deg, rgba(56, 189, 248, 0.15), rgba(14, 165, 233, 0.05));
        border-bottom: 2px solid #38bdf8;
        padding: 1px 4px;
        border-radius: 3px;
        font-weight: 600;
    }}

    /* Pátina del Tiempo (Heatmap de Desgaste Noble) */
    .patina-gold {{
        position: relative;
    }}
    .patina-gold::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        pointer-events: none;
        background: radial-gradient(circle at 95% 5%, rgba(245, 158, 11, 0.15), transparent 60%);
        border-radius: 8px;
    }}
    .consecrated-tag {{
        display: inline-block;
        background-color: var(--circuit-gold);
        color: #111827;
        font-size: 0.68rem;
        font-weight: 800;
        padding: 2px 7px;
        border-radius: 12px;
        text-transform: uppercase;
        margin-left: 8px;
        vertical-align: middle;
        letter-spacing: 0.05em;
    }}

    /* Marginalia Anotaciones */
    .marginalia-marker {{
        cursor: pointer;
        color: var(--circuit-gold);
        margin-left: 6px;
        font-size: 0.9rem;
        opacity: 0.8;
        transition: opacity 0.2s ease, transform 0.2s ease;
    }}
    .marginalia-marker:hover {{
        opacity: 1;
        transform: scale(1.3);
    }}

    /* Scrollbar Rúnico */
    ::-webkit-scrollbar {{
        width: 10px;
        height: 10px;
    }}
    ::-webkit-scrollbar-track {{
        background: var(--bg-sidebar);
    }}
    ::-webkit-scrollbar-thumb {{
        background: var(--border-color);
        border: 2px solid var(--bg-sidebar);
        border-radius: 5px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: var(--circuit-gold);
    }}
    """
