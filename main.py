import asyncio
import websockets
import json
import os
import imagesearch
import random
import requests
from datetime import date

DISCORD_TOKEN = ""

HELLO = {
   "op":2,
   "d":{
      "token": DISCORD_TOKEN,
      "capabilities":4093,
      "properties":{
         "client_build_number":175856,
         "client_event_source": None,
         "design_id":0
      },
      "compress": False,
   }
}

HTTP_MESSAGE_REPLY = {
    "content":"poop",
    "nonce": None,
    "tts": False,
    "message_reference":{
    },
    "allowed_mentions":{
        "parse":[
            "users",
            "roles",
            "everyone"
            ],
        "replied_user": True
    },
    "flags":0
}

HEARTBEAT_ACK = {
    "op": 1,
    "d": {
        "token": DISCORD_TOKEN,
        "properties":{
            "client_build_number":175856,
            "client_event_source": None,
            "design_id":0
        },
    }
}

class DiscordClient:
    def __init__(self):
        self.websocket = None
        self.token = None
        self.logfile = None
        self.interval = None
        self.searcher = imagesearch.ImageSearcher()
        asyncio.run(self.init_websocket())
    
    async def init_websocket(self):
        self.init_logger()
        await self.create_socket_connection()

    def init_logger(self):
        logpath = "Logs"
        if not os.path.exists(logpath):
            os.mkdir(logpath)
        self.logfile = open(logpath + "/" + str(date.today()) + ".txt", "a")
    
    async def create_socket_connection(self):
        self.websocket = await websockets.connect("wss://gateway.discord.gg/?v=10&encoding=json", max_size=5_000_000)
        await self.websocket.send(json.dumps(HELLO))
        asyncio.create_task(self.init_heartbeat_dispatcher())
        while True:
            try:
                message = json.loads(await self.websocket.recv())
            except Exception as Ex:
                print(Ex)
                break
            match message["op"]:
                case 10:
                    self.interval = message["d"]["heartbeat_interval"] / 1000
            match message["t"]:
                case "MESSAGE_CREATE":
                    await self.handle_message(message["d"])
    
    async def handle_message(self, message):
        if message["content"].startswith("!searchbot"):
            split = message["content"].split("-")
            if len(split) < 2:
                return
            query = split[1]
            response = self.searcher.random_image_results(query)
            results = response["results"]
            if results == None or len(results) == 0:
                return
            self.reply_to_message(message, random.choice(results)["image"])
    
    def reply_to_message(self, message, text):
        headers = {
            "Authorization": DISCORD_TOKEN,
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
            "Content-Type": "application/json"
        }
        reply = HTTP_MESSAGE_REPLY.copy()
        if "guild_id" in message:
            reply["message_reference"]["guild_id"] = message["guild_id"]
        reply["message_reference"]["channel_id"] = message["channel_id"]
        reply["message_reference"]["message_id"] = message["id"]
        reply["content"] = text
        req = requests.post("https://discord.com/api/v9/channels/" + str(message["channel_id"]) + "/messages", headers=headers, data=json.dumps(reply))
    
    async def init_heartbeat_dispatcher(self):
        beartbeat_payload = json.dumps(HEARTBEAT_ACK)
        while True:
            await asyncio.sleep(self.interval)
            await self.websocket.send(beartbeat_payload)
            print("Sent Heartbeat")

client = DiscordClient()
