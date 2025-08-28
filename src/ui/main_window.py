from PySide6.QtGui import QPainter, QColor, QPen, QBrush  # QAction moved to QtGui!
from PySide6.QtCore import( Qt, QPoint, QSize, QEvent, QTimer, QRect, QRectF)
from PySide6.QtWidgets import(
     QMainWindow, QWidget, QPushButton, QVBoxLayout
     ,QHBoxLayout, QLabel, QSpacerItem, QSizePolicy
     ,QApplication, QGraphicsDropShadowEffect
    )
from PySide6.QtGui import QCursor

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

class ShadowWindow(QWidget):
    def __init__(self):
        super().__init__(None)  # Top-level window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)  
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(300, 200)  # temp size for testing
        self.show()

class ShadowWindow(QWidget):
    def __init__(self, feather=100):
        super().__init__(None)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(300, 200)

        # Inner widget acts as shadow caster
        self.inner = QWidget(self)
        self.inner.setStyleSheet("background-color: black; border-radius: 0px;")
        self.inner.setGeometry(feather, feather,
                               self.width()-2*feather, self.height()-2*feather)

        effect = QGraphicsDropShadowEffect(self.inner)
        effect.setBlurRadius(feather)       # feather amount
        effect.setOffset(0, 0)              # no offset, uniform shadow
        effect.setColor(QColor(0, 0, 0, 180))
        self.inner.setGraphicsEffect(effect)

        self.show()

    def resizeEvent(self, event):
        feather = 40  # keep consistent
        self.inner.setGeometry(feather, feather, self.width()-2*feather, self.height()-2*feather)

