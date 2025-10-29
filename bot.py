import discord
from discord.ext import commands
from discord import app_commands
import os
import random
import json
import asyncpg
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='MS!', intents=intents)

WELCOME_CHANNEL_ID = 1428075891874861076

# ==================== CONFIGURAÇÕES GLOBAIS ====================
CRAFTING = {
    '🪵⚔️': {'nome': 'Espada de Madeira', 'mats': {'🪵': 2}, 'dano': 1},
    '⚙️⚔️': {'nome': 'Espada de Ferro', 'mats': {'🪵': 2, '⚙️': 1}, 'dano': 1.5},
    '💎⚔️': {'nome': 'Espada de Diamante', 'mats': {'🪵': 2, '💎': 1}, 'dano': 2.5},
    '🔷⚔️': {'nome': 'Espada de Netherita', 'mats': {'💎⚔️': 1, '🔷': 2}, 'dano': 3},
    '🛡️': {'nome': 'Escudo', 'mats': {'⚙️': 1, '🪵': 6}},
    '🥩🧥': {'nome': 'Armadura de Couro', 'mats': {'🥩': 5}, 'def': 1},
    '⚙️🧥': {'nome': 'Armadura de Ferro', 'mats': {'⚙️': 5}, 'def': 1.5},
    '💎🧥': {'nome': 'Armadura de Diamante', 'mats': {'💎': 5}, 'def': 2},
    '🔷🧥': {'nome': 'Armadura de Netherita', 'mats': {'💎🧥': 1, '🔷': 3}, 'def': 2.5},
    '🛏️': {'nome': 'Cama', 'mats': {'🪵': 3}},
    '🕯️': {'nome': 'Tocha', 'mats': {'🪵': 1, '🪨': 1}},
}

MOBS = {
    '🧟': {'nome': 'Zumbi', 'hp': (8, 12), 'dano': (2, 6), 'xp': 8, 'drops': {'🥩': (1, 2)}},
    '🕷️': {'nome': 'Aranha', 'hp': (10, 14), 'dano': (3, 7), 'xp': 10, 'drops': {'🪨': (1, 2)}},
    '💀': {'nome': 'Esqueleto', 'hp': (9, 13), 'dano': (3, 6), 'xp': 12, 'drops': {'⚙️': (1, 1)}},
    '🧨': {'nome': 'Creeper', 'hp': (12, 16), 'dano': (4, 8), 'xp': 15, 'drops': {'🔥': (1, 2)}},
    '🐷': {'nome': 'Piglin', 'hp': (15, 20), 'dano': (7, 8), 'xp': 20, 'drops': {'💎': (2, 5)}},
    '🔥': {'nome': 'Blaze', 'hp': (15, 15), 'dano': (4, 5), 'xp': 25, 'drops': {'🔱': (0, 1)}},
    '🐉': {'nome': 'Ender Dragon', 'hp': (70), 'dano': (10, 15), 'xp': 100, 'drops': {'🔷': (10)}},
}

# ==================== DADOS GLOBAIS ====================
aventuras = {}
db_pool = None

