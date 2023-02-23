import asyncio
import websockets
import json
import os
import imagesearch
import random
import requests
from datetime import date

DISCORD_TOKEN = ""

MESSAGE_HELLO = {
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

class DiscordClient:
    def __init__(self):
        self.websocket = None
        self.token = None
        self.logfile = None
        self.searcher = imagesearch.ImageSearcher()
        asyncio.run(self.WebsocketInit())
    
    async def WebsocketInit(self):
        await self.LoggerInit()
        await self.CreateConnection()

    async def LoggerInit(self):
        if not os.path.exists("Logs"):
            os.mkdir("Logs")
        self.logfile = open("Logs/" + str(date.today()) + ".txt", "a")
    
    async def CreateConnection(self):
        self.websocket = await websockets.connect("wss://gateway.discord.gg/?v=10&encoding=json", max_size=5_000_000)
        await self.websocket.send(json.dumps(MESSAGE_HELLO))
        await self.DispatcherInit()
    
    async def DispatcherInit(self):
        while True:
            if self.websocket == None:
                break
            message = await self.websocket.recv()
            message = json.loads(message)
            match message["t"]:
                case "MESSAGE_CREATE":
                    await self.HandleMessage(message["d"])
    
    async def HandleMessage(self, message):
        if message["content"].startswith("!searchbot"):
            split = message["content"].split("-")
            if len(split) < 2:
                return
            query = split[1]
            results = await self.searcher.random_image_results(query)
            if len(results) == 0:
                return
            await self.ReplyToMessage(message, random.choice(results)["image"])
    
    async def ReplyToMessage(self, message, text):
        headers = {
            "Authorization": DISCORD_TOKEN,
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
            "Content-Type": "application/json"
        }
        if message.keys().__contains__("guild_id"):
            HTTP_MESSAGE_REPLY["message_reference"]["guild_id"] = message["guild_id"]
        HTTP_MESSAGE_REPLY["message_reference"]["channel_id"] = message["channel_id"]
        HTTP_MESSAGE_REPLY["message_reference"]["message_id"] = message["id"]
        HTTP_MESSAGE_REPLY["content"] = text
        req = requests.post("https://discord.com/api/v9/channels/" + str(message["channel_id"]) + "/messages", headers=headers, data=json.dumps(HTTP_MESSAGE_REPLY))


client = DiscordClient()