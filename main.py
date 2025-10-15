#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord Music & Entertainment Bot (Public Version)
==================================================
Ein vielseitiger Discord Bot mit Musik, Memes und NSFW Features

Features:
- 🎵 Musik-Player (YouTube, Spotify, etc.)
- 🎬 NSFW Video/Bild Suche mit verbesserter Filterung
- 😂 Auto-Meme System  
- 🔧 Modulare Konfiguration

Author: MSCgameplayer
Version: 2.1.0 (Public Release)
License: MIT

Installation:
1. pip install discord.py[voice] yt-dlp aiohttp
2. Konfiguriere config.json
3. python main.py

Updates in Version 2.1.0:
- ✅ Ultra-strikte Video-Filterung (nur Videos/GIFs)
- ✅ Intelligent Tag-Kombination System  
- ✅ Verbessertes Anti-Duplicate System
- ✅ Fallback-Mechanismen für bessere Stabilität
- ✅ Detaillierte Logging und Fehlerbehandlung
"""

import os
import sys
import json
import random
import asyncio
import logging
import aiohttp
import discord
from discord.ext import commands, tasks
import yt_dlp
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

# ========================================================================================
# LOGGING SETUP
# ========================================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('MusicBot')

# ========================================================================================
# DISCORD BOT SETUP
# ========================================================================================
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# ========================================================================================
# CONFIGURATION LOADER
# ========================================================================================
def load_config():
    """Lädt die Bot-Konfiguration aus config.json"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Validierung der wichtigsten Einstellungen
        if not config.get('discord_token') or config['discord_token'] == "YOUR_DISCORD_BOT_TOKEN":
            logger.error("❌ Discord Token nicht konfiguriert! Bitte config.json bearbeiten.")
            sys.exit(1)
            
        logger.info("✅ Konfiguration erfolgreich geladen")
        return config
    except FileNotFoundError:
        logger.error("❌ config.json nicht gefunden!")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"❌ Fehler beim Lesen der config.json: {e}")
        sys.exit(1)

# Globale Konfiguration laden
CONFIG = load_config()

# ========================================================================================
# AUDIO SETUP
# ========================================================================================
def setup_opus():
    """Lädt die Opus-Bibliothek für Audio-Support"""
    opus_paths = [
        '/opt/homebrew/lib/libopus.dylib',  # macOS Homebrew
        '/usr/lib/x86_64-linux-gnu/libopus.so.0',  # Ubuntu/Debian
        '/usr/lib64/libopus.so.0',  # CentOS/RHEL
        'libopus.dll'  # Windows
    ]
    
    for path in opus_paths:
        if os.path.exists(path):
            try:
                discord.opus.load_opus(path)
                if discord.opus.is_loaded():
                    logger.info(f"✅ Opus erfolgreich geladen von: {path}")
                    return True
            except Exception as e:
                logger.warning(f"⚠️ Opus-Ladung fehlgeschlagen ({path}): {e}")
                continue
    
    logger.warning("⚠️ Opus konnte nicht geladen werden - Audio möglicherweise nicht verfügbar")
    return False

# Opus beim Start laden
setup_opus()
if discord.opus.is_loaded():
    logger.info("🎵 Opus erfolgreich geladen - Audio bereit!")
else:
    logger.warning("⚠️ Opus nicht verfügbar - Musik-Features eingeschränkt")

# ========================================================================================
# YT-DLP CONFIGURATION
# ========================================================================================
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
    'source_address': '0.0.0.0',
    'cookiefile': None,
    'age_limit': None,
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

def get_ytdl():
    """Erstellt YT-DLP Instanz bei Bedarf"""
    try:
        return yt_dlp.YoutubeDL(ytdl_format_options)  # type: ignore
    except Exception as e:
        logger.error(f"YT-DLP Initialisierung fehlgeschlagen: {e}")
        return None

# ========================================================================================
# GLOBAL VARIABLES
# ========================================================================================
# Musik-System
voice_clients = {}
music_queues = {}

# NSFW Anti-Duplicate System (verbessertes Set-basiertes System)
sent_video_urls = set()

# Meme-System
meme_counters = {}
last_meme_reset = {}

