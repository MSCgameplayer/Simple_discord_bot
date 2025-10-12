"""
Simple Discord Bot - Öffentliche Version
=======================================

WICHTIGER HINWEIS FÜR ENTWICKLER:
Wenn du diesen Bot als Basis für dein eigenes Projekt verwendest,
bitte gib Credits an den ursprünglichen Entwickler!

Entwickelt von: MSCgameplayer
Original Repository: https://github.com/MSCgameplayer/Simple_discord_bot
Mit Unterstützung von: GitHub Copilot

Die Entwicklung war viel Arbeit - Attribution wird sehr geschätzt! 🙏
"""

import discord
from discord.ext import commands, tasks
import yt_dlp
import asyncio
import os
import json
import aiohttp
import random
import logging
from collections import defaultdict
from typing import Any, Optional, Dict, List
from datetime import datetime

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('MusicBot')

# Intents konfigurieren - ALLE Intents aktivieren
intents = discord.Intents.all()

# Bot erstellen
bot = commands.Bot(command_prefix='!', intents=intents)

# Opus Library laden
if not discord.opus.is_loaded():
    # Versuche verschiedene Opus Pfade
    opus_paths = [
        '/opt/homebrew/lib/libopus.dylib',  # M1 Mac
        '/usr/local/lib/libopus.dylib',     # Intel Mac  
        '/usr/lib/x86_64-linux-gnu/libopus.so.0',  # Linux
        'libopus.so.0',
        'libopus.so',
        'opus'
    ]
    
    for path in opus_paths:
        try:
            discord.opus.load_opus(path)
            logger.info(f"✅ Opus erfolgreich geladen von: {path}")
            break
        except:
            logger.info(f"❌ Opus konnte nicht geladen werden von: {path}")
            continue
    
    if not discord.opus.is_loaded():
        logger.error("❌ Konnte Opus nicht laden! Voice wird nicht funktionieren.")
    else:
        logger.info("🎵 Opus erfolgreich geladen - Audio bereit!")

# Globale Variablen
music_queues = defaultdict(list)
voice_clients = {}
meme_config = {}
daily_meme_count = 0
last_reset_date = None

# yt-dlp Optionen - Optimiert für Discord Streaming
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin',
    'options': '-vn -bufsize 512k'
}

# yt-dlp instance für Audio-Extraktion
ytdl = yt_dlp.YoutubeDL(ytdl_format_options)  # type: ignore

class MemeAPI:
    @staticmethod
    async def get_random_meme():
        apis = [
            MemeAPI.get_reddit_meme,
            MemeAPI.get_meme_api,
            MemeAPI.get_imgflip_meme
        ]
        for api_func in random.sample(apis, len(apis)):
            try:
                meme = await api_func()
                if meme:
                    return meme
            except Exception as e:
                print(f"Meme API Fehler: {e}")
                continue
        return None

    @staticmethod
    async def get_reddit_meme():
        subreddits = ['memes', 'dankmemes', 'wholesomememes', 'me_irl', 'programmerhumor']
        subreddit = random.choice(subreddits)
        async with aiohttp.ClientSession() as session:
            url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=50"
            headers = {'User-Agent': 'DiscordBot/1.0'}
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    posts = data['data']['children']
                    image_posts = [post for post in posts if post['data'].get('url', '').endswith(('.jpg', '.png', '.gif', '.jpeg'))]
                    if image_posts:
                        post = random.choice(image_posts)['data']
                        return {
                            'title': post['title'][:100],
                            'url': post['url'],
                            'source': f"r/{subreddit}"
                        }
        return None

    @staticmethod
    async def get_meme_api():
        async with aiohttp.ClientSession() as session:
            async with session.get('https://meme-api.herokuapp.com/gimme') as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'title': data.get('title', 'Random Meme')[:100],
                        'url': data.get('url'),
                        'source': data.get('subreddit', 'meme-api')
                    }
        return None

    @staticmethod
    async def get_imgflip_meme():
        meme_templates = [
            'https://i.imgflip.com/1bij.jpg',
            'https://i.imgflip.com/4t0m5.jpg',
            'https://i.imgflip.com/26am.jpg',
            'https://i.imgflip.com/1otk96.jpg',
            'https://i.imgflip.com/23ls.jpg'
        ]
        return {
            'title': 'Classic Meme Template',
            'url': random.choice(meme_templates),
            'source': 'imgflip'
        }

