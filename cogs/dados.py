import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
import utils

class DiceModal(Modal):
    def __init__(self, cog):
        super().__init__(title="Rolar dados")
        self.cog = cog
        self.expr = TextInput(label="Expressão (ex: 2d6+3)", placeholder="1d20+5", required=True)
        self.add_item(self.expr)
        self.preset = TextInput(label="Salvar como preset (opcional)", placeholder="nome_do_preset", required=False)
        self.add_item(self.preset)

    async def on_submit(self, interaction: discord.Interaction):
        expr = self.expr.value
        try:
            total, breakdown = utils.roll_dice(expr)
        except Exception as e:
            await interaction.response.send_message(f"Erro ao interpretar: {e}", ephemeral=True)
            return
        txt = f"**Rolar:** `{expr}`\n**Total:** {total}\n"
        for desc, rolls, sub in breakdown:
            if rolls:
                txt += f"`{desc}` → {rolls} = {sub}\n"
            else:
                txt += f"`{desc}` → {sub}\n"
        # save preset?
        if self.preset.value.strip():
            presets = utils.load_json("dice_presets", {})
            presets[self.preset.value.strip()] = expr
            utils.save_json("dice_presets", presets)
            txt += f"\n> Preset `{self.preset.value.strip()}` salvo."
        await interaction.response.send_message(txt, ephemeral=False)

class DadosCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="dados")
    async def open_ui(self, ctx_or_inter):
        view = View()
        view.add_item(Button(label="Rolar dados", custom_id="dice_roll"))
        view.add_item(Button(label="Presets", custom_id="dice_presets"))

        async def callback(interaction):
            cid = interaction.data.get("custom_id")
            if cid == "dice_roll":
                await interaction.response.send_modal(DiceModal(self))
            elif cid == "dice_presets":
                presets = utils.load_json("dice_presets", {})
                if not presets:
                    await interaction.response.send_message("Nenhum preset salvo.", ephemeral=True)
                    return
                # create dynamic buttons
                view2 = View()
                async def preset_cb(inter):
                    name = inter.data.get("custom_id").replace("preset_", "")
                    expr = presets.get(name)
                    if not expr:
                        await inter.response.send_message("Preset não encontrado.", ephemeral=True)
                        return
                    total, breakdown = utils.roll_dice(expr)
                    txt = f"**Preset:** `{name}` → `{expr}`\n**Total:** {total}\n"
                    for desc, rolls, sub in breakdown:
                        if rolls:
                            txt += f"`{desc}` → {rolls} = {sub}\n"
                        else:
                            txt += f"`{desc}` → {sub}\n"
                    await inter.response.send_message(txt, ephemeral=False)
                for name in presets:
                    btn = Button(label=name, custom_id=f"preset_{name}")
                    btn.callback = preset_cb
                    view2.add_item(btn)
                await interaction.response.send_message("Escolha um preset:", view=view2, ephemeral=True)

        for child in view.children:
            child.callback = callback

        if isinstance(ctx_or_inter, discord.Interaction):
            await ctx_or_inter.response.send_message("Interface de Dados:", view=view, ephemeral=True)
        else:
            await ctx_or_inter.send("Interface de Dados:", view=view)

    @commands.command(name="rolar")
    async def rolar_cmd(self, ctx, *, expr: str):
        presets = utils.load_json("dice_presets", {})
        if expr in presets:
            expr = presets[expr]
        try:
            total, breakdown = utils.roll_dice(expr)
        except Exception as e:
            await ctx.send(f"Erro: {e}")
            return
        txt = f"**Rolar:** `{expr}`\n**Total:** {total}\n"
        for desc, rolls, sub in breakdown:
            if rolls:
                txt += f"`{desc}` → {rolls} = {sub}\n"
            else:
                txt += f"`{desc}` → {sub}\n"
        await ctx.send(txt)

async def setup(bot):
    await bot.add_cog(DadosCog(bot))
