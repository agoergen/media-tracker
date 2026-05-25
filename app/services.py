import os
import requests
from flask import current_app

class OMDBService:
    @staticmethod
    def search_movies(title):
        api_key = current_app.config.get('OMDB_API_KEY')
        if not api_key:
            return None
        
        url = f"http://www.omdbapi.com/?s={title}&apikey={api_key}&type=movie"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if data.get('Response') == 'True':
                return data.get('Search', [])
            return []
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from OMDB: {e}")
            return None

    @staticmethod
    def get_movie_details(imdb_id):
        api_key = current_app.config.get('OMDB_API_KEY')
        if not api_key:
            return None
        
        url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if data.get('Response') == 'True':
                return data
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching details from OMDB: {e}")
            return None

class TMDBService:
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w200"

    @staticmethod
    def get_headers():
        token = current_app.config.get('TMDB_READ_TOKEN')
        return {
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        }

    @classmethod
    def search_movies(cls, query):
        url = f"{cls.BASE_URL}/search/movie"
        params = {"query": query}
        try:
            response = requests.get(url, headers=cls.get_headers(), params=params)
            response.raise_for_status()
            return response.json().get('results', [])
        except requests.exceptions.RequestException as e:
            print(f"Error searching TMDB: {e}")
            return []

    @classmethod
    def get_movie_details(cls, tmdb_id):
        url = f"{cls.BASE_URL}/movie/{tmdb_id}"
        # Append 'credits', 'videos', 'release_dates', and 'external_ids'
        params = {"append_to_response": "credits,videos,release_dates,external_ids"}
        try:
            response = requests.get(url, headers=cls.get_headers(), params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching TMDB details: {e}")
            return None

    @classmethod
    def search_tv(cls, query):
        url = f"{cls.BASE_URL}/search/tv"
        params = {"query": query}
        try:
            response = requests.get(url, headers=cls.get_headers(), params=params)
            response.raise_for_status()
            return response.json().get('results', [])
        except requests.exceptions.RequestException as e:
            print(f"Error searching TMDB TV: {e}")
            return []

    @classmethod
    def get_tv_show_details(cls, series_id):
        url = f"{cls.BASE_URL}/tv/{series_id}"
        # Append 'external_ids' to get IMDB ID if possible
        params = {"append_to_response": "external_ids,videos"}
        try:
            response = requests.get(url, headers=cls.get_headers(), params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching TMDB TV show details: {e}")
            return None

    @classmethod
    def get_tv_season_details(cls, series_id, season_number):
        url = f"{cls.BASE_URL}/tv/{series_id}/season/{season_number}"
        try:
            response = requests.get(url, headers=cls.get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching TMDB TV season details: {e}")
            return None

    @classmethod
    def download_poster(cls, poster_path):
        if not poster_path:
            return None
        
        # Clean the path to use as a filename
        filename = poster_path.lstrip('/')
        local_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # If it already exists, don't download again
        if os.path.exists(local_path):
            return filename
            
        url = f"https://image.tmdb.org/t/p/original{poster_path}"
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Ensure subdirectories exist if poster_path has them (unlikely with TMDB but safe)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return filename
        except Exception as e:
            print(f"Error downloading poster: {e}")
            return None
