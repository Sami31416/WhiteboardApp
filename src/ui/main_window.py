from PySide6.QtCore import (Qt, QPoint, QSize, QEvent, QTimer, QRect)
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QPushButton, QVBoxLayout,
    QHBoxLayout, QLabel, QSpacerItem, QSizePolicy,
    QApplication
)
from PySide6.QtGui import QCursor
from ui.widgets.resize_handle import ResizeHandle
from ui.widgets.visual_indicator import VisualIndicator
from ui.widgets.shadow_window import ShadowWindow


# ==========================================================
#  Main Window Class
# ==========================================================
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # -----------------------
        # Basic Window Setup
        # -----------------------
        self.setWindowTitle("Whiteboard App")
        self.setWindowFlags(Qt.FramelessWindowHint)  # Hides default title bar
        self.setMinimumSize(400, 300)

        screen = QApplication.primaryScreen()
        screen_size = screen.availableGeometry().size()  # Excluding taskbar
        self.default_size = QSize(screen_size.width() // 1.6,
                                  screen_size.height() // 1.35)

        # -----------------------
        # Central Layout & Title Bar
        # -----------------------
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._setup_title_bar(main_layout)

        # Canvas placeholder
        self.canvas_placeholder = QWidget(central_widget)
        main_layout.addWidget(self.canvas_placeholder)

        # -----------------------
        # Initial Sizing & Geometry
        # -----------------------
        self.resize(self.default_size)
        self.showNormal()
        self.maximize_btn.setText("□")
        self.last_normal_geometry = self.geometry()
        QTimer.singleShot(0, self.showMaximized)
        self.maximize_btn.setText("❐")

        # -----------------------
        # State Tracking
        # -----------------------
        self._was_maximized_before_minimize = False
        self.was_minimized = False
        self.drag_position = None
        self.drag_start_global = None
        self.dragging = False
        self.pending_drag = None

        # -----------------------
        # Helpers: Indicator, Handles, Shadow
        # -----------------------
        self.visual_indicator = VisualIndicator(self)
        self.visual_indicator.hide()

        self._setup_resize_handles()
        self.shadow = ShadowWindow()

    # ==========================================================
    #  Setup Helpers
    # ==========================================================
    def _setup_title_bar(self, main_layout):
        """Builds the custom title bar with buttons"""
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(30)
        self.title_bar.setObjectName("TitleBar")
        main_layout.addWidget(self.title_bar)

        # Layout
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(5, 0, 5, 0)
        title_layout.setSpacing(5)

        # Label
        self.title_label = QLabel("Whiteboard App", self.title_bar)
        self.title_label.setObjectName("TitleLabel")
        title_layout.addWidget(self.title_label)

        # Spacer
        spacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        title_layout.addSpacerItem(spacer)

        # Window buttons
        self.window_buttons = QWidget(self.title_bar)
        button_layout = QHBoxLayout(self.window_buttons)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(2)

        # Minimize button (-)
        self.minimize_btn = QPushButton("–", self.window_buttons)
        self.minimize_btn.setFixedSize(30, 30)
        self.minimize_btn.setObjectName("MinimizeButton")
        self.minimize_btn.clicked.connect(self.minimize_window)

        # Maximize button
        self.maximize_btn = QPushButton("□", self.window_buttons)
        self.maximize_btn.setFixedSize(30, 30)
        self.maximize_btn.setObjectName("MaximizeButton")
        self.maximize_btn.clicked.connect(self.toggle_maximize)

        # Close button (X)
        self.close_btn = QPushButton("✕", self.window_buttons)
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setObjectName("CloseButton")
        self.close_btn.clicked.connect(self.close_window)

        # Add to layout
        for btn in [self.minimize_btn, self.maximize_btn, self.close_btn]:
            button_layout.addWidget(btn)

        title_layout.addWidget(self.window_buttons)

    def _setup_resize_handles(self):
        """Create 8 resize handles and set initial positions"""
        self.resize_handles = {}
        positions = ['top', 'bottom', 'left', 'right',
                     'topleft', 'topright', 'bottomleft', 'bottomright']
        for pos in positions:
            handle = ResizeHandle(self, pos)
            handle.hide()
            self.resize_handles[pos] = handle
        self.update_handle_positions()

    # ==========================================================
    #  Window State Methods
    # ==========================================================
    def minimize_window(self):
        """Minimize; remember if we were maximized so we can return to it."""
        self._was_maximized_before_minimize = self.isMaximized()
        self.was_minimized = True
        self.showMinimized()

    def toggle_maximize(self):
        """Toggle between maximize and restore."""
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

    def close_window(self):
        """Close the window."""
        self.close()

    # ==========================================================
    #  Event Handlers
    # ==========================================================
    def resizeEvent(self, event):
        """Handle window resize events"""
        super().resizeEvent(event)
        self.update_handle_positions()
        if not self.isMaximized():
            self.last_normal_geometry = self.geometry()

    def changeEvent(self, event):
        """Handle state change events (min/max/restore)."""
        if event.type() == QEvent.WindowStateChange:
            if not self.isMinimized() and self._was_maximized_before_minimize:
                self._was_maximized_before_minimize = False
                self.showMaximized()
                self.maximize_btn.setText("❐")
            if self.was_minimized:
                self.was_minimized = False
            else:
                self.maximize_btn.setText("❐" if self.isMaximized() else "□")

            # Update all resize handles visibility
            for handle in self.resize_handles.values():
                handle.setVisible(not self.isMaximized())
        super().changeEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Maximize/Restore on title bar double-click"""
        if event.y() < self.title_bar.height():
            self.toggle_maximize()
            event.accept()

    def mousePressEvent(self, event):
        """Handle mouse press events for window dragging"""
        clicked_widget = self.childAt(event.pos())
        if (event.y() < self.title_bar.height() and
                clicked_widget not in [self.window_buttons]):
            self.drag_start_global = event.globalPosition().toPoint()
            self.dragging = False
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle window dragging and snapping preview"""
        if not hasattr(self, 'drag_start_global') or not self.drag_start_global:
            super().mouseMoveEvent(event)
            return

        cursor_pos = event.globalPosition().toPoint()
        distance = (cursor_pos - self.drag_start_global).manhattanLength()

        if distance <= 5:
            return

        if not getattr(self, 'dragging', False):
            self.dragging = True
            if self.isMaximized():
                self.restore_window()
                self.pending_drag = cursor_pos
                QTimer.singleShot(0, self._start_pending_drag)
                return
            else:
                self.drag_position = cursor_pos - self.frameGeometry().topLeft()

        if self.drag_position:
            cursor_pos = self.constrain_cursor_to_screen(cursor_pos)
            new_pos = cursor_pos - self.drag_position
            self.move(new_pos)

            screen_geometry = QApplication.primaryScreen().geometry()

        # Snap indicators
        if cursor_pos.y() <= 20:
            self.setCursor(Qt.SizeAllCursor)
            self.show_visual_indicator(screen_geometry)
        elif cursor_pos.x() <= 20:
            self.setCursor(Qt.SizeHorCursor)
            left_half = QRect(screen_geometry.x(), screen_geometry.y(),
                              screen_geometry.width() // 2, screen_geometry.height())
            self.show_visual_indicator(left_half)
        elif cursor_pos.x() >= screen_geometry.width() - 20:
            self.setCursor(Qt.SizeHorCursor)
            right_half = QRect(screen_geometry.x() + screen_geometry.width() // 2,
                               screen_geometry.y(), screen_geometry.width() // 2,
                               screen_geometry.height())
            self.show_visual_indicator(right_half)
        else:
            self.setCursor(Qt.ArrowCursor)
            self.hide_visual_indicator()
            event.accept()

    def mouseReleaseEvent(self, event):
        """Handle mouse release to stop dragging"""
        self.hide_visual_indicator()
        self.setCursor(Qt.ArrowCursor)

        if self.dragging:
            screen_geometry = QApplication.primaryScreen().geometry()
            cursor_pos = event.globalPosition().toPoint()

            if cursor_pos.y() <= 20:
                self.maximize_window()
            elif cursor_pos.x() <= 20:
                self.snap_to_left_half()
            elif cursor_pos.x() >= screen_geometry.width() - 20:
                self.snap_to_right_half()

        self.drag_position = None
        self.drag_start_global = None
        self.dragging = False
        self.pending_drag = None

        event.accept()
        super().mouseReleaseEvent(event)

    # ==========================================================
    #  Dragging / Snapping
    # ==========================================================
    def _start_pending_drag(self):
        """Start window dragging after restoring from maximized"""
        if not self.pending_drag:
            return
        cursor_pos = self.pending_drag
        self.pending_drag = None

        new_x = cursor_pos.x() - self.width() // 2
        new_y = cursor_pos.y() - 10
        self.move(new_x, new_y)
        self.drag_position = QPoint(self.width() // 2, 10)

    def snap_to_left_half(self):
        """Snap window to left half of screen"""
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        half_width = screen_geometry.width() // 2
        new_geometry = QRect(screen_geometry.x(), screen_geometry.y(),
                             half_width, screen_geometry.height())
        self.setGeometry(new_geometry)
        self.last_normal_geometry = new_geometry

    def snap_to_right_half(self):
        """Snap window to right half of screen"""
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        half_width = screen_geometry.width() // 2
        new_geometry = QRect(screen_geometry.x() + half_width, screen_geometry.y(),
                             half_width, screen_geometry.height())
        self.setGeometry(new_geometry)
        self.last_normal_geometry = new_geometry

    # ==========================================================
    #  Indicators & Utilities
    # ==========================================================
    def update_handle_positions(self):
        """Update all resize handle positions based on window size"""
        handle_size = 6
        corner_size = 10

        if not hasattr(self, 'resize_handles'):
            return

        self.resize_handles['top'].setGeometry(0, 0, self.width(), handle_size)
        self.resize_handles['bottom'].setGeometry(
            0, self.height() - handle_size, self.width(), handle_size)
        self.resize_handles['left'].setGeometry(
            0, 0, handle_size, self.height())
        self.resize_handles['right'].setGeometry(
            self.width() - handle_size, 0, handle_size, self.height())
        self.resize_handles['topleft'].setGeometry(0, 0, corner_size, corner_size)
        self.resize_handles['topright'].setGeometry(
            self.width() - corner_size, 0, corner_size, corner_size)
        self.resize_handles['bottomleft'].setGeometry(
            0, self.height() - corner_size, corner_size, corner_size)
        self.resize_handles['bottomright'].setGeometry(
            self.width() - corner_size, self.height() - corner_size, corner_size, corner_size)

        for handle in self.resize_handles.values():
            handle.raise_()

    def show_visual_indicator(self, geometry):
        """Show visual indicator at the specified geometry"""
        window_pos = self.mapFromGlobal(geometry.topLeft())
        self.visual_indicator.setGeometry(QRect(window_pos, geometry.size()))
        self.visual_indicator.show()
        self.visual_indicator.raise_()

    def hide_visual_indicator(self):
        """Hide visual indicator"""
        self.visual_indicator.hide()

    def constrain_cursor_to_screen(self, cursor_pos):
        """Constrain cursor to stay within a percentage of screen height"""
        screen_geometry = QApplication.primaryScreen().geometry()
        max_y = screen_geometry.y() + int(screen_geometry.height() * 0.925)

        constrained_x = max(screen_geometry.left(),
                            min(cursor_pos.x(), screen_geometry.right()))
        constrained_y = max(screen_geometry.top(), min(cursor_pos.y(), max_y))

        if constrained_x != cursor_pos.x() or constrained_y != cursor_pos.y():
            QCursor.setPos(constrained_x, constrained_y)

        return QPoint(constrained_x, constrained_y)
