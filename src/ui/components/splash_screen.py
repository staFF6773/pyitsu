from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QPainter, QColor

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Set fixed size
        self.setFixedSize(400, 300)
        
        # Center the window
        screen = self.screen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
        
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Create loading text
        self.loading_label = QLabel("Loading Pyitsu ...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 20px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.loading_label)
        
        # Create dots animation
        self.dots = ""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_dots)
        self.timer.start(500)  # Update every 500ms
        
        # Set style
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(10, 10, 10, 0.95);
                border-radius: 15px;
                border: 2px solid #00b4d8;
            }
        """)
    
    def update_dots(self):
        self.dots = self.dots + "." if len(self.dots) < 3 else ""
        self.loading_label.setText(f"Loading Pyitsu {self.dots}")
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background with rounded corners
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(10, 10, 10, 242))  # 95% opacity
        painter.drawRoundedRect(self.rect(), 15, 15)
        
        # Draw border
        painter.setPen(QColor("#00b4d8"))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 15, 15) 
