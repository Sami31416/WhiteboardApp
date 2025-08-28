from PySide6.QtGui import QPainter, QColor, QPen, QBrush  # QAction moved to QtGui!
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

class VisualIndicator(QWidget):
    """Transparent overlay that shows visual feedback for screen edge actions"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)  # Click-through
        self.hide()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor(255, 255, 255, 100), 3))  # Semi-transparent white border
        painter.setBrush(QBrush(QColor(255, 255, 255, 15)))  # Very subtle fill
        painter.drawRect(self.rect().adjusted(1, 1, -1, -1))  # Slightly inset