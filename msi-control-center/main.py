#!/usr/bin/env python3
"""MSI Control Center — System monitoring and hardware control for MSI laptops."""

import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)


def main():
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
    except ImportError:
        print("Error: PySide6 is not installed.")
        print("Install it with: pip install PySide6")
        sys.exit(1)

    try:
        import psutil  # noqa: F401
    except ImportError:
        print("Error: psutil is not installed.")
        print("Install it with: pip install psutil")
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setApplicationName("MSI Control Center")
    app.setApplicationVersion("1.0.0")
    app.setDesktopFileName("msi-control-center")

    try:
        app.setStyle("Fusion")
    except Exception:
        pass

    from gui.main_window import MainWindow

    window = MainWindow()
    window.show()
    window.start_monitoring()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
