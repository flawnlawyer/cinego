
import requests
import random
from typing import List, Dict, Any

class TMDBClient:
    """Client for TMDB API interactions"""
    
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
    
    # Use environment variables in production, but hardcoding here as requested
    READ_ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhOTVjN2VjMGFmNDY4MDkwOTJjNWQ0NTQzNjQyYWUzNyIsIm5iZiI6MTc3MDc3ODU3MS42NzM5OTk4LCJzdWIiOiI2OThiZWZjYjQ3Yzc4YTk5ZjMwOWMxN2QiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.Mh4ackw_42JqWpvJx9_3rAGVMhKYdFNgsp1USdjen2Y"
    
    @classmethod
    def _get_headers(cls) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {cls.READ_ACCESS_TOKEN}",
            "accept": "application/json"
        }


    @classmethod
    def fetch_trending_movies(cls, page: int = 1, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch trending movies for the week"""
        url = f"{cls.BASE_URL}/trending/movie/week?page={page}"
        response = requests.get(url, headers=cls._get_headers())
        
        if response.status_code == 200:
            results = response.json().get('results', [])
            return [cls._process_movie(m) for m in results[:limit]]
        return []

    @classmethod
    def fetch_top_rated_movies(cls, page: int = 1, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch top rated movies"""
        url = f"{cls.BASE_URL}/movie/top_rated?page={page}"
        response = requests.get(url, headers=cls._get_headers())
        
        if response.status_code == 200:
            results = response.json().get('results', [])
            return [cls._process_movie(m) for m in results[:limit]]
        return []

    @classmethod
    def fetch_now_playing_movies(cls, page: int = 1, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch now playing movies"""
        url = f"{cls.BASE_URL}/movie/now_playing?page={page}"
        response = requests.get(url, headers=cls._get_headers())
        
        if response.status_code == 200:
            results = response.json().get('results', [])
            return [cls._process_movie(m) for m in results[:limit]]
        return []
    
    @classmethod
    def fetch_upcoming_movies(cls, page: int = 1, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch upcoming movies"""
        url = f"{cls.BASE_URL}/movie/upcoming?page={page}"
        response = requests.get(url, headers=cls._get_headers())
        
        if response.status_code == 200:
            results = response.json().get('results', [])
            # For upcoming, we should filter out those without posters to look good
            results = [m for m in results if m.get('poster_path')]
            return [cls._process_movie(m) for m in results[:limit]]
        return []
    
    @classmethod
    def fetch_action_movies(cls, page: int = 1, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch action movies specifically"""
        url = f"{cls.BASE_URL}/discover/movie?with_genres=28&page={page}"
        response = requests.get(url, headers=cls._get_headers())
        
        if response.status_code == 200:
            results = response.json().get('results', [])
            return [cls._process_movie(m) for m in results[:limit]]
        return []
    
    @classmethod
    def fetch_comedy_movies(cls, page: int = 1, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch comedy movies specifically"""
        url = f"{cls.BASE_URL}/discover/movie?with_genres=35&page={page}"
        response = requests.get(url, headers=cls._get_headers())
        
        if response.status_code == 200:
            results = response.json().get('results', [])
            return [cls._process_movie(m) for m in results[:limit]]
        return []

    @classmethod
    def fetch_popular_series(cls, page: int = 1, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch popular TV series"""
        url = f"{cls.BASE_URL}/tv/popular?page={page}"
        response = requests.get(url, headers=cls._get_headers())
        
        if response.status_code == 200:
            results = response.json().get('results', [])
            return [cls._process_series(s) for s in results[:limit]]
        return []

    @classmethod
    def fetch_movie_videos(cls, movie_id: int) -> Dict[str, str]:
        """Fetch best available video (Trailer first)"""
        url = f"{cls.BASE_URL}/movie/{movie_id}/videos"
        response = requests.get(url, headers=cls._get_headers())
        
        if response.status_code == 200:
            results = response.json().get('results', [])
            
            # Priority: Trailer > Teaser > Clip
            for video in results:
                if video.get('site') == 'YouTube' and video.get('type') == 'Trailer':
                    return {'type': 'trailer', 'url': f"https://www.youtube.com/embed/{video.get('key')}"}
            
            for video in results:
                if video.get('site') == 'YouTube' and video.get('type') == 'Teaser':
                    return {'type': 'teaser', 'url': f"https://www.youtube.com/embed/{video.get('key')}"}
                    
            for video in results:
                if video.get('site') == 'YouTube': # Any other youtube video
                    return {'type': 'clip', 'url': f"https://www.youtube.com/embed/{video.get('key')}"}
                    
        return None

    # Keeping old method for compatibility but redirecting to new logic if needed, 
    # though we can just update usage.
    @classmethod
    def fetch_movie_trailer(cls, movie_id: int) -> str:
        video = cls.fetch_movie_videos(movie_id)
        return video['url'] if video else ""

    @classmethod
    def fetch_series_videos(cls, series_id: int) -> Dict[str, str]:
        """Fetch best available video for series (Trailer first)"""
        url = f"{cls.BASE_URL}/tv/{series_id}/videos"
        response = requests.get(url, headers=cls._get_headers())
        
        if response.status_code == 200:
            results = response.json().get('results', [])
            
            # Priority: Trailer > Teaser > Clip
            for video in results:
                if video.get('site') == 'YouTube' and video.get('type') == 'Trailer':
                    return {'type': 'trailer', 'url': f"https://www.youtube.com/embed/{video.get('key')}"}
            
            for video in results:
                if video.get('site') == 'YouTube' and video.get('type') == 'Teaser':
                    return {'type': 'teaser', 'url': f"https://www.youtube.com/embed/{video.get('key')}"}
                    
            for video in results:
                if video.get('site') == 'YouTube': 
                    return {'type': 'clip', 'url': f"https://www.youtube.com/embed/{video.get('key')}"}
        return None

    @classmethod
    def fetch_series_trailer(cls, series_id: int) -> str:
        """Fetch trailer URL for a series"""
        video = cls.fetch_series_videos(series_id)
        return video['url'] if video else ""

    @classmethod
    def _process_movie(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert TMDB movie data to our application format"""
        
        genre_ids = data.get('genre_ids', [])
        # Map primary genre
        genre = cls._get_genre_name(genre_ids[0]) if genre_ids else 'Unknown'
        
        # We can also store full genre list if DB supported it, but schema is simple string.
        # Let's keep it simple for now.
        
        return {
            'id': data.get('id'),
            'title': data.get('title'),
            'year': int(data.get('release_date', '0000')[:4]) if data.get('release_date') else 0,
            'genre': genre,
            'rating': data.get('vote_average', 0),
            'image_url': f"{cls.IMAGE_BASE_URL}{data.get('poster_path')}" if data.get('poster_path') else "",
            'description': data.get('overview', ''),
            'is_trending': 1 if data.get('popularity', 0) > 100 else 0, # Calculate based on popularity
            'view_count': int(data.get('popularity', 0) * 10), 
            'video_url': '', 
            'trailer_url': '' 
        }

    @classmethod
    def _process_series(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        genre_id = data.get('genre_ids', [0])[0] if data.get('genre_ids') else 0
        genre = cls._get_genre_name(genre_id)
        
        return {
            'id': data.get('id'),
            'title': data.get('name'),
            'year': int(data.get('first_air_date', '0000')[:4]) if data.get('first_air_date') else 0,
            'genre': genre,
            'rating': data.get('vote_average', 0),
            'image_url': f"{cls.IMAGE_BASE_URL}{data.get('poster_path')}" if data.get('poster_path') else "",
            'description': data.get('overview', ''),
            'seasons': 1 # Default, as this info usually requires detail fetch
        }

    @classmethod
    def _get_genre_name(cls, genre_id: int) -> str:
        # Basic mapping for common TMDB genre IDs
        genres = {
            28: 'Action', 12: 'Adventure', 16: 'Animation', 35: 'Comedy',
            80: 'Crime', 99: 'Documentary', 18: 'Drama', 10751: 'Family',
            14: 'Fantasy', 36: 'History', 27: 'Horror', 10402: 'Music',
            9648: 'Mystery', 10749: 'Romance', 878: 'Sci-Fi', 10770: 'TV Movie',
            53: 'Thriller', 10752: 'War', 37: 'Western'
        }
        return genres.get(genre_id, 'Drama')