class NSFWContentAPI:
    @staticmethod
    async def get_random_nsfw():
        """Holt NSFW Content von verschiedenen APIs"""
        apis = [
            NSFWContentAPI.get_reddit_nsfw,
            NSFWContentAPI.get_nekos_api
        ]
        
        for api in apis:
            try:
                return await api()
            except Exception as e:
                logger.error(f"NSFW API Fehler: {e}")
                continue
        
        return None
    
    @staticmethod
    async def get_reddit_nsfw():
        """Holt NSFW Content von Reddit"""
        subreddits = [
            'nsfw', 'gonewild', 'RealGirls', 'Amateur', 
            'collegesluts', 'Nude_Selfie', 'adorableporn'
        ]
        
        subreddit = random.choice(subreddits)
        url = f'https://www.reddit.com/r/{subreddit}/hot/.json?limit=50'
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={'User-agent': 'Discord Bot NSFW'}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    posts = data['data']['children']
                    
                    # Filtere nur Bild-Posts
                    image_posts = [post for post in posts if 
                                  post['data']['url'].lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')) and
                                  not post['data']['is_video'] and
                                  post['data']['over_18']]
                    
                    if image_posts:
                        post = random.choice(image_posts)['data']
                        return {
                            'title': post['title'][:100] + '...' if len(post['title']) > 100 else post['title'],
                            'url': post['url'],
                            'subreddit': f"r/{subreddit}",
                            'upvotes': post['ups'],
                            'nsfw': True
                        }
        return None
    
    @staticmethod 
    async def get_nekos_api():
        """Holt NSFW Content von Nekos API"""
        try:
            endpoints = ['boobs', 'pussy', 'ass', 'hentai', 'lewd']
            endpoint = random.choice(endpoints)
            url = f'https://nekos.life/api/v2/img/{endpoint}'
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            'title': f'Random {endpoint.title()}',
                            'url': data['url'],
                            'subreddit': 'nekos.life',
                            'nsfw': True
                        }
        except Exception as e:
            logger.error(f"Nekos API Fehler: {e}")
            return None

