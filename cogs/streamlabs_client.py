# cogs/streamlabs_client.py
import json
import asyncio
import websockets
from discord.ext import commands


class StreamlabsClient(commands.Cog):
    def __init__(self, bot, socket_token: str):
        self.bot = bot
        self.token = socket_token
        self.url = f"wss://sockets.streamlabs.com/socket?token={self.token}"
        self.ws = None
        self.connected = False
        self.task = None  # tarefa de conexão

    # ------------------------------------------------------------
    # CHAMADO AUTOMATICAMENTE QUANDO O COG É CARREGADO
    # ------------------------------------------------------------
    async def cog_load(self):
        print("[STREAMLABS] Cog carregado. Iniciando conexão assíncrona...")
        self.task = asyncio.create_task(self.connect_loop())

    # ------------------------------------------------------------
    # LOOP SEGURO (NUNCA TRAVA O BOT)
    # ------------------------------------------------------------
    async def connect_loop(self):
        """Loop permanente que tenta manter conexão ativa."""
        while True:
            if not self.connected:
                await self.try_connect()

            await asyncio.sleep(1)

    async def try_connect(self):
        """Tenta conectar SEM travar o bot."""
        try:
            print("[STREAMLABS] Conectando...")
            self.ws = await websockets.connect(self.url)
            self.connected = True
            print("[STREAMLABS] Conectado!")
        except Exception as e:
            print(f"[STREAMLABS] Falha ao conectar: {e}")
            self.connected = False
            await asyncio.sleep(3)  # espera sem travar

    # ------------------------------------------------------------
    # ENVIO DE MENSAGENS
    # ------------------------------------------------------------
    async def send(self, payload: dict):
        if not self.connected:
            return print("[STREAMLABS] Não conectado — comando ignorado.")

        try:
            await self.ws.send(json.dumps(payload))
        except Exception:
            print("[STREAMLABS] Conexão perdida. Tentando reconectar...")
            self.connected = False

    # ------------------------------------------------------------
    # CONTROLE DE FONTES
    # ------------------------------------------------------------
    async def show_source(self, scene, source_name):
        await self.send({
            "jsonrpc": "2.0",
            "method": "showSource",
            "params": {
                "resource": "ScenesService",
                "scene_name": scene,
                "source_name": source_name
            }
        })

    async def hide_source(self, scene, source_name):
        await self.send({
            "jsonrpc": "2.0",
            "method": "hideSource",
            "params": {
                "resource": "ScenesService",
                "scene_name": scene,
                "source_name": source_name
            }
        })


async def setup(bot):
    STREAMLABS_SOCKET_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbiI6IkQ0NDU2QjlCRTc2OEI2RkZDQTk0MzIwOTJDNzkwMkVCMzE5MTA5N0VEMTAxMjc5RDFENEEyN0YzOUY1REY3NThFMjQwQkVDRTNEMTk4MDVEMERBOTk3NkVDRTY1MzhDNTVFMkJBNjEwNUY3MTNBMzg5NENCOTNGMDgwRkNEMUU3QUYxNTRENkM0RUQ0Rjc0MTFERTIzQ0Q5Mzg3RUNEMjFBN0RCMUQ0Q0JFNDYyN0M0NTdEM0NFMkNFRkI1MjFBQzc2OEY4MzNEMUEzQjE2Q0NDQ0E2NTU1QTYyN0IyM0U5ODVBQURCMzQwODhFMDNCMDYyREEzRTU4RDgiLCJyZWFkX29ubHkiOnRydWUsInByZXZlbnRfbWFzdGVyIjp0cnVlLCJraWNrX2lkIjoiNjkzMjIwNDIifQ.vBa6gDl9rdFy2UfIQQ5cwN4eXR7Dh1aYjKzF74my7sY"
    await bot.add_cog(StreamlabsClient(bot, STREAMLABS_SOCKET_TOKEN))
