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

@bot.command(name='help')
async def help_prefix(ctx):
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
                    "MS!sorteio (usuario1, usuario2 até usuario50)\n\n"
                    "**Servidor**\n"
                    "MS!user (usuario)\n"
                    "MS!serverinfo"
    )
    embed.set_footer(text="Equipe de ajuda da Minecraft Sinistro")
    await ctx.send(embed=embed)

@bot.tree.command(name="help", description="Mostra todos os comandos disponíveis")
async def help_slash(interaction: discord.Interaction):
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
                    "MS!sorteio (usuario1, usuario2 até usuario50)\n\n"
                    "**Servidor**\n"
                    "MS!user (usuario)\n"
                    "MS!serverinfo"
    )
    embed.set_footer(text="Equipe de ajuda da Minecraft Sinistro")
    await interaction.response.send_message(embed=embed)

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

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
