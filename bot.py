import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()  # for local dev; SquareCloud uses environment variables in dashboard

token = os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN")
if not token:
    print("ERROR: Discord token not found. Set DISCORD_TOKEN environment variable.")
    raise SystemExit(1)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)

async def load_cogs():
    for filename in sorted(os.listdir("cogs")):
        if filename.endswith(".py"):
            ext = f"cogs.{filename[:-3]}"
            try:
                await bot.load_extension(ext)
                print("Loaded cog:", filename)
            except Exception as e:
                print("Failed to load", filename, ":", e)

@bot.event
async def on_ready():
    print(f"Bot ready: {bot.user} (id: {bot.user.id})")

async def main():
    await load_cogs()
    await bot.start(token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")
