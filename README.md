# Discord Music & Entertainment Bot (Public Version) 🎵🤖

Ein vielseitiger Discord Bot mit Musik-Player, Meme-System und optionalen NSFW-Features.

## ✨ Features

### 🎵 Musik-System
- **Multi-Platform Support:** YouTube, direkte Audio-URLs
- **Warteschlange:** Automatische Wiedergabe-Warteschlange
- **Voice-Controls:** Play, Pause, Skip, Stop, Queue-Verwaltung
- **High-Quality Audio:** Optimiert für beste Audioqualität

### 😂 Meme-System
- **Manual Memes:** `!meme` Befehl für sofortige Memes
- **Auto-Meme Poster:** Konfigurierbare automatische Memes
- **Tägliche Limits:** Schutz vor Spam

### 🔞 NSFW-Features (Optional)
- **Ultra-Strikte Video-Filterung:** Nur echte Videos (.mp4/.webm/.mov) und GIFs
- **Intelligente Tag-Suche:** Automatische Tag-Kombinationen für bessere Treffer  
- **Anti-Duplicate System:** 20 URL Blacklist verhindert Wiederholungen
- **NSFW-Only Channels:** Automatische Beschränkung auf NSFW-Channels

## 🚀 Installation

### 1. Voraussetzungen
```bash
# Python 3.8+ erforderlich
python --version

# Dependencies installieren  
pip install discord.py[voice] yt-dlp aiohttp
```