# ========================================================================================
# UTILITY FUNCTIONS
# ========================================================================================
def reset_daily_counters():
    """Setzt tägliche Zähler zurück"""
    global last_meme_reset
    today = datetime.now().strftime('%Y-%m-%d')
    
    for guild_id in list(meme_counters.keys()):
        if last_meme_reset.get(guild_id) != today:
            meme_counters[guild_id] = 0
            last_meme_reset[guild_id] = today
            logger.info(f"🔄 Täglicher Meme-Counter zurückgesetzt (Tag: {today})")

async def is_nsfw_channel(ctx):
    """Überprüft ob Channel NSFW ist"""
    return hasattr(ctx.channel, 'is_nsfw') and ctx.channel.is_nsfw()

# ========================================================================================
# DISCORD BOT EVENTS
# ========================================================================================
@bot.event
async def on_ready():
    """Bot ist bereit und verbunden"""
    logger.info(f"{bot.user.name}#{bot.user.discriminator} ist online!")
    logger.info(f"Bot ID: {bot.user.id}")
    
    # Starte Auto-Systeme
    if CONFIG['meme_settings']['auto_meme']:
        auto_meme_poster.start()
        logger.info(f"🤣 Auto-Meme Poster gestartet (alle {CONFIG['meme_settings']['meme_interval_minutes']} min, max {CONFIG['meme_settings']['max_memes_per_day']} pro Tag)")
    
    logger.info("🎵 Musik & Meme Bot bereit!")
    print("------")

@bot.event
async def on_command_error(ctx, error):
    """Globale Fehlerbehandlung"""
    if isinstance(error, commands.CommandNotFound):
        return  # Ignoriere unbekannte Befehle
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ **Fehlender Parameter:** {error.param.name}")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ **Ungültiger Parameter!** Überprüfe deine Eingabe.")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏰ **Cooldown:** Warte noch {error.retry_after:.1f} Sekunden.")
    else:
        logger.error(f"Unerwarteter Fehler: {error}")
        await ctx.send("❌ **Ein unerwarteter Fehler ist aufgetreten!**")

# ========================================================================================
# MUSIC COMMANDS
# ========================================================================================
class YTDLSource(discord.PCMVolumeTransformer):
    """YouTube Audio Source für Discord"""
    
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = data.get('duration')
        self.thumbnail = data.get('thumbnail')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        """Erstellt Audio-Source von URL"""
        loop = loop or asyncio.get_event_loop()
        try:
            ytdl = get_ytdl()
            if not ytdl:
                raise Exception("YT-DLP konnte nicht initialisiert werden")
                
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
            
            if 'entries' in data:
                data = data['entries'][0]
            
            filename = data.get('url', '') if stream else ytdl.prepare_filename(data)
            return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
        except Exception as e:
            logger.error(f"YT-DL Fehler: {e}")
            raise e

@bot.command(name='join', aliases=['j'])
async def join_voice(ctx):
    """Bot tritt Voice-Channel bei"""
    if not ctx.author.voice:
        return await ctx.send("❌ **Du musst in einem Voice-Channel sein!**")
    
    channel = ctx.author.voice.channel
    
    if ctx.voice_client is not None:
        await ctx.voice_client.move_to(channel)
    else:
        await channel.connect()
    
    await ctx.send(f"🎵 **Verbunden mit:** {channel.name}")

@bot.command(name='leave', aliases=['disconnect', 'dc'])
async def leave_voice(ctx):
    """Bot verlässt Voice-Channel"""
    if ctx.voice_client:
        guild_id = ctx.guild.id
        if guild_id in music_queues:
            music_queues[guild_id].clear()
        await ctx.voice_client.disconnect()
        await ctx.send("👋 **Voice-Channel verlassen!**")
    else:
        await ctx.send("❌ **Bot ist nicht in einem Voice-Channel!**")

