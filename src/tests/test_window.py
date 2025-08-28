from PySide6.QtWidgets import QApplication  # ADD THIS
from ui.main import MainWindow

def test_window_opens():
    app = QApplication.instance() or QApplication([])  # CREATE APP INSTANCE
    window = MainWindow()
    assert window.windowTitle() == "Whiteboard App"
    window.close()  # EXPLICITLY CLOSE WINDOW 