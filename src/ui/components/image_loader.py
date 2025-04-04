from PySide6.QtCore import QThread, Signal, QSize
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QWidget
import requests
from io import BytesIO
from PIL import Image
import queue
from .error_handler import ErrorHandler

class ImageLoader(QThread):
    image_loaded = Signal(str, QPixmap)
    
    def __init__(self, parent: QWidget = None):
        super().__init__()
        self.queue = queue.Queue()
        self.running = True
        self.parent = parent
    
    def enqueue(self, url, size):
        self.queue.put((url, size))
    
    def stop(self):
        self.running = False
        self.queue.put((None, None))  #
    
    def run(self):
        while self.running:
            try:
                url, size = self.queue.get(timeout=1)
                if url is None:  #
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
                ErrorHandler.handle_image_error(self.parent, e) 
