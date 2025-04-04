from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
                            QWidget, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QPixmap

class AnimeCard(QFrame):
    clicked = Signal(dict)
    
    def __init__(self, anime_data, image_loader):
        super().__init__()
        self.image_loader = image_loader
        self.image_url = anime_data['image_url']
        self.anime_data = anime_data
        
        self.setStyleSheet("""
            AnimeCard {
                background-color: #1a1a1a;
                border-radius: 12px;
                border: 1px solid #2a2a2a;
            }
            AnimeCard:hover {
                background-color: #2a2a2a;
                border: 1px solid #00b4d8;
            }
            QLabel {
                color: #ffffff;
            }
            .title {
                font-size: 15px;
                font-weight: bold;
                margin-bottom: 8px;
                color: #ffffff;
            }
            .score {
                color: #00b4d8;
                font-weight: bold;
                font-size: 14px;
            }
            .info {
                color: #a0a0a0;
                font-size: 13px;
            }
        """)
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedSize(280, 420)
        
        # Create animation for hover effect
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Image container
        self.image_label = QLabel()
        self.image_label.setFixedSize(280, 380)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #2a2a2a;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }
        """)
        layout.addWidget(self.image_label)
        
        # Info container
        info_container = QWidget()
        info_container.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
                padding: 16px;
            }
        """)
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(16, 16, 16, 16)
        info_layout.setSpacing(8)
        
        # Title
        title = QLabel(anime_data['title'])
        title.setProperty("class", "title")
        title.setWordWrap(True)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(title)
        
        # Score and info row
        info_row = QHBoxLayout()
        info_row.setSpacing(12)
        
        # Score
        score = float(anime_data['score']) if anime_data['score'] != 'N/A' else 0
        score_label = QLabel(f"★ {score:.1f}" if score else "★ N/A")
        score_label.setProperty("class", "score")
        info_row.addWidget(score_label)
        
        # Episodes
        episodes = QLabel(f"{anime_data['episodes']} eps")
        episodes.setProperty("class", "info")
        info_row.addWidget(episodes)
        
        # Status
        status = QLabel(anime_data['status'])
        status.setProperty("class", "info")
        info_row.addWidget(status)
        
        info_layout.addLayout(info_row)
        layout.addWidget(info_container)
        
        # Request image loading
        if self.image_url:
            self.image_loader.image_loaded.connect(self.on_image_loaded)
            self.image_loader.enqueue(self.image_url, (280, 380))
    
    def enterEvent(self, event):
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(self.pos() + QPoint(0, -10))
        self.animation.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(self.pos() + QPoint(0, 10))
        self.animation.start()
        super().leaveEvent(event)
    
    def on_image_loaded(self, url, pixmap):
        if url == self.image_url:
            self.image_label.setPixmap(pixmap)
    
    def mousePressEvent(self, event):
        self.clicked.emit(self.anime_data)
        super().mousePressEvent(event) 
