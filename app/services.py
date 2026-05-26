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
        # Request US release dates for certification
        params = {"append_to_response": "credits,videos,release_dates,external_ids"}
        try:
            response = requests.get(url, headers=cls.get_headers(), params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting TMDB movie details: {e}")
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
    def get_tv_details(cls, series_id, season_number):
        # We need series info for the name and season info for episode count/poster
        series_url = f"{cls.BASE_URL}/tv/{series_id}"
        season_url = f"{cls.BASE_URL}/tv/{series_id}/season/{season_number}"
        
        try:
            # 1. Get series level data (for network, original name)
            series_resp = requests.get(series_url, headers=cls.get_headers(), params={"append_to_response": "videos"})
            series_resp.raise_for_status()
            series_data = series_resp.json()

            # 2. Get season level data
            season_resp = requests.get(season_url, headers=cls.get_headers())
            season_resp.raise_for_status()
            season_data = season_resp.json()

            return {
                "series_name": series_data.get('name'),
                "network": series_data.get('networks', [{}])[0].get('name') if series_data.get('networks') else None,
                "episode_count": season_data.get('episodes', []),
                "poster_path": season_data.get('poster_path'),
                "vote_average": season_data.get('vote_average'),
                "overview": season_data.get('overview') or series_data.get('overview'),
                "videos": series_data.get('videos', {}),
                "episode_count": len(season_data.get('episodes', []))
            }
        except requests.exceptions.RequestException as e:
            print(f"Error getting TMDB TV details: {e}")
            return None

    @classmethod
    def download_poster(cls, path):
        if not path:
            return None
        url = f"https://image.tmdb.org/t/p/w500{path}"
        filename = path.lstrip('/')
        local_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        if os.path.exists(local_path):
            return filename
            
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return filename
        except Exception as e:
            print(f"Error downloading poster: {e}")
            return None

class IGDBService:
    CLIENT_ID = None
    CLIENT_SECRET = None
    _access_token = None

    @classmethod
    def _get_token(cls):
        if cls._access_token:
            return cls._access_token
            
        cls.CLIENT_ID = current_app.config.get('IGDB_CLIENT_ID')
        cls.CLIENT_SECRET = current_app.config.get('IGDB_CLIENT_SECRET')
        
        url = f"https://id.twitch.tv/oauth2/token?client_id={cls.CLIENT_ID}&client_secret={cls.CLIENT_SECRET}&grant_type=client_credentials"
        resp = requests.post(url)
        resp.raise_for_status()
        cls._access_token = resp.json()['access_token']
        return cls._access_token

    @classmethod
    def search_games(cls, query):
        token = cls._get_token()
        url = "https://api.igdb.com/v4/games"
        headers = {
            "Client-ID": cls.CLIENT_ID,
            "Authorization": f"Bearer {token}"
        }
        body = f'search "{query}"; fields name, first_release_date, cover.url; limit 10;'
        
        try:
            resp = requests.post(url, headers=headers, data=body)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"IGDB search error: {e}")
            return []

    @classmethod
    def get_game_details(cls, igdb_id):
        token = cls._get_token()
        url = "https://api.igdb.com/v4/games"
        headers = {
            "Client-ID": cls.CLIENT_ID,
            "Authorization": f"Bearer {token}"
        }
        body = f'fields name, summary, first_release_date, cover.url, genres.name, involved_companies.developer, involved_companies.publisher, involved_companies.company.name, platforms.name, franchises.name, rating, aggregated_rating; where id = {igdb_id};'
        
        try:
            resp = requests.post(url, headers=headers, data=body)
            resp.raise_for_status()
            results = resp.json()
            return results[0] if results else None
        except Exception as e:
            print(f"IGDB details error: {e}")
            return None

    @classmethod
    def download_cover(cls, image_url):
        if not image_url:
            return None
        # Convert thumbnail URL to high res
        # //images.igdb.com/igdb/image/upload/t_thumb/co1r8v.jpg -> t_cover_big
        high_res_url = "https:" + image_url.replace("t_thumb", "t_720p")
        filename = image_url.split('/')[-1]
        local_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        if os.path.exists(local_path):
            return filename
            
        try:
            response = requests.get(high_res_url, stream=True)
            response.raise_for_status()
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return filename
        except Exception as e:
            print(f"Error downloading game cover: {e}")
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
    HEADERS = {
        "User-Agent": "LeisureLedger/1.0 (agoergen@gmail.com)"
    }

    @classmethod
    def search_posters(cls, show_name):
        # Clean title for better search
        clean_name = show_name.replace(':', '').replace(' - ', ' ').strip()
        
        # 1. Search for the show
        search_params = {
            "action": "query",
            "list": "search",
            "srsearch": f"{clean_name} musical play poster",
            "format": "json"
        }
        
        try:
            resp = requests.get(cls.BASE_URL, params=search_params, headers=cls.HEADERS, timeout=20)
            resp.raise_for_status()
            search_results = resp.json().get('query', {}).get('search', [])
            
            if not search_results:
                search_params["srsearch"] = clean_name
                resp = requests.get(cls.BASE_URL, params=search_params, headers=cls.HEADERS, timeout=20)
                search_results = resp.json().get('query', {}).get('search', [])

            image_urls = []
            # 2. Get the primary thumbnail AND other images for top 5 matches
            for result in search_results[:5]:
                page_title = result['title']
                
                # A. Try page image first (primary thumbnail)
                img_params = {
                    "action": "query",
                    "titles": page_title,
                    "prop": "pageimages|images",
                    "piprop": "thumbnail",
                    "pithumbsize": 800,
                    "format": "json"
                }
                img_resp = requests.get(cls.BASE_URL, params=img_params, headers=cls.HEADERS, timeout=20)
                pages = img_resp.json().get('query', {}).get('pages', {})
                
                for page_id in pages:
                    # Add primary thumbnail
                    thumb = pages[page_id].get('thumbnail', {}).get('source')
                    if thumb:
                        image_urls.append(thumb)
                    
                    # Add other images on page that look like posters
                    page_images = pages[page_id].get('images', [])
                    for img in page_images:
                        title = img.get('title', '').lower()
                        # Filter for things that are likely posters/artwork
                        if any(x in title for x in ['poster', 'logo', 'musical', 'play', 'show', 'theater', 'production']):
                            # Need to get the actual URL for this File:
                            url = cls.get_image_url(img.get('title'))
                            if url:
                                image_urls.append(url)
            
            # Remove duplicates while preserving order
            seen = set()
            return [x for x in image_urls if not (x in seen or seen.add(x))]
        except Exception as e:
            print(f"Wikipedia search error for {show_name}: {e}")
            return []

    @classmethod
    def get_image_url(cls, file_title):
        params = {
            "action": "query",
            "titles": file_title,
            "prop": "imageinfo",
            "iiprop": "url",
            "iiurlwidth": 800,
            "format": "json"
        }
        try:
            resp = requests.get(cls.BASE_URL, params=params, headers=cls.HEADERS, timeout=20)
            pages = resp.json().get('query', {}).get('pages', {})
            for page_id in pages:
                info = pages[page_id].get('imageinfo', [{}])[0]
                # Return the scaled URL if available, else original
                return info.get('thumburl') or info.get('url')
        except:
            return None

    @classmethod
    def get_details(cls, show_name):
        # 1. Search to find the best page
        search_params = {
            "action": "query",
            "list": "search",
            "srsearch": f"{show_name} musical play",
            "format": "json"
        }
        
        details = {"summary": None, "runtime": None}
        
        try:
            resp = requests.get(cls.BASE_URL, params=search_params, headers=cls.HEADERS, timeout=20)
            search_results = resp.json().get('query', {}).get('search', [])
            if not search_results: return details
            
            page_title = search_results[0]['title']
            
            # 2. Get extract AND wikibase_item (for Wikidata)
            info_params = {
                "action": "query",
                "titles": page_title,
                "prop": "extracts|pageprops",
                "exintro": True,
                "explaintext": True,
                "format": "json"
            }
            resp = requests.get(cls.BASE_URL, params=info_params, headers=cls.HEADERS, timeout=20)
            pages = resp.json().get('query', {}).get('pages', {})
            
            wikidata_id = None
            for page_id in pages:
                details["summary"] = pages[page_id].get('extract')
                wikidata_id = pages[page_id].get('pageprops', {}).get('wikibase_item')

            # 3. Fetch runtime from Wikidata if we have an ID
            if wikidata_id:
                wiki_url = f"https://www.wikidata.org/w/api.php"
                wiki_params = {
                    "action": "wbgetclaims",
                    "entity": wikidata_id,
                    "property": "P2047", # Duration
                    "format": "json"
                }
                w_resp = requests.get(wiki_url, params=wiki_params, headers=cls.HEADERS, timeout=20)
                claims = w_resp.json().get('claims', {}).get('P2047', [])
                if claims:
                    # Get the first claim value
                    val = claims[0].get('mainsnak', {}).get('datavalue', {}).get('value', {})
                    amount = val.get('amount')
                    if amount:
                        # amount is usually like "+160"
                        details["runtime"] = int(float(amount))
            
            return details
        except Exception as e:
            print(f"Wikipedia details error for {show_name}: {e}")
            return details

    @classmethod
    def get_summary(cls, show_name):
        # Deprecated: use get_details
        return cls.get_details(show_name).get('summary')

