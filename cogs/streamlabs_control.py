from flask import Flask, request, jsonify
import asyncio
import websockets
import json

app = Flask(__name__)

SL_PORT = 59650        # Porta do Streamlabs (veja nas configurações)
SL_TOKEN = "5914d9a47f2a945911ec29083e45be7f53a326"

async def set_visible(source_name):
    async with websockets.connect(f"ws://127.0.0.1:{SL_PORT}/api/websocket") as ws:
        # autenticar
        await ws.send(json.dumps({
            "jsonrpc": "2.0",
            "method": "auth",
            "params": {"token": SL_TOKEN},
            "id": 1
        }))
        await ws.recv()

        # enviar comando
        await ws.send(json.dumps({
            "jsonrpc": "2.0",
            "method": "setSceneItemEnabled",
            "params": {
                "sceneItemName": source_name,
                "enabled": True
            },
            "id": 2
        }))

@app.route("/toggle_source", methods=["POST"])
def toggle_source():
    data = request.json
    source = data.get("source")
    asyncio.run(set_visible(source))
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(port=3000)   # Servidor HTTP escutando na porta 3000

import discord
from discord.ext import commands

class StreamlabsControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sl_test")
    async def test(self, ctx):
        await ctx.send("✅ Streamlabs Control carregado!")

async def setup(bot):
    await bot.add_cog(StreamlabsControl(bot))
