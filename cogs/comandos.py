import discord
from discord.ext import commands
from discord.ui import View, Button

class ComandosCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="comandos")
    async def comandos(self, ctx):
        view = View(timeout=None)
        view.add_item(Button(label="🎲 Dados", style=discord.ButtonStyle.primary, custom_id="cmd_dados"))
        view.add_item(Button(label="🗺️ Mapa", style=discord.ButtonStyle.primary, custom_id="cmd_mapa"))
        view.add_item(Button(label="⚔️ Iniciativa", style=discord.ButtonStyle.primary, custom_id="cmd_iniciativa"))
        view.add_item(Button(label="🎛️ Painel Principal", style=discord.ButtonStyle.secondary, custom_id="cmd_startui"))

        async def cb(interaction: discord.Interaction):
            cid = interaction.data.get("custom_id")
            if cid == "cmd_dados":
                cog = self.bot.get_cog("DadosCog")
                if cog:
                    await interaction.response.send_message("Abrindo interface de Dados...", ephemeral=True)
                    await cog.open_ui(interaction)
                return
            if cid == "cmd_mapa":
                cog = self.bot.get_cog("MapaCog")
                if cog:
                    await interaction.response.send_message("Abrindo interface de Mapa...", ephemeral=True)
                    await cog.open_ui(interaction)
                return
            if cid == "cmd_iniciativa":
                cog = self.bot.get_cog("IniciativaCog")
                if cog:
                    await interaction.response.send_message("Abrindo interface de Iniciativa...", ephemeral=True)
                    await cog.open_ui(interaction)
                return
            if cid == "cmd_startui":
                cog = self.bot.get_cog("InterfaceCog")
                if cog:
                    await interaction.response.send_message("Abrindo painel principal...", ephemeral=True)
                    await cog.start_ui(interaction)
                return

        for child in view.children:
            child.callback = cb

        await ctx.send("📜 **Painel de Comandos** — escolha uma função:", view=view)

async def setup(bot):
    await bot.add_cog(ComandosCog(bot))
