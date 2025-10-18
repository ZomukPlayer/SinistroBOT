import discord
from discord.ext import commands
import asyncio

# Configuração do bot
intents = discord.Intents.default()
intents.members = True  # Necessário para detectar novos membros
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

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
            name="Bot oficial da Minecraft Sinistro!"
        ),
        status=discord.Status.online
    )

@bot.event
async def on_member_join(member):
    """Chamado quando um novo membro entra no servidor"""
    
    # Obter o canal de boas-vindas
    welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
    
    if welcome_channel is None:
        print(f"Canal de boas-vindas não encontrado!")
        return
    
    # Criar a mensagem de boas-vindas
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
    
    # Enviar a mensagem no canal
    await welcome_channel.send(f"Olá {member.mention}!", embed=embed)

@bot.command(name='dados', prefix='MS!')
async def rolar_dados(ctx):
    """Comando para rolar dois dados"""
    import random
    
    # Rolar dois dados (1-6 cada)
    dado1 = random.randint(1, 6)
    dado2 = random.randint(1, 6)
    total = dado1 + dado2
    
    # Criar embed com o resultado
    embed = discord.Embed(
        title="🎲 Resultado dos Dados",
        description=f"**Dado 1:** {dado1}\n**Dado 2:** {dado2}\n\n**Total:** {total}",
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Solicitado por {ctx.author.name}")
    
    await ctx.send(embed=embed)

# Substituir 'SEU_TOKEN_AQUI' pelo seu token

bot.run('MTQyODA5NTk2NTc1MDg4NjQzMA.G9d9eC.gHn4n9KwGYvy_GPFWJD1iyMJYK_nuO-1seAYdI')
