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
        # Append 'credits' to get cast
        params = {"append_to_response": "credits"}
        try:
            response = requests.get(url, headers=cls.get_headers(), params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching TMDB details: {e}")
            return None
