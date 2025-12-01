import cogs.voice_monitor as voice_monitor
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
import utils, random

class IniciativaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = utils.load_json("initiative", {})

    def save(self):
        utils.save_json("initiative", self.data)

    # =============================
    #  INTERFACE PRINCIPAL (UI)
    # =============================
    @commands.command(name="ini_ui")
    async def open_ui(self, ctx_or_inter):
        if isinstance(ctx_or_inter, voice_monitor.Interaction):
            target = ctx_or_inter
            ephemeral = True
        else:
            target = ctx_or_inter
            ephemeral = False

        # VIEW PRINCIPAL
        view = View()
        view.add_item(Button(label="Adicionar personagem", custom_id="ini_add"))
        view.add_item(Button(label="Mostrar ordem", custom_id="ini_show"))
        view.add_item(Button(label="Rolar iniciativa (todos)", custom_id="ini_rollall"))
        view.add_item(Button(label="Mover personagem", custom_id="ini_move"))
        view.add_item(Button(label="Remover personagem", custom_id="ini_remove"))

        # CALLBACK DOS BOTÕES
        async def callback(interaction):
            cid = interaction.data.get("custom_id")
            ch = str(interaction.channel_id)

            # --- REMOVER PERSONAGEM ---
            if cid == "ini_remove":
                await interaction.response.send_modal(IniRemoveModal(self))
                return

            # --- MOVER PERSONAGEM ---
            if cid == "ini_move":
                await interaction.response.send_modal(IniMoveModal(self))
                return

            # --- ADICIONAR PERSONAGEM ---
            if cid == "ini_add":
                await interaction.response.send_modal(IniAddModal(self))
                return

            # --- MOSTRAR ORDEM ---
            if cid == "ini_show":
                order = self.data.get(ch, [])
                if not order:
                    await interaction.response.send_message("Nenhuma iniciativa.", ephemeral=True)
                    return

                txt = "**Ordem de Iniciativa**\n"
                for i, entry in enumerate(sorted(order, key=lambda e: -e["score"])):
                    txt += f"{i+1}. {entry['name']} — {entry['score']} (mod {entry.get('mod',0)})\n"

                await interaction.response.send_message(txt, ephemeral=True)
                return

            # --- ROLAR TODOS ---
            if cid == "ini_rollall":
                order = self.data.get(ch, [])
                if not order:
                    await interaction.response.send_message("Nenhuma iniciativa.", ephemeral=True)
                    return

                for entry in order:
                    roll = random.randint(1, 20)
                    entry["last_roll"] = roll
                    entry["score"] = roll + entry.get("mod", 0)

                self.data[ch] = order
                self.save()

                txt = "**Rolagens:**\n"
                for e in sorted(order, key=lambda x: -x['score']):
                    txt += f"{e['name']}: roll {e['last_roll']} + mod {e.get('mod',0)} = {e['score']}\n"

                await interaction.response.send_message(txt, ephemeral=False)
                return

        # Atribui callbacks
        for child in view.children:
            child.callback = callback

        # ENVIA A INTERFACE PRINCIPAL
        if isinstance(target, voice_monitor.Interaction):
            await target.response.send_message("Interface de Iniciativa:", view=view, ephemeral=ephemeral)
        else:
            await target.send("Interface de Iniciativa:", view=view)

# =================================================================
#   MODAL — ADICIONAR PERSONAGEM
# =================================================================
class IniAddModal(Modal):
    def __init__(self, cog):
        super().__init__(title="Adicionar personagem (iniciativa)")
        self.cog = cog
        self.name = TextInput(label="Nome", required=True)
        self.mod = TextInput(label="Modificador (ex: 2 ou -1)", required=False, placeholder="0")
        self.add_item(self.name)
        self.add_item(self.mod)

    async def on_submit(self, interaction):
        ch = str(interaction.channel_id)
        try:
            mod = int(self.mod.value) if self.mod.value.strip() else 0
        except:
            await interaction.response.send_message("Modificador inválido.", ephemeral=True)
            return

        entry = {"name": self.name.value, "mod": mod, "score": 0}
        lst = self.cog.data.get(ch, [])
        lst.append(entry)

        self.cog.data[ch] = lst
        self.cog.save()

        await interaction.response.send_message(f"Adicionado {self.name.value} (mod {mod}).", ephemeral=True)

# =================================================================
#   MODAL — MOVER PERSONAGEM
# =================================================================
class IniMoveModal(Modal):
    def __init__(self, cog):
        super().__init__(title="Mover personagem na ordem")
        self.cog = cog
        self.name = TextInput(label="Nome do personagem", required=True)
        self.direction = TextInput(label="Direção (up/down)", placeholder="up ou down", required=True)
        self.add_item(self.name)
        self.add_item(self.direction)

    async def on_submit(self, interaction):
        ch = str(interaction.channel_id)
        order = self.cog.data.get(ch, [])

        nm = self.name.value
        names = [e["name"] for e in order]

        if nm not in names:
            await interaction.response.send_message("Personagem não encontrado.", ephemeral=True)
            return

        direction = self.direction.value.lower().strip()
        idx = names.index(nm)

        if direction == "up":
            if idx == 0:
                await interaction.response.send_message("Já está no topo.", ephemeral=True)
                return
            order[idx], order[idx-1] = order[idx-1], order[idx]

        elif direction == "down":
            if idx == len(order) - 1:
                await interaction.response.send_message("Já está no final.", ephemeral=True)
                return
            order[idx], order[idx+1] = order[idx+1], order[idx]

        else:
            await interaction.response.send_message("Use 'up' ou 'down'.", ephemeral=True)
            return

        self.cog.data[ch] = order
        self.cog.save()

        # =============================
        #  MOSTRAR ORDEM NOVA (NOVO)
        # =============================
        txt = "**Nova ordem de Iniciativa:**\n"
        for i, entry in enumerate(order):
            txt += f"{i+1}. {entry['name']} — {entry['score']} (mod {entry.get('mod',0)})\n"

        await interaction.response.send_message(f"{nm} movido para {direction}.\n\n{txt}", ephemeral=False)

# =================================================================
#   MODAL — REMOVER PERSONAGEM (NOVO)
# =================================================================
class IniRemoveModal(Modal):
    def __init__(self, cog):
        super().__init__(title="Remover personagem")
        self.cog = cog
        self.name = TextInput(label="Nome do personagem", required=True)
        self.add_item(self.name)

    async def on_submit(self, interaction):
        ch = str(interaction.channel_id)
        order = self.cog.data.get(ch, [])

        nm = self.name.value
        names = [e["name"] for e in order]

        if nm not in names:
            await interaction.response.send_message("Personagem não encontrado.", ephemeral=True)
            return

        # remover
        order = [e for e in order if e["name"] != nm]
        self.cog.data[ch] = order
        self.cog.save()

        txt = f"**{nm} removido.**\n\n**Ordem atual:**\n"
        for i, entry in enumerate(order):
            txt += f"{i+1}. {entry['name']} — {entry['score']} (mod {entry.get('mod',0)})\n"

        await interaction.response.send_message(txt, ephemeral=False)

async def setup(bot):
    await bot.add_cog(IniciativaCog(bot))
