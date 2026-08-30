import sys
import os
from PySide6.QtWidgets import QApplication
from view import PriceAnalyzerApp


def main():
    """
    Application entry point.

    Initializes the Qt application environment (QApplication), creates 
    and displays the main application window (PriceAnalyzerApp), and starts 
    the main event loop.
    """
    app = QApplication(sys.argv)
    window = PriceAnalyzerApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()