@bot.command(name='play', aliases=['p'])
async def play_music(ctx, *, search):
    """Spielt Musik von YouTube/URL"""
    if not ctx.author.voice:
        return await ctx.send("❌ **Du musst in einem Voice-Channel sein!**")
    
    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()
    
    guild_id = ctx.guild.id
    if guild_id not in music_queues:
        music_queues[guild_id] = []
    
    # Status-Nachricht
    msg = await ctx.send(f"🔍 **Suche nach:** `{search}`...")
    
    try:
        # Audio-Source erstellen
        source = await YTDLSource.from_url(search, loop=bot.loop, stream=True)
        
        # Zur Warteschlange hinzufügen
        music_queues[guild_id].append(source)
        
        # Abspielen wenn nicht bereits aktiv
        if not ctx.voice_client.is_playing():
            await play_next(ctx)
        else:
            embed = discord.Embed(
                title="➕ Zur Warteschlange hinzugefügt",
                description=f"**{source.title}**",
                color=0x00ff00
            )
            if source.thumbnail:
                embed.set_thumbnail(url=source.thumbnail)
            embed.add_field(name="Position", value=len(music_queues[guild_id]), inline=True)
            await msg.edit(content="", embed=embed)
            
    except Exception as e:
        logger.error(f"Play-Fehler: {e}")
        await msg.edit(content=f"❌ **Fehler beim Laden:** {str(e)[:100]}...")

async def play_next(ctx):
    """Spielt nächsten Song in Warteschlange"""
    guild_id = ctx.guild.id
    
    if guild_id not in music_queues or not music_queues[guild_id]:
        return
    
    source = music_queues[guild_id].pop(0)
    
    def after_playing(error):
        if error:
            logger.error(f"Player Fehler: {error}")
        
        # Nächsten Song asynchron abspielen
        coro = play_next(ctx)
        fut = asyncio.run_coroutine_threadsafe(coro, bot.loop)
        try:
            fut.result()
        except Exception as e:
            logger.error(f"Fehler beim Abspielen des nächsten Songs: {e}")
    
    ctx.voice_client.play(source, after=after_playing)
    
    # Now Playing Embed
    embed = discord.Embed(
        title="🎵 Wird abgespielt",
        description=f"**{source.title}**",
        color=0x1DB954
    )
    if source.thumbnail:
        embed.set_thumbnail(url=source.thumbnail)
    
    if source.duration:
        duration_str = f"{source.duration // 60}:{source.duration % 60:02d}"
        embed.add_field(name="Dauer", value=duration_str, inline=True)
    
    embed.add_field(name="Warteschlange", value=len(music_queues[guild_id]), inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='pause')
async def pause_music(ctx):
    """Pausiert aktuelle Musik"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ **Musik pausiert**")
    else:
        await ctx.send("❌ **Keine Musik läuft!**")

@bot.command(name='resume', aliases=['unpause'])
async def resume_music(ctx):
    """Setzt pausierte Musik fort"""
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ **Musik fortgesetzt**")
    else:
        await ctx.send("❌ **Musik ist nicht pausiert!**")

@bot.command(name='stop')
async def stop_music(ctx):
    """Stoppt Musik und leert Warteschlange"""
    if ctx.voice_client:
        guild_id = ctx.guild.id
        if guild_id in music_queues:
            music_queues[guild_id].clear()
        ctx.voice_client.stop()
        await ctx.send("⏹️ **Musik gestoppt und Warteschlange geleert**")
    else:
        await ctx.send("❌ **Bot spielt keine Musik!**")

@bot.command(name='skip', aliases=['s'])
async def skip_music(ctx):
    """Überspringt aktuellen Song"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ **Song übersprungen**")
    else:
        await ctx.send("❌ **Keine Musik läuft!**")

@bot.command(name='queue', aliases=['q'])
async def show_queue(ctx):
    """Zeigt aktuelle Warteschlange"""
    guild_id = ctx.guild.id
    
    if guild_id not in music_queues or not music_queues[guild_id]:
        return await ctx.send("📭 **Warteschlange ist leer!**")
    
    embed = discord.Embed(title="🎵 Musik-Warteschlange", color=0x1DB954)
    
    queue_text = ""
    for i, source in enumerate(music_queues[guild_id][:10], 1):
        queue_text += f"`{i}.` **{source.title}**\n"
    
    if len(music_queues[guild_id]) > 10:
        queue_text += f"\n*... und {len(music_queues[guild_id]) - 10} weitere Songs*"
    
    embed.description = queue_text
    embed.set_footer(text=f"Gesamt: {len(music_queues[guild_id])} Songs")
    
    await ctx.send(embed=embed)

