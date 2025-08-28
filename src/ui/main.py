import sys
import os  # Required for file path operations
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow


if __name__ == "__main__":
    # Create Qt application instance
    app = QApplication(sys.argv)

    theme_path = os.path.join(os.path.dirname(__file__), 'styles', 'theme.qss')
    if os.path.exists(theme_path):
        app.setStyleSheet(open(theme_path).read())


    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start application event loop
    sys.exit(app.exec())