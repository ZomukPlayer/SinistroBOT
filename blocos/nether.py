"""
BLOCO NETHER MELHORADO
Blazes: 15 HP, 5 dano + 1.5 fogo
Varas de Blaze: 100% drop
"""
import discord
from discord.ext import commands
import random
from __main__ import aventuras, MOBS, salvar_jogadores

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

def calc_dmg(uid):
    p = get_player(uid)
    if not p:
        return 0.5
    dmg_map = {'🔷⚔️': 3, '💎⚔️': 2.5, '⚙️⚔️': 1.5, '🪨⚔️': 1, '🪵⚔️': 0.5}
    dmg = dmg_map.get(p['arma'], 0.5)
    if p['fome'] < 3:
        dmg *= 0.5
    return dmg + random.uniform(-0.2, 0.3)

def apply_dmg(uid, dmg, defending=False):
    p = get_player(uid)
    if not p:
        return False
    
    if defending and p['escudo']:
        dmg *= 0.3
    
    if p['armadura']:
        def_map = {'🔷': 2.5, '💎': 2, '⚙️': 1.5, '🥩': 1}
        for mat, val in def_map.items():
            if mat in p['armadura']:
                dmg = max(0.5, dmg - val)
                break
    
    p['hp'] = max(0, p['hp'] - dmg)
    
    if p['hp'] <= 0:
        p['itens'].clear()
        p['hp'] = 20
        p['fome'] = 10
        p['level'] = max(1, p['level'] - 1)
        p['xp'] = 0
        p['local'] = 'floresta'
        p['arma'] = None
        p['armadura'] = None
        p['escudo'] = False
        p['mortes'] += 1
        return True
    return False

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

