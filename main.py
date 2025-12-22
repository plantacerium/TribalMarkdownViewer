import sys
import os
import re
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QListWidget, QListWidgetItem, QSplitter, QTextBrowser, QLabel,
    QFrame
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QDesktopServices, QFont, QPalette, QColor
import markdown

# --- PREMIUM CSS THEMES ---
# Using a refined palette and modern typography
CSS_BASE = """
    body {
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        line-height: 1.8;
        padding: 40px;
        color: #2c3e50;
        background-color: #ffffff;
    }
    h1 { color: #1a2a6c; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-top: 0; }
    h2 { color: #b21f1f; margin-top: 30px; border-left: 5px solid #b21f1f; padding-left: 15px; }
    h3 { color: #fdbb2d; margin-top: 25px; }
    p { margin-bottom: 15px; }
    a { color: #3498db; text-decoration: none; font-weight: 500; }
    a:hover { text-decoration: underline; color: #2980b9; }
    code { 
        background-color: #f8f9fa; 
        padding: 3px 6px; 
        border-radius: 4px; 
        font-family: 'Cascadia Code', 'Consolas', monospace;
        color: #e83e8c;
        font-size: 0.9em;
    }
    pre {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        font-family: 'Cascadia Code', 'Consolas', monospace;
        line-height: 1.5;
        overflow-x: auto;
    }
    blockquote {
        margin: 20px 0;
        padding: 10px 20px;
        background-color: #fff9db;
        border-left: 6px solid #fcc419;
        color: #5c5f66;
        font-style: italic;
    }
    img { 
        max-width: 100%; 
        height: auto; 
        border-radius: 12px; 
        margin: 25px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 20px 0;
    }
    th, td {
        border: 1px solid #dee2e6;
        padding: 12px;
        text-align: left;
    }
    th { background-color: #f1f3f5; font-weight: 600; }
"""

CSS_DARK = """
    body { background-color: #0f172a; color: #e2e8f0; }
    h1 { color: #38bdf8; border-bottom: 2px solid #1e293b; }
    h2 { color: #fb7185; border-left: 5px solid #fb7185; }
    h3 { color: #fbbf24; }
    p { color: #94a3b8; }
    a { color: #0ea5e9; }
    a:hover { color: #38bdf8; }
    code { background-color: #1e293b; color: #f472b6; }
    pre { background-color: #1e293b; border: 1px solid #334155; color: #cbd5e1; }
    blockquote { background-color: #1e293b; border-left: 6px solid #38bdf8; color: #94a3b8; }
    th { background-color: #1e293b; color: #f1f5f9; }
    td { border: 1px solid #334155; }
    th { border: 1px solid #334155; }
"""

THEMES = {
    "✨ Crystal White": CSS_BASE,
    "🌌 Deep Space": CSS_DARK
}