class AnimeCharacterAPI:
    @staticmethod
    async def search_character(character_name, nsfw=False, category=None):
        """Sucht nach Charakteren über verschiedene APIs - ÖFFENTLICHE VERSION OHNE API KEYS"""
        try:
            # Nur öffentliche APIs verwenden ohne Authentifizierung
            reddit_result = await AnimeCharacterAPI.search_reddit_character(character_name, nsfw, category)
            if reddit_result:
                return reddit_result
                
            # Backup: Safebooru für SFW Content
            if not nsfw:
                safebooru_result = await AnimeCharacterAPI.search_safebooru(character_name)
                if safebooru_result:
                    return safebooru_result
            
            # Nekos API als letzter Ausweg
            nekos_result = await AnimeCharacterAPI.search_nekos_character(character_name)
            return nekos_result
            
        except Exception as e:
            logger.error(f"Character API Fehler: {e}")
            return None
    
    @staticmethod
    async def search_reddit_character(character_name, nsfw=False, category=None):
        """Sucht Charakter auf Reddit mit Kategorie-Support"""
        try:
            # Kategorie-spezifische Subreddits (nur Anime erlaubt)
            category_subreddits = {
                'anime': [
                    'hentai', 'rule34', 'AnimePorn', 'HENTAI_GIF', 'HentaiParadise' if nsfw else 'anime', 'animeart', 'animegifs'
                ]
            }
            
            # Subreddit Auswahl basierend auf Kategorie
            if category and category.lower() in category_subreddits:
                subreddits = category_subreddits[category.lower()]
            elif nsfw:
                subreddits = ['hentai', 'rule34', 'AnimePorn', 'HENTAI_GIF', 'HentaiParadise']
            else:
                subreddits = ['anime', 'animeart', 'animegifs', 'wholesomeanimemes', 'animememes']
            
            for subreddit in subreddits:
                url = f'https://www.reddit.com/r/{subreddit}/search.json?q={character_name}&limit=50&sort=hot'
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers={'User-agent': 'Discord Anime Bot'}) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            posts = data['data']['children']
                            
                            # Filtere nach Bild-Posts
                            image_posts = [post for post in posts if 
                                          post['data']['url'].lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')) and
                                          not post['data']['is_video']]
                            
                            if image_posts:
                                post = random.choice(image_posts)['data']
                                return {
                                    'title': post['title'][:100] + '...' if len(post['title']) > 100 else post['title'],
                                    'url': post['url'],
                                    'subreddit': f"r/{subreddit}",
                                    'upvotes': post['ups'],
                                    'character': character_name,
                                    'nsfw': post.get('over_18', nsfw)
                                }
        except Exception as e:
            logger.error(f"Reddit Character Search Fehler: {e}")
        return None
    
    @staticmethod
    async def search_safebooru(character_name):
        """Sucht auf Safebooru (SFW) nach Charakteren - ÖFFENTLICHE VERSION"""
        try:
            # Safebooru API - SFW only
            url = f"https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&limit=50&tags={character_name.replace(' ', '_')}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers={'User-agent': 'Discord Anime Bot'}) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if isinstance(data, list) and data:
                            post = random.choice(data)
                            return {
                                'title': f'{character_name} - Safebooru',
                                'url': post.get('file_url', f"https://safebooru.org/images/{post.get('directory', '')}/{post.get('image', '')}"),
                                'subreddit': 'Safebooru',
                                'character': character_name,
                                'tags': post.get('tags', '').split()[:5],
                                'nsfw': False
                            }
        except Exception as e:
            logger.error(f"Safebooru Search Fehler: {e}")
        return None
    
    @staticmethod
    async def search_by_tags(tags):
        """Sucht nach spezifischen Tags - ÖFFENTLICHE VERSION (nur Safebooru)"""
        try:
            # Bereite Tags für API vor
            tag_string = tags.replace(' ', '+').replace(',', '+').lower()
            logger.info(f"🔍 Suche Tags (Public): {tag_string}")
            
            # Gesperrte Tags prüfen
            blocked_tags = [
                'furry', 'anthro', 'anthropomorphic', 'fur', 'animal_ears', 'animal_humanoid',
                'brony', 'mlp', 'my_little_pony', 'pony', 'equine', 'horse',
                'bestiality', 'zoophilia', 'feral', 'quadruped'
            ]
            
            # Prüfe ob gesperrte Tags in der Suche enthalten sind
            search_words = tag_string.replace('+', ' ').split()
            for word in search_words:
                if word in blocked_tags:
                    logger.warning(f"🚫 Gesperrter Tag erkannt: {word}")
                    return {
                        'blocked': True,
                        'blocked_tag': word,
                        'message': f"Der Tag '{word}' ist auf diesem Server nicht erlaubt."
                    }
            
            # Verwende nur Safebooru in der öffentlichen Version
            logger.info("🔄 Verwende Safebooru (Public Version)...")
            safebooru_url = f"https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&limit=50&tags={tag_string}"
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                try:
                    async with session.get(safebooru_url, headers={'User-agent': 'Discord Bot'}) as resp:
                        logger.info(f"🌐 Safebooru API Response Status: {resp.status}")
                        if resp.status == 200:
                            data = await resp.json()
                            logger.info(f"📊 Safebooru API Data: {len(data) if isinstance(data, list) else 'nicht Liste'} Einträge")
                            if isinstance(data, list) and data:
                                post = random.choice(data)
                                return {
                                    'title': f'Tags: {tags}',
                                    'url': post.get('file_url', f"https://safebooru.org/images/{post.get('directory', '')}/{post.get('image', '')}"),
                                    'subreddit': 'Safebooru (Public)',
                                    'upvotes': post.get('score', 0),
                                    'tags': post.get('tags', '').split()[:5] if post.get('tags') else []
                                }
                except Exception as safebooru_error:
                    logger.error(f"Safebooru API Fehler: {safebooru_error}")
            
            logger.info("❌ Public API fehlgeschlagen")
            return None
            
        except Exception as e:
            logger.error(f"Tag Search Hauptfehler: {e}")
            return None
    
    @staticmethod
    async def search_nekos_character(character_name):
        """Sucht SFW Anime Content"""
        try:
            # Nekos.life SFW endpoints
            endpoints = ['neko', 'waifu', 'pat', 'hug', 'kiss', 'slap', 'cuddle']
            endpoint = random.choice(endpoints)
            url = f'https://nekos.life/api/v2/img/{endpoint}'
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            'title': f'{character_name} - {endpoint.title()} Style',
                            'url': data['url'],
                            'subreddit': 'nekos.life',
                            'character': character_name,
                            'nsfw': False
                        }
        except Exception as e:
            logger.error(f"Nekos Character Search Fehler: {e}")
        return None

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        logger.info(f"🎵 Versuche Audio zu laden von: {url}")
        logger.info(f"Stream-Modus: {stream}")
        
        try:
            # yt-dlp Extraktion
            logger.info("📥 Starte yt-dlp Extraktion...")
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
            logger.info(f"✅ yt-dlp Extraktion erfolgreich: {data.get('title', 'Unbekannter Titel')}")
            
            if 'entries' in data:
                logger.info(f"📋 Playlist erkannt, nehme ersten Eintrag: {len(data['entries'])} Einträge")
                data = data['entries'][0]
                logger.info(f"🎶 Gewählter Song: {data.get('title', 'Unbekannt')}")
            
            # Audio-URL bestimmen
            filename = data.get('url') if stream else ytdl.prepare_filename(data)
            logger.info(f"🔗 Audio-Quelle: {filename}")
            
            if filename is None:
                logger.error("❌ Keine gültige Audio-URL gefunden!")
                raise Exception("Konnte keine gültige Audio-URL extrahieren")
            
            # FFmpeg-Parameter loggen
            logger.info(f"🎛️ FFmpeg before_options: {ffmpeg_options['before_options']}")
            logger.info(f"🎛️ FFmpeg options: {ffmpeg_options['options']}")
            
            # Audio Source erstellen
            logger.info("🔊 Erstelle FFmpeg Audio Source...")
            audio_source = discord.FFmpegPCMAudio(
                filename, 
                before_options=ffmpeg_options['before_options'], 
                options=ffmpeg_options['options']
            )
            logger.info("✅ Audio Source erfolgreich erstellt!")
            
            return cls(audio_source, data=data)
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Laden der Audio-URL: {str(e)}")
            logger.error(f"🔍 URL war: {url}")
            raise Exception(f"Fehler beim Laden der Audio-URL: {str(e)}")

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except Exception:
        logger.warning("⚠️ config.json nicht gefunden - erstelle eine mit deinem Bot Token!")
        return None

