from PySide6.QtWidgets import QMessageBox, QWidget
from PySide6.QtCore import Qt

class ErrorHandler:
    @staticmethod
    def show_error(parent: QWidget, title: str, message: str, details: str = None):
        """Shows an error message to the user"""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        if details:
            msg.setDetailedText(details)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #1e1e1e;
            }
            QMessageBox QLabel {
                color: white;
            }
            QMessageBox QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QMessageBox QPushButton:hover {
                background-color: #45a049;
            }
        """)
        msg.exec()

    @staticmethod
    def handle_api_error(parent: QWidget, error: Exception):
        """Handles API specific errors"""
        error_message = str(error)
        if "connection" in error_message.lower():
            ErrorHandler.show_error(
                parent,
                "Connection Error",
                "Could not connect to the server. Please check your internet connection.",
                f"Details: {error_message}"
            )
        elif "timeout" in error_message.lower():
            ErrorHandler.show_error(
                parent,
                "Request Timeout",
                "The request took too long to respond. Please try again.",
                f"Details: {error_message}"
            )
        else:
            ErrorHandler.show_error(
                parent,
                "API Error",
                "An error occurred while fetching data. Please try again.",
                f"Details: {error_message}"
            )

    @staticmethod
    def handle_image_error(parent: QWidget, error: Exception):
        """Handles image loading specific errors"""
        ErrorHandler.show_error(
            parent,
            "Image Error",
            "Could not load the image. A placeholder will be shown instead.",
            f"Details: {str(error)}"
        )