# ========================================================================================
# MEME COMMANDS
# ========================================================================================
@bot.command(name='meme', aliases=['funny', 'lol'])
async def send_meme(ctx):
    """Sendet ein zufälliges Meme"""
    reset_daily_counters()
    
    # Einfache Meme-URLs (können erweitert werden)
    meme_urls = [
        "https://i.imgur.com/placeholder1.jpg",
        "https://i.imgur.com/placeholder2.jpg",
        "https://i.imgur.com/placeholder3.jpg",
        # Füge hier echte Meme-URLs hinzu
    ]
    
    if not meme_urls:
        return await ctx.send("😅 **Keine Memes verfügbar!** Bitte konfiguriere Meme-URLs.")
    
    meme_url = random.choice(meme_urls)
    
    embed = discord.Embed(
        title="😂 Random Meme",
        color=0xffaa00
    )
    embed.set_image(url=meme_url)
    embed.set_footer(text="Bot Meme Collection")
    
    await ctx.send(embed=embed)

@tasks.loop(minutes=CONFIG['meme_settings']['meme_interval_minutes'])
async def auto_meme_poster():
    """Automatischer Meme-Poster"""
    if not CONFIG['meme_settings']['auto_meme']:
        return
    
    reset_daily_counters()
    
    for guild in bot.guilds:
        guild_id = guild.id
        
        # Prüfe tägliches Limit
        if meme_counters.get(guild_id, 0) >= CONFIG['meme_settings']['max_memes_per_day']:
            continue
        
        # Zufällige Chance
        if random.random() > CONFIG['meme_settings']['meme_chance']:
            continue
        
        # Finde erlaubte Channels
        allowed_channels = CONFIG['meme_settings']['allowed_channels']
        target_channels = []
        
        for channel in guild.text_channels:
            if not allowed_channels or channel.id in allowed_channels:
                target_channels.append(channel)
        
        if not target_channels:
            continue
        
        # Sende Meme
        channel = random.choice(target_channels)
        try:
            # Hier würde ein echtes Meme gesendet werden
            await channel.send("😂 **Auto-Meme!** (Placeholder)")
            meme_counters[guild_id] = meme_counters.get(guild_id, 0) + 1
            logger.info(f"📨 Auto-Meme gesendet in {guild.name}#{channel.name}")
        except Exception as e:
            logger.error(f"Auto-Meme Fehler: {e}")

# ========================================================================================
# NSFW COMMANDS (IMPROVED)
# ========================================================================================
@bot.command(name='video', aliases=['vid', 'video_search'])
async def video_search(ctx, *, tags=None):
    """
    🎬 VERBESSERTE Video-Suche mit Ultra-Strikter Filterung
    
    Neue Features v2.1.0:
    - ✅ NUR echte Videos (.mp4/.webm/.mov) und GIFs (.gif)
    - ✅ KEINE statischen Bilder mehr (.jpg/.jpeg/.png)
    - ✅ Intelligente Tag-Kombination (tag+video, tag+animated)
    - ✅ Anti-Duplicate System (20 URL Blacklist)
    - ✅ Fallback-Mechanismen für bessere Treffer-Rate
    """
    if not await is_nsfw_channel(ctx):
        await ctx.send("🔞 **Dieser Befehl funktioniert nur in NSFW-Channels!**")
        return
        
    if not tags:
        embed = discord.Embed(
            title="🎬 Video-Suche Hilfe",
            description="Suche nach NSFW Videos mit Tags:",
            color=0xff1493
        )
        
        video_tags = {
            "**Beliebte Video-Tags:**": "animated, 3d_animation, hentai, pov",
            "**Charakter-Tags:**": "anime, manga, character_name",
            "**Style-Tags:**": "flat_chest, big_breasts, petite",
            "**Qualitäts-Tags:**": "high_quality, hd, 60fps"
        }
        
        for category, examples in video_tags.items():
            embed.add_field(name=category, value=f"`{examples}`", inline=False)
        
        embed.add_field(
            name="**🔧 Neue Features v2.1.0:**",
            value="• Ultra-strikte Filterung (nur Videos/GIFs)\n• Intelligente Tag-Kombination\n• Anti-Duplicate System\n• Fallback-Mechanismen",
            inline=False
        )
        
        embed.set_footer(text="Beispiel: !video flat_chest animated")
        await ctx.send(embed=embed)
        return
    
    # Prüfe Rule34 API Konfiguration
    if not CONFIG['rule34_api']['enabled'] or not CONFIG['rule34_api']['api_key']:
        embed = discord.Embed(
            title="⚠️ API nicht konfiguriert",
            description="Die Rule34 API ist nicht konfiguriert.",
            color=0xffa500
        )
        embed.add_field(
            name="Konfiguration:",
            value="Bearbeite `config.json` und füge deine API-Daten hinzu:\n\n```json\n\"rule34_api\": {\n    \"enabled\": true,\n    \"api_key\": \"YOUR_API_KEY\",\n    \"user_id\": \"YOUR_USER_ID\"\n}\n```",
            inline=False
        )
        embed.add_field(
            name="API-Key erhalten:",
            value="Registriere dich auf rule34.xxx und generiere einen API-Key in deinen Account-Einstellungen.",
            inline=False
        )
        embed.set_footer(text="Bot funktioniert ohne API nur eingeschränkt")
        await ctx.send(embed=embed)
        return
    
    # Status-Nachricht
    status_msg = await ctx.send("🔍 **Suche nach Videos...** 📹")
    
    try:
        await enhanced_video_search(ctx, tags, status_msg)
    except Exception as e:
        logger.error(f"Video-Suche Fehler: {e}")
        await status_msg.edit(content="❌ **Fehler bei der Video-Suche!** Versuche es später erneut.")

