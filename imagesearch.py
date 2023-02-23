import requests
import random

class ImageSearcher:
    def __init__(self):
        self.token_cache = {}
        self.session = requests.Session()
        self.session.headers = {
            "authority": "duckduckgo.com",
            "accept": "*/*; q=0.01",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
            "referer": "https://duckduckgo.com/"
        }
    
    def validate_cache(self, query, token):
        if token not in self.token_cache:
            if not self.update_token_cache(query):
                return False
        return True
    
    def update_token_cache(self, query):
        req = self.session.get("https://html.duckduckgo.com/html/?q=" + query)
        vqd_value = '"vqd" value="'
        if vqd_value not in req.text:
            print("update_token_cache: Failed to find vqd token in body")
            return False
        self.token_cache[hash(query)] = req.text.split(vqd_value)[1].split('"')[0]
        return True
    
    def is_api_error(self, pagetext):
        if pagetext == "If this error persists, please let us know: ops@duckduckgo.com":
            return True
        return False
    
    def api_search_results(self, file, query, page = None):
        cache = self.token_cache
        token_hash = hash(query)
        if not self.validate_cache(query, token_hash):
            return None
        if page == None:
            page = str(random.randint(1, 6) * 100)
        req = self.session.get("https://duckduckgo.com/" + file + "?o=json&p=-1&vqd=" + cache[token_hash] + "&q=" + query + "&s=" + str(page))
        if self.is_api_error(req.text):
            return None
        results = req.json()
        return results
    
    def random_image_results(self, query, page = None, is_reload = False):
        cache = self.token_cache
        token_hash = hash(query)
        file = "i.js"
        results = self.api_search_results(file, query)
        if results == None:
            cache.pop(token_hash)
            results = self.api_search_results(file, query, "0")
        return results
    
    def random_video_results(self, query, page = None, is_reload = False):
        token_hash = hash(query)
        cache = self.token_cache
        file = "v.js"
        results = self.api_search_results(file, query)
        if results == None:
            cache.pop(token_hash)
            results = self.api_search_results(file, query, "0")
        return results
