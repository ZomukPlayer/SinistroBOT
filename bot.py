import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='MS!', intents=intents)

WELCOME_CHANNEL_ID = 1428075891874861076

@bot.event
async def on_ready():
    print(f'{bot.user} conectado com sucesso!')
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.playing, name="Bot OFICIAL da Minecraft Sinistro"),
        status=discord.Status.online
    )
    try:
        synced = await bot.tree.sync()
        print(f"Sincronizados {len(synced)} comandos slash")
    except Exception as e:
        print(e)

@bot.event
async def on_member_join(member):
    welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if welcome_channel is None:
        return
    
    embed = discord.Embed(
        title=f"Bem-vindo(a), {member.name}! 👋",
        description=f"Seja bem-vindo(a) ao servidor!",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.add_field(name="Membro #", value=f"{member.guild.member_count}", inline=True)
    embed.add_field(name="Servidor", value=member.guild.name, inline=True)
    embed.set_footer(text=f"ID: {member.id}")
    
    await welcome_channel.send(f"Olá {member.mention}!", embed=embed)

class MeuHelp(commands.DefaultHelpCommand):
    def __init__(self):
        super().__init__()
        self.no_category = "Sem Categoria"
    
    async def send_pages(self):
        destination = self.get_destination()
        embed = discord.Embed(
            title="Perdido? A gente te ajuda!",
            color=0xd66666,
            description="Os comandos aqui em baixo são todos os disponíveis:\n\n"
                        "**Diversão**\n"
                        "MS!piada\n"
                        "MS!sorteio\n"
                        "MS!moeda\n"
                        "MS!sumiu\n"
                        "MS!dados\n"
                        "MS!aventura\n"
                        "MS!sorteio (usuario1, usuario2 até usuario50)\n\n"
                        "**Servidor**\n"
                        "MS!user (usuario)\n"
                        "MS!serverinfo"
        )
        embed.set_footer(text="Equipe de ajuda da Minecraft Sinistro")
        await destination.send(embed=embed)

bot.help_command = MeuHelp()

@bot.command(name='dados')
async def dados_prefix(ctx):
    dado1 = random.randint(1, 6)
    dado2 = random.randint(1, 6)
    total = dado1 + dado2
    
    embed = discord.Embed(
        title="🎲 Resultado dos Dados",
        description=f"**Dado 1:** {dado1}\n**Dado 2:** {dado2}\n\n**Total:** {total}",
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Solicitado por {ctx.author.name}")
    await ctx.send(embed=embed)

@bot.tree.command(name="dados", description="Joga dois dados")
async def dados_slash(interaction: discord.Interaction):
    dado1 = random.randint(1, 6)
    dado2 = random.randint(1, 6)
    total = dado1 + dado2
    
    embed = discord.Embed(
        title="🎲 Resultado dos Dados",
        description=f"**Dado 1:** {dado1}\n**Dado 2:** {dado2}\n\n**Total:** {total}",
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Solicitado por {interaction.user.name}")
    await interaction.response.send_message(embed=embed)

piadas = [
    "Por que a matemática foi à praia? Para usar o cálculo!",
    "O que o Java disse ao C? Você não me classe!",
    "Por que o Python foi ao psicólogo? Tinha muitos problemas com a identação!",
    "Qual é o cúmulo do cúmulo? Um cubo cubado!",
    "Por que o livro de matemática se suicidou? Porque tinha muitos problemas!"
]

@bot.command(name='piada')
async def piada_prefix(ctx):
    piada = random.choice(piadas)
    embed = discord.Embed(title="😂 Piada do Dia", description=piada, color=discord.Color.gold())
    await ctx.send(embed=embed)

@bot.tree.command(name="piada", description="Conta uma piada aleatória")
async def piada_slash(interaction: discord.Interaction):
    piada = random.choice(piadas)
    embed = discord.Embed(title="😂 Piada do Dia", description=piada, color=discord.Color.gold())
    await interaction.response.send_message(embed=embed)

@bot.command(name='moeda')
async def moeda_prefix(ctx):
    resultado = random.choice(["Cara 🪙", "Coroa 🪙"])
    embed = discord.Embed(title="🪙 Resultado da Moeda", description=resultado, color=discord.Color.yellow())
    await ctx.send(embed=embed)

@bot.tree.command(name="moeda", description="Joga uma moeda")
async def moeda_slash(interaction: discord.Interaction):
    resultado = random.choice(["Cara 🪙", "Coroa 🪙"])
    embed = discord.Embed(title="🪙 Resultado da Moeda", description=resultado, color=discord.Color.yellow())
    await interaction.response.send_message(embed=embed)

@bot.command(name='sorteio')
async def sorteio_prefix(ctx):
    if not ctx.message.mentions:
        embed = discord.Embed(title="❌ Erro", description="Mencione pelo menos um usuário!", color=discord.Color.red())
        await ctx.send(embed=embed)
        return
    
    if len(ctx.message.mentions) > 50:
        embed = discord.Embed(title="❌ Erro", description="Máximo de 50 usuários!", color=discord.Color.red())
        await ctx.send(embed=embed)
        return
    
    total = len(ctx.message.mentions)
    porcentagem = (1 / total) * 100
    vencedor = random.choice(ctx.message.mentions)
    
    embed = discord.Embed(
        title="🎉 Resultado do Sorteio",
        description=f"Vencedor: {vencedor.mention}\n📊 Chance: {porcentagem:.2f}%",
        color=discord.Color.purple()
    )
    embed.set_thumbnail(url=vencedor.avatar.url)
    embed.add_field(name="Participantes", value=total, inline=True)
    await ctx.send(embed=embed)

@bot.tree.command(name="sorteio", description="Sorteia um vencedor (até 50 usuários)")
@app_commands.describe(u1="Usuário 1", u2="Usuário 2", u3="Usuário 3", u4="Usuário 4", u5="Usuário 5")
async def sorteio_slash(interaction: discord.Interaction, u1: discord.User, u2: discord.User, u3: discord.User = None, u4: discord.User = None, u5: discord.User = None):
    usuarios = [u1, u2]
    for u in [u3, u4, u5]:
        if u:
            usuarios.append(u)
    
    total = len(usuarios)
    porcentagem = (1 / total) * 100
    vencedor = random.choice(usuarios)
    
    embed = discord.Embed(
        title="🎉 Resultado do Sorteio",
        description=f"Vencedor: {vencedor.mention}\n📊 Chance: {porcentagem:.2f}%",
        color=discord.Color.purple()
    )
    embed.set_thumbnail(url=vencedor.avatar.url)
    embed.add_field(name="Participantes", value=total, inline=True)
    await interaction.response.send_message(embed=embed)

@bot.command(name='user')
async def user_prefix(ctx, usuario: discord.User = None):
    if usuario is None:
        usuario = ctx.author
    
    embed = discord.Embed(title=f"Informações de {usuario.name}", color=discord.Color.blue())
    embed.set_thumbnail(url=usuario.avatar.url)
    embed.add_field(name="Nome", value=usuario.name, inline=True)
    embed.add_field(name="ID", value=usuario.id, inline=True)
    embed.add_field(name="Bot?", value="Sim ✅" if usuario.bot else "Não ❌", inline=True)
    embed.add_field(name="Criado em", value=usuario.created_at.strftime("%d/%m/%Y"), inline=True)
    await ctx.send(embed=embed)

@bot.tree.command(name="user", description="Mostra informações de um usuário")
@app_commands.describe(usuario="Usuário para verificar")
async def user_slash(interaction: discord.Interaction, usuario: discord.User = None):
    if usuario is None:
        usuario = interaction.user
    
    embed = discord.Embed(title=f"Informações de {usuario.name}", color=discord.Color.blue())
    embed.set_thumbnail(url=usuario.avatar.url)
    embed.add_field(name="Nome", value=usuario.name, inline=True)
    embed.add_field(name="ID", value=usuario.id, inline=True)
    embed.add_field(name="Bot?", value="Sim ✅" if usuario.bot else "Não ❌", inline=True)
    embed.add_field(name="Criado em", value=usuario.created_at.strftime("%d/%m/%Y"), inline=True)
    await interaction.response.send_message(embed=embed)

@bot.command(name='serverinfo')
async def serverinfo_prefix(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"Informações de {guild.name}", color=discord.Color.green())
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name="ID", value=guild.id, inline=True)
    embed.add_field(name="Membros", value=guild.member_count, inline=True)
    embed.add_field(name="Canais", value=len(guild.channels), inline=True)
    embed.add_field(name="Dono", value=guild.owner.mention, inline=True)
    embed.add_field(name="Criado em", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
    await ctx.send(embed=embed)

@bot.tree.command(name="serverinfo", description="Mostra informações do servidor")
async def serverinfo_slash(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"Informações de {guild.name}", color=discord.Color.green())
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name="ID", value=guild.id, inline=True)
    embed.add_field(name="Membros", value=guild.member_count, inline=True)
    embed.add_field(name="Canais", value=len(guild.channels), inline=True)
    embed.add_field(name="Dono", value=guild.owner.mention, inline=True)
    embed.add_field(name="Criado em", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
    await interaction.response.send_message(embed=embed)

@bot.command(name='sumiu')
async def sumiu_prefix(ctx):
    try:
        async for message in ctx.channel.history(limit=100):
            if message.author == ctx.author and message.id != ctx.message.id:
                await message.delete()
                embed = discord.Embed(title="💨 Sumiu!", description=f"Mensagem de {ctx.author.mention} apagada!", color=discord.Color.dark_gray())
                await ctx.send(embed=embed, delete_after=5)
                return
        
        embed = discord.Embed(title="❌ Erro", description="Nenhuma mensagem anterior encontrada!", color=discord.Color.red())
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(title="❌ Erro", description=f"Erro ao apagar: {str(e)}", color=discord.Color.red())
        await ctx.send(embed=embed)

@bot.tree.command(name="sumiu", description="Apaga sua última mensagem")
async def sumiu_slash(interaction: discord.Interaction):
    try:
        async for message in interaction.channel.history(limit=100):
            if message.author == interaction.user:
                await message.delete()
                embed = discord.Embed(title="💨 Sumiu!", description=f"Mensagem de {interaction.user.mention} apagada!", color=discord.Color.dark_gray())
                await interaction.response.send_message(embed=embed, delete_after=5)
                return
        
        embed = discord.Embed(title="❌ Erro", description="Nenhuma mensagem anterior encontrada!", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        embed = discord.Embed(title="❌ Erro", description=f"Erro ao apagar: {str(e)}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)

aventuras = {}

def ganhar_xp(user_id, quantidade):
    player = aventuras[user_id]
    player['xp'] += quantidade
    
    xp_necessario = player['level'] * 10
    if player['xp'] >= xp_necessario:
        player['level'] += 1
        player['xp'] = 0
        return True
    return False

def calcular_dano(player):
    dano_base = random.randint(3, 8)
    if player['equipamento']['arma'] == '🗡️':
        dano_base += 5
    elif player['equipamento']['arma'] == '⛏️':
        dano_base += 2
    return dano_base

class BotoesAventura(discord.ui.View):
    def __init__(self, user_id, message=None):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.message = message
    
    async def atualizar_mensagem(self, interaction):
        player = aventuras[self.user_id]
        local_info = {
            'floresta': ('🌲 Floresta', 0x00ff00),
            'caverna': ('🗻 Caverna', 0x808080),
            'nether': ('🔥 Nether', 0xff4500),
            'deserto': ('🏜️ Deserto', 0xf4a460)
        }
        
        titulo, cor = local_info.get(player['local'], ('🌲 Floresta', 0x00ff00))
        
        embed = discord.Embed(
            title=titulo,
            description=f"**{player['nome']}** | Lv. {player['level']} (XP: {player['xp']}/{player['level']*10})\n"
                       f"❤️ HP: {player['hp']}/20\n\n"
                       f"🪵: {player['itens']['🪵']} | 🪨: {player['itens']['🪨']} | 💎: {player['itens']['💎']}\n"
                       f"🔥: {player['itens']['🔥']} | 🕯️: {player['itens']['🕯️']}\n\n"
                       f"⚔️ Arma: {player['equipamento']['arma'] or 'Nenhuma'}",
            color=cor
        )
        await self.message.edit(embed=embed)
    
    @discord.ui.button(label="🪓 Cortar Árvore", style=discord.ButtonStyle.green)
    async def cortar_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Esta aventura não é sua!", ephemeral=True)
            return
        
        player = aventuras[self.user_id]
        if player['local'] == 'deserto':
            await interaction.response.send_message("❌ Não há árvores no deserto!", ephemeral=True)
            return
        
        madeira = random.randint(2, 5)
        player['itens']['🪵'] += madeira
        
        levelup = ganhar_xp(self.user_id, 2)
        desc = f"Você cortou uma árvore e conseguiu **{madeira}x 🪵 Madeira**!\n+2 XP"
        if levelup:
            desc += f"\n\n🎉 **LEVEL UP!** Você chegou ao nível {player['level']}!"
        
        embed = discord.Embed(title="🪓 Cortando Árvore", description=desc, color=0x8B4513)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await self.atualizar_mensagem(interaction)
    
    @discord.ui.button(label="🗺️ Viajar", style=discord.ButtonStyle.primary)
    async def viajar_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Esta aventura não é sua!", ephemeral=True)
            return
        
        view = BotoesViagem(self.user_id, self.message)
        embed = discord.Embed(
            title="🗺️ Para onde viajar?",
            description="Escolha seu destino:",
            color=0x4169e1
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="🔨 Craftar", style=discord.ButtonStyle.secondary)
    async def craftar_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Esta aventura não é sua!", ephemeral=True)
            return
        
        player = aventuras[self.user_id]
        
        embed = discord.Embed(
            title="🔨 Crafting",
            description="**Receitas:**\n\n"
                       "⛏️ Picareta - 3🪵 + 2🪨\n"
                       "🗡️ Espada - 2🪵 + 1💎\n"
                       "🔥 Fornalha - 8🪨\n"
                       "🕯️ Tocha - 1🪵 + 1🪨\n"
                       "🛏️ Cama - 3🪵",
            color=0x8B4513
        )
        embed.add_field(name="Inventário", value=f"🪵: {player['itens']['🪵']} | 🪨: {player['itens']['🪨']} | 💎: {player['itens']['💎']}", inline=False)
        
        view = BotoesCraft(self.user_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="❤️ Comer (5🪵)", style=discord.ButtonStyle.danger, row=1)
    async def comer_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Esta aventura não é sua!", ephemeral=True)
            return
        
        player = aventuras[self.user_id]
        
        if player['itens']['🪵'] >= 5:
            if player['hp'] >= 20:
                await interaction.response.send_message("❌ Seu HP já está cheio!", ephemeral=True)
                return
            
            player['itens']['🪵'] -= 5
            cura = random.randint(5, 10)
            player['hp'] = min(20, player['hp'] + cura)
            
            embed = discord.Embed(
                title="❤️ Comendo...",
                description=f"Você comeu e recuperou **{cura} HP**!\n\n❤️ HP: {player['hp']}/20",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await self.atualizar_mensagem(interaction)
        else:
            embed = discord.Embed(
                title="❌ Itens Insuficientes",
                description="Você precisa de 5x 🪵 Madeira para comer!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🛏️ Dormir", style=discord.ButtonStyle.success, row=1)
    async def dormir_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Esta aventura não é sua!", ephemeral=True)
            return
        
        player = aventuras[self.user_id]
        
        if player['itens']['🛏️'] < 1:
            await interaction.response.send_message("❌ Você precisa craftar uma cama primeiro!", ephemeral=True)
            return
        
        player['hp'] = 20
        embed = discord.Embed(
            title="🛏️ Dormindo...",
            description="Você dormiu e recuperou TODO o HP!\n\n❤️ HP: 20/20",
            color=0x4169e1
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await self.atualizar_mensagem(interaction)

class BotoesViagem(discord.ui.View):
    def __init__(self, user_id, message):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.message = message
    
    @discord.ui.button(label="🗻 Caverna", style=discord.ButtonStyle.primary)
    async def caverna_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = aventuras[self.user_id]
        player['local'] = 'caverna'
        
        embed = discord.Embed(
            title="🗻 Caverna Profunda",
            description=f"**{player['nome']}** | Lv. {player['level']}\n"
                       f"❤️ HP: {player['hp']}/20\n\n"
                       f"Você entrou em uma caverna escura...",
            color=0x808080
        )
        new_view = BotoesCaverna(self.user_id, self.message)
        await self.message.edit(embed=embed, view=new_view)
        await interaction.response.send_message("🗻 Você entrou na caverna!", ephemeral=True)
    
    @discord.ui.button(label="🔥 Nether", style=discord.ButtonStyle.danger)
    async def nether_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = aventuras[self.user_id]
        
        if player['level'] < 5:
            await interaction.response.send_message("❌ Você precisa ser nível 5 para entrar no Nether!", ephemeral=True)
            return
        
        player['local'] = 'nether'
        
        embed = discord.Embed(
            title="🔥 Nether",
            description=f"**{player['nome']}** | Lv. {player['level']}\n"
                       f"❤️ HP: {player['hp']}/20\n\n"
                       f"Você entrou no Nether! Cuidado com os mobs!",
            color=0xff4500
        )
        new_view = BotoesNether(self.user_id, self.message)
        await self.message.edit(embed=embed, view=new_view)
        await interaction.response.send_message("🔥 Bem-vindo ao Nether!", ephemeral=True)
    
    @discord.ui.button(label="🏜️ Deserto", style=discord.ButtonStyle.secondary)
    async def deserto_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = aventuras[self.user_id]
        player['local'] = 'deserto'
        
        embed = discord.Embed(
            title="🏜️ Deserto",
            description=f"**{player['nome']}** | Lv. {player['level']}\n"
                       f"❤️ HP: {player['hp']}/20\n\n"
                       f"Você chegou ao deserto! Muito calor aqui...",
            color=0xf4a460
        )
        new_view = BotoesDeserto(self.user_id, self.message)
        await self.message.edit(embed=embed, view=new_view)
        await interaction.response.send_message("🏜️ Você está no deserto!", ephemeral=True)

class BotoesCaverna(discord.ui.View):
    def __init__(self, user_id, message=None):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.message = message
    
    async def atualizar_mensagem(self, interaction):
        player = aventuras[self.user_id]
        embed = discord.Embed(
            title="🗻 Caverna Profunda",
            description=f"**{player['nome']}** | Lv. {player['level']} (XP: {player['xp']}/{player['level']*10})\n"
                       f"❤️ HP: {player['hp']}/20\n\n"
                       f"🪵: {player['itens']['🪵']} | 🪨: {player['itens']['🪨']} | 💎: {player['itens']['💎']}",
            color=0x808080
        )
        await self.message.edit(embed=embed)
    
    @discord.ui.button(label="⛏️ Minerar", style=discord.ButtonStyle.primary)
    async def minerar_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Esta aventura não é sua!", ephemeral=True)
            return
        
        player = aventuras[self.user_id]
        sorte = random.randint(1, 10)
        
        if sorte >= 9:
            diamantes = random.randint(1, 3)
            player['itens']['💎'] += diamantes
            levelup = ganhar_xp(self.user_id, 10)
            desc = f"🎉 VOCÊ ENCONTROU **{diamantes}x 💎 DIAMANTE**!\n+10 XP"
            if levelup:
                desc += f"\n\n🎉 **LEVEL UP!** Você chegou ao nível {player['level']}!"
            embed = discord.Embed(title="💎 DIAMANTE!", description=desc, color=0x00FFFF)
        else:
            pedras = random.randint(3, 7)
            player['itens']['🪨'] += pedras
            levelup = ganhar_xp(self.user_id, 3)
            desc = f"Você minerou **{pedras}x 🪨 Pedra**.\n+3 XP"
            if levelup:
                desc += f"\n\n🎉 **LEVEL UP!** Você chegou ao nível {player['level']}!"
            embed = discord.Embed(title="⛏️ Minerando...", description=desc, color=0x808080)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await self.atualizar_mensagem(interaction)
    
    @discord.ui.button(label="⚔️ Lutar", style=discord.ButtonStyle.danger)
    async def lutar_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Esta aventura não é sua!", ephemeral=True)
            return
        
        player = aventuras[self.user_id]
        mobs = ['🧟 Zumbi', '🕷️ Aranha', '💀 Esqueleto', '🧨 Creeper']
        mob = random.choice(mobs)
        mob_hp = random.randint(8, 15)
        
        dano_player = calcular_dano(player)
        dano_mob = random.randint(2, 6)
        
        if mob_hp <= dano_player:
            drop = random.randint(1, 3)
            player['itens']['🪨'] += drop
            levelup = ganhar_xp(self.user_id, 8)
            desc = f"Você derrotou o {mob}!\n+{drop}x 🪨 Pedra\n+8 XP"
            if levelup:
                desc += f"\n\n🎉 **LEVEL UP!** Você chegou ao nível {player['level']}!"
            embed = discord.Embed(title="⚔️ Vitória!", description=desc, color=0x00ff00)
        else:
            player['hp'] -= dano_mob
            embed = discord.Embed(
                title="⚔️ Combate!",
                description=f"Você lutou contra {mob} mas levou **{dano_mob} de dano**!\n\n❤️ HP: {player['hp']}/20",
                color=0xff0000
            )
            
            if player['hp'] <= 0:
                player['hp'] = 20
                player['itens'] = {'🪵': 0, '🪨': 0, '⛏️': 0, '🗡️': 0, '💎': 0, '🔥': 0, '🕯️': 0, '🛏️': 0}
                player['local'] = 'floresta'
                player['level'] = max(1, player['level'] - 1)
                embed.description += "\n\n💀 **VOCÊ MORREU!** Perdeu 1 nível e todos os itens."
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await self.atualizar_mensagem(interaction)
    
    @discord.ui.button(label="🏃 Voltar Floresta", style=discord.ButtonStyle.secondary)
    async def voltar_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Esta aventura não é sua!", ephemeral=True)
            return
        
        player = aventuras[self.user_id]
        player['local'] = 'floresta'
        
        embed = discord.Embed(
            title="🌲 Floresta do Minecraft",
            description=f"**{player['nome']}** | Lv. {player['level']}\n"
                       f"❤️ HP: {player['hp']}/20\n\n"
                       "Você voltou para a floresta!",
            color=0x00ff00
        )
        new_view = BotoesAventura(self.user_id, self.message)
        await self.message.edit(embed=embed, view=new_view)
        await interaction.response.send_message("🏃 Você voltou!", ephemeral=True)

class BotoesNether(discord.ui.View):
    def __init__(self, user_id, message=None):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.message = message
    
    @discord.ui.button(label="⛏️ Minerar Netherrack", style=discord.ButtonStyle.danger)
    async def minerar_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Esta aventura não é sua!", ephemeral=True)
            return
        
        player = aventuras[self.user_id]
        netherrack = random.randint(5, 10)
        player['itens']['🔥'] += netherrack
        levelup = ganhar_xp(self.user_id, 5)
        desc = f"Você minerou **{netherrack}x 🔥 Netherrack**!\n+5 XP"
        if levelup:
            desc += f"\n\n🎉 **LEVEL UP!** Você chegou ao nível {player['level']}!"
        
        embed = discord.Embed(title="⛏️ Minerando Nether", description=desc, color=0xff4500)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="⚔️ Lutar Piglin", style=discord.ButtonStyle.danger)
    async def lutar_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Esta aventura não é sua!", ephemeral=True)
            return
        
        player = aventuras[self.user_id]
        mob_hp = random.randint(15, 25)
        
        dano_player = calcular_dano(player)
        dano_mob = random.randint(5, 10)
        
        if mob_hp <= dano_player:
            diamantes = random.randint(2, 5)
            player['itens']['💎'] += diamantes
            levelup = ganhar_xp(self.user_id, 15)
            desc = f"Você derrotou o 🐷 Piglin!\n+{diamantes}x 💎 Diamante\n+15 XP"
            if levelup:
                desc += f"\n\n🎉 **LEVEL UP!** Você chegou ao nível {player['level']}!"
            embed = discord.Embed(title="⚔️ Vitória Épica!", description=desc, color=0x00ff00)
        else:
            player['hp'] -= dano_mob
            embed = discord.Embed(
                title="⚔️ Combate Intenso!",
                description=f"O Piglin é forte! Você levou **{dano_mob} de dano**!\n\n❤️ HP: {player['hp']}/20",
                color=0xff0000
            )
            
            if player['hp'] <= 0:
                player['hp'] = 20
                player['itens'] = {'🪵': 0, '🪨': 0, '⛏️': 0, '🗡️': 0, '💎': 0, '🔥': 0, '🕯️': 0, '🛏️': 0}
                player['local'] = 'floresta'
                player['level'] = max(1, player['level'] - 2)
                embed.description += "\n\n💀 **VOCÊ MORREU NO NETHER!** Perdeu 2 níveis!"
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🏃 Voltar", style=discord.ButtonStyle.secondary)
    async def voltar_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Esta aventura não é sua!", ephemeral=True)
            return
        
        player = aventuras[self.user_id]
        player['local'] = 'floresta'
        
        embed = discord.Embed(title="🌲 Floresta", description="Você escapou do Nether!", color=0x00ff00)
        new_view = BotoesAventura(self.user_id, self.message)
        await self.message.edit(embed=embed, view=new_view)
        await interaction.response.send_message("🏃 Você voltou!", ephemeral=True)

class BotoesDeserto(discord.ui.View):
    def __init__(self, user_id, message=None):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.message = message
    
    @discord.ui.button(label="🏺 Procurar Tesouro", style=discord.ButtonStyle.primary)
    async def tesouro_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Esta aventura não é sua!", ephemeral=True)
            return
        
        player = aventuras[self.user_id]
        sorte = random.randint(1, 10)
        
        if sorte >= 7:
            diamantes = random.randint(3, 6)
            player['itens']['💎'] += diamantes
            levelup = ganhar_xp(self.user_id, 12)
            desc = f"🎉 Você encontrou um baú do tesouro!\n+{diamantes}x 💎 Diamante\n+12 XP"
            if levelup:
                desc += f"\n\n🎉 **LEVEL UP!** Você chegou ao nível {player['level']}!"
            embed = discord.Embed(title="🏺 Tesouro Encontrado!", description=desc, color=0xffd700)
        else:
            pedras = random.randint(2, 4)
            player['itens']['🪨'] += pedras
            levelup = ganhar_xp(self.user_id, 3)
            desc = f"Você achou **{pedras}x 🪨 Pedra** na areia.\n+3 XP"
            if levelup:
                desc += f"\n\n🎉 **LEVEL UP!** Você chegou ao nível {player['level']}!"
            embed = discord.Embed(title="🏜️ Procurando...", description=desc, color=0xf4a460)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🏃 Voltar", style=discord.ButtonStyle.secondary)
    async def voltar_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Esta aventura não é sua!", ephemeral=True)
            return
        
        player = aventuras[self.user_id]
        player['local'] = 'floresta'
        
        embed = discord.Embed(title="🌲 Floresta", description="Você saiu do deserto!", color=0x00ff00)
        new_view = BotoesAventura(self.user_id, self.message)
        await self.message.edit(embed=embed, view=new_view)
        await interaction.response.send_message("🏃 Você voltou!", ephemeral=True)

class BotoesCraft(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id
    
    @discord.ui.button(label="⛏️ Picareta (3🪵+2🪨)", style=discord.ButtonStyle.primary)
    async def craft_picareta(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Esta aventura não é sua!", ephemeral=True)
            return
        
        player = aventuras[self.user_id]
        
        if player['itens']['🪵'] >= 3 and player['itens']['🪨'] >= 2:
            player['itens']['🪵'] -= 3
            player['itens']['🪨'] -= 2
            player['itens']['⛏️'] += 1
            player['equipamento']['arma'] = '⛏️'
            embed = discord.Embed(
                title="✅ Craft Concluído!",
                description="Você craftou uma **⛏️ Picareta** e equipou ela!\n+2 de dano",
                color=0x00ff00
            )
        else:
            embed = discord.Embed(
                title="❌ Itens Insuficientes",
                description="Você precisa de 3x 🪵 e 2x 🪨",
                color=0xff0000
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🗡️ Espada (2🪵+1💎)", style=discord.ButtonStyle.primary)
    async def craft_espada(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Esta aventura não é sua!", ephemeral=True)
            return
        
        player = aventuras[self.user_id]
        
        if player['itens']['🪵'] >= 2 and player['itens']['💎'] >= 1:
            player['itens']['🪵'] -= 2
            player['itens']['💎'] -= 1
            player['itens']['🗡️'] += 1
            player['equipamento']['arma'] = '🗡️'
            embed = discord.Embed(
                title="✅ Craft Concluído!",
                description="Você craftou uma **🗡️ Espada de Diamante** e equipou ela!\n+5 de dano",
                color=0x00FFFF
            )
        else:
            embed = discord.Embed(
                title="❌ Itens Insuficientes",
                description="Você precisa de 2x 🪵 e 1x 💎",
                color=0xff0000
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🔥 Fornalha (8🪨)", style=discord.ButtonStyle.secondary, row=1)
    async def craft_fornalha(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Esta aventura não é sua!", ephemeral=True)
            return
        
        player = aventuras[self.user_id]
        
        if player['itens']['🪨'] >= 8:
            player['itens']['🪨'] -= 8
            player['itens']['🔥'] += 1
            embed = discord.Embed(
                title="✅ Craft Concluído!",
                description="Você craftou uma **🔥 Fornalha**!",
                color=0xff4500
            )
        else:
            embed = discord.Embed(
                title="❌ Itens Insuficientes",
                description="Você precisa de 8x 🪨",
                color=0xff0000
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🕯️ Tocha (1🪵+1🪨)", style=discord.ButtonStyle.secondary, row=1)
    async def craft_tocha(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Esta aventura não é sua!", ephemeral=True)
            return
        
        player = aventuras[self.user_id]
        
        if player['itens']['🪵'] >= 1 and player['itens']['🪨'] >= 1:
            player['itens']['🪵'] -= 1
            player['itens']['🪨'] -= 1
            player['itens']['🕯️'] += 4
            embed = discord.Embed(
                title="✅ Craft Concluído!",
                description="Você craftou **4x 🕯️ Tochas**!",
                color=0xffd700
            )
        else:
            embed = discord.Embed(
                title="❌ Itens Insuficientes",
                description="Você precisa de 1x 🪵 e 1x 🪨",
                color=0xff0000
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🛏️ Cama (3🪵)", style=discord.ButtonStyle.secondary, row=1)
    async def craft_cama(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Esta aventura não é sua!", ephemeral=True)
            return
        
        player = aventuras[self.user_id]
        
        if player['itens']['🪵'] >= 3:
            player['itens']['🪵'] -= 3
            player['itens']['🛏️'] += 1
            embed = discord.Embed(
                title="✅ Craft Concluído!",
                description="Você craftou uma **🛏️ Cama**!\nAgora pode dormir para recuperar HP!",
                color=0x4169e1
            )
        else:
            embed = discord.Embed(
                title="❌ Itens Insuficientes",
                description="Você precisa de 3x 🪵",
                color=0xff0000
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.command(name='aventura')
async def aventura_prefix(ctx):
    user_id = ctx.author.id
    
    aventuras[user_id] = {
        'hp': 20,
        'itens': {'🪵': 0, '🪨': 0, '⛏️': 0, '🗡️': 0, '💎': 0, '🔥': 0, '🕯️': 0, '🛏️': 0},
        'equipamento': {'arma': None},
        'local': 'floresta',
        'nome': ctx.author.display_name,
        'level': 1,
        'xp': 0
    }
    
    player = aventuras[user_id]
    
    embed = discord.Embed(
        title="🌲 Floresta do Minecraft",
        description=f"**{player['nome']}** | Lv. {player['level']}\n"
                   f"❤️ HP: {player['hp']}/20\n\n"
                   "Você acordou em uma floresta densa.\nEscolha uma ação abaixo:",
        color=0x00ff00
    )
    message = await ctx.send(embed=embed)
    view = BotoesAventura(user_id, message)
    await message.edit(view=view)

@bot.tree.command(name="aventura", description="Minecraft 2 - FASE 1")
async def aventura_slash(interaction: discord.Interaction):
    user_id = interaction.user.id
    
    aventuras[user_id] = {
        'hp': 20,
        'itens': {'🪵': 0, '🪨': 0, '⛏️': 0, '🗡️': 0, '💎': 0, '🔥': 0, '🕯️': 0, '🛏️': 0},
        'equipamento': {'arma': None},
        'local': 'floresta',
        'nome': interaction.user.display_name,
        'level': 1,
        'xp': 0
    }
    
    player = aventuras[user_id]
    
    embed = discord.Embed(
        title="🌲 Floresta do Minecraft",
        description=f"**{player['nome']}** | Lv. {player['level']}\n"
                   f"❤️ HP: {player['hp']}/20\n\n"
                   "Você acordou em uma floresta densa.\nEscolha uma ação abaixo:",
        color=0x00ff00
    )
    await interaction.response.send_message(embed=embed)
    message = await interaction.original_response()
    view = BotoesAventura(user_id, message)
    await message.edit(view=view)

token = os.getenv('DISCORD_TOKEN')
print("Token carregado?", "CLARO" if token else "CLARO QUE NAO NE BOT RUIM")
print("minecraft 2 FASE 1 + bot = ✋😐✋ Absolute Cinema")
bot.run(token)
