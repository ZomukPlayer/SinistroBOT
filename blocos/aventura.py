"""
BLOCO AVENTURA
Comandos: MS!aventura, MS!inventario
"""
import discord
from discord.ext import commands
import random

# Importar do bot.py
from __main__ import aventuras, MOBS

# ==================== FUNÇÕES ====================
def get_player(uid):
    return aventuras.get(uid)

def create_player(uid, nome):
    if uid not in aventuras:
        aventuras[uid] = {
            'nome': nome, 'hp': 20, 'fome': 10, 'level': 1, 'xp': 0,
            'local': 'floresta', 'itens': {}, 'arma': None, 'armadura': None,
            'escudo': False, 'mortes': 0,
        }

def has_item(uid, item, qty=1):
    p = get_player(uid)
    return p and p['itens'].get(item, 0) >= qty if p else False

def add_item(uid, item, qty=1):
    p = get_player(uid)
    if p:
        p['itens'][item] = p['itens'].get(item, 0) + qty

def remove_item(uid, item, qty=1):
    p = get_player(uid)
    if p and has_item(uid, item, qty):
        p['itens'][item] -= qty
        if p['itens'][item] == 0:
            del p['itens'][item]

def gain_xp(uid, qty):
    p = get_player(uid)
    if not p:
        return False
    p['xp'] += qty
    if p['xp'] >= p['level'] * 10:
        p['level'] += 1
        p['xp'] = 0
        p['hp'] = 20
        return True
    return False

