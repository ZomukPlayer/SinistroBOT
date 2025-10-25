"""
BLOCO COMBATE
Mecânicas: Bater vs Defender
Dano: Bater basado em arma | Defender reduz 70% com escudo
Morte: Perde tudo e desce 1 nível
"""
import discord
from discord.ext import commands
import random

from __main__ import aventuras

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

def calc_dmg(uid):
    """Calcula dano da arma"""
    p = get_player(uid)
    if not p:
        return 0.5
    
    dmg_map = {'🔷⚔️': 3, '💎⚔️': 2.5, '⚙️⚔️': 1.5, '🪵⚔️': 1}
    dmg = dmg_map.get(p['arma'], 0.5)
    
    # Se fome baixa, reduz dano
    if p['fome'] < 3:
        dmg *= 0.5
    
    return dmg + random.uniform(-0.2, 0.3)

def apply_dmg(uid, dmg, defending=False):
    """Aplica dano ao jogador com defesa e armadura"""
    p = get_player(uid)
    if not p:
        return False
    
    # Reduz dano se defendendo com escudo
    if defending and p['escudo']:
        dmg *= 0.3
    
    # Aplica defesa da armadura
    if p['armadura']:
        def_map = {'🔷': 2.5, '💎': 2, '⚙️': 1.5, '🥩': 1}
        for mat, val in def_map.items():
            if mat in p['armadura']:
                dmg = max(0.5, dmg - val)
                break
    
    # Aplica dano final
    p['hp'] = max(0, p['hp'] - dmg)
    
    # Se morreu
    if p['hp'] <= 0:
        p['itens'].clear()  # PERDE TUDO
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

# ==================== VIEW DE COMBATE ====================
class CombateView(discord.ui.View):
    def __init__(self, uid, mob, msg):
        super().__init__(timeout=60)
        self.uid = uid
        self.mob = mob
        self.msg = msg
        self.mob_hp = random.randint(mob['hp'][0], mob['hp'][1])
        self.turno = 1
    
    @discord.ui.button(label="⚔️ Bater", style=discord.ButtonStyle.danger)
    async def bater(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é seu combate!", ephemeral=True)
            return
        
        # Calcular danos
        dmg_player = calc_dmg(self.uid)
        dmg_mob = random.uniform(self.mob['dano'][0], self.mob['dano'][1])
        self.mob_hp -= dmg_player
        morreu = apply_dmg(self.uid, dmg_mob)
        p = get_player(self.uid)
        
        desc = f"**Turno {self.turno}**\n"
        desc += f"⚔️ Você deu: **{dmg_player:.1f} dmg**\n"
        desc += f"💪 {self.mob['nome']} deu: **{dmg_mob:.1f} dmg**\n\n"
        desc += f"💪 {self.mob['nome']}: {max(0, self.mob_hp):.0f} HP\n"
        desc += f"❤️ Você: {p['hp']:.0f} HP"
        
        if self.mob_hp <= 0:
            # Vitória
            xp = self.mob['xp']
            lvl_up = gain_xp(self.uid, xp)
            p = get_player(self.uid)
            
            desc = f"🎉 **VITÓRIA!**\n\n"
            desc += f"Derrotou o {self.mob['nome']}!\n"
            desc += f"+{xp} XP"
            
            for item, qtd_range in self.mob['drops'].items():
                qtd = random.randint(qtd_range[0], qtd_range[1])
                add_item(self.uid, item, qtd)
                desc += f"\n+{qtd}x {item}"
            
            if lvl_up:
                desc += f"\n\n🎉 **LEVEL UP!** Nível {p['level']}!"
            
            await i.response.send_message(embed=discord.Embed(title="⚔️ Vitória!", description=desc, color=0x00ff00), ephemeral=True)
            await self.msg.edit(view=None)
            self.stop()
        
        elif morreu:
            # Derrota
            desc = f"💀 **VOCÊ MORREU!**\n\n"
            desc += f"O {self.mob['nome']} foi muito forte...\n"
            desc += f"Perdeu 1 nível e TODOS os itens!"
            
            await i.response.send_message(embed=discord.Embed(title="💀 Derrota!", description=desc, color=0xff0000), ephemeral=True)
            await self.msg.edit(view=None)
            self.stop()
        
        else:
            # Continua combate
            self.turno += 1
            embed = discord.Embed(title=f"⚔️ {self.mob['nome']}", description=desc, color=0xff8c00)
            await i.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🛡️ Defender", style=discord.ButtonStyle.primary)
    async def defender(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é seu combate!", ephemeral=True)
            return
        
        # Verificar escudo
        if not has_item(self.uid, '🛡️'):
            embed = discord.Embed(
                title="❌ Sem Escudo",
                description="Você precisa de um escudo para defender!\n\n**Craft:** 1⚙️ + 6🪵",
                color=0xff0000
            )
            await i.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Aplicar defesa
        dmg_mob = random.uniform(self.mob['dano'][0], self.mob['dano'][1])
        morreu = apply_dmg(self.uid, dmg_mob, defending=True)
        p = get_player(self.uid)
        
        dano_final = dmg_mob * 0.3
        
        desc = f"**Turno {self.turno}**\n\n"
        desc += f"🛡️ Você ergueu o escudo!\n"
        desc += f"💥 O {self.mob['nome']} atacou!\n"
        desc += f"Bloqueou **70%** do dano!\n\n"
        desc += f"Dano recebido: **{dano_final:.1f}**\n"
        desc += f"❤️ Você: {p['hp']:.0f} HP"
        
        if morreu:
            # Derrota mesmo defendendo
            desc = f"💀 **VOCÊ MORREU!**\n\n"
            desc += f"Mesmo com a defesa, o {self.mob['nome']} foi muito forte...\n"
            desc += f"Perdeu 1 nível e TODOS os itens!"
            
            await i.response.send_message(embed=discord.Embed(title="💀 Derrota!", description=desc, color=0xff0000), ephemeral=True)
            await self.msg.edit(view=None)
            self.stop()
        
        else:
            # Continua combate
            self.turno += 1
            embed = discord.Embed(title="🛡️ Defesa", description=desc, color=0x4169e1)
            await i.response.send_message(embed=embed, ephemeral=True)

class Combate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(Combate(bot))
