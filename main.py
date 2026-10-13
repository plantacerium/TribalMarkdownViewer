import sys
import os
import json
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QSplitter, QLabel, QFrame,
    QPushButton, QComboBox, QTabWidget, QProgressBar, QTextEdit,
    QDialog, QLineEdit, QMessageBox, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QFont, QColor, QPalette, QIcon, QPixmap
from PySide6.QtWebEngineWidgets import QWebEngineView

from PySide6.QtWebEngineCore import QWebEnginePage

from tribal_engine.state_manager import TribalStateManager
from tribal_engine.circadian import CircadianClock, SEASONS_INFO, CIRCADIAN_PHASES, SPANISH_DAYS
from tribal_engine.alchemy import AlchemyEngine, PORTION_PRESETS
from tribal_engine.fractal import FractalEngine
from tribal_engine.renderer import TribalRenderer

class TribalWebPage(QWebEnginePage):
    """Página WebEngine con puente bidireccional mediante mensajes de consola."""
    def __init__(self, event_callback, parent=None):
        super().__init__(parent)
        self.event_callback = event_callback

    def javaScriptConsoleMessage(self, level, message, line_number, source_id):
        if message.startswith("TRIBAL_EVENT:"):
            try:
                payload = json.loads(message[len("TRIBAL_EVENT:"):])
                self.event_callback(payload)
            except Exception as e:
                print(f"[Bridge Error] {e}")


