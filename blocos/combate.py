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
        dmg_mob = random.uniform(self.mob['
