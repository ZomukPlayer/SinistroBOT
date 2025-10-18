import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random

# Configuração do bot
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='MS!', intents=intents)

# ID do canal de boas-vindas
WELCOME_CHANNEL_ID = 1428075891874861076

@bot.event
async def on_ready():
    """Chamado quando o bot conecta ao Discord"""
    print(f'{bot.user} conectado com sucesso!')
    
    # Deixar o bot sempre online
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name="🎮 MS!help"
        ),
        status=discord.Status.online
    )
    
    # Sincronizar comandos slash
    try:
        synced = await bot.tree.sync()
        print(f"Sincronizados {len(synced)} comandos slash")
    except Exception as e:
        print(e)

@bot.event
async def on_member_join(member):
    """Chamado quando um novo membro entra no servidor"""
    
    welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
    
    if welcome_channel is None:
        print(f"Canal de boas-vindas não encontrado!")
        return
    
    embed = discord.Embed(
        title=f"Bem-vindo(a), {member.name}! 👋",
        description=f"Seja bem-vindo(a) ao servidor!",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.add_field(
        name="Membro #",
        value=f"{member.guild.member_count}",
        inline=True
    )
    embed.add_field(
        name="Servidor",
        value=member.guild.name,
        inline=True
    )
    embed.set_footer(text=f"ID: {member.id}")
    
    await welcome_channel.send(f"Olá {member.mention}!", embed=embed)

# ============ COMANDO: DADOS ============
@bot.command(name='dados')
async def dados_prefix(ctx):
    """Joga dois dados"""
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
    """Joga dois dados (Slash Command)"""
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

# ============ COMANDO: PIADA ============
piadas = [
    "Por que a matemática foi à praia? Para usar o cálculo! 😂",
    "O que o Java disse ao C? Você não me classe! 💻",
    "Por que o Python foi ao psicólogo? Tinha muitos problemas com a identação! 🐍",
    "Qual é o cúmulo do cúmulo? Um cubo cubado! 📦",
    "Por que o livro de matemática se suicidou? Porque tinha muitos problemas! 📚"
]

@bot.command(name='piada')
async def piada_prefix(ctx):
    """Conta uma piada aleatória"""
    piada = random.choice(piadas)
    
    embed = discord.Embed(
        title="😂 Piada do Dia",
        description=piada,
        color=discord.Color.gold()
    )
    
    await ctx.send(embed=embed)

@bot.tree.command(name="piada", description="Conta uma piada aleatória")
async def piada_slash(interaction: discord.Interaction):
    """Conta uma piada aleatória (Slash Command)"""
    piada = random.choice(piadas)
    
    embed = discord.Embed(
        title="😂 Piada do Dia",
        description=piada,
        color=discord.Color.gold()
    )
    
    await interaction.response.send_message(embed=embed)

# ============ COMANDO: MOEDA ============
@bot.command(name='moeda')
async def moeda_prefix(ctx):
    """Joga uma moeda"""
    resultado = random.choice(["Cara 🪙", "Coroa 🪙"])
    
    embed = discord.Embed(
        title="🪙 Resultado da Moeda",
        description=resultado,
        color=discord.Color.yellow()
    )
    
    await ctx.send(embed=embed)

@bot.tree.command(name="moeda", description="Joga uma moeda")
async def moeda_slash(interaction: discord.Interaction):
    """Joga uma moeda (Slash Command)"""
    resultado = random.choice(["Cara 🪙", "Coroa 🪙"])
    
    embed = discord.Embed(
        title="🪙 Resultado da Moeda",
        description=resultado,
        color=discord.Color.yellow()
    )
    
    await interaction.response.send_message(embed=embed)

# ============ COMANDO: SORTEIO ============
@bot.command(name='sorteio')
async def sorteio_prefix(ctx, *, usuarios: str = None):
    """Sorteia um vencedor entre usuários mencionados"""
    if not ctx.message.mentions:
        embed = discord.Embed(
            title="❌ Erro",
            description="Você precisa mencionar pelo menos um usuário!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    vencedor = random.choice(ctx.message.mentions)
    
    embed = discord.Embed(
        title="🎉 Resultado do Sorteio",
        description=f"O vencedor é: {vencedor.mention}",
        color=discord.Color.purple()
    )
    embed.set_thumbnail(url=vencedor.avatar.url)
    
    await ctx.send(embed=embed)

@bot.tree.command(name="sorteio", description="Sorteia um vencedor")
@app_commands.describe(usuario1="Primeiro usuário", usuario2="Segundo usuário", usuario3="Terceiro usuário (opcional)")
async def sorteio_slash(interaction: discord.Interaction, usuario1: discord.User, usuario2: discord.User, usuario3: discord.User = None):
    """Sorteia um vencedor entre usuários (Slash Command)"""
    usuarios = [usuario1, usuario2]
    if usuario3:
        usuarios.append(usuario3)
    
    vencedor = random.choice(usuarios)
    
    embed = discord.Embed(
        title="🎉 Resultado do Sorteio",
        description=f"O vencedor é: {vencedor.mention}",
        color=discord.Color.purple()
    )
    embed.set_thumbnail(url=vencedor.avatar.url)
    
    await interaction.response.send_message(embed=embed)

# ============ COMANDO: USER ============
@bot.command(name='user')
async def user_prefix(ctx, usuario: discord.User = None):
    """Mostra informações de um usuário"""
    if usuario is None:
        usuario = ctx.author
    
    embed = discord.Embed(
        title=f"Informações de {usuario.name}",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=usuario.avatar.url)
    embed.add_field(name="Nome", value=usuario.name, inline=True)
    embed.add_field(name="ID", value=usuario.id, inline=True)
    embed.add_field(name="Bot?", value="Sim ✅" if usuario.bot else "Não ❌", inline=True)
    embed.add_field(name="Conta criada em", value=usuario.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.set_footer(text=f"Solicitado por {ctx.author.name}")
    
    await ctx.send(embed=embed)

@bot.tree.command(name="user", description="Mostra informações de um usuário")
@app_commands.describe(usuario="Usuário para verificar (opcional)")
async def user_slash(interaction: discord.Interaction, usuario: discord.User = None):
    """Mostra informações de um usuário (Slash Command)"""
    if usuario is None:
        usuario = interaction.user
    
    embed = discord.Embed(
        title=f"Informações de {usuario.name}",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=usuario.avatar.url)
    embed.add_field(name="Nome", value=usuario.name, inline=True)
    embed.add_field(name="ID", value=usuario.id, inline=True)
    embed.add_field(name="Bot?", value="Sim ✅" if usuario.bot else "Não ❌", inline=True)
    embed.add_field(name="Conta criada em", value=usuario.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.set_footer(text=f"Solicitado por {interaction.user.name}")
    
    await interaction.response.send_message(embed=embed)

# ============ COMANDO: SERVERINFO ============
@bot.command(name='serverinfo')
async def serverinfo_prefix(ctx):
    """Mostra informações do servidor"""
    guild = ctx.guild
    
    embed = discord.Embed(
        title=f"Informações de {guild.name}",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name="ID", value=guild.id, inline=True)
    embed.add_field(name="Membros", value=guild.member_count, inline=True)
    embed.add_field(name="Canais", value=len(guild.channels), inline=True)
    embed.add_field(name="Dono", value=guild.owner.mention, inline=True)
    embed.add_field(name="Criado em", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.set_footer(text=f"Solicitado por {ctx.author.name}")
    
    await ctx.send(embed=embed)

@bot.tree.command(name="serverinfo", description="Mostra informações do servidor")
async def serverinfo_slash(interaction: discord.Interaction):
    """Mostra informações do servidor (Slash Command)"""
    guild = interaction.guild
    
    embed = discord.Embed(
        title=f"Informações de {guild.name}",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name="ID", value=guild.id, inline=True)
    embed.add_field(name="Membros", value=guild.member_count, inline=True)
    embed.add_field(name="Canais", value=len(guild.channels), inline=True)
    embed.add_field(name="Dono", value=guild.owner.mention, inline=True)
    embed.add_field(name="Criado em", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.set_footer(text=f"Solicitado por {interaction.user.name}")
    
    await interaction.response.send_message(embed=embed)

# ============ COMANDO: SUMIU ============
@bot.command(name='sumiu')
async def sumiu_prefix(ctx):
    """Apaga a última mensagem de quem usou o comando"""
    try:
        # Busca a última mensagem do autor no canal
        async for message in ctx.channel.history(limit=100):
            if message.author == ctx.author and message.id != ctx.message.id:
                await message.delete()
                
                embed = discord.Embed(
                    title="💨 Sumiu!",
                    description=f"Última mensagem de {ctx.author.mention} foi apagada!",
                    color=discord.Color.dark_gray()
                )
                
                await ctx.send(embed=embed, delete_after=5)
                return
        
        embed = discord.Embed(
            title="❌ Erro",
            description="Nenhuma mensagem anterior encontrada!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Erro",
            description=f"Não foi possível apagar a mensagem: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.tree.command(name="sumiu", description="Apaga a última mensagem de quem usou o comando")
async def sumiu_slash(interaction: discord.Interaction):
    """Apaga a última mensagem de quem usou o comando (Slash Command)"""
    try:
        # Busca a última mensagem do autor no canal
        async for message in interaction.channel.history(limit=100):
            if message.author == interaction.user:
                await message.delete()
                
                embed = discord.Embed(
                    title="💨 Sumiu!",
                    description=f"Última mensagem de {interaction.user.mention} foi apagada!",
                    color=discord.Color.dark_gray()
                )
                
                await interaction.response.send_message(embed=embed, delete_after=5)
                return
        
        embed = discord.Embed(
            title="❌ Erro",
            description="Nenhuma mensagem anterior encontrada!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Erro",
            description=f"Não foi possível apagar a mensagem: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
bot.run(token)
```

3. Commit as mudanças

**Passo 3: Atualizar `requirements.txt`**
1. Edite o `requirements.txt`
2. Adicione:
```
discord.py
python-dotenv

