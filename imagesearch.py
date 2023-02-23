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
    
    def update_token_cache(self, query):
        req = self.session.get("https://html.duckduckgo.com/html/?q=" + query)
        vqd_value = '"vqd" value="'
        if vqd_value not in req.text:
            print("update_token_cache: Failed to find vqd token in body")
            return False
        self.token_cache[hash(query)] = req.text.split(vqd_value)[1].split('"')[0]
        return True
    
    def random_image_results(self, query, page = None, is_reload = False):
        token_hash = hash(query)
        if token_hash not in self.token_cache:
            if not self.update_token_cache(query):
                return None
        if page == None:
            page = str(random.randint(1, 6) * 100)
        req = self.session.get("https://duckduckgo.com/i.js?o=json&p=-1&vqd=" + self.token_cache[token_hash] + "&q=" + query + "&s=" + str(page))
        if req.text == "If this error persists, please let us know: ops@duckduckgo.com":
            if is_reload == True:
                return None
            print("random_image_results: Search failed")
            if token_hash in self.token_cache:
                self.token_cache.pop(token_hash)
            return self.random_image_results(query, page = 0, is_reload = True)
        results = req.json()
        return results