# ==================== VIEWS ====================
class LocaisView(discord.ui.View):
    def __init__(self, uid, msg):
        super().__init__(timeout=None)
        self.uid = uid
        self.msg = msg
    
    @discord.ui.button(label="🗻 Caverna (Lv2+)", style=discord.ButtonStyle.primary)
    async def caverna(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        p = get_player(self.uid)
        if p['level'] < 2:
            await i.response.send_message("❌ Nível mínimo: 2", ephemeral=True)
            return
        
        p['local'] = 'caverna'
        
        if random.randint(1, 4) == 1:  # 25% de chance
            mob_e = random.choice(['🧟', '🕷️', '💀', '🧨'])
            mob = MOBS[mob_e]
            
            from .combate import CombateView
            
            view = CombateView(self.uid, mob, self.msg)
            desc = f"**{mob['nome']}**\n💪 HP: {mob['hp'][1]}\n\nEscolha sua ação:"
            embed = discord.Embed(title="⚔️ COMBATE!", description=desc, color=0xff8c00)
            await self.msg.edit(embed=embed, view=view)
            await i.response.send_message(embed=discord.Embed(title="⚠️ MOB APARECEU!", description=f"Um {mob['nome']} te atacou!", color=0xff0000), ephemeral=True)
        else:
            if random.randint(1, 10) >= 9:
                diamantes = random.randint(1, 3)
                add_item(self.uid, '💎', diamantes)
                lvl = gain_xp(self.uid, 10)
                desc = f"💎 **DIAMANTE ENCONTRADO!**\n+{diamantes}x 💎\n+10 XP"
                if lvl:
                    p = get_player(self.uid)
                    desc += f"\n\n🎉 LEVEL UP! Nível {p['level']}!"
                embed = discord.Embed(title="💎 SORTE!", description=desc, color=0x00FFFF)
            elif random.randint(1, 5) == 1:
                # Chance de encontrar Ferro
                ferro = random.randint(1, 3)
                add_item(self.uid, '⚙️', ferro)
                lvl = gain_xp(self.uid, 5)
                desc = f"⚙️ Você encontrou **{ferro}x ⚙️ Ferro**!\n+5 XP"
                if lvl:
                    p = get_player(self.uid)
                    desc += f"\n\n🎉 LEVEL UP! Nível {p['level']}!"
                embed = discord.Embed(title="⚙️ Ferro!", description=desc, color=0xC0C0C0)
            else:
                pedras = random.randint(3, 7)
                add_item(self.uid, '🪨', pedras)
                lvl = gain_xp(self.uid, 3)
                desc = f"⛏️ Você minerou **{pedras}x 🪨 Pedra**\n+3 XP"
                if lvl:
                    p = get_player(self.uid)
                    desc += f"\n\n🎉 LEVEL UP! Nível {p['level']}!"
                embed = discord.Embed(title="⛏️ Minério", description=desc, color=0x808080)
            
            await i.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🔥 Nether (Lv5+)", style=discord.ButtonStyle.danger)
    async def nether(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        p = get_player(self.uid)
        if p['level'] < 5:
            await i.response.send_message("❌ Nível mínimo: 5", ephemeral=True)
            return
        
        p['local'] = 'nether'
        
        from .combate import CombateView
        
        mob = MOBS['🐷']
        view = CombateView(self.uid, mob, self.msg)
        desc = f"**Piglin Feroz**\n💪 HP: {mob['hp'][1]}\n\nEscolha sua ação:"
        embed = discord.Embed(title="⚔️ COMBATE ÉPICO!", description=desc, color=0xff4500)
        await self.msg.edit(embed=embed, view=view)
        await i.response.send_message(embed=discord.Embed(title="🔥 NETHER!", description="Um **Piglin** feroz apareceu!", color=0xff0000), ephemeral=True)
    
    @discord.ui.button(label="🏜️ Deserto (Lv3+)", style=discord.ButtonStyle.secondary)
    async def deserto(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        p = get_player(self.uid)
        if p['level'] < 3:
            await i.response.send_message("❌ Nível mínimo: 3", ephemeral=True)
            return
        
        p['local'] = 'deserto'
        
        if random.randint(1, 10) >= 7:
            diamantes = random.randint(3, 6)
            add_item(self.uid, '💎', diamantes)
            lvl = gain_xp(self.uid, 12)
            desc = f"💎 **TESOURO ENCONTRADO!**\n+{diamantes}x 💎\n+12 XP"
            if lvl:
                p = get_player(self.uid)
                desc += f"\n\n🎉 LEVEL UP! Nível {p['level']}!"
            embed = discord.Embed(title="🏺 SORTE!", description=desc, color=0xffd700)
        else:
            pedras = random.randint(2, 4)
            add_item(self.uid, '🪨', pedras)
            lvl = gain_xp(self.uid, 3)
            desc = f"🏜️ Você achou **{pedras}x 🪨 Pedra** na areia\n+3 XP"
            if lvl:
                p = get_player(self.uid)
                desc += f"\n\n🎉 LEVEL UP! Nível {p['level']}!"
            embed = discord.Embed(title="🏜️ Areia", description=desc, color=0xf4a460)
        
        await i.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🌌 The End (5👁️)", style=discord.ButtonStyle.success)
    async def the_end(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        if not has_item(self.uid, '👁️', 5):
            olhos = get_player(self.uid)['itens'].get('👁️', 0)
            await i.response.send_message(f"❌ Você precisa de 5 Olhos do Fim!\n\n👁️ Você tem: {olhos}/5", ephemeral=True)
            return
        
        p = get_player(self.uid)
        p['local'] = 'the_end'
        
        # Remove os 5 olhos ao entrar
        remove_item(self.uid, '👁️', 5)
        
        from .end import CristaisView
        
        embed = discord.Embed(title="🌌 The End", description=f"**{p['nome']}**\n❤️ HP: {p['hp']:.0f}/20\n\n🐉 O Dragão te aguarda...", color=0x800080)
        await self.msg.edit(embed=embed)
        
        view = CristaisView(self.uid, self.msg)
        await view.update_embed()
        await self.msg.edit(view=view)
        
        await i.response.send_message("🌌 Bem-vindo ao The End!", ephemeral=True)

class OutrosView(discord.ui.View):
    def __init__(self, uid):
        super().__init__(timeout=60)
        self.uid = uid
    
    @discord.ui.button(label="📦 Inventário", style=discord.ButtonStyle.primary)
    async def inventario(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        p = get_player(self.uid)
        inv = "\n".join([f"{item}: **{qty}**" for item, qty in p['itens'].items()]) or "Inventário vazio"
        
        desc = f"**{p['nome']}** | Lv. {p['level']}\n❤️ HP: {p['hp']:.0f}/20 | 🍖 Fome: {p['fome']}/10\n\n"
        desc += f"**Itens:**\n{inv}\n\n"
        desc += f"⚔️ Arma: {p['arma'] if p['arma'] else 'Nenhuma'}\n"
        desc += f"🧥 Armadura: {p['armadura'] if p['armadura'] else 'Nenhuma'}\n"
        desc += f"🛡️ Escudo: {'Sim ✅' if p['escudo'] else 'Não ❌'}"
        
        embed = discord.Embed(title="📦 Inventário", description=desc, color=0x8B4513)
        await i.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🔨 Craftar", style=discord.ButtonStyle.secondary)
    async def craftar(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        from .crafting import CraftView
        
        view = CraftView(self.uid)
        await i.response.send_message(embed=discord.Embed(title="🔨 Crafting", description="Escolha uma opção:", color=0x8B4513), view=view, ephemeral=True)
    
    @discord.ui.button(label="🤝 Trade", style=discord.ButtonStyle.primary)
    async def trade(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🤝 Trade",
            description="Use o comando:\n`MS!trade @usuario`\n\nPara fazer trade com outro jogador!",
            color=0x4169e1
        )
        await i.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="👤 Perfil", style=discord.ButtonStyle.secondary)
    async def perfil(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        p = get_player(self.uid)
        
        desc = f"**{p['nome']}** | Lv. {p['level']}\n"
        desc += f"❤️ HP: {p['hp']:.0f}/20 | 🍖 Fome: {p['fome']}/10\n\n"
        
        desc += f"**STATS:**\n"
        desc += f"📊 XP: {p['xp']}/{p['level']*10}\n"
        desc += f"💀 Mortes: {p['mortes']}\n"
        desc += f"📍 Local: {p['local']}\n\n"
        
        desc += f"**EQUIPAMENTO:**\n"
        desc += f"⚔️ Arma: {p['arma'] if p['arma'] else 'Nenhuma'}\n"
        desc += f"🧥 Armadura: {p['armadura'] if p['armadura'] else 'Nenhuma'}\n"
        desc += f"🛡️ Escudo: {'Sim ✅' if p['escudo'] else 'Não ❌'}"
        
        embed = discord.Embed(title=f"👤 Seu Perfil", description=desc, color=0x8B4513)
        await i.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🏆 Ranking", style=discord.ButtonStyle.secondary)
    async def ranking(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        ranking_list = sorted(aventuras.items(), key=lambda x: (x[1]['level'], x[1]['xp']), reverse=True)[:5]
        
        desc = "🏆 **TOP 5 JOGADORES**\n\n"
        
        for idx, (uid, player) in enumerate(ranking_list, 1):
            emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
            desc += f"{emoji[idx-1]} **{player['nome']}** - Lv. {player['level']}\n"
        
        embed = discord.Embed(title="🏆 Ranking", description=desc, color=0xffd700)
        await i.response.send_message(embed=embed, ephemeral=True)

# ==================== VIEWS ====================
class AventuraView(discord.ui.View):
    def __init__(self, uid, msg):
        super().__init__(timeout=None)  # Timeout None = nunca expira
        self.uid = uid
        self.msg = msg
    
    async def update_embed(self):
        p = get_player(self.uid)
        barra = "🍖" * p['fome'] + "⬛" * (10 - p['fome'])
        desc = f"**{p['nome']}** | Lv. {p['level']} (XP: {p['xp']}/{p['level']*10})\n"
        desc += f"❤️ {p['hp']:.0f}/20 | {barra}\n\n"
        desc += f"⚔️ Arma: {p['arma'] if p['arma'] else 'Nenhuma'}\n"
        desc += f"🧥 Armadura: {p['armadura'] if p['armadura'] else 'Nenhuma'}\n"
        desc += f"🛡️ Escudo: {'Sim ✅' if p['escudo'] else 'Não ❌'}"
        
        embed = discord.Embed(title="🌲 Floresta", description=desc, color=0x00ff00)
        # Recriar a view para os botões não desaparecerem
        new_view = AventuraView(self.uid, self.msg)
        await self.msg.edit(embed=embed, view=new_view)
    
    @discord.ui.button(label="🪓 Cortar Árvore", style=discord.ButtonStyle.green)
    async def cortar(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        p = get_player(self.uid)
        p['fome'] = max(0, p['fome'] - 1)
        
        if random.randint(1, 10) == 1:
            dano = random.randint(3, 6)
            p['hp'] -= dano
            if p['hp'] <= 0:
                p['itens'].clear()
                p['hp'] = 20
                p['fome'] = 10
                p['level'] = max(1, p['level'] - 1)
                p['xp'] = 0
                p['mortes'] += 1
                desc = f"🧟 Um ZUMBI apareceu!\nVocê levou {dano} de dano!\n\n💀 **VOCÊ MORREU!**"
            else:
                desc = f"🧟 Um ZUMBI apareceu!\nVocê levou {dano} de dano!\n❤️ HP: {p['hp']:.0f}/20"
            await i.response.send_message(embed=discord.Embed(title="⚠️ ATAQUE!", description=desc, color=0xff0000), ephemeral=True)
        else:
            madeira = random.randint(2, 5)
            add_item(self.uid, '🪵', madeira)
            lvl = gain_xp(self.uid, 2)
            
            desc = f"🪓 Você cortou uma árvore!\n+{madeira}x 🪵 Madeira\n+2 XP"
            if lvl:
                p = get_player(self.uid)
                desc += f"\n\n🎉 LEVEL UP! Nível {p['level']}!"
            
            await i.response.send_message(embed=discord.Embed(title="🪓 Sucesso!", description=desc, color=0x8B4513), ephemeral=True)
        
        await self.update_embed()
    
    @discord.ui.button(label="✈️ Locais", style=discord.ButtonStyle.primary)
    async def locais(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        view = LocaisView(self.uid, self.msg)
        embed = discord.Embed(title="✈️ Escolha um Local", description="Para onde você quer viajar?", color=0x4169e1)
        await i.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="📋 Outros", style=discord.ButtonStyle.secondary)
    async def outros(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        view = OutrosView(self.uid)
        embed = discord.Embed(title="📋 Menu Outros", description="Escolha uma opção:", color=0x9370DB)
        await i.response.send_message(embed=embed, view=view, ephemeral=True)
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        from .crafting import CraftView
        
        view = CraftView(self.uid)
        await i.response.send_message(embed=discord.Embed(title="🔨 Crafting", description="Escolha uma opção:", color=0x8B4513), view=view, ephemeral=True)
    
    @discord.ui.button(label="🍖 Comer (5🪵)", style=discord.ButtonStyle.danger, row=1)
    async def comer(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        if not has_item(self.uid, '🪵', 5):
            await i.response.send_message(embed=discord.Embed(title="❌ Sem Madeira", description="Você precisa de 5x 🪵!", color=0xff0000), ephemeral=True)
            return
        
        p = get_player(self.uid)
        remove_item(self.uid, '🪵', 5)
        
        # 30% de chance de conseguir Couro de um animal
        couro_obtido = random.randint(1, 4) == 1
        
        # Regenera vida quando fome está cheia
        if p['fome'] >= 10:
            recuperar_hp = random.randint(2, 4)
            p['hp'] = min(20, p['hp'] + recuperar_hp)
            desc = f"🍖 Você comeu carne e regenerou **{recuperar_hp} HP**!\n❤️ {p['hp']:.0f}/20"
            
            if couro_obtido:
                add_item(self.uid, '🥩', 1)
                desc += f"\n\n🥩 Você obteve um Couro de animal!"
        else:
            recuperar_fome = random.randint(3, 5)
            p['fome'] = min(10, p['fome'] + recuperar_fome)
            desc = f"🍖 Você comeu e recuperou **{recuperar_fome} fome**!\n🍖 {p['fome']}/10"
            
            if couro_obtido:
                add_item(self.uid, '🥩', 1)
                desc += f"\n\n🥩 Você obteve um Couro de animal!"
        
        await i.response.send_message(embed=discord.Embed(title="🍖 Comeu!", description=desc, color=0xff0000), ephemeral=True)
        await self.update_embed()
    
    @discord.ui.button(label="😴 Dormir", style=discord.ButtonStyle.success, row=1)
    async def dormir(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        if not has_item(self.uid, '🛏️'):
            await i.response.send_message(embed=discord.Embed(title="❌ Sem Cama", description="Craft uma cama (3🪵)", color=0xff0000), ephemeral=True)
            return
        
        p = get_player(self.uid)
        p['hp'] = 20
        p['fome'] = 10
        
        await i.response.send_message(embed=discord.Embed(title="😴 Dormiu!", description="Recuperou TODO HP e fome!\n❤️ 20/20 | 🍖 10/10", color=0x4169e1), ephemeral=True)
        await self.update_embed()

# ==================== COG ====================
class Aventura(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='aventura')
    async def aventura_cmd(self, ctx):
        """Inicia uma aventura Minecraft"""
        uid = ctx.author.id
        create_player(uid, ctx.author.display_name)
        p = get_player(uid)
        
        barra = "🍖" * p['fome'] + "⬛" * (10 - p['fome'])
        desc = f"**{p['nome']}** | Lv. {p['level']}\n❤️ {p['hp']}/20 | {barra}\n\n"
        desc += "Você acordou em uma floresta densa.\nEscolha uma ação:"
        
        embed = discord.Embed(title="🌲 Floresta do Minecraft", description=desc, color=0x00ff00)
        msg = await ctx.send(embed=embed)
        view = AventuraView(uid, msg)
        await msg.edit(view=view)
    
    @commands.command(name='inventario')
    async def inventario_cmd(self, ctx):
        """Mostra seu inventário"""
        uid = ctx.author.id
        p = get_player(uid)
        
        if not p:
            embed = discord.Embed(title="❌ Sem Aventura", description="Use `MS!aventura` para começar!", color=0xff0000)
            await ctx.send(embed=embed)
            return
        
        inv = "\n".join([f"{item}: **{qty}**" for item, qty in p['itens'].items()]) or "Inventário vazio"
        
        desc = f"**{p['nome']}** | Lv. {p['level']}\n❤️ HP: {p['hp']:.0f}/20 | 🍖 Fome: {p['fome']}/10\n\n"
        desc += f"**Itens:**\n{inv}\n\n"
        desc += f"⚔️ Arma: {p['arma'] if p['arma'] else 'Nenhuma'}\n"
        desc += f"🧥 Armadura: {p['armadura'] if p['armadura'] else 'Nenhuma'}\n"
        desc += f"🛡️ Escudo: {'Sim ✅' if p['escudo'] else 'Não ❌'}\n\n"
        desc += f"💀 Mortes: {p['mortes']}"
        
        embed = discord.Embed(title="📦 Inventário", description=desc, color=0x8B4513)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Aventura(bot))
