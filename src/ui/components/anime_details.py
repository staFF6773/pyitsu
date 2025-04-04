from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QScrollArea, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QImage, QPainter
import requests
from io import BytesIO
from PIL import Image

class AnimeDetails(QWidget):
    def __init__(self, anime_data, image_loader):
        super().__init__()
        self.anime_data = anime_data
        self.image_loader = image_loader
        
        self.setStyleSheet("""
            QWidget {
                background-color: #0a0a0a;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            .title {
                font-size: 36px;
                font-weight: bold;
                color: #ffffff;
            }
            .subtitle {
                font-size: 24px;
                color: #00b4d8;
            }
            .info-label {
                font-size: 16px;
                color: #ffffff;
            }
            .info-value {
                font-size: 16px;
                color: #00b4d8;
            }
            .synopsis {
                font-size: 16px;
                color: #ffffff;
                line-height: 1.6;
            }
            .genre-tag {
                background-color: #00b4d8;
                color: #ffffff;
                padding: 6px 12px;
                border-radius: 15px;
                font-size: 14px;
                margin: 4px;
            }
            .section-title {
                font-size: 20px;
                font-weight: bold;
                color: #ffffff;
                margin-top: 20px;
                margin-bottom: 10px;
            }
        """)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
                padding-right: 20px;
            }
            QScrollBar:vertical {
                border: none;
                background: #1a1a1a;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #00b4d8;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(30)
        
        # Top section with cover image and basic info
        top_section = QWidget()
        top_layout = QHBoxLayout(top_section)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(40)
        
        # Cover image
        cover_container = QWidget()
        cover_container.setFixedSize(400, 600)
        cover_container.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 12px;
                overflow: hidden;
            }
        """)
        cover_layout = QVBoxLayout(cover_container)
        cover_layout.setContentsMargins(0, 0, 0, 0)
        
        self.cover_label = QLabel()
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_label.setFixedSize(400, 600)
        self.cover_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
            }
        """)
        cover_layout.addWidget(self.cover_label)
        
        # Load cover image
        if self.anime_data.get('cover_url'):
            self.image_loader.image_loaded.connect(self.on_cover_loaded)
            self.image_loader.enqueue(self.anime_data['cover_url'], (400, 600))
        
        # Info section
        info_section = QWidget()
        info_layout = QVBoxLayout(info_section)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(20)
        
        # Title
        title_label = QLabel(self.anime_data['title'])
        title_label.setProperty("class", "title")
        title_label.setWordWrap(True)
        info_layout.addWidget(title_label)
        
        # Alternative titles
        if self.anime_data.get('title_english') or self.anime_data.get('title_japanese'):
            alt_titles = []
            if self.anime_data.get('title_english'):
                alt_titles.append(f"English: {self.anime_data['title_english']}")
            if self.anime_data.get('title_japanese'):
                alt_titles.append(f"Japanese: {self.anime_data['title_japanese']}")
            
            alt_title_label = QLabel(" | ".join(alt_titles))
            alt_title_label.setProperty("class", "subtitle")
            alt_title_label.setWordWrap(True)
            info_layout.addWidget(alt_title_label)
        
        # Score and rank
        score_section = QWidget()
        score_layout = QHBoxLayout(score_section)
        score_layout.setContentsMargins(0, 0, 0, 0)
        score_layout.setSpacing(20)
        
        if self.anime_data.get('score'):
            score_label = QLabel(f"★ {self.anime_data['score']}")
            score_label.setProperty("class", "info-value")
            score_layout.addWidget(score_label)
            
            if self.anime_data.get('scored_by'):
                scored_by = QLabel(f"({self.anime_data['scored_by']:,} votos)")
                scored_by.setProperty("class", "info-label")
                score_layout.addWidget(scored_by)
        
        if self.anime_data.get('rank'):
            rank_label = QLabel(f"Rank #{self.anime_data['rank']}")
            rank_label.setProperty("class", "info-value")
            score_layout.addWidget(rank_label)
        
        score_layout.addStretch()
        info_layout.addWidget(score_section)
        
        # Info grid
        info_grid = QWidget()
        grid_layout = QHBoxLayout(info_grid)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(40)
        
        # Left column
        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)
        
        # Right column
        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        # Add info items
        info_items = [
            ('Tipo', 'type'),
            ('Episodios', 'episodes'),
            ('Estado', 'status'),
            ('Emitido', 'aired'),
            ('Duración', 'duration'),
            ('Clasificación', 'rating'),
            ('Estudio', 'studios'),
            ('Fuente', 'source'),
            ('Géneros', 'genres'),
            ('Temas', 'themes'),
            ('Demografía', 'demographics')
        ]
        
        for i, (label, key) in enumerate(info_items):
            if self.anime_data.get(key):
                layout_to_use = left_layout if i < len(info_items) // 2 else right_layout
                value = self.anime_data[key]
                
                if isinstance(value, list):
                    value = ", ".join(value)
                
                info_item = QWidget()
                item_layout = QHBoxLayout(info_item)
                item_layout.setContentsMargins(0, 0, 0, 0)
                item_layout.setSpacing(10)
                
                label_widget = QLabel(f"{label}:")
                label_widget.setProperty("class", "info-label")
                value_widget = QLabel(str(value))
                value_widget.setProperty("class", "info-value")
                value_widget.setWordWrap(True)
                
                item_layout.addWidget(label_widget)
                item_layout.addWidget(value_widget)
                item_layout.addStretch()
                
                layout_to_use.addWidget(info_item)
        
        grid_layout.addWidget(left_column)
        grid_layout.addWidget(right_column)
        info_layout.addWidget(info_grid)
        
        # Add sections to top layout
        top_layout.addWidget(cover_container)
        top_layout.addWidget(info_section)
        
        content_layout.addWidget(top_section)
        
        # Synopsis section
        if self.anime_data.get('synopsis'):
            synopsis_title = QLabel("Sinopsis")
            synopsis_title.setProperty("class", "section-title")
            content_layout.addWidget(synopsis_title)
            
            synopsis_container = QWidget()
            synopsis_container_layout = QVBoxLayout(synopsis_container)
            synopsis_container_layout.setContentsMargins(0, 0, 20, 0)
            
            synopsis = QLabel(self.anime_data['synopsis'])
            synopsis.setProperty("class", "synopsis")
            synopsis.setWordWrap(True)
            synopsis.setAlignment(Qt.AlignmentFlag.AlignJustify)
            synopsis.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            synopsis.setStyleSheet("""
                QLabel {
                    padding-right: 20px;
                }
            """)
            synopsis_container_layout.addWidget(synopsis)
            
            content_layout.addWidget(synopsis_container)
        
        # Background section
        if self.anime_data.get('background'):
            background_title = QLabel("Información Adicional")
            background_title.setProperty("class", "section-title")
            content_layout.addWidget(background_title)
            
            background_container = QWidget()
            background_container_layout = QVBoxLayout(background_container)
            background_container_layout.setContentsMargins(0, 0, 20, 0)
            
            background = QLabel(self.anime_data['background'])
            background.setProperty("class", "synopsis")
            background.setWordWrap(True)
            background.setAlignment(Qt.AlignmentFlag.AlignJustify)
            background.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            background.setStyleSheet("""
                QLabel {
                    padding-right: 20px;
                }
            """)
            background_container_layout.addWidget(background)
            
            content_layout.addWidget(background_container)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
    
    def on_cover_loaded(self, url, pixmap):
        if url == self.anime_data.get('cover_url'):
            # Calculate the scaled size maintaining aspect ratio
            original_size = pixmap.size()
            target_size = QSize(400, 600)
            
            # Calculate the scaling factor
            width_ratio = target_size.width() / original_size.width()
            height_ratio = target_size.height() / original_size.height()
            scale_factor = min(width_ratio, height_ratio)
            
            # Calculate the new size
            new_width = int(original_size.width() * scale_factor)
            new_height = int(original_size.height() * scale_factor)
            
            # Scale the pixmap
            scaled_pixmap = pixmap.scaled(
                new_width, 
                new_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Create a new pixmap with the target size and transparent background
            final_pixmap = QPixmap(target_size)
            final_pixmap.fill(Qt.GlobalColor.transparent)
            
            # Calculate the position to center the scaled image
            x = (target_size.width() - new_width) // 2
            y = (target_size.height() - new_height) // 2
            
            # Paint the scaled image onto the final pixmap
            painter = QPainter(final_pixmap)
            painter.drawPixmap(x, y, scaled_pixmap)
            painter.end()
            
            self.cover_label.setPixmap(final_pixmap) 
