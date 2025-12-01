ROG_RPG - SquareCloud deployment package
---------------------------------------

How to deploy:
1. Upload this ZIP to SquareCloud (or GitHub linked).
2. In SquareCloud Dashboard -> Variables, add:
   - DISCORD_TOKEN = your_bot_token

3. Start command is already set to: python bot.py

Local dev:
- Copy .env (not included) with DISCORD_TOKEN or TOKEN
- Create virtualenv and install requirements:
    pip install -r requirements.txt
- Run:
    python bot.py

Files of interest:
- bot.py: loader and startup
- utils.py: simple persistence and dice roller
- cogs/: all bot extensions (dados, interface, iniciativa, mapa, comandos)

