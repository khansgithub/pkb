#!/usr/bin/env python3
import sys
import logging
from enum import Enum, auto
from PyQt5 import QtWidgets, QtGui, QtCore  # Or PySide6 if you prefer
from PyQt5.QtGui import QFontDatabase

# Import material theme
from qt_material import apply_stylesheet

# -------- Logging Setup --------
logger = logging.getLogger("ModernLineHighlighter")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

fh = logging.FileHandler("modern_highlighter.log", mode='w')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)


# -------- Highlight Enum --------
class Highlight(Enum):
    NONE = auto()
    RED = auto()
    GREEN = auto()
    YELLOW = auto()


HIGHLIGHT_COLORS = {
    Highlight.NONE: None,
    Highlight.RED: QtGui.QColor("#6A000B"),         # light red
    Highlight.GREEN: QtGui.QColor("#5A6A00"),       # light green
    Highlight.YELLOW: QtGui.QColor("#6A000B"),      # light yellow
}


# -------- Context-​Aware Analysis Function --------
def analyze_line(line: str, context: dict) -> Highlight:
    if line.startswith("```"):
        context["is_code_block"] = not context["is_code_block"]
        return Highlight.RED
    
    if context["is_code_block"]:
        return Highlight.RED

# -------- Main Window --------
class ModernLineHighlighter(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Modern Line Highlighter")
        self.resize(900, 600)

        # Central widget
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        self.layout = QtWidgets.QVBoxLayout(central)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        # Toolbar
        toolbar = QtWidgets.QToolBar()
        toolbar.setIconSize(QtCore.QSize(24, 24))
        self.addToolBar(toolbar)

        # Actions
        open_icon = QtGui.QIcon.fromTheme("document-open")
        save_icon = QtGui.QIcon.fromTheme("document-save")
        process_icon = QtGui.QIcon.fromTheme("media-playback-start")
        clear_icon = QtGui.QIcon.fromTheme("edit-clear")
        theme_icon = QtGui.QIcon.fromTheme("preferences-desktop-theme")

        self.action_open = QtWidgets.QAction("Open", self)
        self.action_open.setToolTip("Open a text file containing lines")
        self.action_save = QtWidgets.QAction(save_icon, "Save Highlighted", self)
        self.action_save.setToolTip("Save output with highlights (HTML)")
        self.action_process = QtWidgets.QAction(process_icon, "Process Lines", self)
        self.action_process.setToolTip("Analyze and highlight lines")
        self.action_clear = QtWidgets.QAction(clear_icon, "Clear", self)
        self.action_clear.setToolTip("Clear all text")
        self.action_toggle_theme = QtWidgets.QAction(theme_icon, "Toggle Dark/Light", self)
        self.action_toggle_theme.setToolTip("Switch between Dark and Light theme")

        toolbar.addAction(self.action_open)
        toolbar.addAction(self.action_process)
        toolbar.addAction(self.action_clear)
        toolbar.addAction(self.action_save)
        toolbar.addSeparator()
        toolbar.addAction(self.action_toggle_theme)

        # Text area
        self.text_edit = QtWidgets.QPlainTextEdit()
        font = QtGui.QFont("Roboto Mono", 10)
        self.text_edit.setFont(font)
        self.text_edit.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        self.layout.addWidget(self.text_edit)

        # Status bar
        self.statusbar = self.statusBar()

        # State
        self.lines = []
        self.theme = "light"  # or "dark"

        # Connect
        self.action_open.triggered.connect(self.load_file)
        self.action_process.triggered.connect(self.process_lines)
        self.action_clear.triggered.connect(self.clear_text)
        self.action_save.triggered.connect(self.save_highlighted)
        self.action_toggle_theme.triggered.connect(self.toggle_theme)

        # Initially disable some actions
        self.action_process.setEnabled(False)
        self.action_save.setEnabled(False)
        # open and clear are always enabled

    def load_file(self):
        try:
            fname, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "Open Text File", "", "All Files (*)"
            )
            if not fname:
                return

            with open(fname, 'r', encoding='utf-8') as f:
                content = f.read()

            self.text_edit.setPlainText(content)
            self.lines = content.splitlines()
            self.statusbar.showMessage(f"Loaded {len(self.lines)} lines.")
            logger.info("Loaded file: %s (%d lines)", fname, len(self.lines))

            self.action_process.setEnabled(True)
            self.action_clear.setEnabled(True)
            self.action_save.setEnabled(False)

        except Exception as e:
            logger.exception("Failed loading file")
            QtWidgets.QMessageBox.critical(self, "Error loading file", str(e))

    def clear_text(self):
        self.text_edit.clear()
        self.lines = []
        self.statusbar.showMessage("Cleared text.")
        logger.info("Cleared text.")
        self.action_process.setEnabled(False)
        self.action_save.setEnabled(False)

    def process_lines(self):
        try:
            content = self.text_edit.toPlainText()
            self.lines = content.splitlines()
            if not self.lines:
                self.statusbar.showMessage("No lines to process.")
                return

            context = {"is_code_block": False}
            doc = self.text_edit.document()

            # reset formatting
            cursor = QtGui.QTextCursor(doc)
            cursor.select(QtGui.QTextCursor.Document)
            default_fmt = QtGui.QTextCharFormat()
            default_fmt.setBackground(QtGui.QBrush(QtGui.QColor("transparent")))
            cursor.setCharFormat(default_fmt)

            for idx, line in enumerate(self.lines):
                context["current_line"] = idx + 1
                result = analyze_line(line, context)
                color = HIGHLIGHT_COLORS.get(result)
                if color:
                    block = doc.findBlockByNumber(idx)
                    cur = QtGui.QTextCursor(block)
                    cur.select(QtGui.QTextCursor.LineUnderCursor)
                    fmt = QtGui.QTextCharFormat()
                    fmt.setBackground(QtGui.QBrush(color))
                    cur.setCharFormat(fmt)

            self.statusbar.showMessage(f"Processed {len(self.lines)} lines.")
            logger.info("Processing done. Context at end: %s", context)
            self.action_save.setEnabled(True)

        except Exception as e:
            logger.exception("Error during processing")
            QtWidgets.QMessageBox.critical(self, "Processing Error", str(e))

    def save_highlighted(self):
        try:
            fname, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Save As HTML", "", "HTML Files (*.html);;All Files (*)"
            )
            if not fname:
                return

            doc = self.text_edit.document()
            html = doc.toHtml()
            with open(fname, 'w', encoding='utf-8') as f:
                f.write(html)

            self.statusbar.showMessage(f"Saved highlighted output to {fname}")
            logger.info("Saved output to: %s", fname)

        except Exception as e:
            logger.exception("Error saving file")
            QtWidgets.QMessageBox.critical(self, "Save Error", str(e))

    def toggle_theme(self):
        # switch
        if self.theme == "light":
            self.theme = "dark"
            apply_stylesheet(QtWidgets.QApplication.instance(), theme="light_blue.xml")
            logger.info("Theme switched to dark")
        else:
            self.theme = "light"
            apply_stylesheet(QtWidgets.QApplication.instance(), theme="dark_cyan.xml")
            logger.info("Theme switched to light")

        # re‑apply UI that might need redrawing
        self.text_edit.update()
        self.statusbar.clearMessage()

def main():
    app = QtWidgets.QApplication(sys.argv)

    # Apply initial material style
    apply_stylesheet(app, theme="light_green.xml")

    window = ModernLineHighlighter()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