class IBDBService:
    BASE_URL = "https://www.ibdb.com"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    @classmethod
    def search_shows(cls, query):
        url = f"{cls.BASE_URL}/Search/QuickSearchInfo"
        params = {"Keyword": query, "Category": "show"}
        
        try:
            resp = requests.get(url, params=params, headers=cls.HEADERS, timeout=30)
            resp.raise_for_status()
            html = resp.text
            
            # Handle Direct Redirect (e.g. 'shucked' redirects to show page)
            if "/broadway-show/" in resp.url:
                slug_id = resp.url.split("/broadway-show/")[1].rstrip('/')
                title = query.capitalize() # Default to query if we can't find title
                if '<title>' in html:
                    title = html.split('<title>')[1].split(' – ')[0].strip()
                
                show_type = "Show"
                if "Musical" in html: show_type = "Musical"
                elif "Play" in html: show_type = "Play"
                
                return [{
                    "title": title,
                    "type": show_type,
                    "ibdb_id": slug_id,
                    "source": "IBDB"
                }]

            results = []
            if '<div class="row" id="shows"' not in html:
                return []
                
            shows_section = html.split('<div class="row" id="shows"')[1].split('<div class="pagination-wrap">')[0]
            show_blocks = shows_section.split('<div class="row">')[1:]
            
            for block in show_blocks:
                if 'broadway-show' not in block:
                    continue
                
                try:
                    title_part = block.split('href="/broadway-show/')[1]
                    slug_id = title_part.split('">')[0]
                    title = title_part.split('">')[1].split('</a>')[0]
                    
                    show_type = "Show"
                    if '<b>Musical</b>' in block: show_type = "Musical"
                    elif '<b>Play</b>' in block: show_type = "Play"
                    
                    results.append({
                        "title": title,
                        "type": show_type,
                        "ibdb_id": slug_id,
                        "source": "IBDB"
                    })
                except:
                    continue
                    
            return results[:15]
        except Exception as e:
            print(f"IBDB search error: {e}")
            return []

    @classmethod
    def get_show_details(cls, slug_id):
        url = f"{cls.BASE_URL}/broadway-show/{slug_id}"
        try:
            resp = requests.get(url, headers=cls.HEADERS, timeout=30)
            resp.raise_for_status()
            html = resp.text
            
            opening_date = None
            if 'broadway-production' in html:
                try:
                    prod_part = html.split('broadway-production')[1].split('">')[1]
                    opening_date = prod_part.split('–')[0].split('</a>')[0].strip()
                except: pass
            
            theater = None
            if "span class='block'>" in html:
                try:
                    theater = html.split("span class='block'>")[1].split("</span>")[0].strip()
                except: pass

            # Scrape Description
            summary = None
            if 'description-info' in html:
                try:
                    summary = html.split('description-info')[1].split('">')[1].split('</p>')[0].strip()
                    # Clean up any HTML tags inside summary if they exist
                    import re
                    summary = re.sub('<[^<]+?>', '', summary)
                except: pass
            
            return {
                "opening_date": opening_date,
                "theater": theater,
                "summary": summary
            }
        except Exception as e:
            print(f"IBDB detail error for {slug_id}: {e}")
            return {}

class ImageSearchService:
    @classmethod
    def download_image(cls, image_url, prefix, item_id):
        if not image_url:
            return None
            
        # Handle protocol-relative URLs (e.g., //upload.wikimedia.org/...)
        if image_url.startswith('//'):
            image_url = 'https:' + image_url
            
        filename = f"{prefix}_{item_id}.jpg"
        local_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        headers = {"User-Agent": "LeisureLedger/1.0 (agoergen@gmail.com)"}
        
        try:
            response = requests.get(image_url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return filename
        except Exception as e:
            print(f"Error downloading image from {image_url}: {e}")
            return None
