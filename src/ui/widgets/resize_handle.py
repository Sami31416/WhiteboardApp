from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt

class ResizeHandle(QWidget):
    def __init__(self, parent, position):
        super().__init__(parent)
        self.position = position
        self.setProperty("position", position)
        self.setMouseTracking(True)
        self.mouse_pressed = False
        self.mouse_pos = None
        self.window_pos = None
        self.window_size = None
        
        # Set appropriate cursor based on position
        cursors = {
            'top': Qt.SizeVerCursor,
            'bottom': Qt.SizeVerCursor,
            'left': Qt.SizeHorCursor,
            'right': Qt.SizeHorCursor,
            'topleft': Qt.SizeFDiagCursor,
            'topright': Qt.SizeBDiagCursor,
            'bottomleft': Qt.SizeBDiagCursor,
            'bottomright': Qt.SizeFDiagCursor
        }
        self.setCursor(cursors.get(position, Qt.ArrowCursor))
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_pressed = True
            self.mouse_pos = event.globalPosition().toPoint()
            self.window_pos = self.window().pos()
            self.window_size = self.window().size()
            event.accept()
            
    def mouseMoveEvent(self, event):
        if self.mouse_pressed:
            self.handle_resize(event.globalPosition().toPoint())
            event.accept()
        else:
            event.ignore()
            
    def mouseReleaseEvent(self, event):
        self.mouse_pressed = False
        event.accept()
        
    def handle_resize(self, global_pos):
        delta = global_pos - self.mouse_pos
        x, y, w, h = self.window_pos.x(), self.window_pos.y(), self.window_size.width(), self.window_size.height()
        min_width = self.window().minimumWidth()
        min_height = self.window().minimumHeight()
        
        # Calculate proposed changes
        if 'right' in self.position:
            w = max(w + delta.x(), min_width)
        if 'left' in self.position:
            proposed_width = max(w - delta.x(), min_width)
            # Only move left edge if we're not at minimum width
            if proposed_width > min_width or delta.x() <= 0:
                x += delta.x()
                w = proposed_width
            else:
                # At minimum width, keep right edge fixed
                x = self.window_pos.x() + self.window_size.width() - min_width
                w = min_width
        if 'bottom' in self.position:
            h = max(h + delta.y(), min_height)
        if 'top' in self.position:
            proposed_height = max(h - delta.y(), min_height)
            # Only move top edge if we're not at minimum height
            if proposed_height > min_height or delta.y() <= 0:
                y += delta.y()
                h = proposed_height
            else:
                # At minimum height, keep bottom edge fixed
                y = self.window_pos.y() + self.window_size.height() - min_height
                h = min_height
                
        self.window().setGeometry(x, y, w, h)