# ==================== BANCO DE DADOS ====================
async def init_db():
    """Inicializa o pool de conexões e cria a tabela"""
    global db_pool
    try:
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("❌ DATABASE_URL não encontrada no .env!")
            return False
        
        db_pool = await asyncpg.create_pool(db_url, min_size=1, max_size=10)
        print("✅ Pool de conexões criado")
        
        # Criar tabela se não existir
        async with db_pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS jogadores (
                    uid BIGINT PRIMARY KEY,
                    dados JSONB NOT NULL
                )
            ''')
        print("✅ Tabela de jogadores criada")
        return True
    except Exception as e:
        print(f"❌ Erro ao inicializar DB: {e}")
        return False

async def salvar_jogador(uid, dados):
    """Salva um jogador no banco de dados"""
    try:
        async with db_pool.acquire() as conn:
            await conn.execute(
                'INSERT INTO jogadores (uid, dados) VALUES ($1, $2) ON CONFLICT (uid) DO UPDATE SET dados = $2',
                uid, json.dumps(dados)
            )
    except Exception as e:
        print(f"❌ Erro ao salvar jogador {uid}: {e}")

async def carregar_jogador(uid):
    """Carrega um jogador do banco de dados"""
    try:
        async with db_pool.acquire() as conn:
            resultado = await conn.fetchval(
                'SELECT dados FROM jogadores WHERE uid = $1',
                uid
            )
            if resultado:
                return json.loads(resultado)
        return None
    except Exception as e:
        print(f"❌ Erro ao carregar jogador {uid}: {e}")
        return None

async def carregar_todos_jogadores():
    """Carrega TODOS os jogadores do banco"""
    try:
        async with db_pool.acquire() as conn:
            resultados = await conn.fetch(
                'SELECT uid, dados FROM jogadores'
            )
            jogadores = {}
            for row in resultados:
                jogadores[row['uid']] = json.loads(row['dados'])
            print(f"✅ {len(jogadores)} jogadores carregados do banco")
            return jogadores
    except Exception as e:
        print(f"❌ Erro ao carregar todos os jogadores: {e}")
        return {}

async def salvar_jogadores():
    """Salva TODOS os jogadores (função global)"""
    try:
        async with db_pool.acquire() as conn:
            for uid, dados in aventuras.items():
                await conn.execute(
                    'INSERT INTO jogadores (uid, dados) VALUES ($1, $2) ON CONFLICT (uid) DO UPDATE SET dados = $2',
                    uid, json.dumps(dados)
                )
        print(f"✅ {len(aventuras)} jogadores salvos no banco")
    except Exception as e:
        print(f"❌ Erro ao salvar jogadores: {e}")

# ==================== EVENTOS ====================
@bot.event
async def on_ready():
    print(f'{bot.user} conectado com sucesso!')
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.playing, name="Minecraft 2 - FASE 2.0"),
        status=discord.Status.online
    )
    try:
        synced = await bot.tree.sync()
        print(f"✅ Sincronizados {len(synced)} comandos slash")
    except Exception as e:
        print(f"❌ Erro: {e}")

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
    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
    embed.add_field(name="Membro #", value=f"{member.guild.member_count}", inline=True)
    embed.add_field(name="Servidor", value=member.guild.name, inline=True)
    
    await welcome_channel.send(f"Olá {member.mention}!", embed=embed)

# ==================== COMMANDS DE DIVERSÃO ====================
piadas = [
    "Por que a matemática foi à praia? Para usar o cálculo!",
    "O que o Java disse ao C? Você não me classe!",
    "Por que o Python foi ao psicólogo? Tinha problemas com identação!",
]

@bot.command(name='dados')
async def dados(ctx):
    d1, d2 = random.randint(1, 6), random.randint(1, 6)
    embed = discord.Embed(title="🎲 Dados", description=f"**Dado 1:** {d1}\n**Dado 2:** {d2}\n**Total:** {d1+d2}", color=discord.Color.blue())
    embed.set_footer(text=f"Solicitado por {ctx.author.name}")
    await ctx.send(embed=embed)

@bot.command(name='piada')
async def piada(ctx):
    embed = discord.Embed(title="😂 Piada", description=random.choice(piadas), color=discord.Color.gold())
    await ctx.send(embed=embed)

@bot.command(name='moeda')
async def moeda(ctx):
    resultado = random.choice(["Cara 🪙", "Coroa 🪙"])
    embed = discord.Embed(title="🪙 Moeda", description=resultado, color=discord.Color.yellow())
    await ctx.send(embed=embed)

@bot.command(name='sorteio')
async def sorteio(ctx):
    """Sorteia um vencedor entre as pessoas mencionadas"""
    if not ctx.message.mentions:
        embed = discord.Embed(title="❌ Erro", description="Mencione pelo menos um usuário!\n\nExemplo: `MS!sorteio @user1 @user2`", color=discord.Color.red())
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
    embed.set_thumbnail(url=vencedor.avatar.url if vencedor.avatar else None)
    embed.add_field(name="Participantes", value=total, inline=True)
    await ctx.send(embed=embed)

# ==================== COMMANDS DE INFO ====================
@bot.command(name='user')
async def user_cmd(ctx, usuario: discord.User = None):
    """Mostra informações de um usuário"""
    try:
        if usuario is None:
            usuario = ctx.author
        
        embed = discord.Embed(title=f"Informações de {usuario.name}", color=discord.Color.blue())
        embed.set_thumbnail(url=usuario.avatar.url if usuario.avatar else None)
        embed.add_field(name="Nome", value=usuario.name, inline=True)
        embed.add_field(name="ID", value=usuario.id, inline=True)
        embed.add_field(name="Bot?", value="Sim ✅" if usuario.bot else "Não ❌", inline=True)
        embed.add_field(name="Criado em", value=usuario.created_at.strftime("%d/%m/%Y"), inline=True)
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(title="❌ Erro", description=f"Usuário não encontrado: {e}", color=discord.Color.red())
        await ctx.send(embed=embed)

@bot.command(name='serverinfo')
async def serverinfo_cmd(ctx):
    """Mostra informações do servidor"""
    guild = ctx.guild
    embed = discord.Embed(title=f"Informações de {guild.name}", color=discord.Color.green())
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name="ID", value=guild.id, inline=True)
    embed.add_field(name="Membros", value=guild.member_count, inline=True)
    embed.add_field(name="Canais", value=len(guild.channels), inline=True)
    embed.add_field(name="Dono", value=guild.owner.mention, inline=True)
    embed.add_field(name="Criado em", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
    await ctx.send(embed=embed)

# ==================== CARREGAR MÓDULOS ====================
async def load_modules():
    """Carrega todos os módulos de blocos"""
    modules = ['blocos.aventura', 'blocos.combate', 'blocos.crafting', 'blocos.multiplayer', 'blocos.nether', 'blocos.end']
    
    for module in modules:
        try:
            await bot.load_extension(module)
            print(f"✅ Módulo {module} carregado com sucesso")
        except Exception as e:
            print(f"❌ ERRO ao carregar {module}: {e}")

@bot.event
async def setup_hook():
    global aventuras
    # ⭐ Inicializar banco de dados
    if await init_db():
        aventuras = await carregar_todos_jogadores()
    await load_modules()

# ==================== COMANDO PARA SALVAR MANUALMENTE ====================
@bot.command(name='salvar')
@commands.is_owner()
async def salvar_cmd(ctx):
    """Salva todos os dados dos jogadores (admin only)"""
    await salvar_jogadores()
    embed = discord.Embed(title="💾 Dados Salvos!", description=f"✅ {len(aventuras)} jogadores salvos", color=discord.Color.green())
    await ctx.send(embed=embed)

# ==================== RUN ====================
token = os.getenv('DISCORD_TOKEN')
if not token or token.strip() == "":
    print("❌ ERRO: Token não encontrado no .env!")
    exit()
else:
    print("✅ Token carregado com sucesso")
    print("🎮 Minecraft 2 - FASE 2.0 (Modular com PostgreSQL)")
    bot.run(token)