async def enhanced_video_search(ctx, tags, status_msg):
    """
    🎯 Erweiterte Video-Suche mit Ultra-Strikter Filterung
    
    Suchstrategie:
    1. Primäre Suche: Nutzer-Tag (z.B. "flat_chest")
    2. Fallback 1: Tag + "video" (z.B. "flat_chest video")  
    3. Fallback 2: Tag + "animated" (z.B. "flat_chest animated")
    4. Letzter Ausweg: Klare Fehlermeldung
    """
    global sent_video_urls
    
    url = 'https://api.rule34.xxx/index.php'
    
    # Basis-Parameter mit Authentifizierung
    base_params = {
        'page': 'dapi',
        's': 'post',
        'q': 'index',
        'limit': 100,  # Erhöht für bessere Auswahl
        'pid': random.randint(0, 50),  # Zufällige Seite für Variation
        'api_key': CONFIG['rule34_api']['api_key'],
        'user_id': CONFIG['rule34_api']['user_id']
    }
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
        # 🎯 PRIMÄRE SUCHE: Nutzer-Tag
        params = base_params.copy()
        params['tags'] = tags
        
        async with session.get(url, params=params) as response:
            if response.status != 200:
                await status_msg.edit(content=f"❌ **API-Fehler:** Status {response.status}")
                return
            
            content = await response.text()
            root = ET.fromstring(content)
            posts = [post.attrib for post in root.findall('.//post')]
            
            logger.info(f"📊 Primäre Suche '{tags}': {len(posts)} posts gefunden")
            
            # 🔍 ULTRA-STRIKTE VIDEO-FILTERUNG
            real_videos = []
            real_gifs = []
            
            for post in posts:
                file_url = post.get('file_url', '')
                if file_url:
                    # Nur ECHTE Videoformate akzeptieren
                    if any(ext in file_url.lower() for ext in ['.mp4', '.webm', '.mov']):
                        real_videos.append(post)
                    elif '.gif' in file_url.lower():
                        real_gifs.append(post)
            
            # Wähle beste verfügbare Medien
            if real_videos:
                media_posts = real_videos
                logger.info(f"🎬 Gefunden: {len(media_posts)} ECHTE VIDEOS für '{tags}'")
            elif real_gifs:
                media_posts = real_gifs
                logger.info(f"🎭 Gefunden: {len(media_posts)} ECHTE GIFS für '{tags}'")
            else:
                media_posts = []
                logger.warning(f"❌ KEINE Videos/GIFs für '{tags}' in {len(posts)} Posts!")
            
            logger.info(f"📊 Primär '{tags}': {len(posts)} total | Videos: {len(real_videos)} | GIFs: {len(real_gifs)} | Gewählt: {len(media_posts)}")
            
            # 🎬 SENDE GEFUNDENES VIDEO
            if media_posts:
                await send_video_result(ctx, media_posts, tags, status_msg)
                return
            
            # 🔄 INTELLIGENT FALLBACK: Tag-Kombinationen
            logger.info(f"🔄 Keine Videos für '{tags}' - versuche Tag-Kombinationen")
            await status_msg.edit(content="🔄 **Erweitere Suche mit Video-Tags...**")
            
            # Versuche Tag-Kombinationen: "tag video" dann "tag animated"
            for video_tag in ['video', 'animated']:
                combined_tags = f"{tags} {video_tag}"
                fallback_params = base_params.copy()
                fallback_params['tags'] = combined_tags
                
                async with session.get(url, params=fallback_params) as fallback_response:
                    if fallback_response.status == 200:
                        fallback_content = await fallback_response.text()
                        fallback_root = ET.fromstring(fallback_content)
                        fallback_posts = [post.attrib for post in fallback_root.findall('.//post')]
                        
                        # Videos/GIFs aus Fallback filtern
                        fallback_videos = []
                        fallback_gifs = []
                        
                        for post in fallback_posts:
                            file_url = post.get('file_url', '')
                            if file_url and file_url not in sent_video_urls:
                                if any(ext in file_url.lower() for ext in ['.mp4', '.webm', '.mov']):
                                    fallback_videos.append(post)
                                elif '.gif' in file_url.lower():
                                    fallback_gifs.append(post)
                        
                        logger.info(f"📊 Fallback '{combined_tags}': {len(fallback_posts)} posts | Videos: {len(fallback_videos)} | GIFs: {len(fallback_gifs)}")
                        
                        # Verwende gefundene Videos/GIFs
                        if fallback_videos:
                            await send_video_result(ctx, fallback_videos, combined_tags, status_msg)
                            return
                        elif fallback_gifs:
                            await send_video_result(ctx, fallback_gifs, combined_tags, status_msg)
                            return
            
            # 🚫 WENN ALLE FALLBACKS FEHLSCHLAGEN
            embed = discord.Embed(
                title="❌ Keine Videos gefunden",
                description=f"Leider keine Videos für Tag `{tags}` verfügbar.",
                color=0xff4444
            )
            embed.add_field(
                name="💡 Tipps:",
                value="• Versuche andere Tags\n• Nutze populäre Tags wie `animated`\n• Kombiniere mehrere Tags",
                inline=False
            )
            embed.set_footer(text="Versuche: !video animated")
            await status_msg.edit(content="", embed=embed)
            logger.warning("❌ Keine Videos mit allen Fallback-Tags gefunden!")

