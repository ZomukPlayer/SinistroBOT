"""
BLOCO AVENTURA - v2.0
VERSÃO: 2.0
ÚLTIMA ATUALIZAÇÃO: 28/10/2025

SISTEMAS:
- Criar/Pausar/Retomar/Recomeçar aventura
- Caça de comida (🔱 Caçar)
- Dormir (😴 Dormir)
- Menu Outros (Inventário, Craftar, Trade, Perfil, Ranking)
- Locais (Caverna, Nether, Deserto, The End)
"""
import discord
from discord.ext import commands
import random

# Variável global que será injetada pelo bot.py
aventuras = {}

def set_aventuras(dict_ref):
    """Função para injetar a referência do dicionário global"""
    global aventuras
    aventuras = dict_ref

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

# ==================== MENU PAUSA ====================
class MenuAventuraView(discord.ui.View):
    def __init__(self, uid, ctx):
        super().__init__(timeout=60)
        self.uid = uid
        self.ctx = ctx
    
    @discord.ui.button(label="▶️ Retomar", style=discord.ButtonStyle.green)
    async def retomar(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        p = get_player(self.uid)
        barra = "🍖" * p['fome'] + "⬛" * (10 - p['fome'])
        
        desc = f"**{p['nome']}** | Lv. {p['level']} (XP: {p['xp']}/{p['level']*10})\n"
        desc += f"❤️ {p['hp']:.0f}/20 | {barra}\n\n"
        desc += f"⚔️ Arma: {p['arma'] if p['arma'] else 'Nenhuma'}\n"
        desc += f"🧥 Armadura: {p['armadura'] if p['armadura'] else 'Nenhuma'}\n"
        desc += f"🛡️ Escudo: {'Sim ✅' if p['escudo'] else 'Não ❌'}"
        
        embed = discord.Embed(title="🌲 Floresta", description=desc, color=0x00ff00)
        msg = await self.ctx.send(embed=embed)
        view = AventuraView(self.uid, msg)
        await msg.edit(view=view)
        await i.response.send_message("▶️ Aventura retomada!", ephemeral=True)
    
    @discord.ui.button(label="⏸️ Pausar", style=discord.ButtonStyle.primary)
    async def pausar(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        p = get_player(self.uid)
        desc = f"⏸️ **Aventura Pausada**\n\n"
        desc += f"**{p['nome']}** | Lv. {p['level']}\n"
        desc += f"❤️ HP: {p['hp']:.0f}/20 | 🍖 Fome: {p['fome']}/10\n\n"
        desc += f"Use `MS!aventura` para retomar!"
        
        embed = discord.Embed(title="⏸️ Pausado", description=desc, color=0xFFD700)
        await i.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🔄 Recomeçar", style=discord.ButtonStyle.danger)
    async def recomecar(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        view = ConfirmarView(self.uid, self.ctx)
        embed = discord.Embed(title="⚠️ Confirmar?", description="Tem certeza que quer recomeçar?\n\n⚠️ Você perderá TODO progresso!", color=0xff0000)
        await i.response.send_message(embed=embed, view=view, ephemeral=True)

class ConfirmarView(discord.ui.View):
    def __init__(self, uid, ctx):
        super().__init__(timeout=30)
        self.uid = uid
        self.ctx = ctx
    
    @discord.ui.button(label="✅ Sim, Recomeçar", style=discord.ButtonStyle.danger)
    async def confirmar(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        if self.uid in aventuras:
            del aventuras[self.uid]
        
        create_player(self.uid, i.user.display_name)
        p = get_player(self.uid)
        
        barra = "🍖" * p['fome'] + "⬛" * (10 - p['fome'])
        desc = f"**{p['nome']}** | Lv. {p['level']}\n❤️ {p['hp']}/20 | {barra}\n\n"
        desc += "Você acordou em uma floresta densa.\nEscolha uma ação:"
        
        embed = discord.Embed(title="🌲 Floresta do Minecraft", description=desc, color=0x00ff00)
        msg = await self.ctx.send(embed=embed)
        view = AventuraView(self.uid, msg)
        await msg.edit(view=view)
        await i.response.send_message("🔄 Aventura recomeçada!", ephemeral=True)
    
    @discord.ui.button(label="❌ Cancelar", style=discord.ButtonStyle.secondary)
    async def cancelar(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.send_message("❌ Recomeço cancelado!", ephemeral=True)

# ==================== LOCAIS ====================
class LocaisView(discord.ui.View):
    def __init__(self, uid, msg):
        super().__init__(timeout=60)
        self.uid = uid
        self.msg = msg
    
    @discord.ui.button(label="🕳️ Caverna", style=discord.ButtonStyle.primary)
    async def caverna(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        p = get_player(self.uid)
        p['local'] = 'caverna'
        p['fome'] = max(0, p['fome'] - 2)
        
        desc = f"🕳️ Você entrou em uma caverna escura!\n\n-2 Fome\n\nLocal: {p['local'].title()}"
        embed = discord.Embed(title="🕳️ Caverna", description=desc, color=0x696969)
        await i.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🔥 Nether", style=discord.ButtonStyle.danger)
    async def nether(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        p = get_player(self.uid)
        dano = random.randint(2, 5)
        p['hp'] -= dano
        p['fome'] = max(0, p['fome'] - 3)
        
        if p['hp'] <= 0:
            p['hp'] = 20
            p['fome'] = 10
            p['itens'].clear()
            desc = f"🔥 Você foi para o Nether!\n\n💀 **VOCÊ MORREU NA LAVA!**"
        else:
            desc = f"🔥 Você entrou no Nether!\nTomou {dano} de dano!\n\n❤️ HP: {p['hp']:.0f}/20"
        
        embed = discord.Embed(title="🔥 Nether", description=desc, color=0xFF6347)
        await i.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🏜️ Deserto", style=discord.ButtonStyle.secondary)
    async def deserto(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        p = get_player(self.uid)
        p['local'] = 'deserto'
        p['fome'] = max(0, p['fome'] - 3)
        
        desc = f"🏜️ Você está no Deserto!\n\n-3 Fome (muito quente!)\n\nLocal: {p['local'].title()}"
        embed = discord.Embed(title="🏜️ Deserto", description=desc, color=0xEDC9AF)
        await i.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🌑 The End", style=discord.ButtonStyle.primary)
    async def the_end(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        if not has_item(self.uid, '🔷'):
            await i.response.send_message(embed=discord.Embed(title="❌ Acesso Negado", description="Você precisa de Netherita (🔷) para entrar!", color=0xff0000), ephemeral=True)
            return
        
        p = get_player(self.uid)
        p['local'] = 'the_end'
        p['fome'] = max(0, p['fome'] - 1)
        
        desc = f"🌑 Você entrou em The End!\n\nLocal: {p['local'].title()}\n-1 Fome"
        embed = discord.Embed(title="🌑 The End", description=desc, color=0x1a1a2e)
        await i.response.send_message(embed=embed, ephemeral=True)

# ==================== OUTROS ====================
class OutrosView(discord.ui.View):
    def __init__(self, uid):
        super().__init__(timeout=60)
        self.uid = uid
    
    @discord.ui.button(label="🎒 Inventário", style=discord.ButtonStyle.primary)
    async def inventario(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        p = get_player(self.uid)
        if not p['itens']:
            desc = "🎒 Inventário vazio!"
        else:
            desc = "🎒 Seu Inventário:\n\n"
            for item, qty in p['itens'].items():
                desc += f"{item} x{qty}\n"
        
        embed = discord.Embed(title="🎒 Inventário", description=desc, color=0x8B4513)
        await i.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🔨 Craftar", style=discord.ButtonStyle.secondary)
    async def craftar(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        desc = "🔨 Sistema de Crafting em desenvolvimento!"
        embed = discord.Embed(title="🔨 Crafting", description=desc, color=0xC0C0C0)
        await i.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="👤 Perfil", style=discord.ButtonStyle.success)
    async def perfil(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        p = get_player(self.uid)
        barra = "🍖" * p['fome'] + "⬛" * (10 - p['fome'])
        
        desc = f"**{p['nome']}** | Lv. {p['level']}\n"
        desc += f"❤️ HP: {p['hp']:.0f}/20 | Fome: {barra}\n"
        desc += f"XP: {p['xp']}/{p['level']*10}\n"
        desc += f"📍 Local: {p['local'].title()}\n"
        desc += f"💀 Mortes: {p['mortes']}"
        
        embed = discord.Embed(title="👤 Seu Perfil", description=desc, color=0x9370DB)
        await i.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🍖 Comer", style=discord.ButtonStyle.danger)
    async def comer(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        if not has_item(self.uid, '🍗'):
            await i.response.send_message(embed=discord.Embed(title="❌ Sem Comida", description="Você não tem 🍗 Comida!", color=0xff0000), ephemeral=True)
            return
        
        p = get_player(self.uid)
        remove_item(self.uid, '🍗', 1)
        p['fome'] = min(10, p['fome'] + 3)
        
        desc = f"🍖 Você comeu!\n+3 Fome\n\nFome atual: {p['fome']}/10"
        embed = discord.Embed(title="🍖 Comendo", description=desc, color=0xFF6347)
        await i.response.send_message(embed=embed, ephemeral=True)

# ==================== AVENTURA ====================
class AventuraView(discord.ui.View):
    def __init__(self, uid, msg):
        super().__init__(timeout=None)
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
            
            desc = f"🪓 Cortou uma árvore!\n+{madeira}x 🪵\n+2 XP"
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
    
    @discord.ui.button(label="🔱 Caçar", style=discord.ButtonStyle.danger, row=1)
    async def cacar(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        p = get_player(self.uid)
        comida_atual = p['itens'].get('🍗', 0)
        
        if comida_atual >= 16:
            await i.response.send_message(embed=discord.Embed(title="❌ Mochila Cheia", description=f"🍗 Você já tem 16/16 comidas!\n\nUse 🍖 Comer para liberar espaço", color=0xff0000), ephemeral=True)
            return
        
        p['fome'] = max(0, p['fome'] - 1)
        
        if random.randint(1, 10) <= 7:
            comida = random.randint(1, 3)
            comida_total = min(16, comida_atual + comida)
            comida_obtida = comida_total - comida_atual
            add_item(self.uid, '🍗', comida_obtida)
            
            desc = f"🔱 Você caçou e conseguiu **{comida_obtida}x 🍗 Comida**!\n\n🍗 Total: {comida_total}/16"
            embed = discord.Embed(title="🔱 Caça bem-sucedida!", description=desc, color=0x8B4513)
        else:
            desc = f"🔱 Você tentou caçar mas não encontrou nada...\n\n-1 Fome"
            embed = discord.Embed(title="🔱 Caça falhou", description=desc, color=0xAA6B35)
        
        await i.response.send_message(embed=embed, ephemeral=True)
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
    
    @discord.ui.button(label="📋 Outros", style=discord.ButtonStyle.secondary, row=2)
    async def outros(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        view = OutrosView(self.uid)
        embed = discord.Embed(title="📋 Menu Outros", description="Escolha uma opção:", color=0x9370DB)
        await i.response.defer()
        await i.followup.send(embed=embed, view=view, ephemeral=True)

class Aventura(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='aventura')
    async def aventura_cmd(self, ctx, acao: str = None):
        """Controla sua aventura: cria, pausa, retoma ou recomeça"""
        uid = ctx.author.id
        p = get_player(uid)
        
        if acao is None:
            if not p:
                create_player(uid, ctx.author.display_name)
                p = get_player(uid)
                
                barra = "🍖" * p['fome'] + "⬛" * (10 - p['fome'])
                desc = f"**{p['nome']}** | Lv. {p['level']}\n❤️ {p['hp']}/20 | {barra}\n\n"
                desc += "Você acordou em uma floresta densa.\nEscolha uma ação:"
                
                embed = discord.Embed(title="🌲 Floresta do Minecraft", description=desc, color=0x00ff00)
                msg = await ctx.send(embed=embed)
                view = AventuraView(uid, msg)
                await msg.edit(view=view)
            else:
                view = MenuAventuraView(uid, ctx)
                embed = discord.Embed(title="📋 Menu de Aventura", description="Escolha uma opção:", color=0x4169e1)
                await ctx.send(embed=embed, view=view)

async def setup(bot):
    # Injetar a referência do dicionário global
    set_aventuras(bot.aventuras if hasattr(bot, 'aventuras') else {})
    await bot.add_cog(Aventura(bot))
