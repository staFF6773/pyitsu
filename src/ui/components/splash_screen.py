from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                              QProgressBar, QFrame)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QPainter, QColor, QLinearGradient, QGradient

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Set fixed size
        self.setFixedSize(500, 350)
        
        # Center the window
        screen = self.screen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
        
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Add logo placeholder
        self.logo_label = QLabel()
        # TODO: Replace with your actual logo
        self.logo_label.setFixedSize(120, 120)
        self.logo_label.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 60px;
            }
        """)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Create loading text
        self.loading_label = QLabel("PYITSU")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
                letter-spacing: 2px;
            }
        """)
        layout.addWidget(self.loading_label)
        
        # Add status message
        self.status_label = QLabel("Starting...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.7);
                font-size: 14px;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 2px;
                border: none;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00b4d8, stop:1 #48cae4);
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Initialize progress animation
        self.progress_value = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(30)
        
        # Set window style
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(15, 15, 15, 0.98);
                border-radius: 20px;
            }
        """)
    
    def update_progress(self):
        self.progress_value = (self.progress_value + 1) % 101
        self.progress_bar.setValue(self.progress_value)
        
        # Update status message based on progress
        if self.progress_value < 30:
            self.status_label.setText("Loading resources...")
        elif self.progress_value < 60:
            self.status_label.setText("Initializing components...")
        elif self.progress_value < 90:
            self.status_label.setText("Preparing interface...")
        else:
            self.status_label.setText("Completing...")
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Create gradient background
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(15, 15, 15, 250))
        gradient.setColorAt(1, QColor(25, 25, 25, 250))
        
        # Draw background with rounded corners
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawRoundedRect(self.rect(), 20, 20)
        
        # Draw subtle border
        painter.setPen(QColor(255, 255, 255, 30))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 20, 20) 