# Define the main window class
class MainWindow(QMainWindow):

    def __init__(self):  
        # Initialize the parent QMainWindow class
        super().__init__()

        # Set the window title
        self.setWindowTitle("Whiteboard App")

        self.setWindowFlags(Qt.FramelessWindowHint) # Hides default title bar

        screen = QApplication.primaryScreen()
        screen_size = screen.availableGeometry().size()  # Get available screen size (excluding taskbar)

        # Scale by 0.5
        self.default_size = QSize(screen_size.width() // 1.6, screen_size.height() // 1.35)

        # Set minimum window size
        self.setMinimumSize(400, 300)       
            
        # Create main container widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        
        # Create main layout (vertical box)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.title_bar = QWidget(central_widget) # Create container for custom title bar
        self.title_bar.setFixedHeight(30) # Set fixed height for title bar
        self.title_bar.setObjectName("TitleBar") # For CSS styling later
        # Add title bar to layout (top position)
        main_layout.addWidget(self.title_bar)

        # Create horizontal layout for title bar
        title_layout = QHBoxLayout(self.title_bar)  # Layout for title bar
        title_layout.setContentsMargins(5, 0, 5, 0)  # Small left/right padding
        title_layout.setSpacing(5)  # Spacing between elements
        
        # Add window title text (left side)
        self.title_label = QLabel("Whiteboard App", self.title_bar)
        self.title_label.setObjectName("TitleLabel")
        title_layout.addWidget(self.title_label)  # Add to left side
        
        # Add spacer to push buttons to right
        spacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        title_layout.addSpacerItem(spacer)  # This pushes everything right
        
        # Create container for window buttons
        self.window_buttons = QWidget(self.title_bar)

        button_layout = QHBoxLayout(self.window_buttons)
        button_layout.setContentsMargins(0, 0, 0, 0)  # No margins
        button_layout.setSpacing(2)  # Small spacing between buttons
        
        # Minimize button (-)
        self.minimize_btn = QPushButton("–", self.window_buttons)  # Unicode minus
        self.minimize_btn.setFixedSize(30, 30)
        self.minimize_btn.clicked.connect(self.minimize_window)  # Minimize window
        self.minimize_btn.setObjectName("MinimizeButton")
        button_layout.addWidget(self.minimize_btn)

        # Maximize button
        self.maximize_btn = QPushButton("□", self.window_buttons)  # Square symbol
        self.maximize_btn.setObjectName("MaximizeButton")
        self.maximize_btn.setFixedSize(30, 30)
        self.maximize_btn.clicked.connect(self.toggle_maximize)  # Connect to handler
        button_layout.addWidget(self.maximize_btn)  # Add to layout  
        
        # Close button (X)
        self.close_btn = QPushButton("✕", self.window_buttons)
        self.close_btn.setObjectName("CloseButton")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.clicked.connect(self.close_window)
        button_layout.addWidget(self.close_btn)
        
        # Add button container to title layout
        title_layout.addWidget(self.window_buttons)

        # Canvas placeholder WITH CENTRAL_WIDGET AS PARENT
        self.canvas_placeholder = QWidget(central_widget)  # Correct parent
        main_layout.addWidget(self.canvas_placeholder)


        # Then use it to resize the window
        self.resize(self.default_size)


        self.showNormal()
        self.maximize_btn.setText("□")

        # ✅ Save the default "normal" geometry here before going maximized
        self.last_normal_geometry = self.geometry()

        QTimer.singleShot(0, self.showMaximized)
        self.maximize_btn.setText("❐")

        # State tracking variables
        self._was_maximized_before_minimize = False  # Track minimized state
        self.drag_position = None
        self.drag_start_global = None
        self.dragging = False
        self.pending_drag = None
        self.was_minimized = False

        self.visual_indicator = VisualIndicator(self)
        self.visual_indicator.hide()

        # Create all 8 resize handles
        self.resize_handles = {}
        positions = ['top', 'bottom', 'left', 'right', 'topleft', 'topright', 'bottomleft', 'bottomright']
        
        for pos in positions:
            handle = ResizeHandle(self, pos)
            handle.hide()
            self.resize_handles[pos] = handle
        
        # Update handle positions
        self.update_handle_positions()

        self.shadow = ShadowWindow()



    def update_handle_positions(self):
        """Update all resize handle positions based on window size"""
        handle_size = 6  # Increased from 5 to 8 pixels for better targeting
        corner_size = 10  # Even larger for corners

        if not hasattr(self, 'resize_handles'):
            return

        # Position each handle
        self.resize_handles['top'].setGeometry(
            0, 0, self.width(), handle_size  # Full width top edge
        )
        self.resize_handles['bottom'].setGeometry(
            0, self.height() - handle_size, self.width(), handle_size  # Full width bottom edge
        )
        self.resize_handles['left'].setGeometry(
            0, 0, handle_size, self.height()  # Full height left edge
        )
        self.resize_handles['right'].setGeometry(
            self.width() - handle_size, 0, handle_size, self.height()  # Full height right edge
        )
        self.resize_handles['topleft'].setGeometry(
            0, 0, corner_size, corner_size  # Larger corner area
        )
        self.resize_handles['topright'].setGeometry(
            self.width() - corner_size, 0, corner_size, corner_size  # Larger corner area
        )
        self.resize_handles['bottomleft'].setGeometry(
            0, self.height() - corner_size, corner_size, corner_size  # Larger corner area
        )
        self.resize_handles['bottomright'].setGeometry(
            self.width() - corner_size, self.height() - corner_size, corner_size, corner_size  # Larger corner area
        )
        # Ensure handles are always on top of other widgets
        for handle in self.resize_handles.values():
            handle.raise_()


    def resizeEvent(self, event):
        """Handle window resize events"""
        super().resizeEvent(event)
        self.update_handle_positions()

        # Update last normal geometry if not maximized
        if not self.isMaximized():
            self.last_normal_geometry = self.geometry()


    def minimize_window(self):
        """Minimize; remember if we were maximized so we can return to it."""
        self._was_maximized_before_minimize = self.isMaximized()
        self.was_minimized = True
        self.showMinimized()



    def toggle_maximize(self):
        
        if self.isMaximized():
            self.restore_window()
        else:
            self.maximize_window()
            # Show/hide all resize handles based on window state
        for handle in self.resize_handles.values():
            handle.setVisible(not self.isMaximized())

    def maximize_window(self):
        """Maximize the window and update state."""
        self.last_normal_geometry = self.geometry()
        self.showMaximized()
        self.maximize_btn.setText("❐")


    def restore_window(self):
        """Restore to saved normal geometry."""
        self.showNormal()
        if self.last_normal_geometry and not self.last_normal_geometry.isEmpty():
            self.setGeometry(self.last_normal_geometry)
        self.maximize_btn.setText("□")


    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if not self.isMinimized() and self._was_maximized_before_minimize:
                self._was_maximized_before_minimize = False
                self.showMaximized()   # restore maximize state
                self.maximize_btn.setText("❐")
            if self.was_minimized:
                self.was_minimized = False
            else:
                self.maximize_btn.setText("❐" if self.isMaximized() else "□")

            # Update all resize handles visibility
            for handle in self.resize_handles.values():
                handle.setVisible(not self.isMaximized())
            
        super().changeEvent(event)

    def close_window(self):
        self.close()


    def mouseDoubleClickEvent(self, event):
        """Maximize/Restore on title bar double-click"""
        if event.y() < self.title_bar.height():
            self.toggle_maximize()  # Trigger same toggle function
            event.accept()  # Mark as handled


    def mousePressEvent(self, event):
        """Handle mouse press events for window dragging"""
        clicked_widget = self.childAt(event.pos())

        if (event.y() < self.title_bar.height() and 
            clicked_widget not in [self.window_buttons]):

            self.drag_start_global = event.globalPosition().toPoint()  # Remember mouse start
            self.dragging = False  # Only start drag after movement threshold
            event.accept()
        else:
            super().mousePressEvent(event)

    
    def mouseMoveEvent(self, event):
        if not hasattr(self, 'drag_start_global') or not self.drag_start_global:
            super().mouseMoveEvent(event)
            return
    
        cursor_pos = event.globalPosition().toPoint()
        distance = (cursor_pos - self.drag_start_global).manhattanLength()
    
        # Start drag only after moving a threshold
        if distance <= 5:
            return
    
        if not getattr(self, 'dragging', False):
            self.dragging = True
    
            if self.isMaximized():
                # Restore from maximized
                self.restore_window()
                self.pending_drag = cursor_pos
                QTimer.singleShot(0, self._start_pending_drag)
                return
            else:
                # Normal window: compute drag offset immediately
                self.drag_position = cursor_pos - self.frameGeometry().topLeft()
    
        # Move window if drag_position is set
        if self.drag_position:

             # Constrain cursor movement
            cursor_pos = self.constrain_cursor_to_screen(cursor_pos)

            new_pos = cursor_pos - self.drag_position
            self.move(new_pos)

            # Provide visual feedback when near screen edges
            screen_geometry = QApplication.primaryScreen().geometry()
            
        # Show visual indicator based on edge proximity
        if cursor_pos.y() <= 20:
            # Top edge - show full screen indicator
            self.setCursor(Qt.SizeAllCursor)
            self.show_visual_indicator(screen_geometry)
        elif cursor_pos.x() <= 20:
            # Left edge - show left half indicator
            self.setCursor(Qt.SizeHorCursor)
            left_half = QRect(screen_geometry.x(), screen_geometry.y(), 
                             screen_geometry.width() // 2, screen_geometry.height())
            self.show_visual_indicator(left_half)
        elif cursor_pos.x() >= screen_geometry.width() - 20:
            # Right edge - show right half indicator
            self.setCursor(Qt.SizeHorCursor)
            right_half = QRect(screen_geometry.x() + screen_geometry.width() // 2,
                              screen_geometry.y(), screen_geometry.width() // 2,
                              screen_geometry.height())
            self.show_visual_indicator(right_half)
        else:
            self.setCursor(Qt.ArrowCursor)
            self.hide_visual_indicator()
            event.accept()


    def _start_pending_drag(self):
        
        if not self.pending_drag:
            return
        
        cursor_pos = self.pending_drag
        self.pending_drag = None

        # Move window so cursor is at top-center
        new_x = cursor_pos.x() - self.width() // 2
        new_y = cursor_pos.y() - 10
        self.move(new_x, new_y)

        # Set drag offset for smooth dragging
        self.drag_position = QPoint(self.width() // 2, 10)


    def mouseReleaseEvent(self, event):
        """Handle mouse release to stop dragging"""
        # Hide visual indicator
        self.hide_visual_indicator()

        # Reset cursor to default
        self.setCursor(Qt.ArrowCursor)
    
        # Check if we were dragging and cursor is at top of screen
        if self.dragging:
            screen_geometry = QApplication.primaryScreen().geometry()
            cursor_pos = event.globalPosition().toPoint()

            # Check if cursor is at top of screen (within 20px threshold)
            if cursor_pos.y() <= 20:  # Top screen edge threshold
                self.maximize_window()

            # Left screen edge - snap to left half
            elif cursor_pos.x() <= 20:
                self.snap_to_left_half()

            # Right screen edge - snap to right half  
            elif cursor_pos.x() >= screen_geometry.width() - 20:
                self.snap_to_right_half()


        self.drag_position = None  # Stop dragging
        self.drag_start_global = None
        self.dragging = False
        self.pending_drag = None


        event.accept()  # Mark event as handled
        super().mouseReleaseEvent(event)  # Pass to default handler

    def snap_to_left_half(self):
        """Snap window to left half of screen"""
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        half_width = screen_geometry.width() // 2
        new_geometry = QRect(
            screen_geometry.x(),  # Left edge of screen
            screen_geometry.y(),  # Top edge of screen
            half_width,           # Half screen width
            screen_geometry.height()  # Full screen height
        )
        self.setGeometry(new_geometry)
        self.last_normal_geometry = new_geometry  # Update last normal geometry

    def snap_to_right_half(self):
        """Snap window to right half of screen"""
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        half_width = screen_geometry.width() // 2
        new_geometry = QRect(
            screen_geometry.x() + half_width,  # Right half of screen
            screen_geometry.y(),               # Top edge of screen
            half_width,                        # Half screen width
            screen_geometry.height()           # Full screen height
        )
        self.setGeometry(new_geometry)
        self.last_normal_geometry = new_geometry  # Update last normal geometry

    def show_visual_indicator(self, geometry):
        """Show visual indicator at the specified geometry"""
        # Convert screen coordinates to window coordinates
        window_pos = self.mapFromGlobal(geometry.topLeft())
        self.visual_indicator.setGeometry(QRect(window_pos, geometry.size()))
        self.visual_indicator.show()
        self.visual_indicator.raise_()  # Ensure it's on top

    def hide_visual_indicator(self):
        """Hide visual indicator"""
        self.visual_indicator.hide()

    def constrain_cursor_to_screen(self, cursor_pos):
        """Constrain cursor to stay within a percentage of screen height"""
        screen_geometry = QApplication.primaryScreen().geometry()

        # Calculate maximum Y position (90% of screen height)
        max_y = screen_geometry.y() + int(screen_geometry.height() * 0.925)

        # Constrain position
        constrained_x = max(screen_geometry.left(), min(cursor_pos.x(), screen_geometry.right()))
        constrained_y = max(screen_geometry.top(), min(cursor_pos.y(), max_y))

        # If cursor was constrained, move it to the constrained position
        if constrained_x != cursor_pos.x() or constrained_y != cursor_pos.y():
            QCursor.setPos(constrained_x, constrained_y)

        return QPoint(constrained_x, constrained_y)
