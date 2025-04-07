# pyitsu - Anime Information Desktop Application

A modern desktop application for browsing and searching anime information. Built with Python.

## Features
- Search anime by title 
- View detailed anime information
- Modern and user-friendly interface
- Automatic data fetching from MyAnimeList
- Responsive UI with custom styling

## Installation
1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run the application:
```bash
python src/main.py
```

## Dependencies
- PySide6: For the modern GUI interface
- requests: For API communication
- python-dotenv: For environment variable management
- Pillow: For image handling

## Project Structure
```
pyitsu/
├── src/
│ ├── main.py # Application entry point
│ ├── ui/ # User interface components
│ │ ├── main_window.py # Main window implementation
│ │ └── components/ # UI components
│ ├── api/ # API integration
│ │ └── jikan_client.py # Jikan API client for MyAnimeList
│ ├── models/ # Data models
│ │ └── anime.py # Anime data model
│ └── resources/ # Application resources
│ ├── icons/ # Application icons
│ └── fonts/ # Custom fonts
├── requirements.txt # Project dependencies
└── README.md # Project documentation
```

## Contributing
Feel free to submit issues and enhancement requests! 
