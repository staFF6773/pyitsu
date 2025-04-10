from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLineEdit, QPushButton, QLabel, QScrollArea,
                            QFrame, QGridLayout, QSplitter, QDialog, QCheckBox,
                            QComboBox, QSpinBox, QFormLayout, QMenuBar, QMenu, QStatusBar)
from PySide6.QtCore import Qt, QThread, Signal, QSize, QPoint
from PySide6.QtGui import QPixmap, QImage, QIcon
import requests
from io import BytesIO
from PIL import Image
from api.jikan_client import JikanClient
import queue
import threading
import os

from .components.anime_card import AnimeCard
from .components.loading_overlay import LoadingOverlay
from .components.search_thread import SearchThread
from .components.image_loader import ImageLoader

class ImageLoader(QThread):
    image_loaded = Signal(str, QPixmap)
    
    def __init__(self, parent):
        super().__init__(parent)
        self.queue = queue.Queue()
        self.running = True
    
    def enqueue(self, url, size):
        self.queue.put((url, size))
    
    def stop(self):
        self.running = False
        self.queue.put((None, None))
    
    def run(self):
        while self.running:
            try:
                url, size = self.queue.get(timeout=1)
                if url is None:
                    break
                    
                response = requests.get(url)
                image = Image.open(BytesIO(response.content))
                image = image.resize(size, Image.Resampling.LANCZOS)
                image = image.convert("RGBA")
                data = image.tobytes("raw", "RGBA")
                qim = QImage(data, image.size[0], image.size[1], QImage.Format.Format_RGBA8888)
                pixmap = QPixmap.fromImage(qim)
                
                self.image_loaded.emit(url, pixmap)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error loading image: {e}")

