// This code is not part of the app code it is just a js api of our python api.
// It is used to fetch anime data from the kitsu api.

class KitsuClient {     
    constructor(pageLimit = 20) {
        this.BASE_URL = "https://kitsu.io/api/edge";
        this.DEFAULT_PAGE_LIMIT = 20;
        this.MAX_PAGE_LIMIT = 20;
        this.pageLimit = Math.min(pageLimit, this.MAX_PAGE_LIMIT);
        this.headers = {
            'Accept': 'application/vnd.api+json',
            'Content-Type': 'application/vnd.api+json'
        };
    }

    _processAnimeData(animeData) {
        const attributes = animeData.attributes || {};
        return {
            id: animeData.id,
            title: attributes.canonicalTitle || "Unknown Title",
            image_url: attributes.posterImage?.original || "",
            score: attributes.averageRating || "N/A",
            synopsis: attributes.synopsis || "No synopsis available",
            episodes: attributes.episodeCount || "N/A",
            status: attributes.status || "Unknown",
            aired: `${attributes.startDate || 'Unknown'} to ${attributes.endDate || 'Unknown'}`
        };
    }

    async getTopAnime() {
        try {
            const response = await fetch(
                `${this.BASE_URL}/anime?sort=-averageRating&page[limit]=${this.pageLimit}`,
                { headers: this.headers }
            );
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (!data.data) {
                console.log(`No data in response: ${data}`);
                return [];
            }
            
            return data.data.map(anime => this._processAnimeData(anime));
        } catch (error) {
            console.error(`Error fetching top anime: ${error}`);
            return [];
        }
    }

    async searchAnime(query) {
        try {
            if (!query || query.trim() === "") {
                return [];
            }
            
            console.log(`Searching for: ${query}`);
            
            const response = await fetch(
                `${this.BASE_URL}/anime?filter[text]=${encodeURIComponent(query)}&page[limit]=${this.pageLimit}`,
                { headers: this.headers }
            );
            
            console.log(`Response status: ${response.status}`);
            console.log(`Response URL: ${response.url}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (!data.data) {
                console.log(`No data in response: ${data}`);
                return [];
            }
            
            const results = data.data.map(anime => this._processAnimeData(anime));
            console.log(`Found ${results.length} results`);
            return results;
            
        } catch (error) {
            console.error(`Error fetching anime data: ${error}`);
            return [];
        }
    }

    async getAnimeDetails(animeId) {
        try {
            const response = await fetch(
                `${this.BASE_URL}/anime/${animeId}`,
                { headers: this.headers }
            );
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (!data.data) {
                console.log(`No data found for anime ID: ${animeId}`);
                return null;
            }
            
            const anime = data.data;
            const attributes = anime.attributes || {};
            
            // Extract images with safe fallbacks
            const posterImage = attributes.posterImage || {};
            const coverImage = attributes.coverImage || {};
            
            // Extract genres
            const genres = data.included
                ?.filter(item => item.type === 'genres')
                .map(item => item.attributes.name) || [];
            
            // Extract themes
            const themes = data.included
                ?.filter(item => item.type === 'categories')
                .map(item => item.attributes.title) || [];
            
            // Extract studios
            const studios = data.included
                ?.filter(item => item.type === 'animeProductions')
                .map(item => {
                    const studioId = item.relationships.producer.data.id;
                    const studio = data.included.find(s => s.type === 'producers' && s.id === studioId);
                    return studio?.attributes.name;
                })
                .filter(Boolean) || [];
            
            return {
                id: anime.id,
                title: attributes.canonicalTitle,
                title_english: attributes.titles?.en,
                title_japanese: attributes.titles?.ja_jp,
                image_url: posterImage.original,
                cover_url: coverImage.original || posterImage.original || null,
                score: attributes.averageRating,
                scored_by: attributes.userCount,
                rank: attributes.ratingRank,
                popularity: attributes.popularityRank,
                members: attributes.favoritesCount,
                favorites: attributes.favoritesCount,
                synopsis: attributes.synopsis,
                background: attributes.description,
                type: attributes.showType,
                source: attributes.source,
                episodes: attributes.episodeCount,
                status: attributes.status,
                aired: `${attributes.startDate} to ${attributes.endDate}`,
                premiered: attributes.startDate,
                broadcast: null,
                producers: [],
                licensors: [],
                studios,
                genres,
                themes,
                demographics: [],
                duration: attributes.episodeLength,
                rating: attributes.ageRating,
                trailer_url: attributes.youtubeVideoId,
                year: attributes.startDate?.split('-')[0] || null,
                season: attributes.season,
                url: `https://kitsu.io/anime/${anime.id}`
            };
        } catch (error) {
            console.error(`Error fetching anime details: ${error}`);
            return null;
        }
    }
}

// Export the class
export default KitsuClient; 
