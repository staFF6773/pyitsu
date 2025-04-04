import requests

class JikanClient:
    BASE_URL = "https://kitsu.io/api/edge"
    
    def get_top_anime(self):
        try:
            headers = {
                'Accept': 'application/vnd.api+json',
                'Content-Type': 'application/vnd.api+json'
            }
            
            response = requests.get(
                f"{self.BASE_URL}/anime", 
                params={
                    "sort": "-averageRating",
                    "page[limit]": 9
                },
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for anime in data.get("data", []):
                attributes = anime.get("attributes", {})
                results.append({
                    "id": anime.get("id"),
                    "title": attributes.get("canonicalTitle", "Unknown Title"),
                    "image_url": attributes.get("posterImage", {}).get("original", ""),
                    "score": attributes.get("averageRating", "N/A"),
                    "synopsis": attributes.get("synopsis", "No synopsis available"),
                    "episodes": attributes.get("episodeCount", "N/A"),
                    "status": attributes.get("status", "Unknown"),
                    "aired": f"{attributes.get('startDate', 'Unknown')} to {attributes.get('endDate', 'Unknown')}"
                })
            return results
        except requests.exceptions.RequestException as e:
            print(f"Error fetching top anime: {e}")
            return []
    
    def search_anime(self, query):
        try:
            if not query or query.strip() == "":
                return []
            
            headers = {
                'Accept': 'application/vnd.api+json',
                'Content-Type': 'application/vnd.api+json'
            }
            
            response = requests.get(
                f"{self.BASE_URL}/anime", 
                params={
                    "filter[text]": query,
                    "page[limit]": 9
                },
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for anime in data.get("data", []):
                attributes = anime.get("attributes", {})
                results.append({
                    "id": anime.get("id"),
                    "title": attributes.get("canonicalTitle", "Unknown Title"),
                    "image_url": attributes.get("posterImage", {}).get("original", ""),
                    "score": attributes.get("averageRating", "N/A"),
                    "synopsis": attributes.get("synopsis", "No synopsis available"),
                    "episodes": attributes.get("episodeCount", "N/A"),
                    "status": attributes.get("status", "Unknown"),
                    "aired": f"{attributes.get('startDate', 'Unknown')} to {attributes.get('endDate', 'Unknown')}"
                })
            return results
        except requests.exceptions.RequestException as e:
            print(f"Error fetching anime data: {e}")
            return []

    def get_anime_details(self, anime_id: int) -> dict:
        """Get detailed information about a specific anime."""
        try:
            headers = {
                'Accept': 'application/vnd.api+json',
                'Content-Type': 'application/vnd.api+json'
            }
            
            response = requests.get(
                f"{self.BASE_URL}/anime/{anime_id}",
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get('data'):
                return None
                
            anime = data['data']
            attributes = anime.get('attributes', {})
            
            # Extract images
            poster_image = attributes.get('posterImage', {})
            cover_image = attributes.get('coverImage', {})
            
            # Extract genres
            genres = []
            if 'genres' in data.get('included', []):
                for item in data['included']:
                    if item['type'] == 'genres':
                        genres.append(item['attributes']['name'])
            
            # Extract categories (themes)
            themes = []
            if 'categories' in data.get('included', []):
                for item in data['included']:
                    if item['type'] == 'categories':
                        themes.append(item['attributes']['title'])
            
            # Extract studios
            studios = []
            if 'animeProductions' in data.get('included', []):
                for item in data['included']:
                    if item['type'] == 'animeProductions':
                        studio_id = item['relationships']['producer']['data']['id']
                        for studio in data['included']:
                            if studio['type'] == 'producers' and studio['id'] == studio_id:
                                studios.append(studio['attributes']['name'])
            
            return {
                'id': anime.get('id'),
                'title': attributes.get('canonicalTitle'),
                'title_english': attributes.get('titles', {}).get('en'),
                'title_japanese': attributes.get('titles', {}).get('ja_jp'),
                'image_url': poster_image.get('original'),
                'cover_url': cover_image.get('original'),
                'score': attributes.get('averageRating'),
                'scored_by': attributes.get('userCount'),
                'rank': attributes.get('ratingRank'),
                'popularity': attributes.get('popularityRank'),
                'members': attributes.get('favoritesCount'),
                'favorites': attributes.get('favoritesCount'),
                'synopsis': attributes.get('synopsis'),
                'background': attributes.get('description'),
                'type': attributes.get('showType'),
                'source': attributes.get('source'),
                'episodes': attributes.get('episodeCount'),
                'status': attributes.get('status'),
                'aired': f"{attributes.get('startDate')} to {attributes.get('endDate')}",
                'premiered': attributes.get('startDate'),
                'broadcast': None,  # Kitsu doesn't provide broadcast info
                'producers': [],  # Kitsu doesn't provide producers separately
                'licensors': [],  # Kitsu doesn't provide licensors
                'studios': studios,
                'genres': genres,
                'themes': themes,
                'demographics': [],  # Kitsu doesn't provide demographics
                'duration': attributes.get('episodeLength'),
                'rating': attributes.get('ageRating'),
                'trailer_url': attributes.get('youtubeVideoId'),
                'year': attributes.get('startDate', '').split('-')[0] if attributes.get('startDate') else None,
                'season': attributes.get('season'),
                'url': f"https://kitsu.io/anime/{anime.get('id')}"
            }
        except requests.RequestException as e:
            print(f"Error fetching anime details: {e}")
            return None 
