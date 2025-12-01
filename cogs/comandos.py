import cogs.voice_monitor as voice_monitor
from discord.ext import commands
from discord.ui import View, Button

class ComandosCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="comandos")
    async def comandos(self, ctx):
        """
        Abre uma interface com todos os comandos principais do bot.
        """
        view = View(timeout=None)

        # Botão: Dados
        view.add_item(Button(
            label="🎲 Dados",
            style=voice_monitor.ButtonStyle.primary,
            custom_id="cmd_dados"
        ))

        # Botão: Mapa
        view.add_item(Button(
            label="🗺️ Mapa",
            style=voice_monitor.ButtonStyle.primary,
            custom_id="cmd_mapa"
        ))

        # Botão: Iniciativa
        view.add_item(Button(
            label="⚔️ Iniciativa",
            style=voice_monitor.ButtonStyle.primary,
            custom_id="cmd_iniciativa"
        ))

        # Botão: Painel Principal (equiv. start_ui)
        view.add_item(Button(
            label="🎛️ Painel Principal",
            style=voice_monitor.ButtonStyle.secondary,
            custom_id="cmd_startui"
        ))

        async def cb(interaction: voice_monitor.Interaction):
            cid = interaction.data.get("custom_id")

            # --- Dados ---
            if cid == "cmd_dados":
                cog = self.bot.get_cog("DadosCog")
                if cog:
                    await interaction.response.send_message(
                        "Abrindo interface de Dados...",
                        ephemeral=True
                    )
                    await cog.open_ui(interaction)
                return

            # --- Mapa ---
            if cid == "cmd_mapa":
                cog = self.bot.get_cog("MapaCog")
                if cog:
                    await interaction.response.send_message(
                        "Abrindo interface de Mapa...",
                        ephemeral=True
                    )
                    await cog.open_ui(interaction)
                return

            # --- Iniciativa ---
            if cid == "cmd_iniciativa":
                cog = self.bot.get_cog("IniciativaCog")
                if cog:
                    await interaction.response.send_message(
                        "Abrindo interface de Iniciativa...",
                        ephemeral=True
                    )
                    await cog.open_ui(interaction)
                return

            # --- Painel Principal ---
            if cid == "cmd_startui":
                cog = self.bot.get_cog("InterfaceCog")
                if cog:
                    await interaction.response.send_message(
                        "Abrindo painel principal...",
                        ephemeral=True
                    )
                    await cog.start_ui(ctx)
                return

        # atribuir callbacks
        for child in view.children:
            child.callback = cb

        await ctx.send("📜 **Painel de Comandos** — escolha uma função:", view=view)


async def setup(bot):
    await bot.add_cog(ComandosCog(bot))
