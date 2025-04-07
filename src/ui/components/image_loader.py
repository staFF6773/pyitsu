from PySide6.QtCore import QThread, Signal, QSize
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QWidget
import requests
from io import BytesIO
from PIL import Image
import queue
import threading
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
import time
from .error_handler import ErrorHandler

class ImageLoader(QThread):
    image_loaded = Signal(str, QPixmap)
    
    def __init__(self, parent: QWidget = None, max_workers=4, cache_size=100):
        super().__init__()
        self.queue = queue.Queue()
        self.running = True
        self.parent = parent
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.cache_size = cache_size
        self._load_image = lru_cache(maxsize=cache_size)(self._load_image_impl)
        self.lock = threading.Lock()
    
    def enqueue(self, url, size):
        """Enqueue an image to be loaded with the specified size."""
        if not url:
            return
        self.queue.put((url, size))
    
    def stop(self):
        """Stop the image loader and cleanup resources."""
        self.running = False
        self.queue.put((None, None))
        self.executor.shutdown(wait=True)
    
    @staticmethod
    def _optimize_image_size(image: Image.Image, target_size: tuple) -> Image.Image:
        """Optimize image size before loading into memory."""
        # Calculate the scaling factor
        width_ratio = target_size[0] / image.size[0]
        height_ratio = target_size[1] / image.size[1]
        scale_factor = min(width_ratio, height_ratio)
        
        # Only resize if the image is larger than target
        if scale_factor < 1:
            new_size = (int(image.size[0] * scale_factor), int(image.size[1] * scale_factor))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        return image
    
    def _load_image_impl(self, url: str, size: tuple) -> QPixmap:
        """Internal method to load an image with retries."""
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                image = Image.open(BytesIO(response.content))
                image = self._optimize_image_size(image, size)
                image = image.convert("RGBA")
                
                data = image.tobytes("raw", "RGBA")
                qim = QImage(data, image.size[0], image.size[1], QImage.Format.Format_RGBA8888)
                return QPixmap.fromImage(qim)
                
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
    
    def _process_image(self, url: str, size: tuple):
        """Process a single image loading task."""
        try:
            pixmap = self._load_image(url, size)
            self.image_loaded.emit(url, pixmap)
        except Exception as e:
            ErrorHandler.handle_image_error(self.parent, e)
    
    def run(self):
        """Main thread loop for processing image loading tasks."""
        while self.running:
            try:
                url, size = self.queue.get(timeout=1)
                if url is None:
                    break
                
                # Submit the task to the thread pool
                self.executor.submit(self._process_image, url, size)
                
            except queue.Empty:
                continue
            except Exception as e:
                ErrorHandler.handle_image_error(self.parent, e) 
