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

class IGDBService:
    @staticmethod
    def get_token():
        client_id = current_app.config.get('IGDB_CLIENT_ID')
        client_secret = current_app.config.get('IGDB_CLIENT_SECRET')
        if not client_id or not client_secret:
            return None
            
        url = f"https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials"
        try:
            response = requests.post(url, timeout=30)
            response.raise_for_status()
            return response.json().get('access_token')
        except Exception as e:
            print(f"Failed to get IGDB token: {e}")
            return None

    @classmethod
    def search_games(cls, query):
        token = cls.get_token()
        client_id = current_app.config.get('IGDB_CLIENT_ID')
        if not token:
            return []

        url = "https://api.igdb.com/v4/games"
        headers = {
            'Client-ID': client_id,
            'Authorization': f'Bearer {token}',
            'Content-Type': 'text/plain'
        }
        # Fetching basic search results
        body = f'search "{query}"; fields name, first_release_date, cover.url; limit 10;'
        try:
            response = requests.post(url, headers=headers, data=body, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"IGDB search error for '{query}': {e}")
            return []

    @classmethod
    def get_game_details(cls, igdb_id):
        token = cls.get_token()
        client_id = current_app.config.get('IGDB_CLIENT_ID')
        if not token:
            return None

        url = "https://api.igdb.com/v4/games"
        headers = {
            'Client-ID': client_id,
            'Authorization': f'Bearer {token}',
            'Content-Type': 'text/plain'
        }
        body = f"""
        fields name, summary, first_release_date, 
               genres.name, involved_companies.company.name, involved_companies.developer, involved_companies.publisher,
               franchises.name, platforms.name, rating, aggregated_rating, cover.url;
        where id = {igdb_id};
        """
        try:
            response = requests.post(url, headers=headers, data=body, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data[0] if data else None
        except Exception as e:
            print(f"IGDB details error for ID {igdb_id}: {e}")
            return None

    @classmethod
    def download_cover(cls, cover_url):
        if not cover_url:
            return None
        
        # IGDB urls are usually //images.igdb.com/igdb/image/upload/t_thumb/co1r7h.jpg
        if cover_url.startswith('//'):
            cover_url = 'https:' + cover_url
            
        # Swap 't_thumb' for 't_cover_big' or 't_720p' for better quality
        cover_url = cover_url.replace('t_thumb', 't_cover_big')
        
        filename = cover_url.split('/')[-1]
        local_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        if os.path.exists(local_path):
            return filename
            
        try:
            response = requests.get(cover_url, stream=True)
            response.raise_for_status()
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return filename
        except Exception as e:
            print(f"Error downloading cover: {e}")
            return None

class OpenLibraryService:
    BASE_URL = "https://openlibrary.org"
    HEADERS = {
        "User-Agent": "LeisureLedger/1.0 (agoergen@gmail.com)"
    }

    @classmethod
    def search_books(cls, query):
        url = f"{cls.BASE_URL}/search.json"
        params = {"q": query}
        try:
            response = requests.get(url, params=params, headers=cls.HEADERS, timeout=30)
            response.raise_for_status()
            return response.json().get('docs', [])
        except Exception as e:
            print(f"OpenLibrary search error for '{query}': {e}")
            return []

    @classmethod
    def get_book_details(cls, ol_id):
        # ol_id is usually a 'work' ID like 'OL12345W'
        url = f"{cls.BASE_URL}/works/{ol_id}.json"
        try:
            response = requests.get(url, headers=cls.HEADERS, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"OpenLibrary details error for {ol_id}: {e}")
            return None

    @classmethod
    def download_book_cover(cls, cover_id=None, ol_id=None):
        if not cover_id and not ol_id:
            return None
            
        if cover_id:
            url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
            filename = f"book_{cover_id}.jpg"
        else:
            url = f"https://covers.openlibrary.org/b/olid/{ol_id}-L.jpg"
            filename = f"book_{ol_id}.jpg"

        local_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        if os.path.exists(local_path):
            return filename
            
        try:
            response = requests.get(url, headers=cls.HEADERS, stream=True)
            response.raise_for_status()
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return filename
        except Exception as e:
            print(f"Error downloading book cover: {e}")
            return None

class GoogleBooksService:
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"
    HEADERS = {
        "User-Agent": "LeisureLedger/1.0 (agoergen@gmail.com)"
    }

    @classmethod
    def search_books(cls, query):
        params = {"q": query, "maxResults": 10}
        api_key = current_app.config.get('GOOGLE_BOOKS_API_KEY')
        if api_key:
            params['key'] = api_key
            
        try:
            response = requests.get(cls.BASE_URL, params=params, headers=cls.HEADERS, timeout=30)
            if response.status_code == 429:
                print("Google Books Quota Exhausted (429).")
                return "RATE_LIMIT"
            if response.status_code != 200:
                print(f"Google Books API Error: {response.status_code} - {response.text}")
            response.raise_for_status()
            return response.json().get('items', [])
        except Exception as e:
            print(f"Google Books search error for '{query}': {e}")
            return []

    @classmethod
    def get_book_details(cls, volume_id):
        url = f"{cls.BASE_URL}/{volume_id}"
        params = {}
        api_key = current_app.config.get('GOOGLE_BOOKS_API_KEY')
        if api_key:
            params['key'] = api_key

        try:
            response = requests.get(url, params=params, headers=cls.HEADERS, timeout=30)
            if response.status_code != 200:
                print(f"Google Books Detail Error: {response.status_code} - {response.text}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Google Books details error for {volume_id}: {e}")
            return None

    @classmethod
    def download_cover(cls, image_url, volume_id):
        if not image_url:
            return None
            
        filename = f"book_{volume_id}.jpg"
        local_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        if os.path.exists(local_path):
            return filename
            
        try:
            # Google Books image URLs often use http, better to force https
            if image_url.startswith('http://'):
                image_url = image_url.replace('http://', 'https://')
            
            response = requests.get(image_url, headers=cls.HEADERS, stream=True)
            response.raise_for_status()
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return filename
        except Exception as e:
            print(f"Error downloading Google Books cover: {e}")
            return None

class WikipediaService:
    BASE_URL = "https://en.wikipedia.org/w/api.php"

    @classmethod
    def search_posters(cls, show_name):
        # 1. Search for the show
        search_params = {
            "action": "query",
            "list": "search",
            "srsearch": f"{show_name} musical play poster",
            "format": "json"
        }
        
        try:
            resp = requests.get(cls.BASE_URL, params=search_params, timeout=20)
            resp.raise_for_status()
            search_results = resp.json().get('query', {}).get('search', [])
            
            if not search_results:
                # Try without 'musical play poster' tags if too restrictive
                search_params["srsearch"] = show_name
                resp = requests.get(cls.BASE_URL, params=search_params, timeout=20)
                search_results = resp.json().get('query', {}).get('search', [])

            image_urls = []
            # 2. Get the primary thumbnail for the top 5 matches
            for result in search_results[:5]:
                page_title = result['title']
                img_params = {
                    "action": "query",
                    "titles": page_title,
                    "prop": "pageimages",
                    "piprop": "thumbnail",
                    "pithumbsize": 600,
                    "format": "json"
                }
                img_resp = requests.get(cls.BASE_URL, params=img_params, timeout=20)
                pages = img_resp.json().get('query', {}).get('pages', {})
                for page_id in pages:
                    thumb = pages[page_id].get('thumbnail', {}).get('source')
                    if thumb:
                        image_urls.append(thumb)
            
            return image_urls
        except Exception as e:
            print(f"Wikipedia search error: {e}")
            return []

class ImageSearchService:
    @classmethod
    def search_images(cls, query):
        key = current_app.config.get('GOOGLE_SEARCH_KEY')
        cx = current_app.config.get('GOOGLE_SEARCH_ID')
        
        if not key or not cx:
            print(f"DEBUG: Missing config. Key present: {bool(key)}, CX present: {bool(cx)}")
            return []
            
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "q": query + " theater poster",
            "searchType": "image",
            "key": key,
            "cx": cx,
            "num": 8
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code != 200:
                print(f"Google Image Search API Error: {response.status_code} - {response.text}")
            response.raise_for_status()
            items = response.json().get('items', [])
            return [item['link'] for item in items]
        except Exception as e:
            print(f"Image search error for '{query}': {e}")
            return []

    @classmethod
    def download_image(cls, image_url, prefix, item_id):
        filename = f"{prefix}_{item_id}.jpg"
        local_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        try:
            response = requests.get(image_url, stream=True, timeout=30)
            response.raise_for_status()
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return filename
        except Exception as e:
            print(f"Error downloading image from {image_url}: {e}")
            return None