### 2. Bot Setup
1. **Discord Bot erstellen:**
   - Gehe zu [Discord Developer Portal](https://discord.com/developers/applications)
   - Erstelle neue Application → Bot
   - Kopiere Bot Token

2. **Bot-Permissions:**
   ```
   ✅ Send Messages
   ✅ Embed Links  
   ✅ Attach Files
   ✅ Connect (Voice)
   ✅ Speak (Voice)
   ✅ Use Voice Activity
   ```

### 3. Konfiguration
```bash
# 1. Konfigurationsdatei kopieren
cp config_public_template.json config_public.json

# 2. Bot Token eintragen
nano config_public.json
# Ersetze: "YOUR_DISCORD_BOT_TOKEN" mit deinem echten Token
```

### 4. Bot starten
```bash
python main_public.py
```

## ⚙️ Konfiguration

### Discord Token (Erforderlich)
```json
{
  "discord_token": "YOUR_DISCORD_BOT_TOKEN"
}
```

### NSFW-Features (Optional)
```json
{
  "rule34_api": {
    "enabled": true,
    "api_key": "YOUR_API_KEY",
    "user_id": "YOUR_USER_ID"
  }
}
```

**API-Key erhalten:**
1. Registriere dich auf [rule34.xxx](https://rule34.xxx)
2. Account Settings → API → Generate Key

### Auto-Meme System (Optional)
```json
{
  "meme_settings": {
    "auto_meme": true,
    "meme_interval_minutes": 60,
    "max_memes_per_day": 10,
    "allowed_channels": []
  }
}
```

## 🎮 Bot-Befehle

### 🎵 Musik-Befehle
| Befehl | Alias | Beschreibung |
|--------|-------|--------------|
| `!join` | `!j` | Bot tritt Voice-Channel bei |
| `!play <song>` | `!p` | Spielt Musik von YouTube/URL |
| `!pause` | | Pausiert aktuelle Musik |
| `!resume` | `!unpause` | Setzt Musik fort |
| `!skip` | `!s` | Überspringt aktuellen Song |
| `!stop` | | Stoppt Musik und leert Queue |
| `!queue` | `!q` | Zeigt aktuelle Warteschlange |
| `!leave` | `!dc` | Bot verlässt Voice-Channel |

### 🎪 Entertainment
| Befehl | Beschreibung |
|--------|--------------|
| `!meme` | Sendet zufälliges Meme |
| `!video <tags>` | 🔞 NSFW Video-Suche (nur NSFW-Channels) |

### 🔧 Utility
| Befehl | Alias | Beschreibung |
|--------|-------|--------------|
| `!commands` | `!cmd` | Zeigt alle Befehle |
| `!help_music` | | Detaillierte Musik-Hilfe |

## 🆕 Version 2.1.0 Updates

### 🎯 Ultra-Strikte Video-Filterung
- **Nur echte Videos:** `.mp4`, `.webm`, `.mov` 
- **Nur echte GIFs:** `.gif`
- **KEINE Bilder mehr:** `.jpg`, `.jpeg`, `.png` komplett ausgeschlossen

### 🧠 Intelligentes Tag-System
```
Suchstrategie:
1. Primäre Suche: "dein_tag"
2. Fallback 1: "dein_tag video"  
3. Fallback 2: "dein_tag animated"
4. Klare Fehlermeldung wenn nichts gefunden
```

### 🛡️ Anti-Duplicate System
- 20 URL Blacklist verhindert sofortige Wiederholungen
- Automatische Rotation alter URLs
- Bessere Variation in Ergebnissen

### 📊 Verbessertes Logging
```
📊 Primär 'flat_chest': 45 total | Videos: 12 | GIFs: 8 | Gewählt: 12
🔄 Fallback 'flat_chest video': 23 posts | Videos: 15 | GIFs: 3  
✅ Sent Video (flat_chest video): https://...
```

## 🛠️ Troubleshooting

### Bot startet nicht
```bash
# Token prüfen
cat config_public.json | grep discord_token

# Dependencies prüfen
pip list | grep -E "(discord|yt-dlp|aiohttp)"

# Python Version prüfen
python --version  # >= 3.8 erforderlich
```

### Audio funktioniert nicht
```bash
# FFmpeg installieren (macOS)
brew install ffmpeg

# FFmpeg installieren (Ubuntu)
sudo apt install ffmpeg

# Opus-Library prüfen
python -c "import discord; print(discord.opus.is_loaded())"
```

### NSFW-Befehle funktionieren nicht
1. **API konfiguriert?** Prüfe `config_public.json`
2. **NSFW-Channel?** Befehle nur in NSFW-Channels
3. **API-Key gültig?** Teste auf rule34.xxx Website

### Auto-Memes kommen nicht
1. **Auto-Meme aktiviert?** `"auto_meme": true`
2. **Tägliches Limit erreicht?** Prüfe `max_memes_per_day`
3. **Berechtigung?** Bot braucht Send Messages in Channels

## 📁 Dateistruktur
```
discord_bot/
├── main_public.py              # 🤖 Haupt-Bot Code
├── config_public_template.json # 📋 Konfigurations-Template  
├── config_public.json         # ⚙️  Deine echte Konfiguration (nicht committen!)
├── README.md                  # 📖 Diese Anleitung
└── requirements.txt           # 📦 Python Dependencies
```

## 🔒 Sicherheit

### ⚠️ Wichtige Sicherheitshinweise
- **NIEMALS** echte Tokens/API-Keys in Git committen
- **Nur** `config_public_template.json` committen
- **Immer** `.gitignore` für `config_public.json` verwenden
- **Regelmäßig** Bot-Token rotieren bei Verdacht auf Kompromittierung

### 🛡️ .gitignore Beispiel
```gitignore
# Bot Configuration (enthält Secrets)
config_public.json
config.json

# Logs
*.log
bot.log

# Python
__pycache__/
*.pyc
```

## 📞 Support & Updates

### 🐛 Bug Reports
Bei Problemen bitte folgende Infos bereitstellen:
1. **Python Version:** `python --version`
2. **Bot Version:** Siehe `_version_info` in config
3. **Error Logs:** Komplette Fehlermeldung
4. **Konfiguration:** `config_public.json` (OHNE Tokens!)

### 🔄 Updates installieren
```bash
# Dependencies aktualisieren
pip install --upgrade discord.py[voice] yt-dlp aiohttp

# Neue Bot Version herunterladen  
# Backup von config_public.json machen
cp config_public.json config_backup.json

# Neue Dateien kopieren und Konfiguration wiederherstellen
```

## 📜 Lizenz

MIT License - Siehe LICENSE-Datei für Details

---

**Bot Version:** 2.1.0 Public Release  
**Letztes Update:** Oktober 2025  
**Author:** MSCgameplayer  

**🎵 Viel Spaß mit deinem Music Bot! 🤖**