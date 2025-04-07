from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QWidget
from api.jikan_client import JikanClient
from .error_handler import ErrorHandler

class SearchThread(QThread):
    results_ready = Signal(list)
    
    def __init__(self, query, parent=None, page_limit=20):
        super().__init__(parent)
        self.query = query
        self.page_limit = page_limit
        
    def run(self):
        try:
            client = JikanClient(page_limit=self.page_limit)
            if self.query == "":
                results = client.get_top_anime()
            else:
                results = client.search_anime(self.query)
            self.results_ready.emit(results)
        except Exception as e:
            ErrorHandler.handle_api_error(self.parent, e)
            self.results_ready.emit([])
