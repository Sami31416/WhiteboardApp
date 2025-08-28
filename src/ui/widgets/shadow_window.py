from PySide6.QtWidgets import QWidget, QGraphicsDropShadowEffect
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt

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