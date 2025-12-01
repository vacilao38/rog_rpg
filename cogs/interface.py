import cogs.voice_monitor as voice_monitor
from discord.ext import commands
from discord.ui import View, Button

class InterfaceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="start_ui")
    async def start_ui(self, ctx):
        view = View()
        view.add_item(Button(label="Dados", custom_id="ui_dados"))
        view.add_item(Button(label="Mapa", custom_id="ui_mapa"))
        view.add_item(Button(label="Iniciativa", custom_id="ui_iniciativa"))

        async def callback(interaction):
            cid = interaction.data.get("custom_id")

            if cid == "ui_dados":
                cog = self.bot.get_cog("DadosCog")
                if cog:
                    await cog.open_ui(interaction)
                return

            if cid == "ui_mapa":
                cog = self.bot.get_cog("MapaCog")
                if cog:
                    await cog.open_ui(interaction)
                return

            if cid == "ui_iniciativa":
                cog = self.bot.get_cog("IniciativaCog")
                if cog:
                    await cog.open_ui(interaction)
                return

        for child in view.children:
            child.callback = callback

        await ctx.send("Painel principal — escolha uma função:", view=view)


async def setup(bot):
    await bot.add_cog(InterfaceCog(bot))
