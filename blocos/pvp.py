"""
BLOCO PVP - v1.0
Sistemas:
- Duelo Casual (foge fácil, perde 1 level)
- Duelo Arena (perde inventário, perde 4xp)
- Defender 3x com escudo
- Revida 70%, toma 30%
- Desafio com timeout 5 min
"""
import discord
from discord.ext import commands
import random
import asyncio
from __main__ import aventuras, salvar_jogadores

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

# ==================== DESAFIO ====================
desafios_pendentes = {}

class DesafioView(discord.ui.View):
    def __init__(self, desafiador_id, desafiado_id, tipo):
        super().__init__(timeout=300)  # 5 minutos
        self.desafiador_id = desafiador_id
        self.desafiado_id = desafiado_id
        self.tipo = tipo
    
    @discord.ui.button(label="✅ Aceitar", style=discord.ButtonStyle.green)
    async def aceitar(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.desafiado_id:
            await i.response.send_message("❌ Esse desafio não é pra você!", ephemeral=True)
            return
        
        p_desafiador = get_player(self.desafiador_id)
        p_desafiado = get_player(self.desafiado_id)
        
        if not p_desafiador or not p_desafiado:
            await i.response.send_message("❌ Um dos jogadores não tem aventura!", ephemeral=True)
            return
        
        # Marcar como em PvP
        p_desafiador['em_combate'] = True
        p_desafiado['em_combate'] = True
        
        view = DueloView(self.desafiador_id, self.desafiado_id, self.tipo)
        
        desc = f"**{p_desafiador['nome']}** vs **{p_desafiado['nome']}**\n\n"
        desc += f"❤️ {p_desafiador['nome']}: {p_desafiador['hp']:.0f}/20\n"
        desc += f"❤️ {p_desafiado['nome']}: {p_desafiado['hp']:.0f}/20\n\n"
        desc += f"Tipo: **{self.tipo.upper()}**"
        
        embed = discord.Embed(title="⚔️ DUELO INICIADO!", description=desc, color=0xff0000)
        
        await i.response.send_message(embed=embed, view=view)
    
    @discord.ui.button(label="❌ Recusar", style=discord.ButtonStyle.red)
    async def recusar(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.desafiado_id:
            await i.response.send_message("❌ Esse desafio não é pra você!", ephemeral=True)
            return
        
        await i.response.send_message("❌ Desafio recusado!", ephemeral=True)
        self.stop()

class DueloView(discord.ui.View):
    def __init__(self, desafiador_id, desafiado_id, tipo):
        super().__init__(timeout=None)
        self.desafiador_id = desafiador_id
        self.desafiado_id = desafiado_id
        self.tipo = tipo
        self.turno = 1
        self.defesas_desafiador = 3
        self.defesas_desafiado = 3
    
    @discord.ui.button(label="⚔️ Bater", style=discord.ButtonStyle.danger)
    async def bater(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id not in [self.desafiador_id, self.desafiado_id]:
            await i.response.send_message("❌ Você não está nesse duelo!", ephemeral=True)
            return
        
        atacante_id = i.user.id
        defensor_id = self.desafiado_id if atacante_id == self.desafiador_id else self.desafiador_id
        
        p_atacante = get_player(atacante_id)
        p_defensor = get_player(defensor_id)
        
        dmg = calc_dmg(atacante_id)
        p_defensor['hp'] -= dmg
        
        desc = f"**Turno {self.turno}**\n"
        desc += f"⚔️ {p_atacante['nome']} atacou!\n"
        desc += f"💥 Dano: {dmg:.1f}\n\n"
        desc += f"❤️ {p_atacante['nome']}: {p_atacante['hp']:.0f}/20\n"
        desc += f"❤️ {p_defensor['nome']}: {max(0, p_defensor['hp']):.0f}/20"
        
        if p_defensor['hp'] <= 0:
            await self._fim_duelo(atacante_id, defensor_id, i)
        else:
            self.turno += 1
            embed = discord.Embed(title="⚔️ Duelo", description=desc, color=0xff8c00)
            await i.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🛡️ Defender", style=discord.ButtonStyle.primary)
    async def defender(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id not in [self.desafiador_id, self.desafiado_id]:
            await i.response.send_message("❌ Você não está nesse duelo!", ephemeral=True)
            return
        
        if not has_item(i.user.id, '🛡️'):
            await i.response.send_message("❌ Você não tem escudo!", ephemeral=True)
            return
        
        if i.user.id == self.desafiador_id:
            if self.defesas_desafiador <= 0:
                await i.response.send_message("❌ Você usou todas suas defesas!", ephemeral=True)
                return
            self.defesas_desafiador -= 1
        else:
            if self.defesas_desafiado <= 0:
                await i.response.send_message("❌ Você usou todas suas defesas!", ephemeral=True)
                return
            self.defesas_desafiado -= 1
        
        desc = f"🛡️ {get_player(i.user.id)['nome']} se defendeu!\n\n"
        desc += f"Defesas restantes: {self.defesas_desafiador if i.user.id == self.desafiador_id else self.defesas_desafiado}/3"
        
        await i.response.send_message(embed=discord.Embed(title="🛡️ Defesa", description=desc, color=0x4169e1), ephemeral=True)
    
    @discord.ui.button(label="🍗 Comer", style=discord.ButtonStyle.success, row=1)
    async def comer(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id not in [self.desafiador_id, self.desafiado_id]:
            await i.response.send_message("❌ Você não está nesse duelo!", ephemeral=True)
            return
        
        p = get_player(i.user.id)
        
        if not has_item(i.user.id, '🍗', 1):
            await i.response.send_message("❌ Sem comida!", ephemeral=True)
            return
        
        remove_item(i.user.id, '🍗', 1)
        recuperar_hp = random.randint(3, 5)
        p['hp'] = min(20, p['hp'] + recuperar_hp)
        
        desc = f"🍗 {p['nome']} comeu!\n+{recuperar_hp} HP\n\n❤️ HP: {p['hp']:.0f}/20"
        
        salvar_jogadores()
        await i.response.send_message(embed=discord.Embed(title="🍗 Comeu!", description=desc, color=0xFF6347), ephemeral=True)
    
    @discord.ui.button(label="🏃 Desistir", style=discord.ButtonStyle.secondary, row=1)
    async def desistir(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id not in [self.desafiador_id, self.desafiado_id]:
            await i.response.send_message("❌ Você não está nesse duelo!", ephemeral=True)
            return
        
        vencedor_id = self.desafiado_id if i.user.id == self.desafiador_id else self.desafiador_id
        perdedor_id = i.user.id
        
        await self._fim_duelo(vencedor_id, perdedor_id, i)
    
    async def _fim_duelo(self, vencedor_id, perdedor_id, i):
        p_vencedor = get_player(vencedor_id)
        p_perdedor = get_player(perdedor_id)
        
        p_vencedor['em_combate'] = False
        p_perdedor['em_combate'] = False
        
        if self.tipo == 'casual':
            p_perdedor['level'] = max(1, p_perdedor['level'] - 1)
            desc = f"🎉 {p_vencedor['nome']} venceu!\n\n"
            desc += f"❌ {p_perdedor['nome']} perdeu 1 level"
        else:  # arena
            # Vencedor ganha todos os itens do perdedor
            for item, qty in p_perdedor['itens'].items():
                add_item(vencedor_id, item, qty)
            
            p_perdedor['itens'].clear()
            p_perdedor['arma'] = None
            p_perdedor['armadura'] = None
            p_perdedor['escudo'] = False
            p_perdedor['xp'] = max(0, p_perdedor['xp'] - 4)
            
            p_vencedor['xp'] += 35
            if p_vencedor['xp'] >= p_vencedor['level'] * 10:
                p_vencedor['level'] += 1
                p_vencedor['xp'] = 0
            
            desc = f"🏆 {p_vencedor['nome']} venceu a ARENA!\n\n"
            desc += f"🎁 Ganhou todos os itens\n"
            desc += f"➕ Ganhou 35 XP\n\n"
            desc += f"❌ {p_perdedor['nome']} perdeu tudo e 4 XP"
        
        salvar_jogadores()
        await i.response.send_message(embed=discord.Embed(title="⚔️ FIM DO DUELO!", description=desc, color=0x00ff00), ephemeral=True)
        self.stop()

class PvP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='duelo')
    async def duelo_cmd(self, ctx, tipo: str, usuario: discord.User = None):
        """Desafia alguém para um duelo: MS!duelo <casual|arena> @usuario"""
        uid = ctx.author.id
        p = get_player(uid)
        
        if not p:
            embed = discord.Embed(title="❌ Sem Aventura", description="Use `MS!aventura` para começar!", color=0xff0000)
            await ctx.send(embed=embed)
            return
        
        if p.get('em_combate'):
            embed = discord.Embed(title="❌ Já está em combate!", description="Termine a luta atual!", color=0xff0000)
            await ctx.send(embed=embed)
            return
        
        if tipo.lower() not in ['casual', 'arena']:
            embed = discord.Embed(title="❌ Tipo inválido", description="Use: `casual` ou `arena`", color=0xff0000)
            await ctx.send(embed=embed)
            return
        
        if not usuario:
            embed = discord.Embed(title="❌ Usuário não encontrado", description="Use: `MS!duelo <tipo> @usuario`", color=0xff0000)
            await ctx.send(embed=embed)
            return
        
        p_adversario = get_player(usuario.id)
        if not p_adversario:
            embed = discord.Embed(title="❌ Adversário sem aventura", description=f"{usuario.mention} não tem aventura!", color=0xff0000)
            await ctx.send(embed=embed)
            return
        
        if p_adversario.get('em_combate'):
            embed = discord.Embed(title="❌ Adversário em combate", description=f"{usuario.mention} já está em duelo!", color=0xff0000)
            await ctx.send(embed=embed)
            return
        
        view = DesafioView(uid, usuario.id, tipo)
        desc = f"⚔️ {ctx.author.mention} desafiou {usuario.mention}!\n\n"
        desc += f"Tipo: **{tipo.upper()}**\n"
        desc += f"Você tem 5 minutos para aceitar!"
        
        embed = discord.Embed(title="⚔️ DESAFIO DE DUELO!", description=desc, color=0xff0000)
        await ctx.send(f"{usuario.mention}", embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(PvP(bot))
