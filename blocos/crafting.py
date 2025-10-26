"""
BLOCO CRAFTING
Receitas: Armas (madeira/ferro/diamante/netherita)
         Escudo, Armaduras, Cama, Tocha
"""
import discord
from discord.ext import commands

from __main__ import aventuras, CRAFTING

# ==================== FUNÇÕES ====================
def get_player(uid):
    return aventuras.get(uid)

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

# ==================== VIEWS ====================
class CraftView(discord.ui.View):
    def __init__(self, uid):
        super().__init__(timeout=60)
        self.uid = uid
    
    @discord.ui.button(label="⚔️ Espada de Madeira", style=discord.ButtonStyle.primary)
    async def espada_madeira(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        if has_item(self.uid, '🪵', 2):
            remove_item(self.uid, '🪵', 2)
            add_item(self.uid, '🪵⚔️')
            p = get_player(self.uid)
            p['arma'] = '🪵⚔️'
            
            desc = "✅ Você craftou uma **Espada de Madeira**!\n⚔️ Equipou! (Dano: 0.5)"
            await i.response.send_message(embed=discord.Embed(title="🔨 Craft!", description=desc, color=0x00ff00), ephemeral=True)
        else:
            await i.response.send_message(embed=discord.Embed(title="❌ Faltam Materiais", description="Você precisa: 2x 🪵", color=0xff0000), ephemeral=True)
    
    @discord.ui.button(label="⚔️ Espada de Pedra", style=discord.ButtonStyle.primary)
    async def espada_pedra(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        if has_item(self.uid, '🪵', 1) and has_item(self.uid, '🪨', 1):
            remove_item(self.uid, '🪵', 1)
            remove_item(self.uid, '🪨', 1)
            add_item(self.uid, '🪨⚔️')
            p = get_player(self.uid)
            p['arma'] = '🪨⚔️'
            
            desc = "✅ Você craftou uma **Espada de Pedra**!\n⚔️ Equipou! (Dano: 1)"
            await i.response.send_message(embed=discord.Embed(title="🔨 Craft!", description=desc, color=0x00ff00), ephemeral=True)
        else:
            await i.response.send_message(embed=discord.Embed(title="❌ Faltam Materiais", description="Você precisa: 1x 🪵 + 1x 🪨", color=0xff0000), ephemeral=True)
    
    @discord.ui.button(label="⚔️ Espada de Ferro", style=discord.ButtonStyle.primary)
    async def espada_ferro(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        if has_item(self.uid, '🪵', 2) and has_item(self.uid, '⚙️', 1):
            remove_item(self.uid, '🪵', 2)
            remove_item(self.uid, '⚙️', 1)
            add_item(self.uid, '⚙️⚔️')
            p = get_player(self.uid)
            p['arma'] = '⚙️⚔️'
            
            desc = "✅ Você craftou uma **Espada de Ferro**!\n⚔️ Equipou! (Dano: 1.5)"
            await i.response.send_message(embed=discord.Embed(title="🔨 Craft!", description=desc, color=0x00ff00), ephemeral=True)
        else:
            await i.response.send_message(embed=discord.Embed(title="❌ Faltam Materiais", description="Você precisa: 2x 🪵 + 1x ⚙️", color=0xff0000), ephemeral=True)
    
    @discord.ui.button(label="⚔️ Espada de Diamante", style=discord.ButtonStyle.primary)
    async def espada_diamante(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        if has_item(self.uid, '🪵', 2) and has_item(self.uid, '💎', 1):
            remove_item(self.uid, '🪵', 2)
            remove_item(self.uid, '💎', 1)
            add_item(self.uid, '💎⚔️')
            p = get_player(self.uid)
            p['arma'] = '💎⚔️'
            
            desc = "✅ Você craftou uma **Espada de Diamante**!\n⚔️ Equipou! (Dano: 2.5)"
            await i.response.send_message(embed=discord.Embed(title="🔨 Craft!", description=desc, color=0x00FFFF), ephemeral=True)
        else:
            await i.response.send_message(embed=discord.Embed(title="❌ Faltam Materiais", description="Você precisa: 2x 🪵 + 1x 💎", color=0xff0000), ephemeral=True)
    
    @discord.ui.button(label="⚔️ Espada de Netherita", style=discord.ButtonStyle.danger, row=1)
    async def espada_netherita(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        if has_item(self.uid, '💎⚔️', 1) and has_item(self.uid, '🔷', 2):
            remove_item(self.uid, '💎⚔️', 1)
            remove_item(self.uid, '🔷', 2)
            add_item(self.uid, '🔷⚔️')
            p = get_player(self.uid)
            p['arma'] = '🔷⚔️'
            
            desc = "✅ Você craftou uma **Espada de Netherita**!\n⚔️ Equipou! (Dano: 3 - MÁXIMA!)"
            await i.response.send_message(embed=discord.Embed(title="🔨 Craft!", description=desc, color=0xFF6B00), ephemeral=True)
        else:
            await i.response.send_message(embed=discord.Embed(title="❌ Faltam Materiais", description="Você precisa: 1x 💎⚔️ + 2x 🔷", color=0xff0000), ephemeral=True)
    
    @discord.ui.button(label="🛡️ Escudo", style=discord.ButtonStyle.secondary, row=1)
    async def escudo(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        if has_item(self.uid, '⚙️', 1) and has_item(self.uid, '🪵', 6):
            remove_item(self.uid, '⚙️', 1)
            remove_item(self.uid, '🪵', 6)
            add_item(self.uid, '🛡️')
            p = get_player(self.uid)
            p['escudo'] = True
            
            desc = "✅ Você craftou um **Escudo**!\n🛡️ Equipou! (Reduz 70% de dano)"
            await i.response.send_message(embed=discord.Embed(title="🔨 Craft!", description=desc, color=0x00ff00), ephemeral=True)
        else:
            await i.response.send_message(embed=discord.Embed(title="❌ Faltam Materiais", description="Você precisa: 1x ⚙️ + 6x 🪵", color=0xff0000), ephemeral=True)
    
    @discord.ui.button(label="🧥 Armadura de Couro", style=discord.ButtonStyle.primary, row=2)
    async def armadura_couro(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        if has_item(self.uid, '🥩', 5):
            remove_item(self.uid, '🥩', 5)
            add_item(self.uid, '🥩🧥')
            p = get_player(self.uid)
            p['armadura'] = '🥩🧥'
            
            desc = "✅ Você craftou uma **Armadura de Couro**!\n🧥 Equipou! (Defesa: 1)"
            await i.response.send_message(embed=discord.Embed(title="🔨 Craft!", description=desc, color=0x00ff00), ephemeral=True)
        else:
            await i.response.send_message(embed=discord.Embed(title="❌ Faltam Materiais", description="Você precisa: 5x 🥩", color=0xff0000), ephemeral=True)
    
    @discord.ui.button(label="🧥 Armadura de Ferro", style=discord.ButtonStyle.primary, row=2)
    async def armadura_ferro(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        if has_item(self.uid, '⚙️', 5):
            remove_item(self.uid, '⚙️', 5)
            add_item(self.uid, '⚙️🧥')
            p = get_player(self.uid)
            p['armadura'] = '⚙️🧥'
            
            desc = "✅ Você craftou uma **Armadura de Ferro**!\n🧥 Equipou! (Defesa: 1.5)"
            await i.response.send_message(embed=discord.Embed(title="🔨 Craft!", description=desc, color=0x00ff00), ephemeral=True)
        else:
            await i.response.send_message(embed=discord.Embed(title="❌ Faltam Materiais", description="Você precisa: 5x ⚙️", color=0xff0000), ephemeral=True)
    
    @discord.ui.button(label="🧥 Armadura de Diamante", style=discord.ButtonStyle.primary, row=2)
    async def armadura_diamante(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        if has_item(self.uid, '💎', 5):
            remove_item(self.uid, '💎', 5)
            add_item(self.uid, '💎🧥')
            p = get_player(self.uid)
            p['armadura'] = '💎🧥'
            
            desc = "✅ Você craftou uma **Armadura de Diamante**!\n🧥 Equipou! (Defesa: 2)"
            await i.response.send_message(embed=discord.Embed(title="🔨 Craft!", description=desc, color=0x00FFFF), ephemeral=True)
        else:
            await i.response.send_message(embed=discord.Embed(title="❌ Faltam Materiais", description="Você precisa: 5x 💎", color=0xff0000), ephemeral=True)
    
    @discord.ui.button(label="🧥 Armadura de Netherita", style=discord.ButtonStyle.danger, row=2)
    async def armadura_netherita(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        if has_item(self.uid, '💎🧥', 1) and has_item(self.uid, '🔷', 3):
            remove_item(self.uid, '💎🧥', 1)
            remove_item(self.uid, '🔷', 3)
            add_item(self.uid, '🔷🧥')
            p = get_player(self.uid)
            p['armadura'] = '🔷🧥'
            
            desc = "✅ Você craftou uma **Armadura de Netherita**!\n🧥 Equipou! (Defesa: 2.5 - MÁXIMA!)"
            await i.response.send_message(embed=discord.Embed(title="🔨 Craft!", description=desc, color=0xFF6B00), ephemeral=True)
        else:
            await i.response.send_message(embed=discord.Embed(title="❌ Faltam Materiais", description="Você precisa: 1x 💎🧥 + 3x 🔷", color=0xff0000), ephemeral=True)
    
    @discord.ui.button(label="🛏️ Cama", style=discord.ButtonStyle.secondary, row=3)
    async def cama(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        if has_item(self.uid, '🪵', 3):
            remove_item(self.uid, '🪵', 3)
            add_item(self.uid, '🛏️')
            
            desc = "✅ Você craftou uma **Cama**!\nAgora pode dormir para recuperar TODO HP e fome!"
            await i.response.send_message(embed=discord.Embed(title="🔨 Craft!", description=desc, color=0x00ff00), ephemeral=True)
        else:
            await i.response.send_message(embed=discord.Embed(title="❌ Faltam Materiais", description="Você precisa: 3x 🪵", color=0xff0000), ephemeral=True)
    
    @discord.ui.button(label="🕯️ Tocha", style=discord.ButtonStyle.secondary, row=3)
    async def tocha(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        if has_item(self.uid, '🪵', 1) and has_item(self.uid, '🪨', 1):
            remove_item(self.uid, '🪵', 1)
            remove_item(self.uid, '🪨', 1)
            add_item(self.uid, '🕯️', 4)
            
            desc = "✅ Você craftou **4x Tocha**!"
            await i.response.send_message(embed=discord.Embed(title="🔨 Craft!", description=desc, color=0x00ff00), ephemeral=True)
        else:
            await i.response.send_message(embed=discord.Embed(title="❌ Faltam Materiais", description="Você precisa: 1x 🪵 + 1x 🪨", color=0xff0000), ephemeral=True)

class Crafting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(Crafting(bot))
