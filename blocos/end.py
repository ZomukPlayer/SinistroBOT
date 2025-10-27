"""
BLOCO END
Cristais: 25% chance perder 3/4 vida
Dragão: 70 HP, insta kill sem armadura
Vitória: 1000 XP + embed roxo especial
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

def calc_dmg(uid):
    p = get_player(uid)
    if not p:
        return 0.5
    dmg_map = {'🔷⚔️': 3, '💎⚔️': 2.5, '⚙️⚔️': 1.5, '🪨⚔️': 1, '🪵⚔️': 0.5}
    dmg = dmg_map.get(p['arma'], 0.5)
    if p['fome'] < 3:
        dmg *= 0.5
    return dmg + random.uniform(-0.2, 0.3)

def apply_dmg(uid, dmg):
    p = get_player(uid)
    if not p:
        return False
    
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

# ==================== VIEW CRISTAIS ====================
class CristaisView(discord.ui.View):
    def __init__(self, uid, msg):
        super().__init__(timeout=None)
        self.uid = uid
        self.msg = msg
        self.cristais_destruidos = 0
        self.dragao_desbloqueado = False
    
    async def update_embed(self):
        p = get_player(self.uid)
        desc = f"**{p['nome']}** | Lv. {p['level']}\n"
        desc += f"❤️ HP: {p['hp']:.0f}/20\n\n"
        desc += f"🔮 Cristais Destruídos: **{self.cristais_destruidos}/8**\n\n"
        
        if self.cristais_destruidos >= 8:
            desc += "✅ Dragão desbloqueado! Clique em 💥 Enfrentar Dragão"
        else:
            desc += "Destrua os 8 cristais para enfrentar o Dragão!"
        
        embed = discord.Embed(title="💜 The End", description=desc, color=0x800080)
        await self.msg.edit(embed=embed)
    
    @discord.ui.button(label="💥 Explodir Cristal", style=discord.ButtonStyle.danger)
    async def explodir(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        if self.cristais_destruidos >= 8:
            await i.response.send_message("❌ Todos os cristais já foram destruídos!", ephemeral=True)
            return
        
        p = get_player(self.uid)
        
        # 25% de chance de perder 3/4 vida
        if random.randint(1, 4) == 1:
            dano = p['hp'] * 0.75  # 3/4 de vida
            apply_dmg(self.uid, dano)
            p = get_player(self.uid)
            
            desc = f"⚠️ **EXPLOSÃO PERIGOSA!**\n\n"
            desc += f"Você ativou a armadilha do cristal!\n"
            desc += f"Perdeu **{dano:.0f} HP** (3/4 da vida)\n\n"
            desc += f"❤️ HP: {p['hp']:.0f}/20"
            
            if p['hp'] <= 0:
                desc += f"\n\n💀 **VOCÊ MORREU!**"
            
            await i.response.send_message(embed=discord.Embed(title="💥 ARMADILHA!", description=desc, color=0xff0000), ephemeral=True)
        else:
            self.cristais_destruidos += 1
            desc = f"💜 Cristal destruído com segurança!\n\n"
            desc += f"🔮 Cristais: {self.cristais_destruidos}/8"
            
            if self.cristais_destruidos >= 8:
                desc += f"\n\n✅ **Todos os cristais destruídos!**\nO Dragão está vulnerável!"
            
            await i.response.send_message(embed=discord.Embed(title="💜 Cristal", description=desc, color=0x800080), ephemeral=True)
        
        await self.update_embed()
    
    @discord.ui.button(label="⚔️ Enfrentar Dragão", style=discord.ButtonStyle.danger)
    async def dragao(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é sua aventura!", ephemeral=True)
            return
        
        if self.cristais_destruidos < 8:
            await i.response.send_message("❌ Você precisa destruir todos os 8 cristais!", ephemeral=True)
            return
        
        p = get_player(self.uid)
        
        view = DragaoView(self.uid, self.msg)
        desc = f"**Dragão do Fim**\n🐉 HP: 70\n\n🔥 **BOSS FINAL!**"
        embed = discord.Embed(title="🐉 DRAGÃO DO FIM!", description=desc, color=0x800080)
        await self.msg.edit(embed=embed, view=view)
        await i.response.send_message(embed=discord.Embed(title="🐉 COMBATE ÉPICO!", description="O Dragão do Fim apareceu!", color=0xff0000), ephemeral=True)

# ==================== VIEW DRAGÃO ====================
class DragaoView(discord.ui.View):
    def __init__(self, uid, msg):
        super().__init__(timeout=60)
        self.uid = uid
        self.msg = msg
        self.dragao_hp = 70
        self.turno = 1
    
    @discord.ui.button(label="⚔️ Bater", style=discord.ButtonStyle.danger)
    async def bater(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.uid:
            await i.response.send_message("❌ Não é seu combate!", ephemeral=True)
            return
        
        dmg_player = calc_dmg(self.uid)
        p = get_player(self.uid)
        
        # Dragão dá insta kill sem armadura
        if not p['armadura']:
            p['hp'] = 0
            morreu = True
            dmg_dragao = 999  # Insta kill
        else:
            # Com armadura, tira dano normal
            dmg_dragao = random.uniform(10, 15)
            morreu = apply_dmg(self.uid, dmg_dragao)
            p = get_player(self.uid)
        
        self.dragao_hp -= dmg_player
        
        desc = f"**Turno {self.turno}**\n"
        desc += f"⚔️ Você deu: **{dmg_player:.1f} dmg**\n"
        
        if not morreu:
            desc += f"🐉 Dragão deu: **{dmg_dragao:.1f} dmg**\n\n"
            desc += f"🐉 Dragão: {max(0, self.dragao_hp):.0f} HP\n"
            desc += f"❤️ Você: {p['hp']:.0f} HP"
        else:
            if not p['armadura']:
                desc += f"🐉 Dragão: **INSTA KILL SEM ARMADURA!**\n\n💀 **VOCÊ MORREU!**"
            else:
                desc += f"🐉 Dragão deu: **{dmg_dragao:.1f} dmg**\n\n💀 **VOCÊ MORREU!**"
        
        if self.dragao_hp <= 0:
            # VITÓRIA!
            xp_ganho = 1000
            netherita_ganho = 10
            
            gain_xp(self.uid, xp_ganho)
            add_item(self.uid, '🔷', netherita_ganho)
            
            p = get_player(self.uid)
            
            desc_vitoria = f"🎉 **PARABÉNS!**\n\n"
            desc_vitoria += f"Você foi o 1º a matar o Dragão do Fim!\n\n"
            desc_vitoria += f"Recebeu **{xp_ganho} XP**!\n"
            desc_vitoria += f"XP Total: **{p['xp']}/{p['level']*10}**\n\n"
            desc_vitoria += f"Ganhou **{netherita_ganho}x 🔷 Netherita**!\n\n"
            desc_vitoria += f"Nível: **{p['level']}**"
            
            embed = discord.Embed(title="🎉 VITÓRIA ÉPICA!", description=desc_vitoria, color=0x800080)
            await i.response.send_message(embed=embed, ephemeral=True)
            await self.msg.edit(view=None)
            self.stop()
        
        elif morreu:
            desc = f"💀 **VOCÊ MORREU!**\n\n"
            if not p['armadura']:
                desc += f"🐉 O Dragão te destruiu!\n"
            desc += f"Perdeu 1 nível e TODOS os itens!"
            
            await i.response.send_message(embed=discord.Embed(title="💀 Derrota!", description=desc, color=0xff0000), ephemeral=True)
            await self.msg.edit(view=None)
            self.stop()
        
        else:
            self.turno += 1
            embed = discord.Embed(title="🐉 Dragão do Fim", description=desc, color=0x800080)
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
        
        p = get_player(self.uid)
        
        # Dragão dá insta kill sem armadura mesmo defendendo
        if not p['armadura']:
            p['hp'] = 0
            morreu = True
            desc = f"💀 **VOCÊ MORREU!**\n\n"
            desc += f"🐉 O Dragão é muito poderoso!\n"
            desc += f"Nem o escudo pode salvá-lo sem armadura!"
            
            await i.response.send_message(embed=discord.Embed(title="💀 Insta Kill!", description=desc, color=0xff0000), ephemeral=True)
            await self.msg.edit(view=None)
            self.stop()
            return
        
        # Com armadura + escudo, reduz bastante
        dmg_dragao = random.uniform(10, 15) * 0.3
        morreu = apply_dmg(self.uid, dmg_dragao, defending=True)
        p = get_player(self.uid)
        
        desc = f"**Turno {self.turno}**\n\n"
        desc += f"🛡️ Você ergueu o escudo!\n"
        desc += f"💥 O Dragão atacou com força bruta!\n"
        desc += f"Bloqueou **70%** do dano!\n\n"
        desc += f"Dano recebido: **{dmg_dragao:.1f}**\n"
        desc += f"❤️ Você: {p['hp']:.0f} HP"
        
        if morreu:
            desc = f"💀 **VOCÊ MORREU!**\n\n"
            desc += f"O Dragão foi muito forte...\n"
            desc += f"Perdeu 1 nível e TODOS os itens!"
            
            await i.response.send_message(embed=discord.Embed(title="💀 Derrota!", description=desc, color=0xff0000), ephemeral=True)
            await self.msg.edit(view=None)
            self.stop()
        
        else:
            self.turno += 1
            embed = discord.Embed(title="🛡️ Defesa", description=desc, color=0x800080)
            await i.response.send_message(embed=embed, ephemeral=True)

class End(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(End(bot))
