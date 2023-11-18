from PySide2.QtGui import QColor, QPalette
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication

# Move to a stylesheet.qss?


def light_theme(app: QApplication):
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(240, 240, 240))  # Light gray
    palette.setColor(QPalette.WindowText, Qt.black)  # Black
    palette.setColor(QPalette.Base, QColor(255, 255, 255))  # White
    palette.setColor(QPalette.AlternateBase, QColor(230, 230, 230))  # Slightly darker gray
    palette.setColor(QPalette.ToolTipBase, Qt.black)  # Black
    palette.setColor(QPalette.ToolTipText, Qt.white)  # White
    palette.setColor(QPalette.Text, Qt.black)  # Black
    palette.setColor(QPalette.Dark, QColor(210, 210, 210))  # Lighter gray
    palette.setColor(QPalette.Shadow, QColor(220, 220, 220))  # Slightly darker than Window color
    palette.setColor(QPalette.Button, QColor(240, 240, 240))  # Light gray
    palette.setColor(QPalette.ButtonText, Qt.black)  # Black
    palette.setColor(QPalette.BrightText, Qt.red)  # Red
    palette.setColor(QPalette.Link, QColor(42, 130, 218))  # Same as dark theme
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))  # Same as dark theme
    palette.setColor(QPalette.HighlightedText, Qt.white)  # White

    palette.setColor(QPalette.Disabled, QPalette.Text, QColor(180, 180, 180))  # Light gray
    palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))  # Dark gray
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))  # Dark gray
    palette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(210, 210, 210))  # Lighter gray
    palette.setColor(QPalette.Disabled, QPalette.HighlightedText,
                     QColor(127, 127, 127))  # Dark gray

    app.setPalette(palette)
    app.setStyle('Fusion')


def dark_theme(app: QApplication):
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(42, 42, 42))
    palette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.black)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Dark, QColor(32, 32, 32))
    palette.setColor(QPalette.Shadow, QColor(20, 20, 20))
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.white)

    palette.setColor(QPalette.Disabled, QPalette.Text, QColor(65, 65, 65))
    palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
    palette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80))
    palette.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(127, 127, 127))

    app.setPalette(palette)
    app.setStyle('Fusion')


def set_theme(app: QApplication, theme: str = 'dark') -> None:
    if theme == 'dark':
        dark_theme(app)
    else:
        light_theme(app)