def save_config(config):
    try:
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception:
        return False

# =================== BERECHTIGUNGSSYSTEM ===================

def has_moderator_permissions(member):
    """Prüft ob ein Member Moderator-Berechtigung oder höher hat"""
    return (
        member.guild_permissions.administrator or
        member.guild_permissions.manage_guild or 
        member.guild_permissions.manage_channels or
        member.guild_permissions.manage_messages or
        member.guild_permissions.kick_members or
        member.guild_permissions.ban_members or
        member.guild_permissions.moderate_members
    )

def moderator_required():
    """Decorator für Befehle die Moderator-Rechte erfordern"""
    async def predicate(ctx):
        if not has_moderator_permissions(ctx.author):
            embed = discord.Embed(
                title="🚫 Keine Berechtigung",
                description="Dieser Befehl erfordert **Moderator-Berechtigung** oder höher!",
                color=0xff0000
            )
            embed.add_field(
                name="📋 Benötigte Berechtigungen (eine davon):",
                value="• Administrator\n"
                      "• Server verwalten\n"
                      "• Kanäle verwalten\n"
                      "• Nachrichten verwalten\n"
                      "• Mitglieder kicken\n"
                      "• Mitglieder bannen\n"
                      "• Mitglieder moderieren",
                inline=False
            )
            embed.set_footer(text="💡 Wende dich an einen Administrator für Hilfe")
            await ctx.send(embed=embed)
            return False
        return True
    return commands.check(predicate)

@tasks.loop(minutes=120)
async def auto_meme_poster():
    global daily_meme_count, last_reset_date
    if not meme_config.get('auto_meme', False):
        return
    
    from datetime import datetime, date
    today = date.today()
    reset_hour = meme_config.get('daily_reset_hour', 6)
    
    if last_reset_date != today:
        if datetime.now().hour >= reset_hour:
            daily_meme_count = 0
            last_reset_date = today
            print(f"🔄 Täglicher Meme-Counter zurückgesetzt (Tag: {today})")
    
    max_memes = meme_config.get('max_memes_per_day', 3)
    if daily_meme_count >= max_memes:
        print(f"📊 Tägliches Meme-Limit erreicht ({daily_meme_count}/{max_memes})")
        return
    
    if random.random() > meme_config.get('meme_chance', 0.15):
        return
    
    available_channels = []
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                if not meme_config.get('allowed_channels') or channel.id in meme_config.get('allowed_channels', []):
                    available_channels.append(channel)
    
    if not available_channels:
        return
    
    target_channel = random.choice(available_channels)
    
    try:
        meme = await MemeAPI.get_random_meme()
        if meme:
            embed = discord.Embed(
                title="🤣 Random Meme Time!",
                description=meme['title'],
                color=0xff6b9d
            )
            embed.set_image(url=meme['url'])
            embed.set_footer(text=f"Quelle: {meme['source']} | Auto-Meme 🤖")
            await target_channel.send(embed=embed)
            daily_meme_count += 1
            print(f"🤣 Auto-Meme #{daily_meme_count}/{meme_config.get('max_memes_per_day', 3)} gepostet")
    except Exception as e:
        print(f"❌ Fehler beim Auto-Meme posting: {e}")

@auto_meme_poster.before_loop
async def before_auto_meme():
    await bot.wait_until_ready()

@bot.event
async def on_ready():
    global meme_config
    print(f'{bot.user} ist online!')
    if bot.user:
        print(f'Bot ID: {bot.user.id}')
    
    config = load_config()
    if config:
        meme_config = config.get('meme_settings', {})
        if meme_config.get('auto_meme', False):
            interval = meme_config.get('meme_interval_minutes', 120)
            max_daily = meme_config.get('max_memes_per_day', 3)
            auto_meme_poster.change_interval(minutes=interval)
            auto_meme_poster.start()
            print(f"🤣 Auto-Meme Poster gestartet (alle {interval} min, max {max_daily} pro Tag)")
    
    print('🎵 Musik & Meme Bot bereit!')
    print('------')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Dieser Command existiert nicht!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Es fehlen Parameter für diesen Command!")
    else:
        print(f'Fehler: {error}')
        await ctx.send("❌ Ein Fehler ist aufgetreten!")

