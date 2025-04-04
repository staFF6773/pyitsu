class Anime:
    def __init__(self, data):
        self.title = data.get("title", "Unknown Title")
        self.image_url = data.get("image_url", "")
        self.score = data.get("score", "N/A")
        self.synopsis = data.get("synopsis", "No synopsis available")
        self.episodes = data.get("episodes", "N/A")
        self.status = data.get("status", "Unknown")
        self.aired = data.get("aired", "Unknown")
        
    def to_dict(self):
        return {
            "title": self.title,
            "image_url": self.image_url,
            "score": self.score,
            "synopsis": self.synopsis,
            "episodes": self.episodes,
            "status": self.status,
            "aired": self.aired
        } 