async def send_video_result(ctx, media_posts, tags, status_msg):
    """
    📤 Sendet Video-Ergebnis mit Anti-Duplicate System
    """
    global sent_video_urls
    
    # Wähle zufälliges Medium
    post = random.choice(media_posts)
    video_url = post.get('file_url', '')
    
    # Anti-Duplicate: Versuche anderen Post zu finden
    if video_url in sent_video_urls:
        other_posts = [p for p in media_posts if p.get('file_url') not in sent_video_urls]
        if other_posts:
            post = random.choice(other_posts)
            video_url = post.get('file_url', '')
    
    # Zur Blacklist hinzufügen (Max 20 URLs)
    sent_video_urls.add(video_url)
    if len(sent_video_urls) > 20:
        sent_video_urls.pop()  # Älteste URL entfernen
    
    # Bestimme Medientyp für Anzeige
    is_video = any(ext in video_url.lower() for ext in ['.mp4', '.webm', '.mov'])
    is_gif = '.gif' in video_url.lower()
    
    if is_video:
        media_icon = "🎬"
        media_type = "Video"
    elif is_gif:
        media_icon = "🎭" 
        media_type = "GIF"
    else:
        media_icon = "❓"
        media_type = "Unknown"
        logger.warning(f"🚨 UNEXPECTED FILE TYPE: {video_url}")
    
    # Sende Ergebnis
    result_text = f"{media_icon} **Rule34 {media_type}** (Tags: {tags})\n{video_url}"
    await status_msg.edit(content=result_text)
    
    logger.info(f"✅ Sent {media_type} ({tags}): {video_url[:50]}...")