def get_voice_client(ctx):
    return voice_clients.get(ctx.guild.id)

@bot.command(name='join', aliases=['j'])
async def join(ctx):
    logger.info(f"🔗 Join-Befehl von {ctx.author.name}")
    
    if not ctx.author.voice:
        logger.warning(f"❌ User nicht in Voice Channel")
        await ctx.send("❌ Du musst in einem Voice Channel sein!")
        return
        
    channel = ctx.author.voice.channel
    logger.info(f"🎯 Versuche Voice Channel beizutreten: {channel.name}")
    
    try:
        if ctx.guild.id in voice_clients:
            logger.info(f"🔄 Voice Client existiert, bewege zu neuem Channel...")
            await voice_clients[ctx.guild.id].move_to(channel)
        else:
            logger.info(f"🆕 Erstelle neue Voice Connection...")
            voice_client = await channel.connect(timeout=10.0, reconnect=True)
            voice_clients[ctx.guild.id] = voice_client
            logger.info(f"✅ Voice Client erfolgreich erstellt")
            
        await ctx.send(f"✅ Dem Channel **{channel.name}** beigetreten!")
        logger.info(f"✅ Erfolgreich Channel {channel.name} beigetreten")
        
    except Exception as e:
        logger.error(f"❌ Fehler beim Voice Channel beitreten: {str(e)}")
        await ctx.send(f"❌ Fehler beim Beitreten: {str(e)}")
        raise e

@bot.command(name='leave', aliases=['disconnect', 'dc'])
async def leave(ctx):
    voice_client = get_voice_client(ctx)
    if voice_client:
        music_queues[ctx.guild.id].clear()
        await voice_client.disconnect()
        del voice_clients[ctx.guild.id]
        await ctx.send("✅ Voice Channel verlassen!")
    else:
        await ctx.send("❌ Bot ist nicht in einem Voice Channel!")

@bot.command(name='play', aliases=['p'])
async def play(ctx, *, query):
    logger.info(f"🎵 Play-Befehl von {ctx.author.name}: {query}")
    
    if not ctx.author.voice:
        logger.warning(f"❌ User {ctx.author.name} ist nicht in einem Voice Channel")
        await ctx.send("❌ Du musst in einem Voice Channel sein!")
        return
    
    if ctx.guild.id not in voice_clients:
        logger.info(f"🔗 Bot nicht verbunden, versuche beizutreten...")
        await join(ctx)
    
    voice_client = get_voice_client(ctx)
    if not voice_client:
        logger.error(f"❌ Konnte Voice Client nicht erhalten")
        await ctx.send("❌ Konnte nicht dem Voice Channel beitreten!")
        return
    
    try:
        await ctx.send(f"🔍 Suche nach: **{query}**")
        logger.info(f"🔍 Verarbeite Query: {query}")
        
        if not query.startswith('http'):
            query = f"ytsearch:{query}"
            logger.info(f"🔄 Query umgewandelt zu: {query}")
        
        logger.info(f"📥 Starte YTDLSource.from_url...")
        player = await YTDLSource.from_url(query, loop=bot.loop, stream=True)
        logger.info(f"✅ Player erstellt: {player.title}")
        
        music_queues[ctx.guild.id].append(player)
        logger.info(f"📋 Player zur Queue hinzugefügt. Queue-Länge: {len(music_queues[ctx.guild.id])}")
        
        if voice_client.is_playing():
            logger.info(f"🎶 Bot spielt bereits, Song zur Queue hinzugefügt")
            await ctx.send(f"📋 **{player.title}** zur Queue hinzugefügt!")
        else:
            logger.info(f"▶️ Bot spielt nicht, starte Wiedergabe...")
            await play_next(ctx)
            
    except Exception as e:
        error_msg = str(e) if str(e) else "Unbekannter Fehler beim Laden der Musik"
        logger.error(f"❌ Fehler im Play-Befehl: {error_msg}")
        logger.error(f"🔍 Exception Type: {type(e).__name__}")
        logger.error(f"🔍 Original Query war: {query}")
        await ctx.send(f"❌ Fehler beim Laden der Musik: {error_msg}")