class MarkdownViewerApp(QMainWindow):
    def __init__(self, content_folder_name="content"):
        super().__init__()
        self.setWindowTitle("Tribal Markdown Viewer")
        self.resize(1200, 850)

        # Path Setup
        self.repo_root = os.path.dirname(os.path.abspath(__file__))
        self.content_path = os.path.join(self.repo_root, content_folder_name)
        self.current_theme = "✨ Crystal White"
        self.current_file_dir = ""

        self.init_ui()
        self.check_content_folder()
        self.load_file_list()

    def init_ui(self):
        # Apply Global Style
        self.setStyleSheet("""
            QMainWindow { background-color: #f1f5f9; }
            QSplitter::handle { background-color: #cbd5e1; }
            QListWidget {
                border: none;
                background-color: #ffffff;
                border-radius: 12px;
                margin: 10px;
                padding: 5px;
                outline: none;
            }
            QListWidget::item {
                padding: 12px;
                border-radius: 8px;
                margin: 2px 5px;
                color: #475569;
                font-weight: 500;
            }
            QListWidget::item:selected {
                background-color: #3b82f6;
                color: white;
            }
            QListWidget::item:hover:!selected {
                background-color: #eff6ff;
                color: #2563eb;
            }
            QTextBrowser {
                border: none;
                background-color: #ffffff;
                border-radius: 12px;
                margin: 10px;
                padding: 10px;
            }
        """)

        # Central Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Custom Header
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet("background-color: #ffffff; border-bottom: 1px solid #e2e8f0;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        title_label = QLabel("Tribal Markdown")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet("color: #1e293b;")
        
        self.status_label = QLabel("Welcome to the Viewer")
        self.status_label.setStyleSheet("color: #64748b; font-size: 13px;")

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)
        
        main_layout.addWidget(header)

        # Main Body (Splitter)
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0,0,0,0)

        self.splitter = QSplitter(Qt.Horizontal)
        
        # 1. Sidebar Container
        sidebar_container = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.setContentsMargins(10, 10, 0, 10)
        
        sidebar_label = QLabel("DOCUMENTATION")
        sidebar_label.setStyleSheet("color: #94a3b8; font-weight: bold; font-size: 10px; margin-left: 20px; margin-top: 10px;")
        
        self.file_list = QListWidget()
        sidebar_layout.addWidget(sidebar_label)
        sidebar_layout.addWidget(self.file_list)
        
        # 2. Preview Container
        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(0, 10, 10, 10)
        
        self.preview = QTextBrowser()
        self.preview.setOpenExternalLinks(False)
        self.preview.anchorClicked.connect(self.handle_link_click)
        
        preview_layout.addWidget(self.preview)

        self.splitter.addWidget(sidebar_container)
        self.splitter.addWidget(preview_container)
        self.splitter.setSizes([300, 900])

        body_layout.addWidget(self.splitter)
        main_layout.addWidget(body)
        
        # Connections
        self.file_list.currentItemChanged.connect(self.load_selected_file)

        # Menu
        self.create_menus()

    def create_menus(self):
        menubar = self.menuBar()
        theme_menu = menubar.addMenu("Themes")
        
        for theme_name in THEMES:
            action = QAction(theme_name, self)
            action.triggered.connect(lambda chk, t=theme_name: self.set_theme(t))
            theme_menu.addAction(action)

    def set_theme(self, theme_name):
        self.current_theme = theme_name
        self.status_label.setText(f"Theme: {theme_name}")
        
        # Update app palette for dark mode UI elements if needed
        if "Deep Space" in theme_name:
            self.setStyleSheet(self.styleSheet().replace("#ffffff", "#1e293b").replace("#f1f5f9", "#0f172a").replace("#475569", "#cbd5e1"))
        else:
            self.setStyleSheet(self.styleSheet().replace("#1e293b", "#ffffff").replace("#0f172a", "#f1f5f9").replace("#cbd5e1", "#475569"))

        if self.file_list.currentItem():
            self.load_selected_file(self.file_list.currentItem(), None)

    def check_content_folder(self):
        if not os.path.exists(self.content_path):
            os.makedirs(self.content_path)
            with open(os.path.join(self.content_path, "welcome.md"), 'w', encoding='utf-8') as f:
                f.write("# Welcome\n\nWelcome to your new Markdown Viewer. Add your files to the `content` folder!")

    def load_file_list(self):
        self.file_list.clear()
        if os.path.exists(self.content_path):
            files = sorted([f for f in os.listdir(self.content_path) if f.endswith(('.md', '.markdown'))])
            for f in files:
                item = QListWidgetItem(f)
                item.setData(Qt.UserRole, f)
                self.file_list.addItem(item)
            if self.file_list.count() > 0:
                self.file_list.setCurrentRow(0)

    def load_selected_file(self, current, previous):
        if not current: return
        filename = current.data(Qt.UserRole)
        filepath = os.path.join(self.content_path, filename)
        self.current_file_dir = os.path.dirname(filepath)
        self.status_label.setText(f"Reading: {filename}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                md_text = f.read()
            self.render_content(md_text)
        except Exception as e:
            self.preview.setText(f"Error loading file: {e}")

    def render_content(self, md_text):
        # Convert Markdown to HTML with common extensions
        html = markdown.markdown(md_text, extensions=['extra', 'fenced_code', 'tables', 'toc'])

        # Fix Image Paths
        html = self.fix_image_paths(html)

        # Add CSS
        css = THEMES[self.current_theme]
        full_html = f"<html><head><style>{css}</style></head><body>{html}</body></html>"
        
        self.preview.setHtml(full_html)

    def fix_image_paths(self, html_content):
        def replace_path(match):
            img_src = match.group(1)
            if img_src.startswith(('http://', 'https://', 'ftp://', 'file://')):
                return f'src="{img_src}"'
            
            abs_path = os.path.abspath(os.path.join(self.current_file_dir, img_src))
            file_url = f"file:///{abs_path.replace(os.sep, '/')}"
            return f'src="{file_url}"'

        pattern = r'src="([^"]+)"'
        return re.sub(pattern, replace_path, html_content)

    def handle_link_click(self, url):
        QDesktopServices.openUrl(url)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # Consistent look across platforms
    
    # Global Font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    win = MarkdownViewerApp()
    win.show()
    sys.exit(app.exec())
