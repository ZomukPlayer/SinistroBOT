"""
BLOCO MULTIPLAYER
Comandos: MS!trade @usuario, MS!perfil @usuario, MS!ranking
Funcionalidades: Trocar itens, ver perfil, leaderboard
"""
import discord
from discord.ext import commands
from __main__ import aventuras

# ==================== DADOS GLOBAIS ====================
trades_pendentes = {}

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
class TradeView(discord.ui.View):
    def __init__(self, sender_id, receiver_id, sender_name, receiver_name):
        super().__init__(timeout=300)  # 5 minutos para aceitar
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.sender_name = sender_name
        self.receiver_name = receiver_name
        self.sender_items = {}
        self.receiver_items = {}
    
    @discord.ui.button(label="✅ Aceitar Trade", style=discord.ButtonStyle.green)
    async def aceitar(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.receiver_id:
            await i.response.send_message("❌ Você não é o receptor!", ephemeral=True)
            return
        
        # Verificar se sender ainda tem os itens
        for item, qty in self.sender_items.items():
            if not has_item(self.sender_id, item, qty):
                await i.response.send_message(f"❌ {self.sender_name} não tem mais {qty}x {item}!", ephemeral=True)
                return
        
        # Fazer a troca
        for item, qty in self.sender_items.items():
            remove_item(self.sender_id, item, qty)
            add_item(self.receiver_id, item, qty)
        
        for item, qty in self.receiver_items.items():
            remove_item(self.receiver_id, item, qty)
            add_item(self.sender_id, item, qty)
        
        desc = f"✅ **TRADE REALIZADO COM SUCESSO!**\n\n"
        desc += f"**{self.sender_name}** deu:\n"
        for item, qty in self.sender_items.items():
            desc += f"{item} x{qty}\n"
        
        desc += f"\n**{self.receiver_name}** deu:\n"
        for item, qty in self.receiver_items.items():
            desc += f"{item} x{qty}\n"
        
        embed = discord.Embed(title="🤝 Trade Completo!", description=desc, color=0x00ff00)
        await i.response.send_message(embed=embed)
        await i.message.edit(view=None)
        self.stop()
    
    @discord.ui.button(label="❌ Recusar Trade", style=discord.ButtonStyle.red)
    async def recusar(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user.id != self.receiver_id:
            await i.response.send_message("❌ Você não é o receptor!", ephemeral=True)
            return
        
        embed = discord.Embed(title="❌ Trade Recusado", description=f"{self.receiver_name} recusou o trade!", color=0xff0000)
        await i.response.send_message(embed=embed)
        await i.message.edit(view=None)
        self.stop()

# ==================== COG ====================
class Multiplayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='trade')
    async def trade_cmd(self, ctx, usuario: discord.User):
        """Inicia uma troca com outro jogador"""
        sender_id = ctx.author.id
        receiver_id = usuario.id
        
        sender = get_player(sender_id)
        receiver = get_player(receiver_id)
        
        if not sender or not receiver:
            embed = discord.Embed(title="❌ Erro", description="Ambos os jogadores devem estar em aventura!", color=0xff0000)
            await ctx.send(embed=embed)
            return
        
        if sender_id == receiver_id:
            embed = discord.Embed(title="❌ Erro", description="Você não pode fazer trade consigo mesmo!", color=0xff0000)
            await ctx.send(embed=embed)
            return
        
        trade_id = f"{sender_id}_{receiver_id}"
        
        desc = f"🤝 **PEDIDO DE TRADE**\n\n"
        desc += f"**{ctx.author.name}** quer fazer trade com **{usuario.name}**\n\n"
        desc += f"Clique em **Aceitar** para confirmar ou **Recusar** para cancelar.\n"
        desc += f"⏰ Válido por 5 minutos"
        
        embed = discord.Embed(title="🤝 Novo Trade", description=desc, color=0x4169e1)
        embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else None)
        
        view = TradeView(sender_id, receiver_id, ctx.author.name, usuario.name)
        trades_pendentes[trade_id] = view
        
        msg = await ctx.send(f"{usuario.mention}", embed=embed, view=view)
        
        # Aguardar timeout
        await view.wait()
        if trade_id in trades_pendentes:
            del trades_pendentes[trade_id]
    
    @commands.command(name='perfil')
    async def perfil_cmd(self, ctx, usuario: discord.User = None):
        """Mostra o perfil de um jogador"""
        if usuario is None:
            usuario = ctx.author
        
        p = get_player(usuario.id)
        
        if not p:
            embed = discord.Embed(title="❌ Sem Aventura", description=f"{usuario.name} ainda não iniciou uma aventura!", color=0xff0000)
            await ctx.send(embed=embed)
            return
        
        inv = "\n".join([f"{item}: **{qty}**" for item, qty in p['itens'].items()]) or "Vazio"
        
        desc = f"**{p['nome']}** | Lv. {p['level']}\n"
        desc += f"❤️ HP: {p['hp']:.0f}/20 | 🍖 Fome: {p['fome']}/10\n\n"
        
        desc += f"**STATS:**\n"
        desc += f"📊 XP: {p['xp']}/{p['level']*10}\n"
        desc += f"💀 Mortes: {p['mortes']}\n"
        desc += f"📍 Local: {p['local']}\n\n"
        
        desc += f"**EQUIPAMENTO:**\n"
        desc += f"⚔️ Arma: {p['arma'] if p['arma'] else 'Nenhuma'}\n"
        desc += f"🧥 Armadura: {p['armadura'] if p['armadura'] else 'Nenhuma'}\n"
        desc += f"🛡️ Escudo: {'Sim ✅' if p['escudo'] else 'Não ❌'}\n\n"
        
        desc += f"**INVENTÁRIO:**\n{inv}"
        
        embed = discord.Embed(title=f"📊 Perfil de {usuario.name}", description=desc, color=0x8B4513)
        embed.set_thumbnail(url=usuario.avatar.url if usuario.avatar else None)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='ranking')
    async def ranking_cmd(self, ctx):
        """Mostra o ranking de níveis"""
        if not aventuras:
            embed = discord.Embed(title="❌ Sem Jogadores", description="Ninguém iniciou uma aventura ainda!", color=0xff0000)
            await ctx.send(embed=embed)
            return
        
        # Ordenar por level (decrescente)
        ranking = sorted(aventuras.items(), key=lambda x: (x[1]['level'], x[1]['xp']), reverse=True)[:10]
        
        desc = "🏆 **TOP 10 JOGADORES**\n\n"
        
        for idx, (uid, player) in enumerate(ranking, 1):
            emoji = ["🥇", "🥈", "🥉"] + ["#" for _ in range(7)]
            desc += f"{emoji[idx-1]} **{idx}º - {player['nome']}**\n"
            desc += f"└ Lv. {player['level']} | XP: {player['xp']}/{player['level']*10} | Mortes: {player['mortes']}\n\n"
        
        embed = discord.Embed(title="🏆 Ranking de Níveis", description=desc, color=0xffd700)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Multiplayer(bot))