async def play_next(ctx):
    voice_client = get_voice_client(ctx)
    guild_id = ctx.guild.id
    
    logger.info(f"🎵 play_next aufgerufen für Guild {guild_id}")
    
    if not voice_client:
        logger.error(f"❌ Kein Voice Client gefunden")
        return
        
    if len(music_queues[guild_id]) == 0:
        logger.info(f"📋 Queue ist leer")
        return
    
    player = music_queues[guild_id].pop(0)
    logger.info(f"▶️ Starte Wiedergabe: {player.title}")
    
    def after_playing(error):
        if error:
            logger.error(f'❌ Wiedergabe-Fehler: {error}')
        else:
            logger.info(f'✅ Wiedergabe beendet: {player.title}')
        if guild_id in music_queues and len(music_queues[guild_id]) > 0:
            logger.info(f"🔄 Nächster Song in Queue, starte automatisch...")
            coro = play_next(ctx)
            fut = asyncio.run_coroutine_threadsafe(coro, bot.loop)
            try:
                fut.result()
            except Exception as e:
                logger.error(f'❌ Fehler beim Auto-Play: {e}')
    
    try:
        # Prüfe Voice Client Status vor Wiedergabe
        if not voice_client.is_connected():
            logger.warning(f"⚠️ Voice Client nicht verbunden, versuche Reconnect...")
            await asyncio.sleep(1)  # Warte kurz
            if not voice_client.is_connected():
                logger.error(f"❌ Voice Client immer noch nicht verbunden")
                await ctx.send(f"❌ Voice Connection verloren. Verwende `!join` erneut.")
                return
        
        logger.info(f"🔊 Starte voice_client.play() für: {player.title}")
        logger.info(f"🔍 Voice Client Status - Connected: {voice_client.is_connected()}, Playing: {voice_client.is_playing()}")
        
        voice_client.play(player, after=after_playing)
        await ctx.send(f"🎵 Spielt jetzt: **{player.title}**")
        logger.info(f"✅ Wiedergabe erfolgreich gestartet!")
        
    except Exception as e:
        error_msg = str(e) if str(e) else "Unbekannter Wiedergabefehler"
        logger.error(f"❌ Fehler beim Starten der Wiedergabe: {error_msg}")
        logger.error(f"🔍 Exception Type: {type(e).__name__}")
        await ctx.send(f"❌ Fehler beim Abspielen: {error_msg}")
        raise e

@bot.command(name='queue', aliases=['q'])
async def queue(ctx):
    guild_queue = music_queues[ctx.guild.id]
    if len(guild_queue) == 0:
        await ctx.send("📋 Die Queue ist leer!")
        return
    
    queue_text = "📋 **Aktuelle Queue:**\n"
    for i, player in enumerate(guild_queue[:10], 1):
        queue_text += f"{i}. {player.title}\n"
    
    if len(guild_queue) > 10:
        queue_text += f"\n... und {len(guild_queue) - 10} weitere Songs"
    
    await ctx.send(queue_text)

@bot.command(name='pause')
async def pause(ctx):
    voice_client = get_voice_client(ctx)
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await ctx.send("⏸️ Musik pausiert!")
    else:
        await ctx.send("❌ Es läuft gerade keine Musik!")

@bot.command(name='resume', aliases=['unpause'])
async def resume(ctx):
    voice_client = get_voice_client(ctx)
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await ctx.send("▶️ Musik fortgesetzt!")
    else:
        await ctx.send("❌ Die Musik ist nicht pausiert!")

@bot.command(name='stop')
async def stop(ctx):
    voice_client = get_voice_client(ctx)
    if voice_client:
        music_queues[ctx.guild.id].clear()
        voice_client.stop()
        await ctx.send("⏹️ Musik gestoppt und Queue geleert!")
    else:
        await ctx.send("❌ Es läuft gerade keine Musik!")

@bot.command(name='skip', aliases=['s'])
async def skip(ctx):
    voice_client = get_voice_client(ctx)
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send("⏭️ Song übersprungen!")
    else:
        await ctx.send("❌ Es läuft gerade keine Musik!")

@bot.command(name='meme', aliases=['funny', 'lol'])
async def post_meme(ctx):
    async with ctx.typing():
        try:
            meme = await MemeAPI.get_random_meme()
            if meme:
                embed = discord.Embed(
                    title="🤣 Hier ist dein Meme!",
                    description=meme['title'],
                    color=0xff6b9d
                )
                embed.set_image(url=meme['url'])
                embed.set_footer(text=f"Quelle: {meme['source']} | Angefordert von {ctx.author.display_name}")
                await ctx.send(embed=embed)
            else:
                await ctx.send("😭 Konnte kein Meme finden! Versuche es später nochmal.")
        except Exception as e:
            await ctx.send(f"❌ Fehler beim Laden des Memes: {str(e)}")

# Vereinfachte NSFW Commands für öffentliche Version

