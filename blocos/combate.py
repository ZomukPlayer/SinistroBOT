"""
BLOCO COMBATE - v2.0
VERSÃO: 2.0
ÚLTIMA ATUALIZAÇÃO: 26/10/2025

SISTEMAS:
- Bater (dano por arma)
- Defender (reduz 70%)
- Fugir (50% chance)
- Comer (regenera 3-5 HP)
- Morte (perde tudo)
"""
import discord
from discord.ext import commands
import random
from __main__ import aventuras

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
    """Calcula dano da arma"""
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
        def_map = {'🔷': 3.5, '💎': 3, '⚙️': 1.5, '🥩': 1}
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
        
        dmg_player = calc_dmg(self.uid)
        p = get_player(self.uid)
        
        # CREEPER ESPECIAL: dá 18 de dano e se mata
        if self.mob['nome'] == 'Creeper':
            dmg_mob = 18
            self.mob_hp = -1
        else:
            dmg_mob = random.uniform(self.mob['dano'][0], self.mob['dano'][1])
            self.mob_hp -= dmg_player
        
        morreu = apply_dmg(self.uid, dmg_mob)
        p = get_player(self.uid)
        
        desc = f"**Turno {self.turno}**\n"
        desc += f"⚔️ Você deu: **{dmg_player:.1f} dmg**\n"
        
        if self.mob['nome'] == 'Creeper':
            desc += f"💥 Creeper: **EXPLODIU! (AUTO-MORTE)** Deu 18 de dano!\n\n"
        else:
            desc += f"💪 {self.mob['nome']} deu: **{dmg_mob:.1f} dmg**\n\n"
        
        desc += f"💪 {self.mob['nome']}: {max(0, self.mob_hp):.0f} HP\n"
        desc += f"❤️ Você: {p['hp']:.0f} HP"
        
        if self.mob_hp <= 0:
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
            
            # Voltar automaticamente pra floresta
            p = get_player(self.uid)
            p['local'] = 'floresta'
            barra = "🍖" * p['fome'] + "⬛" * (10 - p['fome'])
            embed_volta = discord.Embed(title="🌲 Floresta", description=f"**{p['nome']}** | Lv. {p['level']}\n❤️ {p['hp']:.0f}/20 | {barra}\n\nVocê voltou para a floresta", color=0x00ff00)
            from .aventura import AventuraView
            view_volta = AventuraView(self.uid, self.msg)
            await self.msg.edit(embed=embed_volta, view=view_volta)
            
            self.stop()
        
        elif morreu:
            desc = f"💀 **VOCÊ MORREU!**\n\n"
            desc += f"O {self.mob['nome']} foi muito forte...\n"
            desc += f"Você morreu e terá que começar tudo de novo!\n\n"
            desc += f"Use `MS!aventura` para recomeçar"
            
            await i.response.send_message(embed=discord.Embed(title="💀 Derrota!", description=desc, color=0xff0000), ephemeral=True)
            await self.msg.edit(view=None)
            self.stop()
        
        else:
            self.turno += 1
            embed = discord.Embed(title=f"⚔️ {self.mob['nome']}", description=desc, color=0xff8c00)
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
            desc = f"💀 **VOCÊ MORREU!**\n\n"
            desc += f"Mesmo com a defesa, o {self.mob['nome']} foi muito forte...\n"
            desc += f"Você morreu e terá que começar tudo de novo!\n\n"
            desc += f"Use `MS!aventura` para recomeçar"
            
            await i.response.send_message(embed=discord.Embed(title="💀 Derrota!", description=desc, color=0xff0000), ephemeral=True)
            await self.msg.edit(view=None)
            self.stop()
        
        else:
            self.turno += 1
            embed = discord.Embed(title="🛡️ Defesa", description=desc, color=0x4169e1)
            await i.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="❌ Fugir", style=discord.ButtonStyle.secondary)
    async def fugir(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é seu combate!", ephemeral=True)
            return
        
        # 50% de chance de conseguir fugir
        if random.randint(1, 2) == 1:
            desc = f"🏃 Você conseguiu fugir do {self.mob['nome']}!\n\nVoltando pra floresta..."
            
            p = get_player(self.uid)
            p['local'] = 'floresta'
            barra = "🍖" * p['fome'] + "⬛" * (10 - p['fome'])
            embed_volta = discord.Embed(title="🌲 Floresta", description=f"**{p['nome']}** | Lv. {p['level']}\n❤️ {p['hp']:.0f}/20 | {barra}\n\nVocê voltou para a floresta", color=0x00ff00)
            from .aventura import AventuraView
            view_volta = AventuraView(self.uid, self.msg)
            await self.msg.edit(embed=embed_volta, view=view_volta)
            await i.response.send_message(embed=discord.Embed(title="🏃 Fuga!", description=desc, color=0x00ff00), ephemeral=True)
            self.stop()
        else:
            desc = f"❌ O {self.mob['nome']} não deixou você fugir!\n\nTem que lutar!"
            await i.response.send_message(embed=discord.Embed(title="❌ Fuga Falhou!", description=desc, color=0xff0000), ephemeral=True)
    
    @discord.ui.button(label="🍗 Comer", style=discord.ButtonStyle.success, row=1)
    async def comer(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é seu combate!", ephemeral=True)
            return
        
        p = get_player(self.uid)
        
        if not has_item(self.uid, '🍗', 1):
            await i.response.send_message(embed=discord.Embed(title="❌ Sem Comida", description="Você precisa de 🍗 Comida!\n\nUse 🔱 Caçar antes da batalha", color=0xff0000), ephemeral=True)
            return
        
        remove_item(self.uid, '🍗', 1)
        recuperar_hp = random.randint(3, 5)
        p['hp'] = min(20, p['hp'] + recuperar_hp)
        
        desc = f"🍗 Você comeu durante a batalha!\n\n"
        desc += f"Regenerou **{recuperar_hp} HP**!\n"
        desc += f"❤️ HP: {p['hp']:.0f}/20\n\n"
        desc += f"🍗 Comida restante: {p['itens'].get('🍗', 0)}/16"
        
        await i.response.send_message(embed=discord.Embed(title="🍗 Comeu!", description=desc, color=0xFF6347), ephemeral=True)

class Combate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(Combate(bot))

# BLOCO COMBATE - v2.0
print "VERSÃO: 2.0 26/10/25"
# ÚLTIMA ATUALIZAÇÃO: 26/10/2025
print "- Bater (dano por arma) Defender (reduz 70%) Fugir (50% chance) Comer (regenera 3-5 HP) Morte (perde tudo)"