class TribalViewerApp(QMainWindow):
    def __init__(self, content_folder_name="content"):
        super().__init__()
        self.setWindowTitle("Tribal Markdown Viewer • Sanctuario de Artefactos Inmutables")
        self.resize(1400, 900)

        # Rutas del repositorio
        self.repo_root = os.path.dirname(os.path.abspath(__file__))
        self.content_path = os.path.join(self.repo_root, content_folder_name)
        self.state_file = os.path.join(self.content_path, ".tribal_state.json")

        # Motores
        self.state_manager = TribalStateManager(self.state_file)
        self.renderer = TribalRenderer(self.state_manager)

        self.current_filepath = ""
        self.current_raw_md = ""
        self.last_circadian_phase = ""

        # Icono de la ventana
        icon_path = os.path.join(self.repo_root, "assets", "logo.ico")
        png_path = os.path.join(self.repo_root, "assets", "logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        elif os.path.exists(png_path):
            self.setWindowIcon(QIcon(png_path))

        # Temporizador circadiano y de rituales (1 tick cada segundo)

        self.heartbeat_timer = QTimer(self)
        self.heartbeat_timer.timeout.connect(self.on_heartbeat_tick)
        self.heartbeat_timer.start(1000)


        self.init_ui()
        self.load_file_list()

    def init_ui(self):
        # Estilos QSS Cyber-Tribal: Madera, Piedra y Circuitos Dorados
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0d0c11;
            }
            QWidget {
                color: #e2e8f0;
                font-family: 'Segoe UI', serif;
            }
            QSplitter::handle {
                background-color: #2b2233;
                width: 3px;
            }
            QFrame#header_frame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1a1521, stop:0.5 #261f2f, stop:1 #1a1521);
                border-bottom: 2px solid #b45309;
            }
            QLabel#title_label {
                color: #f59e0b;
                font-weight: bold;
                font-size: 17px;
                letter-spacing: 1px;
            }
            QLabel#manifesto_label {
                color: #a8a29e;
                font-size: 11px;
                font-style: italic;
            }
            QListWidget {
                background-color: #15131c;
                border: 1px solid #362942;
                border-radius: 8px;
                padding: 6px;
                outline: none;
            }
            QListWidget::item {
                padding: 10px 12px;
                border-radius: 6px;
                margin-bottom: 4px;
                color: #cbd5e1;
                border-left: 3px solid transparent;
            }
            QListWidget::item:selected {
                background-color: #2e2338;
                border-left: 3px solid #f59e0b;
                color: #fbbf24;
                font-weight: bold;
            }
            QListWidget::item:hover:!selected {
                background-color: #1e1b29;
                color: #e2e8f0;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2c2236, stop:1 #1d1624);
                border: 1px solid #6b4e2a;
                border-radius: 6px;
                padding: 6px 12px;
                color: #fef08a;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover {
                border-color: #f59e0b;
                background-color: #382946;
            }
            QPushButton:checked {
                background-color: #d97706;
                color: #0f0e13;
                border-color: #fbbf24;
            }
            QComboBox {
                background-color: #1f1b29;
                border: 1px solid #6b4e2a;
                border-radius: 6px;
                padding: 4px 10px;
                color: #fef08a;
                font-size: 12px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QTabWidget::pane {
                border: 1px solid #362942;
                background-color: #15131c;
                border-radius: 6px;
            }
            QTabBar::tab {
                background-color: #1c1824;
                color: #94a3b8;
                padding: 8px 14px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #2b2236;
                color: #f59e0b;
                border-bottom: 2px solid #f59e0b;
                font-weight: bold;
            }
            QProgressBar {
                background-color: #1e1b29;
                border: 1px solid #4a3821;
                border-radius: 4px;
                text-align: center;
                color: #fef08a;
                font-size: 11px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #d97706, stop:1 #f59e0b);
                border-radius: 3px;
            }
            QScrollBar:vertical {
                background: #120f18;
                width: 7px;
                margin: 0;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #473656;
                min-height: 25px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: #f59e0b;
            }
            QScrollBar:horizontal {
                background: #120f18;
                height: 7px;
                margin: 0;
                border-radius: 3px;
            }
            QScrollBar::handle:horizontal {
                background: #473656;
                min-width: 25px;
                border-radius: 3px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #f59e0b;
            }
            QScrollBar::add-line, QScrollBar::sub-line {
                background: none;
                border: none;
            }
        """)


        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Cabecera Cyber-Tribal
        header = self._create_header()
        main_layout.addWidget(header, 0)

        # 2. Barra de Herramientas Alquímicas y Circadianas
        control_bar = self._create_control_bar()
        main_layout.addWidget(control_bar, 0)

        # 3. Cuerpo Principal: Tres Columnas (Archivos + Lector + Rituales/Micelio)
        body = QWidget()
        body.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(6, 6, 6, 6)

        self.splitter = QSplitter(Qt.Horizontal)

        # Columna Izquierda: Explorador de Artefactos + Balance Elemental
        left_pane = self._create_left_pane()
        self.splitter.addWidget(left_pane)

        # Columna Central: Lector WebEngine
        center_pane = self._create_center_pane()
        self.splitter.addWidget(center_pane)

        # Columna Derecha: Cámara de Rituales y Red de Micelio
        right_pane = self._create_right_pane()
        self.splitter.addWidget(right_pane)

        self.splitter.setSizes([260, 880, 290])
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setStretchFactor(2, 0)

        body_layout.addWidget(self.splitter)
        main_layout.addWidget(body, 1)

    def _create_header(self) -> QFrame:
        header = QFrame()
        header.setObjectName("header_frame")
        header.setFixedHeight(58)
        header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(18, 4, 18, 4)

        # Logo Cyber-Tribal
        logo_path = os.path.join(self.repo_root, "assets", "logo.png")
        if os.path.exists(logo_path):
            logo_lbl = QLabel()
            pix = QPixmap(logo_path).scaled(42, 42, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_lbl.setPixmap(pix)
            logo_lbl.setFixedSize(44, 44)
            layout.addWidget(logo_lbl)
            layout.addSpacing(4)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)


        title_label = QLabel("✦ TRIBAL MARKDOWN VIEWER ✦")
        title_label.setObjectName("title_label")

        manifesto_label = QLabel("SANCTUARIO DE ARTEFACTOS INMUTABLES • La Fuente permanece Inmaculada; el Ritual Florece Vivo")
        manifesto_label.setObjectName("manifesto_label")

        title_box.addWidget(title_label)
        title_box.addWidget(manifesto_label)
        layout.addLayout(title_box)

        layout.addStretch()

        # Insignia de Estado Cósmico y Reloj
        self.cosmic_badge = QLabel("Iniciando reloj...")
        self.cosmic_badge.setStyleSheet("""
            background-color: #241c2c;
            border: 1px solid #78350f;
            border-radius: 6px;
            padding: 5px 12px;
            color: #fbbf24;
            font-size: 12px;
            font-weight: 600;
        """)
        layout.addWidget(self.cosmic_badge)

        return header

    def _create_control_bar(self) -> QFrame:
        bar = QFrame()
        bar.setFixedHeight(48)
        bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        bar.setStyleSheet("background-color: #17131e; border-bottom: 1px solid #2b2233; padding: 4px;")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(15, 2, 15, 2)
        layout.setSpacing(14)

        # Toggle: Modo Aquí y Ahora
        self.btn_here_and_now = QPushButton("⚡ Aquí y Ahora: ACTIVO")
        self.btn_here_and_now.setCheckable(True)
        self.btn_here_and_now.setChecked(self.state_manager.state["settings"].get("here_and_now", True))
        self.btn_here_and_now.clicked.connect(self.toggle_here_and_now)
        layout.addWidget(self.btn_here_and_now)

        # Selector: Fase Circadiana & Temas
        layout.addWidget(QLabel("☀️ Ciclo / Tema:"))
        self.combo_circadian = QComboBox()
        self.combo_circadian.addItem("Auto-Solar (Reloj Real)", "auto")
        self.combo_circadian.addItem("🗿 Piedra & Bioluminiscencia", "bioluminescent_stone")
        self.combo_circadian.addItem("🌅 Amanecer Dorado", "sunrise")
        self.combo_circadian.addItem("☀️ Cenit Solar", "zenith")
        self.combo_circadian.addItem("🌇 Atardecer Arcilla", "sunset")
        self.combo_circadian.addItem("🌌 Fuego & Obsidiana", "night")
        current_mode = self.state_manager.state["settings"].get("circadian_mode", "auto")
        idx = self.combo_circadian.findData(current_mode)
        if idx >= 0: self.combo_circadian.setCurrentIndex(idx)
        self.combo_circadian.currentIndexChanged.connect(self.on_circadian_changed)
        layout.addWidget(self.combo_circadian)


        # Selector: Escalado de Porciones
        layout.addWidget(QLabel("👥 Porciones:"))
        self.combo_portions = QComboBox()
        for p in PORTION_PRESETS:
            self.combo_portions.addItem(f"{p['icon']} {p['label']}", p['multiplier'])
        current_mult = self.state_manager.state["settings"].get("portion_multiplier", 1.0)
        for i in range(self.combo_portions.count()):
            if self.combo_portions.itemData(i) == current_mult:
                self.combo_portions.setCurrentIndex(i)
                break
        self.combo_portions.currentIndexChanged.connect(self.on_portion_changed)
        layout.addWidget(self.combo_portions)

        # Selector: Zoom Semántico Fractal
        layout.addWidget(QLabel("🔍 Zoom Fractal:"))
        self.combo_zoom = QComboBox()
        self.combo_zoom.addItem("🌐 Tejido Completo (Micro)", "micro")
        self.combo_zoom.addItem("🌿 Ramas & Enfoques (Meso)", "meso")
        self.combo_zoom.addItem("🧬 Semilla Sagrada (Macro)", "macro")
        current_zoom = self.state_manager.state["settings"].get("semantic_zoom", "micro")
        idx_zoom = self.combo_zoom.findData(current_zoom)
        if idx_zoom >= 0: self.combo_zoom.setCurrentIndex(idx_zoom)
        self.combo_zoom.currentIndexChanged.connect(self.on_zoom_changed)
        layout.addWidget(self.combo_zoom)

        # Selector: Estación Cósmica
        layout.addWidget(QLabel("❄️ Estación:"))
        self.combo_season = QComboBox()
        for k, s in SEASONS_INFO.items():
            self.combo_season.addItem(f"{s['icon']} {s['name']}", k)
        current_season = self.state_manager.state["settings"].get("season", "invierno")
        idx_season = self.combo_season.findData(current_season)
        if idx_season >= 0: self.combo_season.setCurrentIndex(idx_season)
        self.combo_season.currentIndexChanged.connect(self.on_season_changed)
        layout.addWidget(self.combo_season)

        layout.addStretch()

        # Botón Viaje en el Tiempo / Simulación
        btn_time_travel = QPushButton("⏳ Viaje Cíclico")
        btn_time_travel.setToolTip("Simular otro día o momento del plan sin tocar el reloj del PC")
        btn_time_travel.clicked.connect(self.open_time_travel_dialog)
        layout.addWidget(btn_time_travel)

        return bar

    def _create_left_pane(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(10)

        # Título Artefactos
        label_docs = QLabel("📜 ARTEFACTOS INMUTABLES")
        label_docs.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        layout.addWidget(label_docs)

        # Lista de Archivos Markdown
        self.file_list = QListWidget()
        self.file_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.file_list.currentItemChanged.connect(self.on_file_selected)
        layout.addWidget(self.file_list)


        # Balance de los 4 Elementos
        elem_box = QFrame()
        elem_box.setStyleSheet("background-color: #171420; border: 1px solid #362942; border-radius: 8px; padding: 10px;")
        elem_layout = QVBoxLayout(elem_box)
        elem_layout.setContentsMargins(6, 6, 6, 6)
        elem_layout.setSpacing(6)

        elem_title = QLabel("⚖️ ARMONÍA DE LOS 4 ELEMENTOS")
        elem_title.setStyleSheet("color: #f59e0b; font-size: 11px; font-weight: bold; letter-spacing: 0.5px;")
        elem_layout.addWidget(elem_title)

        self.elem_bars = {}
        for k, (name, icon, color) in {
            "fuego": ("Fuego", "🔥", "#ef4444"),
            "tierra": ("Tierra", "🌍", "#d97706"),
            "agua": ("Agua", "💧", "#06b6d4"),
            "eter": ("Éter", "🌀", "#8b5cf6")
        }.items():
            row = QHBoxLayout()
            lbl = QLabel(f"{icon} {name}")
            lbl.setStyleSheet("font-size: 11px;")
            bar = QProgressBar()
            bar.setFixedHeight(12)
            bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {color}; }}")
            row.addWidget(lbl)
            row.addWidget(bar)
            elem_layout.addLayout(row)
            self.elem_bars[k] = bar

        layout.addWidget(elem_box)

        # Resumen de Hábitos Consumados
        self.habits_summary_label = QLabel("Hábitos: 0 consumados")
        self.habits_summary_label.setStyleSheet("color: #a8a29e; font-size: 11px; margin-top: 4px;")
        layout.addWidget(self.habits_summary_label)

        return container

    def _create_center_pane(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        # Vista WebEngine
        self.web_view = QWebEngineView()
        self.custom_page = TribalWebPage(self.handle_web_event, self)
        self.web_view.setPage(self.custom_page)

        layout.addWidget(self.web_view)
        return container

    def _create_right_pane(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)

        tabs = QTabWidget()

        # Tab 1: Cámara de Rituales Activos
        tab_rituals = QWidget()
        rituals_layout = QVBoxLayout(tab_rituals)
        rituals_layout.setContentsMargins(8, 8, 8, 8)

        rituals_header = QLabel("⏱️ RITUALES EN CURSO")
        rituals_header.setStyleSheet("color: #f59e0b; font-weight: bold; font-size: 11px;")
        rituals_layout.addWidget(rituals_header)

        self.rituals_scroll = QScrollArea()
        self.rituals_scroll.setWidgetResizable(True)
        self.rituals_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.rituals_scroll.setStyleSheet("background: transparent; border: none;")
        self.rituals_container = QWidget()
        self.rituals_list_layout = QVBoxLayout(self.rituals_container)
        self.rituals_list_layout.setAlignment(Qt.AlignTop)
        self.rituals_scroll.setWidget(self.rituals_container)
        rituals_layout.addWidget(self.rituals_scroll)

        # Botón para añadir ritual rápido de prueba
        btn_quick_timer = QPushButton("🔥 Añadir Ritual Rápido (30s)")
        btn_quick_timer.clicked.connect(lambda: self.add_manual_ritual("Infusión Reparadora", 30))
        rituals_layout.addWidget(btn_quick_timer)

        tabs.addTab(tab_rituals, "Rituales")

        # Tab 2: Red de Micelio (Árbol Fractal)
        tab_mycelium = QWidget()
        mycelium_layout = QVBoxLayout(tab_mycelium)
        mycelium_layout.setContentsMargins(8, 8, 8, 8)

        mycelium_header = QLabel("🕸️ RED DE MICELIO (ESTRUCTURA)")
        mycelium_header.setStyleSheet("color: #f59e0b; font-weight: bold; font-size: 11px;")
        mycelium_layout.addWidget(mycelium_header)

        self.mycelium_list = QListWidget()
        self.mycelium_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.mycelium_list.itemClicked.connect(self.on_mycelium_item_clicked)
        mycelium_layout.addWidget(self.mycelium_list)

        tabs.addTab(tab_mycelium, "Micelio")

        # Tab 3: Marginalia (Notas al Margen)
        tab_marginalia = QWidget()
        marg_layout = QVBoxLayout(tab_marginalia)
        marg_layout.setContentsMargins(8, 8, 8, 8)

        marg_header = QLabel("✎ NOTAS AL MARGEN (PERGAMINO)")
        marg_header.setStyleSheet("color: #f59e0b; font-weight: bold; font-size: 11px;")
        marg_layout.addWidget(marg_header)

        self.marginalia_list = QListWidget()
        self.marginalia_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        marg_layout.addWidget(self.marginalia_list)


        btn_add_note = QPushButton("✍️ Escribir Nota General")
        btn_add_note.clicked.connect(lambda: self.open_marginalia_dialog("general", "Documento"))
        marg_layout.addWidget(btn_add_note)

        tabs.addTab(tab_marginalia, "Marginalia")

        layout.addWidget(tabs)
        return container

    # --- CARGA Y SELECCIÓN DE ARCHIVOS ---

    def load_file_list(self):
        self.file_list.clear()
        if not os.path.exists(self.content_path):
            os.makedirs(self.content_path, exist_ok=True)
            welcome_file = os.path.join(self.content_path, "Bienvenida_Tribal.md")
            with open(welcome_file, "w", encoding="utf-8") as f:
                f.write("# Bienvenida a la Tribu\n\nAñade tus documentos Markdown aquí.")

        files = sorted([f for f in os.listdir(self.content_path) if f.endswith(('.md', '.markdown'))])
        for f in files:
            full_path = os.path.join(self.content_path, f)
            sha = self.state_manager.compute_file_hash(full_path)
            item = QListWidgetItem(f"📜 {f}")
            item.setToolTip(f"SHA-256: {sha}\nEstado: Artefacto Inmutable")
            item.setData(Qt.UserRole, full_path)
            self.file_list.addItem(item)

        if self.file_list.count() > 0:
            self.file_list.setCurrentRow(0)

    def on_file_selected(self, current, previous):
        if not current: return
        filepath = current.data(Qt.UserRole)
        self.current_filepath = filepath
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                self.current_raw_md = f.read()
            self.refresh_document_view()
            self.update_elemental_harmony()
            self.update_mycelium_tree()
            self.update_marginalia_list()
        except Exception as e:
            QMessageBox.critical(self, "Error de Lectura", f"No se pudo cargar el artefacto: {e}")

    def refresh_document_view(self):
        """Renderiza el documento actual con todas las capas vivas activas."""
        if not self.current_raw_md or not self.current_filepath:
            return
        html = self.renderer.render(self.current_raw_md, self.current_filepath)
        self.web_view.setHtml(html, baseUrl=QUrl.fromLocalFile(self.content_path + "/"))
        self.update_habits_counter()

    # --- GESTIÓN DE EVENTOS DESDE JAVASCRIPT ---

    def handle_web_event(self, data: dict):
        action = data.get("action")
        payload = data.get("payload", {})
        file_hash = data.get("file_hash")

        if action == "toggle_habit":
            item_id = payload.get("item_id")
            if item_id and file_hash:
                self.state_manager.toggle_habit(file_hash, item_id)
                self.update_habits_counter()

        elif action == "start_timer":
            title = payload.get("title", "Ritual Alquímico")
            duration_sec = payload.get("duration_sec", 60)
            self.state_manager.add_timer(title, duration_sec)
            self.render_active_timers()

        elif action == "record_patina":
            section_id = payload.get("section_id")
            dwell_sec = payload.get("dwell_sec", 5)
            if section_id and file_hash:
                self.state_manager.record_patina(file_hash, section_id, dwell_sec)

        elif action == "open_marginalia":
            sec_id = payload.get("section_id")
            sec_title = payload.get("section_title")
            self.open_marginalia_dialog(sec_id, sec_title)

    # --- RITUALES Y TEMPORIZADORES ---

    def on_heartbeat_tick(self):
        """Tick regular: avanza cronómetros y actualiza insignias cósmicas."""
        # 1. Actualizar timers activos
        completed = self.state_manager.update_timers(1)
        if completed:
            for c in completed:
                # Alerta ceremonial
                self.web_view.page().runJavaScript("AudioTribal.playTibetanBowl(432);")
                QMessageBox.information(
                    self, "✦ Ritual Alquímico Culminado ✦",
                    f"El proceso sagrado '{c['title']}' ha concluido su ciclo.\nLa transformación está lista."
                )
        self.render_active_timers()

        # 2. Actualizar indicador cósmico de cabecera
        sim_day = self.state_manager.state["settings"].get("simulated_day", "")
        sim_meal = self.state_manager.state["settings"].get("simulated_meal", "")
        now_info = CircadianClock.get_current_moment(sim_day, sim_meal)
        sim_tag = " [Simulado]" if sim_day else ""
        self.cosmic_badge.setText(
            f"{now_info['day']}{sim_tag} {now_info['time_str']} • "
            f"{now_info['phase_info']['icon']} {now_info['phase_info']['name']} • "
            f"Momento: {now_info['meal']} • "
            f"{now_info['moon_icon']} {now_info['moon_phase']}"
        )

        # 3. Transición en vivo de tema solar si la hora cruzó el umbral circadiano
        if self.state_manager.state["settings"].get("circadian_mode") == "auto":
            current_phase = now_info["circadian_phase"]
            if self.last_circadian_phase and self.last_circadian_phase != current_phase:
                self.last_circadian_phase = current_phase
                self.refresh_document_view()
            else:
                self.last_circadian_phase = current_phase


    def render_active_timers(self):
        # Limpiar contenedor de timers
        while self.rituals_list_layout.count():
            child = self.rituals_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        timers = self.state_manager.state.get("active_timers", [])
        if not timers:
            empty_lbl = QLabel("No hay rituales activos.\nInicia uno desde las recetas o el botón inferior.")
            empty_lbl.setStyleSheet("color: #64748b; font-size: 11px; padding: 10px;")
            self.rituals_list_layout.addWidget(empty_lbl)
            return

        for t in timers:
            item_frame = QFrame()
            item_frame.setStyleSheet("""
                background-color: #1e1927;
                border: 1px solid #78350f;
                border-radius: 6px;
                padding: 6px;
                margin-bottom: 4px;
            """)
            item_layout = QVBoxLayout(item_frame)
            item_layout.setContentsMargins(6, 4, 6, 4)

            top_row = QHBoxLayout()
            title_lbl = QLabel(f"⏱️ {t['title']}")
            title_lbl.setStyleSheet("color: #fbbf24; font-weight: bold; font-size: 11px;")
            top_row.addWidget(title_lbl)

            btn_del = QPushButton("✕")
            btn_del.setFixedSize(20, 20)
            btn_del.setStyleSheet("padding: 0; font-size: 10px; background-color: #3f1d24; border: 1px solid #991b1b;")
            btn_del.clicked.connect(lambda chk, tid=t['id']: self.delete_timer(tid))
            top_row.addWidget(btn_del)
            item_layout.addLayout(top_row)

            # Barra de progreso
            total = max(1, t['total_sec'])
            remain = t['remaining_sec']
            elapsed = total - remain
            pbar = QProgressBar()
            pbar.setFixedHeight(10)
            pbar.setMaximum(total)
            pbar.setValue(elapsed)
            item_layout.addWidget(pbar)

            time_str = AlchemyEngine.format_duration(remain)
            status_lbl = QLabel(f"Restante: {time_str}")
            status_lbl.setStyleSheet("color: #e2e8f0; font-size: 10px;")
            item_layout.addWidget(status_lbl)

            self.rituals_list_layout.addWidget(item_frame)

    def delete_timer(self, timer_id: str):
        self.state_manager.remove_timer(timer_id)
        self.render_active_timers()

    def add_manual_ritual(self, title: str, seconds: int):
        self.state_manager.add_timer(title, seconds)
        self.render_active_timers()

    # --- RED DE MICELIO ---

    def update_mycelium_tree(self):
        self.mycelium_list.clear()
        if not self.current_raw_md: return
        headers = FractalEngine.extract_header_tree(self.current_raw_md)
        for h in headers:
            indent = "  " * (h["level"] - 1)
            icon = "🌿" if h["level"] == 1 else ("🌱" if h["level"] == 2 else "•")
            item = QListWidgetItem(f"{indent}{icon} {h['title']}")
            item.setData(Qt.UserRole, h["id"])
            self.mycelium_list.addItem(item)

    def on_mycelium_item_clicked(self, item):
        section_id = item.data(Qt.UserRole)
        if section_id:
            js = f"document.getElementById('{section_id}')?.scrollIntoView({{behavior: 'smooth', block: 'start'}});"
            self.web_view.page().runJavaScript(js)

    # --- ARMONÍA ELEMENTAL ---

    def update_elemental_harmony(self):
        if not self.current_raw_md: return
        harmony = FractalEngine.calculate_elemental_harmony(self.current_raw_md)
        for k, bar in self.elem_bars.items():
            if k in harmony:
                pct = int(harmony[k]["percentage"])
                bar.setValue(pct)
                bar.setFormat(f"{pct}%")

    # --- MARGINALIA Y NOTAS ---

    def update_marginalia_list(self):
        self.marginalia_list.clear()
        if not self.current_filepath: return
        file_hash = self.state_manager.compute_file_hash(self.current_filepath)
        notes = self.state_manager.get_marginalia(file_hash)
        if not notes:
            item = QListWidgetItem("No hay notas aún en este pergamino.")
            item.setFlags(Qt.NoItemFlags)
            self.marginalia_list.addItem(item)
            return

        for n in notes:
            item = QListWidgetItem(f"✎ [{n.get('timestamp')}]\n{n.get('text')}")
            item.setData(Qt.UserRole, n.get("id"))
            self.marginalia_list.addItem(item)

    def open_marginalia_dialog(self, section_id: str, section_title: str):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Marginalia Sagrada • {section_title}")
        dialog.setMinimumWidth(400)
        d_layout = QVBoxLayout(dialog)

        d_layout.addWidget(QLabel(f"Anotación al margen para: <strong>{section_title}</strong>"))
        text_edit = QTextEdit()
        text_edit.setPlaceholderText("Escribe tu reflexión, ajuste de ingredientes o medicina intuitiva...")
        text_edit.setStyleSheet("background-color: #17131e; color: #fef08a; border: 1px solid #78350f; border-radius: 6px;")
        d_layout.addWidget(text_edit)

        btn_box = QHBoxLayout()
        btn_save = QPushButton("Guardar en el Pergamino")
        btn_save.clicked.connect(dialog.accept)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(dialog.reject)
        btn_box.addWidget(btn_save)
        btn_box.addWidget(btn_cancel)
        d_layout.addLayout(btn_box)

        if dialog.exec() == QDialog.Accepted:
            note_content = text_edit.toPlainText().strip()
            if note_content and self.current_filepath:
                file_hash = self.state_manager.compute_file_hash(self.current_filepath)
                self.state_manager.add_marginalia(file_hash, section_id, note_content)
                self.update_marginalia_list()
                self.refresh_document_view()

    # --- CONTROLES DE LA BARRA ALQUÍMICA ---

    def toggle_here_and_now(self):
        active = self.btn_here_and_now.isChecked()
        self.state_manager.state["settings"]["here_and_now"] = active
        self.btn_here_and_now.setText("⚡ Aquí y Ahora: ACTIVO" if active else "⚡ Aquí y Ahora: Reposo")
        self.state_manager.save()
        self.refresh_document_view()

    def on_circadian_changed(self):
        mode = self.combo_circadian.currentData()
        self.state_manager.state["settings"]["circadian_mode"] = mode
        self.state_manager.save()
        self.refresh_document_view()

    def on_portion_changed(self):
        mult = self.combo_portions.currentData()
        label = self.combo_portions.currentText()
        self.state_manager.state["settings"]["portion_multiplier"] = mult
        self.state_manager.state["settings"]["portion_label"] = label
        self.state_manager.save()
        self.refresh_document_view()

    def on_zoom_changed(self):
        zoom = self.combo_zoom.currentData()
        self.state_manager.state["settings"]["semantic_zoom"] = zoom
        self.state_manager.save()
        self.refresh_document_view()

    def on_season_changed(self):
        season = self.combo_season.currentData()
        self.state_manager.state["settings"]["season"] = season
        self.state_manager.save()
        self.refresh_document_view()

    def update_habits_counter(self):
        if not self.current_filepath: return
        file_hash = self.state_manager.compute_file_hash(self.current_filepath)
        habits = self.state_manager.state.get("habits", {}).get(file_hash, {})
        completed = sum(1 for v in habits.values() if v)
        self.habits_summary_label.setText(f"Rituales Consumados: {completed} sellos")

    def open_time_travel_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Viaje Cíclico • Simulación de Tiempo")
        dialog.setMinimumWidth(320)
        d_layout = QVBoxLayout(dialog)

        d_layout.addWidget(QLabel("Simular día de la semana:"))
        combo_day = QComboBox()
        combo_day.addItem("Tiempo Real (Hoy)", "")
        for d in SPANISH_DAYS:
            combo_day.addItem(d, d)
        current_sim_day = self.state_manager.state["settings"].get("simulated_day", "")
        idx = combo_day.findData(current_sim_day)
        if idx >= 0: combo_day.setCurrentIndex(idx)
        d_layout.addWidget(combo_day)

        d_layout.addWidget(QLabel("Simular momento de comida:"))
        combo_meal = QComboBox()
        combo_meal.addItem("Tiempo Real (Automático)", "")
        combo_meal.addItem("Desayuno", "Desayuno")
        combo_meal.addItem("Almuerzo (Comida Fuerte)", "Almuerzo")
        combo_meal.addItem("Cena (Ligera y Reparadora)", "Cena")
        combo_meal.addItem("Bebida Medicina", "Bebida Medicina")
        current_sim_meal = self.state_manager.state["settings"].get("simulated_meal", "")
        idx_m = combo_meal.findData(current_sim_meal)
        if idx_m >= 0: combo_meal.setCurrentIndex(idx_m)
        d_layout.addWidget(combo_meal)

        btn_box = QHBoxLayout()
        btn_apply = QPushButton("Aplicar Alineación")
        btn_apply.clicked.connect(dialog.accept)
        btn_reset = QPushButton("Reset a Tiempo Real")
        btn_reset.clicked.connect(lambda: (combo_day.setCurrentIndex(0), combo_meal.setCurrentIndex(0), dialog.accept()))
        btn_box.addWidget(btn_apply)
        btn_box.addWidget(btn_reset)
        d_layout.addLayout(btn_box)

        if dialog.exec() == QDialog.Accepted:
            self.state_manager.state["settings"]["simulated_day"] = combo_day.currentData()
            self.state_manager.state["settings"]["simulated_meal"] = combo_meal.currentData()
            self.state_manager.save()
            self.refresh_document_view()


if __name__ == "__main__":
    # Identificador explícito para la barra de tareas de Windows
    import ctypes
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("plantacerium.tribalmarkdown.viewer.2.0")
    except Exception:
        pass

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    ico_path = os.path.join(base_dir, "assets", "logo.ico")
    png_path = os.path.join(base_dir, "assets", "logo.png")
    if os.path.exists(ico_path):
        app.setWindowIcon(QIcon(ico_path))
    elif os.path.exists(png_path):
        app.setWindowIcon(QIcon(png_path))

    font = QFont("Cinzel", 10)
    if not font.exactMatch():
        font = QFont("Georgia", 10)
    app.setFont(font)

    viewer = TribalViewerApp()
    viewer.show()
    sys.exit(app.exec())