class AnimeCard(QFrame):
    clicked = Signal(dict)
    
    def __init__(self, anime_data, image_loader):
        super().__init__()
        self.image_loader = image_loader
        self.image_url = anime_data['image_url']
        self.anime_data = anime_data
        
        self.setStyleSheet("""
            AnimeCard {
                background-color: #3c3f41;
                border-radius: 12px;
                padding: 15px;
                margin: 8px;
            }
            AnimeCard:hover {
                background-color: #454749;
                cursor: pointer;
            }
            QLabel {
                color: white;
            }
            .title {
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 8px;
            }
            .score {
                color: #4CAF50;
                font-weight: bold;
            }
        """)
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Title
        title = QLabel(anime_data['title'])
        title.setProperty("class", "title")
        title.setWordWrap(True)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Image placeholder
        self.image_label = QLabel()
        self.image_label.setFixedSize(200, 300)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #2b2b2b;
                border-radius: 8px;
            }
        """)
        
        # Loading text
        loading_label = QLabel("loading...")
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setText("loading...")
        layout.addWidget(self.image_label)
        
        # Info container
        info_container = QFrame()
        info_layout = QVBoxLayout(info_container)
        info_layout.setSpacing(5)
        
        # Score with star emoji
        score = float(anime_data['score']) if anime_data['score'] != 'N/A' else 0
        score_label = QLabel(f"★ {score:.1f}/100" if score else "★ N/A")
        score_label.setProperty("class", "score")
        score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(score_label)
        
        # Episodes
        episodes = QLabel(f"Episodes: {anime_data['episodes']}")
        episodes.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(episodes)
        
        # Status
        status = QLabel(f"Status: {anime_data['status']}")
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(status)
        
        layout.addWidget(info_container)
        
        # Request image loading
        if self.image_url:
            self.image_loader.image_loaded.connect(self.on_image_loaded)
            self.image_loader.enqueue(self.image_url, (200, 300))
    
    def on_image_loaded(self, url, pixmap):
        if url == self.image_url:
            self.image_label.setPixmap(pixmap)

    def mousePressEvent(self, event):
        self.clicked.emit(self.anime_data)
        super().mousePressEvent(event)

class SearchThread(QThread):
    results_ready = Signal(list)
    
    def __init__(self, query, parent):
        super().__init__(parent)
        self.query = query
        
    def run(self):
        client = JikanClient()
        if self.query == "":
            results = client.get_top_anime()
        else:
            results = client.search_anime(self.query)
        self.results_ready.emit(results)

class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 0.7);
            }
            QLabel {
                color: white;
                font-size: 18px;
                background-color: transparent;
            }
        """)
        layout = QVBoxLayout(self)
        label = QLabel("Looking for anime...")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        self.hide()

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        self.setStyleSheet("""
            QDialog {
                background-color: #0a0a0a;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QCheckBox {
                color: #ffffff;
                font-size: 14px;
            }
            QComboBox {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #2a2a2a;
                border-radius: 4px;
                padding: 5px;
                min-width: 150px;
            }
            QComboBox:focus {
                border: 1px solid #00b4d8;
            }
            QSpinBox {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #2a2a2a;
                border-radius: 4px;
                padding: 5px;
                min-width: 100px;
            }
            QSpinBox:focus {
                border: 1px solid #00b4d8;
            }
            QPushButton {
                background-color: #00b4d8;
                color: #ffffff;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #0096c7;
            }
            QPushButton:pressed {
                background-color: #0077b6;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Configuration form
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        # Option to show score
        self.show_score = QCheckBox("Show score")
        self.show_score.setChecked(True)
        form_layout.addRow("Display:", self.show_score)
        
        # Option to show episodes
        self.show_episodes = QCheckBox("Show episodes")
        self.show_episodes.setChecked(True)
        form_layout.addRow("", self.show_episodes)
        
        # Option to show status
        self.show_status = QCheckBox("Show status")
        self.show_status.setChecked(True)
        form_layout.addRow("", self.show_status)
        
        # Option to sort by
        self.sort_by = QComboBox()
        self.sort_by.addItems(["Score", "Title", "Episodes", "Status"])
        form_layout.addRow("Sort by:", self.sort_by)
        
        # Option for cards per row
        self.cards_per_row = QSpinBox()
        self.cards_per_row.setRange(1, 6)
        self.cards_per_row.setValue(4)
        form_layout.addRow("Cards per row:", self.cards_per_row)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        buttons_layout.addWidget(save_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)
        
        layout.addLayout(buttons_layout)

class FloatingConfigButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 50)
        
        # Cargar el icono SVG
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "icons", "Setting-icon.svg")
        self.setIcon(QIcon(icon_path))
        self.setIconSize(QSize(24, 24))
        
        self.setStyleSheet("""
            QPushButton {
                background-color: #00b4d8;
                color: white;
                border: none;
                border-radius: 25px;
            }
            QPushButton:hover {
                background-color: #0096c7;
            }
            QPushButton:pressed {
                background-color: #0077b6;
            }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.move(self.pos() + QPoint(0, 2))
        
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.move(self.pos() - QPoint(0, 2))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pyitsu")
        self.setMinimumSize(1400, 900)
        
        # Default configuration
        self.config = {
            "show_score": True,
            "show_episodes": True,
            "show_status": True,
            "sort_by": "Score",
            "cards_per_row": 4
        }
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0a0a;
            }
            QWidget {
                background-color: #0a0a0a;
                color: #ffffff;
            }
            QLineEdit {
                padding: 16px;
                border-radius: 8px;
                border: 1px solid #2a2a2a;
                background-color: #1a1a1a;
                color: #ffffff;
                font-size: 15px;
            }
            QLineEdit:focus {
                border: 1px solid #00b4d8;
            }
            QPushButton {
                background-color: #00b4d8;
                color: #ffffff;
                border: none;
                padding: 16px 32px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #0096c7;
            }
            QPushButton:pressed {
                background-color: #0077b6;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
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
        
        # Initialize image loader
        self.image_loader = ImageLoader(self)
        self.image_loader.start()
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(60, 30, 60, 30)
        main_layout.setSpacing(30)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #0a0a0a;
                color: #ffffff;
                border-top: 1px solid #2a2a2a;
            }
        """)
        
        # Header section
        header = QWidget()
        header.setFixedHeight(140)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(20)
        
        # Top row (title and back button)
        top_row = QWidget()
        top_row_layout = QHBoxLayout(top_row)
        top_row_layout.setContentsMargins(0, 0, 0, 0)
        top_row_layout.setSpacing(0)
        
        # Title container
        title_container = QWidget()
        title_container.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border-bottom: 2px solid #00b4d8;
                padding-bottom: 10px;
            }
        """)
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        
        # Title
        title_label = QLabel("Pyitsu")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 42px;
                font-weight: bold;
                color: #ffffff;
                letter-spacing: 2px;
            }
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        top_row_layout.addWidget(title_container)
        
        # Back button (initially hidden)
        self.back_button = QPushButton("← Back")
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #00b4d8;
                border: 2px solid #00b4d8;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #00b4d8;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #0096c7;
            }
        """)
        self.back_button.clicked.connect(self.go_home)
        self.back_button.hide()
        top_row_layout.addWidget(self.back_button)
        
        header_layout.addWidget(top_row)
        
        # Search container
        search_container = QWidget()
        search_container.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(15)
        
        # Search icon
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("""
            QLabel {
                font-size: 20px;
                color: #00b4d8;
                padding: 0 10px;
            }
        """)
        search_layout.addWidget(search_icon)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search anime...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 15px;
                border-radius: 8px;
                border: 2px solid #2a2a2a;
                background-color: #1a1a1a;
                color: #ffffff;
                font-size: 16px;
                min-width: 400px;
            }
            QLineEdit:focus {
                border: 2px solid #00b4d8;
                background-color: #2a2a2a;
            }
        """)
        self.search_input.returnPressed.connect(self.search_anime)
        search_layout.addWidget(self.search_input)
        
        # Search button
        search_button = QPushButton("Search")
        search_button.setStyleSheet("""
            QPushButton {
                background-color: #00b4d8;
                color: #ffffff;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #0096c7;
            }
            QPushButton:pressed {
                background-color: #0077b6;
            }
        """)
        search_button.clicked.connect(self.search_anime)
        search_layout.addWidget(search_button)
        
        # Add search container to header
        header_layout.addWidget(search_container)
        
        main_layout.addWidget(header)
        
        # Content area
        self.content_area = QScrollArea()
        self.content_area.setWidgetResizable(True)
        self.content_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(30)
        
        self.content_area.setWidget(content_widget)
        main_layout.addWidget(self.content_area)
        
        # Floating config button
        self.config_button = FloatingConfigButton(self)
        self.config_button.clicked.connect(self.show_config)
        self.config_button.move(self.width() - 70, self.height() - 70)
        
        # Loading overlay
        self.loading_overlay = LoadingOverlay(self)
        self.loading_overlay.setGeometry(0, 0, self.width(), self.height())
        
        # Show initial top anime
        self.search_anime()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.loading_overlay.resize(self.size())
        # Reposition config button
        self.config_button.move(self.width() - 70, self.height() - 70)
    
    def show_config(self):
        dialog = ConfigDialog(self)
        
        # Establecer valores actuales
        dialog.show_score.setChecked(self.config["show_score"])
        dialog.show_episodes.setChecked(self.config["show_episodes"])
        dialog.show_status.setChecked(self.config["show_status"])
        dialog.sort_by.setCurrentText(self.config["sort_by"])
        dialog.cards_per_row.setValue(self.config["cards_per_row"])
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Guardar configuración
            self.config["show_score"] = dialog.show_score.isChecked()
            self.config["show_episodes"] = dialog.show_episodes.isChecked()
            self.config["show_status"] = dialog.show_status.isChecked()
            self.config["sort_by"] = dialog.sort_by.currentText()
            self.config["cards_per_row"] = dialog.cards_per_row.value()
            
            # Actualizar la vista actual
            self.refresh_current_view()
    
    def refresh_current_view(self):
        # Si estamos en la vista de detalles, volver a cargar los detalles
        if self.back_button.isVisible():
            # Obtener el ID del anime actual
            for i in range(self.content_layout.count()):
                widget = self.content_layout.itemAt(i).widget()
                if hasattr(widget, 'anime_data'):
                    self.show_anime_details(widget.anime_data)
                    break
        else:
            # Si estamos en la vista principal, volver a cargar los resultados
            self.search_anime()
    
    def go_home(self):
        self.back_button.hide()
        self.search_input.clear()
        self.search_anime()
        
    def search_anime(self):
        query = self.search_input.text()
        
        # Show loading overlay
        self.loading_overlay.show()
            
        # Clear previous results
        for i in reversed(range(self.content_layout.count())): 
            self.content_layout.itemAt(i).widget().setParent(None)
            
        # Start search thread
        self.search_thread = SearchThread(query, self)
        self.search_thread.results_ready.connect(self.display_results)
        self.search_thread.start()
        
    def display_results(self, results):
        # Clear previous content
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Sort results according to configuration
        if self.config["sort_by"] == "Score":
            results = sorted(results, key=lambda x: float(x['score']) if x['score'] != 'N/A' else 0, reverse=True)
        elif self.config["sort_by"] == "Title":
            results = sorted(results, key=lambda x: x['title'])
        elif self.config["sort_by"] == "Episodes":
            results = sorted(results, key=lambda x: int(x['episodes']) if x['episodes'] != '?' else 0)
        elif self.config["sort_by"] == "Status":
            results = sorted(results, key=lambda x: x['status'])
        
        # Create grid layout for anime cards
        grid = QWidget()
        grid_layout = QGridLayout(grid)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(30)
        
        row = 0
        col = 0
        for anime in results:
            card = AnimeCard(anime, self.image_loader)
            card.clicked.connect(self.show_anime_details)
            
            # Apply display configuration
            if not self.config["show_score"]:
                for i in range(card.layout().count()):
                    widget = card.layout().itemAt(i).widget()
                    if isinstance(widget, QFrame) and widget.layout():
                        for j in range(widget.layout().count()):
                            child = widget.layout().itemAt(j).widget()
                            if isinstance(child, QLabel) and "★" in child.text():
                                child.hide()
            
            if not self.config["show_episodes"]:
                for i in range(card.layout().count()):
                    widget = card.layout().itemAt(i).widget()
                    if isinstance(widget, QFrame) and widget.layout():
                        for j in range(widget.layout().count()):
                            child = widget.layout().itemAt(j).widget()
                            if isinstance(child, QLabel) and "Episodes:" in child.text():
                                child.hide()
            
            if not self.config["show_status"]:
                for i in range(card.layout().count()):
                    widget = card.layout().itemAt(i).widget()
                    if isinstance(widget, QFrame) and widget.layout():
                        for j in range(widget.layout().count()):
                            child = widget.layout().itemAt(j).widget()
                            if isinstance(child, QLabel) and "Status:" in child.text():
                                child.hide()
            
            grid_layout.addWidget(card, row, col)
            col += 1
            if col >= self.config["cards_per_row"]:
                col = 0
                row += 1
        
        self.content_layout.addWidget(grid)
        
        # Update status bar
        self.status_bar.showMessage(f"Found {len(results)} results")
        
        # Hide loading overlay
        self.loading_overlay.hide()
    
    def show_anime_details(self, anime_data):
        # Clear previous content
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Show back button
        self.back_button.show()
        
        # Show loading overlay
        self.loading_overlay.show()
        
        # Fetch complete anime details
        client = JikanClient()
        complete_details = client.get_anime_details(anime_data['id'])
        
        if complete_details:
            # Create and show details view with complete data
            from .components.anime_details import AnimeDetails
            details_view = AnimeDetails(complete_details, self.image_loader)
            self.content_layout.addWidget(details_view)
        else:
            # If we can't get complete details, show a message
            error_label = QLabel("Anime details could not be loaded")
            error_label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 16px;
                    text-align: center;
                }
            """)
            self.content_layout.addWidget(error_label)
        
        # Hide loading overlay
        self.loading_overlay.hide()
    
    def closeEvent(self, event):
        self.image_loader.stop()
        self.image_loader.wait()
        super().closeEvent(event)

    def create_menu_bar(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #0a0a0a;
                color: #ffffff;
                border-bottom: 1px solid #2a2a2a;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 12px;
            }
            QMenuBar::item:selected {
                background-color: #2a2a2a;
            }
            QMenu {
                background-color: #0a0a0a;
                color: #ffffff;
                border: 1px solid #2a2a2a;
            }
            QMenu::item {
                padding: 8px 20px;
            }
            QMenu::item:selected {
                background-color: #2a2a2a;
            }
        """)