@bot.command(name='nsfw', aliases=['lewd'])
async def nsfw_command(ctx):
    """Sendet zufälliges NSFW Content - ÖFFENTLICHE VERSION (nur Reddit & Nekos)"""
    # Prüfe ob Channel NSFW ist
    if not ctx.channel.is_nsfw():
        await ctx.send("🔞 **Dieser Befehl funktioniert nur in NSFW-Channels!**\n"
                      "Aktiviere NSFW in den Channel-Einstellungen.")
        return
    
    await ctx.send("🔍 **Suche nach NSFW Content...**\n⚠️ *Öffentliche Version - begrenzte APIs*")
    
    try:
        nsfw_content = await NSFWContentAPI.get_random_nsfw()
        
        if nsfw_content:
            embed = discord.Embed(
                title=f"🔞 {nsfw_content['title']}", 
                color=0xff1493
            )
            embed.set_image(url=nsfw_content['url'])
            embed.set_footer(text=f"📍 {nsfw_content['subreddit']} | Public Version" + 
                           (f" | 👍 {nsfw_content['upvotes']}" if 'upvotes' in nsfw_content else ""))
            
            await ctx.send(embed=embed)
            logger.info(f"🔞 NSFW Content gesendet von {ctx.author.name}: {nsfw_content['title']}")
        else:
            await ctx.send("❌ **Konnte kein NSFW Content finden!** Versuche es später erneut.")
            
    except Exception as e:
        logger.error(f"NSFW Command Fehler: {e}")
        await ctx.send("❌ **Fehler beim Laden von NSFW Content!**")

@bot.command(name='figure', aliases=['char', 'character_search', 'fig'])
async def figure_search_nsfw(ctx, *, character_name):
    """Sucht nach NSFW Content von spezifischen Figuren/Charakteren - ÖFFENTLICHE VERSION"""
    if not ctx.channel.is_nsfw():
        await ctx.send("🔞 **Dieser Befehl funktioniert nur in NSFW-Channels!**\n"
                      "Aktiviere NSFW in den Channel-Einstellungen.")
        return
        
    if not character_name:
        await ctx.send("❌ **Bitte gib einen Figurennamen an!**\n"
                      "**Beispiele:**\n"
                      "`!figure Frieren` - Anime Charakter\n"
                      "`!figure Zero Two` - Darling in the Franxx\n"
                      "⚠️ *Öffentliche Version - begrenzte APIs*")
        return
    
    await ctx.send(f"🔍 **Suche nach NSFW Content von: {character_name}...**\n⚠️ *Öffentliche Version - nur Reddit APIs*")
    
    try:
        character_content = await AnimeCharacterAPI.search_character(character_name, nsfw=True)
        
        if character_content:
            embed = discord.Embed(
                title=f"🔞 {character_content['title']}", 
                color=0xff1493
            )
            embed.set_image(url=character_content['url'])
            
            footer_text = f"📍 {character_content['subreddit']} | Public Version"
            if 'upvotes' in character_content:
                footer_text += f" | 👍 {character_content['upvotes']}"
            if 'tags' in character_content and character_content['tags']:
                footer_text += f" | 🏷️ {', '.join(character_content['tags'][:3])}"
            
            embed.set_footer(text=footer_text)
            
            await ctx.send(embed=embed)
            logger.info(f"🔞 NSFW Figur gesendet von {ctx.author.name}: {character_name}")
        else:
            await ctx.send(f"❌ **Konnte keinen NSFW Content für '{character_name}' finden!**\n"
                          "**Tipps für öffentliche Version:**\n"
                          "• Versuche andere Schreibweisen\n"
                          "• Verwende englische Namen\n"
                          "• Probiere bekanntere Charaktere\n"
                          "• Nutze `!figure_list` für beliebte Charaktere\n"
                          "⚠️ *Premium APIs nicht in öffentlicher Version verfügbar*")
            
    except Exception as e:
        logger.error(f"NSFW Figuren-Suche Fehler: {e}")
        await ctx.send("❌ **Fehler beim Suchen der Figur!**")

