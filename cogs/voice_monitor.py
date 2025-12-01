import discord
from discord.ext import commands
from discord import app_commands
import asyncio

from .streamlabs_client import StreamlabsClient


class VoiceMonitor(commands.Cog):
    """
    Cog que monitora eventos de voz e controla o Streamlabs.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # Apensa definimos; não conectamos ainda.
        self.sls = StreamlabsClient(
            "wss://sockets.streamlabs.com/v1/socket?token=51d5c7a9b4258e5566516fcc7a7454a64b62a41"

        )

        self.scene_name = "sessão Realidades"
        self.fontes = {
            "fonte1": "5914d9a47f2a945911ec29083e45be7f53a326",
            "fonte2": "OutraFonteAqui",
            "fonte3": "MaisUmaFonteAqui",
        }

    # ============================================================
    #   Inicialização ASSÍNCRONA correta (sem acessar bot.loop)
    # ============================================================
    async def cog_load(self):
        """
        Executa quando o cog é carregado — isso é seguro e async.
        """
        await asyncio.sleep(1)  # pequeno delay para o bot estabilizar
        print("[VOICE_MONITOR] Conectando ao Streamlabs...")
        await self.sls.connect()


    # ============================================================
    #   EVENTOS DE VOZ
    # ============================================================
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is None and after.channel is not None:
            print(f"[VOICE] {member} entrou")
            await self.sls.show_source(self.scene_name, self.fontes["fonte1"])

        if before.channel is not None and after.channel is None:
            print(f"[VOICE] {member} saiu")
            await self.sls.hide_source(self.scene_name, self.fontes["fonte1"])

        if before.self_mute is False and after.self_mute is True:
            print(f"[VOICE] {member} mutou")
            await self.sls.show_source(self.scene_name, self.fontes["fonte2"])

        if before.self_mute is True and after.self_mute is False:
            print(f"[VOICE] {member} desmutou")
            await self.sls.hide_source(self.scene_name, self.fontes["fonte2"])


    # ============================================================
    #   SLASH COMMANDS
    # ============================================================
    group = app_commands.Group(
        name="streamlabs",
        description="Controle manual do Streamlabs"
    )

    @group.command(name="ligar")
    async def ligar_cmd(self, interaction: discord.Interaction, fonte: str):
        if fonte not in self.fontes:
            await interaction.response.send_message("Fonte não existe.")
            return
        
        await self.sls.show_source(self.scene_name, self.fontes[fonte])
        await interaction.response.send_message(f"Ativada {fonte}!")

    @group.command(name="desligar")
    async def desligar_cmd(self, interaction: discord.Interaction, fonte: str):
        if fonte not in self.fontes:
            await interaction.response.send_message("Fonte não existe.")
            return
        
        await self.sls.hide_source(self.scene_name, self.fontes[fonte])
        await interaction.response.send_message(f"Desativada {fonte}!")

    @group.command(name="listar")
    async def listar_cmd(self, interaction: discord.Interaction):
        linhas = "\n".join(
            [f"- **{k}** → `{v}`" for k, v in self.fontes.items()]
        )
        await interaction.response.send_message(f"Fontes:\n{linhas}")


async def setup(bot):
    await bot.add_cog(VoiceMonitor(bot))
