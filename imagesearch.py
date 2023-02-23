import asyncio
import requests
import random
import re

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
    
    async def update_token_cache(self, query):
        req = self.session.get("https://duckduckgo.com/?q=" + query)
        token = re.search(r'vqd=([\d-]+)\&', req.text, re.M | re.I)
        if token == None:
            print("Failed to find vqd token in body")
            return False
        self.token_cache[hash(query)] = token.group(1)
        return True
    
    async def random_image_results(self, query, is_reload = False):
        token_hash = hash(query)
        if not self.token_cache.keys().__contains__(token_hash):
            success = await self.update_token_cache(query)
            if not success:
                print("Failed to update token cache 1")
                return None
        offset = str(random.randint(1, 6) * 100)
        req = self.session.get("https://duckduckgo.com/i.js?o=json&p=-1&vqd=" + self.token_cache[token_hash] + "&q=" + query + "&s=" + offset)
        if req.text == "If this error persists, please let us know: ops@duckduckgo.com":
            if is_reload == True:
                return None
            print("Search failed. Refreshing vqd token and trying again")
            self.token_cache.pop(token_hash)
            await self.random_image_results(query, is_reload = True)
        return req.json()["results"]