@bot.command(name='tag', aliases=['tags', 'tag_search'])
async def tag_search(ctx, *, tags=None):
    """Suche nach spezifischen NSFW Tags - ÖFFENTLICHE VERSION (nur SFW via Safebooru)"""
    if not tags:
        embed = discord.Embed(
            title="🏷️ Tag-Suche Hilfe - Öffentliche Version",
            description="⚠️ **Nur SFW Tags verfügbar in der öffentlichen Version**",
            color=0xff69b4
        )
        
        public_tags = {
            "**Verfügbare Tags (SFW):**": "anime, solo, group, detailed, masterpiece",
            "**Charakter-Tags:**": "blonde_hair, blue_eyes, long_hair, short_hair",
            "**Stil-Tags:**": "digital_art, traditional_art, sketch, painting",
            "**Qualität:**": "high_resolution, detailed, masterpiece, wallpaper"
        }
        
        for category, tag_list in public_tags.items():
            embed.add_field(name=category, value=tag_list, inline=False)
            
        embed.add_field(
            name="**Beispiele:**",
            value="`!tag anime solo`\n`!tag masterpiece detailed`\n`!tag blonde_hair blue_eyes`",
            inline=False
        )
        
        embed.add_field(
            name="⚠️ **Hinweis zur öffentlichen Version:**",
            value="Diese Version verwendet nur Safebooru (SFW)\nFür erweiterte NSFW Features benötigst du API Keys",
            inline=False
        )
        
        embed.set_footer(text="Nur SFW Content in der öffentlichen Version!")
        await ctx.send(embed=embed)
        return
    
    await ctx.send(f"🏷️ **Tag-Suche: {tags}...**\n⚠️ *Öffentliche Version - nur SFW via Safebooru*")
    
    try:
        logger.info(f"🏷️ Tag-Suche gestartet von {ctx.author.name}: {tags} (Public)")
        tag_content = await AnimeCharacterAPI.search_by_tags(tags)
        
        if tag_content and not tag_content.get('blocked'):
            embed = discord.Embed(
                title=f"🏷️ Tags: {tags} (SFW)",
                color=0xff69b4
            )
            
            embed.set_image(url=tag_content['url'])
            
            # Score anzeigen
            if tag_content.get('upvotes'):
                embed.add_field(
                    name="👍 Score",
                    value=f"`{tag_content['upvotes']}`",
                    inline=True
                )
            
            # Tags als Footer
            footer_text = f"📍 {tag_content['subreddit']} | Public Version (SFW only)"
            if 'tags' in tag_content and tag_content['tags']:
                footer_text += f" | 🏷️ {', '.join(tag_content['tags'][:3])}"
            
            embed.set_footer(text=footer_text)
            
            await ctx.send(embed=embed)
            logger.info(f"✅ Tag Content erfolgreich gesendet: {tags} (Public)")
            
        else:
            await ctx.send(f"❌ **Konnte keine Bilder für Tags '{tags}' finden!**\n"
                          "**Öffentliche Version Tipps:**\n"
                          "• Verwende SFW Tags (anime, solo, detailed)\n"
                          "• Kombiniere allgemeine Tags\n"
                          "• Nutze `!tag` für verfügbare Tags\n"
                          "⚠️ *NSFW Tags benötigen Premium APIs*")
            
    except Exception as e:
        logger.error(f"Tag Search Fehler: {e}")
        await ctx.send("❌ **Fehler bei der Tag-Suche!**")

@bot.command(name='help_public')
async def help_public(ctx):
    """Zeigt Hilfe für die öffentliche Version"""
    embed = discord.Embed(
        title="ℹ️ Öffentliche Bot Version - Info",
        description="**Dies ist die öffentliche Version ohne API Keys**",
        color=0x3498db
    )
    
    embed.add_field(
        name="✅ **Verfügbare Features:**",
        value="• **Musik Bot** - Vollständig funktional\n"
              "• **Meme Commands** - Reddit & öffentliche APIs\n"
              "• **Basic NSFW** - Reddit basiert\n"
              "• **SFW Anime** - Safebooru & Nekos API",
        inline=False
    )
    
    embed.add_field(
        name="⚠️ **Eingeschränkte Features:**",
        value="• **Erweiterte NSFW Tags** - Benötigt Rule34 API Key\n"
              "• **Video Suche** - Premium APIs erforderlich\n"
              "• **Advanced Character Search** - API Limits",
        inline=False
    )
    
    embed.add_field(
        name="🔧 **Setup:**",
        value="1. Erstelle `config.json` mit deinem Bot Token\n"
              "2. Installiere Requirements: `pip install -r requirements.txt`\n"
              "3. Starte mit: `python main.py`",
        inline=False
    )
    
    embed.add_field(
        name="📋 **Hauptbefehle:**",
        value="`!play [song]` - Musik\n`!meme` - Zufälliges Meme\n`!nsfw` - Basic NSFW (NSFW Channels)\n`!help` - Vollständige Hilfe",
        inline=False
    )
    
    embed.set_footer(text="Entwickelt von MSCgameplayer mit GitHub Copilot | Öffentliche Version")
    await ctx.send(embed=embed)

# Bot starten - aber nur wenn Token in config.json vorhanden ist
if __name__ == "__main__":
    config = load_config()
    if config and config.get('bot_token'):
        print("🚀 Starte Bot mit Token aus config.json...")
        bot.run(config['bot_token'])
    else:
        print("❌ FEHLER: Kein Bot Token in config.json gefunden!")
        print("📝 Erstelle eine config.json Datei mit folgendem Inhalt:")
        print("""
{
    "bot_token": "DEIN_BOT_TOKEN_HIER",
    "meme_settings": {
        "auto_meme": false,
        "meme_interval_minutes": 120,
        "meme_chance": 0.15,
        "max_memes_per_day": 3,
        "daily_reset_hour": 6,
        "allowed_channels": []
    }
}
        """)
        print("\n💡 Ersetze DEIN_BOT_TOKEN_HIER mit deinem echten Discord Bot Token!")