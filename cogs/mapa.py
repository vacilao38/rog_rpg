import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
import utils
from copy import deepcopy

DEFAULT_ROWS = 30
DEFAULT_COLS = 30
MAX_CHAR = 50

def letters_to_index(letters: str) -> int:
    letters = letters.upper()
    total = 0
    for ch in letters:
        if not ('A' <= ch <= 'Z'):
            raise ValueError("Invalid row letter")
        total = total * 26 + (ord(ch) - ord('A') + 1)
    return total - 1

def index_to_letters(index: int) -> str:
    if index < 0:
        raise ValueError("Negative index")
    s = ""
    i = index + 1
    while i > 0:
        i, r = divmod(i - 1, 26)
        s = chr(ord('A') + r) + s
    return s

def parse_coord(coord: str):
    coord = coord.strip().upper()
    if not coord:
        raise ValueError("Empty coordinate")
    i = 0
    while i < len(coord) and coord[i].isalpha():
        i += 1
    if i == 0 or i == len(coord):
        raise ValueError("Coordinate must be LETTERS+NUMBERS, ex: A1 or AA12")
    letters = coord[:i]
    numbers = coord[i:]
    if not numbers.isdigit():
        raise ValueError("Column must be numeric")
    row = letters_to_index(letters)
    col = int(numbers) - 1
    return row, col

def render_map_text(m: dict) -> str:
    rows = m.get("rows", DEFAULT_ROWS)
    cols = m.get("cols", DEFAULT_COLS)
    base = [["." for _ in range(cols)] for _ in range(rows)]
    tokens = m.get("tokens", {})
    for name, data in tokens.items():
        coord = data.get("coord")
        emoji = data.get("emoji", data.get("sym", "?"))
        try:
            r, c = parse_coord(coord)
        except Exception:
            continue
        if 0 <= r < rows and 0 <= c < cols:
            base[r][c] = emoji
    header = "    " + " ".join(f"{i+1:2}" for i in range(cols))
    lines = [header]
    for r in range(rows):
        row_letter = index_to_letters(r)
        row_cells = " ".join(f"{base[r][c]:2}" for c in range(cols))
        lines.append(f"{row_letter:>2} | {row_cells}")
    return "```\n" + "\n".join(lines) + "\n```"

class MapaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.maps = utils.load_json("maps", {})

    def save(self):
        utils.save_json("maps", self.maps)

    @commands.command(name="mapa_ui")
    async def open_ui(self, ctx_or_inter):
        if isinstance(ctx_or_inter, discord.Interaction):
            target = ctx_or_inter
            ephemeral = True
        else:
            target = ctx_or_inter
            ephemeral = False

        view = View()
        view.add_item(Button(label="Criar mapa (paste)", custom_id="map_create"))
        view.add_item(Button(label="Colocar token", custom_id="map_place"))
        view.add_item(Button(label="Mover token", custom_id="map_move"))
        view.add_item(Button(label="Remover token", custom_id="map_remove"))
        view.add_item(Button(label="Mostrar mapa", custom_id="map_show"))
        view.add_item(Button(label="Apagar mapa", custom_id="map_delete"))

        async def callback(interaction: discord.Interaction):
            cid = interaction.data.get("custom_id")
            ch = str(interaction.channel_id)

            if cid == "map_create":
                await interaction.response.send_modal(MapCreateModal(self))
                return

            if cid == "map_place":
                await interaction.response.send_modal(MapPlaceModal(self))
                return

            if cid == "map_move":
                await interaction.response.send_modal(MapMoveModal(self))
                return

            if cid == "map_remove":
                await interaction.response.send_modal(MapRemoveModal(self))
                return

            if cid == "map_show":
                m = self.maps.get(ch)
                if not m:
                    await interaction.response.send_message("Nenhum mapa criado neste canal.", ephemeral=True)
                    return
                await interaction.response.send_message(render_map_text(m), ephemeral=False)
                return

            if cid == "map_delete":
                if ch in self.maps:
                    del self.maps[ch]
                    self.save()
                    await interaction.response.send_message("Mapa apagado.", ephemeral=True)
                else:
                    await interaction.response.send_message("Nenhum mapa para apagar.", ephemeral=True)
                return

        for child in view.children:
            child.callback = callback

        if isinstance(target, discord.Interaction):
            await target.response.send_message("Interface de Mapa:", view=view, ephemeral=ephemeral)
        else:
            await target.send("Interface de Mapa:", view=view)

    @commands.command(name="mapa")
    async def mapa_cmd(self, ctx, rows: int = DEFAULT_ROWS, cols: int = DEFAULT_COLS):
        ch = str(ctx.channel.id)
        rows = max(1, min(100, rows))
        cols = max(1, min(100, cols))
        self.maps[ch] = {"rows": rows, "cols": cols, "tokens": {}}
        self.save()
        await ctx.send(f"Mapa criado com tamanho {rows}x{cols}.")

