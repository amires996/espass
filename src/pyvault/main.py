from __future__ import annotations

import sys

if sys.platform == "win32":
    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("espass.PasswordManager")
    except (AttributeError, OSError):
        pass

from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication

from pyvault.ui.main_window import MainWindow
from pyvault.utils.paths import resource_path


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("espass")
    app.setOrganizationName("espass")
    app.setWindowIcon(QIcon(str(resource_path("assets/icons/espass.ico"))))
    app.setFont(QFont("Segoe UI", 10))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
