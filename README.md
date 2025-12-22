<h1 align="center">Tribal Markdown Viewer</h1>

<p align="center">
  <strong>A sleek, lightweight, and modern Markdown viewer built with Python and PySide6.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python Version">
  <img src="https://img.shields.io/badge/PySide6-Qt%20for%20Python-green?style=for-the-badge&logo=qt&logoColor=white" alt="PySide6">
</p>

---

## ✨ Overview

**Tribal Markdown Viewer** is a professional-grade desktop application designed to provide a high-fidelity preview of your Markdown files. Whether you're managing documentation, personal notes, or complex guides, this viewer offers a clean and distraction-free environment to read and navigate your content.

## 🚀 Key Features

- **🌓 Dynamic Themes**: Toggle between beautifully crafted **Light** and **Dark** modes to suit your preference and environment.
- **📂 Intuitive Sidebar**: A dedicated file explorer that automatically lists all `.md` and `.markdown` files from your `content` directory for quick access.
- **🖼️ Smart Image Handling**: Relative image paths are automatically resolved, ensuring your visuals always show up correctly.
- **🔗 External Link Redirection**: Click on web links to open them instantly in your default system browser.
- **⚡ High Performance**: Built with PySide6 for a snappy, native-feeling desktop experience.
- **📝 Extended Syntax**: Support for standard Markdown plus common extensions like `fenced_code` and `extra`.

## 🛠️ Tech Stack

- **[Python](https://www.python.org/)**: The core programming language.
- **[PySide6](https://doc.qt.io/qtforpython/)**: The Python binding for the Qt framework, providing a robust UI.
- **[Markdown](https://pypi.org/project/Markdown/)**: The engine for converting Markdown text to beautiful HTML.

## 📥 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/plantacerium/TribalMarkdownViewer.git
   cd TribalMarkdownViewer
   ```

2. **Set up a virtual environment (optional but recommended)**:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   # source venv/bin/activate    # On Linux/macOS
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 Usage

1. **Add your content**: Place your Markdown files and associated images in the `content/` folder within the project root.
2. **Launch the application**:
   ```bash
   python main.py
   ```
3. **Browse and Read**: Use the sidebar to switch between files and use the **Themes** menu to change the visual look.

## 📂 Project Structure

```text
markdown-viewer/
├── assets/             # Branding and images for README
├── content/            # The directory where your .md files
├── main.py             # The core application logic
├── requirements.txt    # Project dependencies
└── README.md           # You are here!
```