# ========================================================================================
# UTILITY COMMANDS
# ========================================================================================
@bot.command(name='commands', aliases=['hilfe', 'bot_help', 'cmd'])
async def show_commands(ctx):
    """Zeigt alle verfügbaren Bot-Befehle"""
    embed = discord.Embed(
        title="🤖 Bot Befehle",
        description="Alle verfügbaren Befehle:",
        color=0x00aaff
    )
    
    # Musik-Befehle
    music_cmds = {
        "!join (!j)": "Tritt Voice-Channel bei",
        "!play <song> (!p)": "Spielt Musik ab",
        "!pause": "Pausiert Musik",
        "!resume": "Setzt Musik fort", 
        "!skip (!s)": "Überspringt Song",
        "!stop": "Stoppt Musik",
        "!queue (!q)": "Zeigt Warteschlange",
        "!leave (!dc)": "Verlässt Voice-Channel"
    }
    
    embed.add_field(
        name="🎵 Musik-Befehle",
        value="\n".join([f"`{cmd}` - {desc}" for cmd, desc in music_cmds.items()]),
        inline=False
    )
    
    # Entertainment-Befehle
    fun_cmds = {
        "!meme": "Zufälliges Meme",
        "!video <tags>": "🔞 NSFW Video-Suche (nur NSFW-Channel)"
    }
    
    embed.add_field(
        name="🎪 Entertainment-Befehle", 
        value="\n".join([f"`{cmd}` - {desc}" for cmd, desc in fun_cmds.items()]),
        inline=False
    )
    
    # Utility-Befehle
    util_cmds = {
        "!commands (!cmd)": "Zeigt diese Hilfe",
        "!help_music": "Detaillierte Musik-Hilfe"
    }
    
    embed.add_field(
        name="🔧 Utility-Befehle",
        value="\n".join([f"`{cmd}` - {desc}" for cmd, desc in util_cmds.items()]),
        inline=False
    )
    
    embed.add_field(
        name="🆕 Neue Features v2.1.0",
        value="• Ultra-strikte Video-Filterung\n• Anti-Duplicate System\n• Intelligente Tag-Kombinationen\n• Verbesserte Fehlerbehandlung",
        inline=False
    )
    
    embed.set_footer(text="Präfix: ! | Bot Version 2.1.0 (Public)")
    
    await ctx.send(embed=embed)

@bot.command(name='help_music', aliases=['music_help'])
async def music_help(ctx):
    """Detaillierte Musik-Hilfe"""
    embed = discord.Embed(
        title="🎵 Musik-Bot Anleitung",
        description="Vollständige Anleitung für Musik-Befehle:",
        color=0x1DB954
    )
    
    sections = {
        "🚀 **Schnellstart:**": "1. `!join` - Bot beitreten lassen\n2. `!play <song>` - Musik abspielen\n3. `!leave` - Bot entfernen",
        
        "🔍 **Suchfunktionen:**": "• YouTube-URLs direkt verwenden\n• Songtitel eingeben\n• Playlist-URLs (erster Song)\n• Spotify-Links (falls unterstützt)",
        
        "⏯️ **Wiedergabe-Steuerung:**": "`!pause` - Pausieren\n`!resume` - Fortsetzen\n`!skip` - Nächster Song\n`!stop` - Alles stoppen",
        
        "📋 **Warteschlange:**": "`!queue` - Aktuelle Warteschlange\n`!play <song>` - Zur Warteschlange hinzufügen\nAutomatische Wiedergabe der Warteschlange",
        
        "🔧 **Hinweise:**": "• Bot benötigt Voice-Channel Berechtigung\n• Unterstützt YouTube, direkte Links\n• Warteschlange automatisch abgearbeitet"
    }
    
    for title, content in sections.items():
        embed.add_field(name=title, value=content, inline=False)
    
    embed.set_footer(text="Für alle Befehle: !commands")
    
    await ctx.send(embed=embed)

# ========================================================================================
# BOT STARTUP
# ========================================================================================
def main():
    """Hauptfunktion zum Starten des Bots"""
    try:
        logger.info("🚀 Starte Discord Bot...")
        logger.info("📋 Konfiguration geladen")
        logger.info("🎵 Audio-System bereit")
        
        if CONFIG['rule34_api']['enabled']:
            logger.info("🔞 NSFW-Features aktiviert")
        else:
            logger.info("⚠️  NSFW-Features deaktiviert (API nicht konfiguriert)")
            
        if CONFIG['meme_settings']['auto_meme']:
            logger.info("😂 Auto-Meme System aktiviert")
        else:
            logger.info("😴 Auto-Meme System deaktiviert")
        
        # Bot starten
        bot.run(CONFIG['discord_token'])
        
    except discord.LoginFailure:
        logger.error("❌ Discord Login fehlgeschlagen! Überprüfe deinen Bot-Token.")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("👋 Bot wird beendet...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Unerwarteter Fehler: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()