
import cogs.voice_monitor as voice_monitor
import cogs.streamlabs_client as streamlabs_client
from discord.ext import commands
import os
import dotenv
import discord

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)

# Auto-load all cogs in cogs/ folder
import os
import cogs.voice_monitor as voice_monitor
from discord.ext import commands

token = "MTM4MzEyMzc4OTM2MDkyMjg0NA.GMD9Xn.oZTrxRMgEssOs_32SKhDIf-8f-9w07GZ7dsdZI"

bot = commands.Bot(command_prefix=".", intents=intents)

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"Loaded cog: {filename}")
            except Exception as e:
                print(f"Failed to load {filename}: {e}")

@bot.event
async def on_ready():
    print(f"Bot ready: {bot.user}")

async def main():
    await load_cogs()
    await bot.start(token)

import asyncio
asyncio.run(main())


@bot.event
async def on_ready():
    print(f"Bot ready: {bot.user} (id: {bot.user.id})")

if __name__ == "__main__":
    bot.run(token)