class MapCreateModal(Modal):
    def __init__(self, cog):
        super().__init__(title="Criar mapa (cole o grid opcional)")
        self.cog = cog
        self.rows = TextInput(label="Linhas (A..)", placeholder=str(DEFAULT_ROWS), required=False)
        self.add_item(self.rows)
        self.cols = TextInput(label="Colunas", placeholder=str(DEFAULT_COLS), required=False)
        self.add_item(self.cols)
        self.raw = TextInput(label="Grid (opcional, cada linha no formato 'A . . .')", style=discord.TextStyle.long, required=False)
        self.add_item(self.raw)

    async def on_submit(self, interaction: discord.Interaction):
        ch = str(interaction.channel_id)
        try:
            r = int(self.rows.value) if self.rows.value and self.rows.value.strip() else DEFAULT_ROWS
            c = int(self.cols.value) if self.cols.value and self.cols.value.strip() else DEFAULT_COLS
        except:
            await interaction.response.send_message("Linhas/colunas inválidas.", ephemeral=True)
            return
        r = max(1, min(100, r))
        c = max(1, min(100, c))
        m = {"rows": r, "cols": c, "tokens": {}}
        self.cog.maps[ch] = m
        self.cog.save()
        await interaction.response.send_message(f"Mapa criado ({r}x{c}). Use 'Colocar token' para adicionar.", ephemeral=True)

class MapPlaceModal(Modal):
    def __init__(self, cog):
        super().__init__(title="Colocar token")
        self.cog = cog
        self.emoji = TextInput(label="Emoji / Símbolo (ex: 🧙‍♂️ ou @P)", required=True)
        self.add_item(self.emoji)
        self.name = TextInput(label="Nome do token (único)", required=True)
        self.add_item(self.name)
        self.coord = TextInput(label="Coordenada (ex: A1)", required=True)
        self.add_item(self.coord)

    async def on_submit(self, interaction: discord.Interaction):
        ch = str(interaction.channel_id)
        m = self.cog.maps.get(ch)
        if not m:
            await interaction.response.send_message("Nenhum mapa criado neste canal. Use Criar mapa.", ephemeral=True)
            return
        nm = self.name.value.strip()
        emoji = self.emoji.value.strip()
        coord = self.coord.value.strip().upper()
        tokens = m.setdefault("tokens", {})
        if nm in tokens:
            await interaction.response.send_message("Já existe um token com esse nome.", ephemeral=True)
            return
        if len(tokens) >= MAX_CHAR:
            await interaction.response.send_message(f"Máximo de tokens ({MAX_CHAR}) atingido.", ephemeral=True)
            return
        try:
            r, c = parse_coord(coord)
        except Exception as e:
            await interaction.response.send_message(f"Coordenada inválida: {e}", ephemeral=True)
            return
        if not (0 <= r < m["rows"] and 0 <= c < m["cols"]):
            await interaction.response.send_message("Coordenada fora do mapa.", ephemeral=True)
            return
        for other, d in tokens.items():
            if d.get("coord") == coord:
                await interaction.response.send_message("Coord já ocupada por " + other, ephemeral=True)
                return
        tokens[nm] = {"emoji": emoji, "coord": coord}
        self.cog.save()
        await interaction.response.send_message(f"{nm} colocado em {coord}.", ephemeral=True)

class MapMoveModal(Modal):
    def __init__(self, cog):
        super().__init__(title="Mover token")
        self.cog = cog
        self.name = TextInput(label="Nome do token", required=True)
        self.add_item(self.name)
        self.coord = TextInput(label="Nova coordenada (ex: A1)", required=True)
        self.add_item(self.coord)

    async def on_submit(self, interaction: discord.Interaction):
        ch = str(interaction.channel_id)
        m = self.cog.maps.get(ch)
        if not m:
            await interaction.response.send_message("Nenhum mapa criado neste canal.", ephemeral=True)
            return
        nm = self.name.value.strip()
        newcoord = self.coord.value.strip().upper()
        tokens = m.get("tokens", {})
        if nm not in tokens:
            await interaction.response.send_message("Token não encontrado.", ephemeral=True)
            return
        try:
            r, c = parse_coord(newcoord)
        except Exception as e:
            await interaction.response.send_message(f"Coordenada inválida: {e}", ephemeral=True)
            return
        if not (0 <= r < m["rows"] and 0 <= c < m["cols"]):
            await interaction.response.send_message("Coordenada fora do mapa.", ephemeral=True)
            return
        for other, d in tokens.items():
            if d.get("coord") == newcoord:
                await interaction.response.send_message(f"Coord já ocupada por {other}.", ephemeral=True)
                return
        tokens[nm]["coord"] = newcoord
        self.cog.save()
        txt = render_map_text(m)
        await interaction.response.send_message(f"{nm} movido para {newcoord}.\n{txt}", ephemeral=False)

class MapRemoveModal(Modal):
    def __init__(self, cog):
        super().__init__(title="Remover token")
        self.cog = cog
        self.name = TextInput(label="Nome do token", required=True)
        self.add_item(self.name)

    async def on_submit(self, interaction: discord.Interaction):
        ch = str(interaction.channel_id)
        m = self.cog.maps.get(ch)
        if not m:
            await interaction.response.send_message("Nenhum mapa criado neste canal.", ephemeral=True)
            return
        nm = self.name.value.strip()
        tokens = m.get("tokens", {})
        if nm not in tokens:
            await interaction.response.send_message("Token não encontrado.", ephemeral=True)
            return
        del tokens[nm]
        self.cog.save()
        await interaction.response.send_message(f"{nm} removido do mapa.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(MapaCog(bot))
