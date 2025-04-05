import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.components.splash_screen import SplashScreen
from PySide6.QtCore import QTimer

def main():
    app = QApplication(sys.argv)
    
    # Create and show splash screen
    splash = SplashScreen()
    splash.show()
    
    # Create main window
    window = MainWindow()
    
    # Use a timer to show the main window after a delay
    QTimer.singleShot(2000, lambda: (
        window.show(),
        splash.close()
    ))
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 