# ==================== VIEW DE COMBATE BLAZE ====================
class CombateBlazeView(discord.ui.View):
    def __init__(self, uid, msg):
        super().__init__(timeout=60)
        self.uid = uid
        self.msg = msg
        self.blaze_hp = 15
        self.turno = 1
    
    @discord.ui.button(label="⚔️ Bater", style=discord.ButtonStyle.danger)
    async def bater(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é seu combate!", ephemeral=True)
            return
        
        dmg_player = calc_dmg(self.uid)
        dmg_blaze = 4.5
        
        self.blaze_hp -= dmg_player
        morreu = apply_dmg(self.uid, dmg_blaze)
        p = get_player(self.uid)
        
        desc = f"**Turno {self.turno}**\n"
        desc += f"⚔️ Você deu: **{dmg_player:.1f} dmg**\n"
        desc += f"🔥 Blaze deu: **{dmg_blaze:.1f} dmg**\n\n"
        desc += f"🔥 Blaze: {max(0, self.blaze_hp):.0f} HP\n"
        desc += f"❤️ Você: {p['hp']:.0f} HP"
        
        if self.blaze_hp <= 0:
            xp = 25
            p['em_combate'] = False
            p['local'] = 'floresta'
            lvl_up = gain_xp(self.uid, xp)
            p = get_player(self.uid)
            
            desc = f"🎉 **VITÓRIA!**\n\n"
            desc += f"Derrotou o Blaze!\n"
            desc += f"+{xp} XP\n"
            desc += f"+1x 🔱 Vara de Blaze!"
            
            add_item(self.uid, '🔱', 1)
            
            if lvl_up:
                desc += f"\n\n🎉 **LEVEL UP!** Nível {p['level']}!"
            
            await salvar_jogadores()
            
            await i.response.send_message(embed=discord.Embed(title="🔥 Vitória!", description=desc, color=0xff4500), ephemeral=True)
            
            # ⭐ VOLTAR PRA FLORESTA
            barra = "🍖" * p['fome'] + "⬛" * (10 - p['fome'])
            embed_volta = discord.Embed(title="🌲 Floresta", description=f"**{p['nome']}** | Lv. {p['level']}\n❤️ {p['hp']:.0f}/20 | {barra}\n\nVocê voltou para a floresta", color=0x00ff00)
            from .aventura import AventuraView
            view_volta = AventuraView(self.uid, self.msg)
            await self.msg.edit(embed=embed_volta, view=view_volta)
            
            self.stop()
        
        elif morreu:
            p['em_combate'] = False
            p['local'] = 'floresta'
            desc = f"💀 **VOCÊ MORREU!**\n\n"
            desc += f"O Blaze foi muito forte...\n"
            desc += f"blaze e o goat pai"
            
            await salvar_jogadores()
            
            await i.response.send_message(embed=discord.Embed(title="💀 Derrota!", description=desc, color=0xff0000), ephemeral=True)
            
            # ⭐ VOLTAR PRA FLORESTA
            barra = "🍖" * p['fome'] + "⬛" * (10 - p['fome'])
            embed_volta = discord.Embed(title="🌲 Floresta", description=f"**{p['nome']}** | Lv. {p['level']}\n❤️ {p['hp']:.0f}/20 | {barra}\n\nVocê voltou para a floresta", color=0x00ff00)
            from .aventura import AventuraView
            view_volta = AventuraView(self.uid, self.msg)
            await self.msg.edit(embed=embed_volta, view=view_volta)
            
            self.stop()
        
        else:
            self.turno += 1
            embed = discord.Embed(title="🔥 Blaze", description=desc, color=0xff4500)
            await i.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🛡️ Defender", style=discord.ButtonStyle.primary)
    async def defender(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é seu combate!", ephemeral=True)
            return
        
        if not has_item(self.uid, '🛡️'):
            embed = discord.Embed(
                title="❌ Sem Escudo",
                description="Você precisa de um escudo para defender!\n\n**Craft:** 1⚙️ + 6🪵",
                color=0xff0000
            )
            await i.response.send_message(embed=embed, ephemeral=True)
            return
        
        dmg_blaze = 6.5 * 0.3
        morreu = apply_dmg(self.uid, dmg_blaze, defending=True)
        p = get_player(self.uid)
        
        desc = f"**Turno {self.turno}**\n\n"
        desc += f"🛡️ Você ergueu o escudo!\n"
        desc += f"💥 O Blaze atacou!\n"
        desc += f"Bloqueou **70%** do dano!\n\n"
        desc += f"Dano recebido: **{dmg_blaze:.1f}**\n"
        desc += f"❤️ Você: {p['hp']:.0f} HP"
        
        if morreu:
            p['em_combate'] = False
            p['local'] = 'floresta'
            desc = f"💀 **VOCÊ MORREU!**\n\n"
            desc += f"Mesmo com a defesa, o Blaze foi forte...\n"
            desc += f"Perdeu 1 nível e TODOS os itens!"
            
            await salvar_jogadores()
            
            await i.response.send_message(embed=discord.Embed(title="💀 Derrota!", description=desc, color=0xff0000), ephemeral=True)
            
            # ⭐ VOLTAR PRA FLORESTA
            barra = "🍖" * p['fome'] + "⬛" * (10 - p['fome'])
            embed_volta = discord.Embed(title="🌲 Floresta", description=f"**{p['nome']}** | Lv. {p['level']}\n❤️ {p['hp']:.0f}/20 | {barra}\n\nVocê voltou para a floresta", color=0x00ff00)
            from .aventura import AventuraView
            view_volta = AventuraView(self.uid, self.msg)
            await self.msg.edit(embed=embed_volta, view=view_volta)
            
            self.stop()
        
        else:
            self.turno += 1
            embed = discord.Embed(title="🛡️ Defesa", description=desc, color=0xff4500)
            await i.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🍗 Comer", style=discord.ButtonStyle.success, row=1)
    async def comer(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é seu combate!", ephemeral=True)
            return
        
        p = get_player(self.uid)
        
        if not has_item(self.uid, '🍗', 1):
            await i.response.send_message(embed=discord.Embed(title="❌ Sem Comida", description="Você precisa de 🍗 Comida!", color=0xff0000), ephemeral=True)
            return
        
        remove_item(self.uid, '🍗', 1)
        recuperar_hp = random.randint(3, 5)
        p['hp'] = min(20, p['hp'] + recuperar_hp)
        
        desc = f"🍗 Comeu!! \n\n"
        desc += f"Regenerou **{recuperar_hp} HP**!\n"
        desc += f"❤️ HP: {p['hp']:.0f}/20\n\n"
        desc += f"🍗 Comida restante: {p['itens'].get('🍗', 0)}/16"
        
        await salvar_jogadores()
        
        await i.response.send_message(embed=discord.Embed(title="🍗 Comeu!", description=desc, color=0xFF6347), ephemeral=True)

class NetherMenuView(discord.ui.View):
    def __init__(self, uid, msg):
        super().__init__(timeout=None)
        self.uid = uid
        self.msg = msg
    
    @discord.ui.button(label="🔥 Fortaleza (Blaze)", style=discord.ButtonStyle.danger)
    async def fortaleza(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        p = get_player(self.uid)
        p['em_combate'] = True
        
        view = CombateBlazeView(self.uid, self.msg)
        desc = f"**Blaze Infernal**\n💪 HP: 15\n\nEscolha sua ação:"
        embed = discord.Embed(title="🔥 FORTALEZA DO NETHER!", description=desc, color=0xff4500)
        await self.msg.edit(embed=embed, view=view)
        await i.response.send_message(embed=discord.Embed(title="🔥 BLAZE APARECEU!", description="Um **Blaze** explosivo apareceu na fortaleza!", color=0xff0000), ephemeral=True)
    
    @discord.ui.button(label="🐷 Bastião (Piglin)", style=discord.ButtonStyle.primary)
    async def bastiao(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        from .combate import CombateView
        
        p = get_player(self.uid)
        p['em_combate'] = True
        
        mob = MOBS['🐷']
        view = CombateView(self.uid, mob, self.msg)
        desc = f"**Piglin Feroz**\n💪 HP: {mob['hp'][1]}\n\nEscolha sua ação:"
        embed = discord.Embed(title="⚔️ BASTIÃO!", description=desc, color=0xff8c00)
        await self.msg.edit(embed=embed, view=view)
        await i.response.send_message(embed=discord.Embed(title="🐷 PIGLIN APARECEU!", description="Um **Piglin** apareceu no bastião!", color=0xff0000), ephemeral=True)

class NetherMelhorado(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(NetherMelhorado(bot))
