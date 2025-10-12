# Discord Bot - Öffentliche Version

Ein vielseitiger Discord Bot mit Musik-, Meme- und Unterhaltungsfunktionen.

## ⚠️ **Wichtiger Hinweis für Entwickler**

**Wenn du diesen Bot als Basis für dein eigenes Projekt verwendest, bitte ich um Attribution!**  
Die Entwicklung dieses Bots war viel Arbeit - ein kleiner Credit bedeutet mir viel! 🙏

**Einfach in deine README schreiben:**
```
Basiert auf Simple Discord Bot von MSCgameplayer
https://github.com/MSCgameplayer/Simple_discord_bot
```

## 🚀 Features

### ✅ Vollständig verfügbar (Öffentliche Version)
- **🎵 Musik Bot** - YouTube, Spotify, SoundCloud Support
- **🤣 Meme Generator** - Reddit & öffentliche APIs  
- **🔞 Basic NSFW** - Reddit basierte Inhalte (nur NSFW Channels)
- **🎨 SFW Anime** - Safebooru & Nekos.life API

### ⚠️ Eingeschränkt (API Keys erforderlich)
- **Advanced NSFW Tags** - Rule34 API Premium Features
- **Video Content** - Premium APIs  
- **Extended Character Search** - API Rate Limits

## 📋 Hauptbefehle

### 🎵 Musik
- `!play [song/url]` - Spielt Musik ab
- `!pause` - Pausiert die Musik
- `!resume` - Setzt die Musik fort
- `!skip` - Überspringt den aktuellen Song
- `!queue` - Zeigt die Warteschlange
- `!stop` - Stoppt die Musik
- `!join` - Bot tritt Voice Channel bei
- `!leave` - Bot verlässt Voice Channel

### 🤣 Memes & Fun
- `!meme` - Zufälliges Meme
- `!nsfw` - NSFW Content (nur in NSFW Channels)
- `!figure [name]` - Sucht Anime Charaktere
- `!tag [tags]` - Tag-basierte Suche (SFW)

### ℹ️ Hilfe & Info
- `!help` - Vollständige Befehlsliste
- `!help_public` - Info zur öffentlichen Version

## 🔧 Installation & Setup

### Voraussetzungen
- Python 3.8+
- Discord Developer Account
- FFmpeg (für Musik)

### 1. Repository klonen
```bash
git clone https://github.com/MSCgameplayer/Discord-Bot.git
cd Discord-Bot
```

### 2. Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

### 3. FFmpeg installieren

**Windows:**
- Lade FFmpeg von https://ffmpeg.org/download.html
- Füge FFmpeg zum PATH hinzu

**macOS:**
```bash
brew install ffmpeg opus
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg libopus0
```

### 4. Bot Token konfigurieren

1. Gehe zu https://discord.com/developers/applications
2. Erstelle eine neue Application
3. Gehe zu "Bot" → "Add Bot"
4. Kopiere den Bot Token
5. Bearbeite `config.json`:

```json
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
```

### 5. Bot Berechtigungen

Stelle sicher, dass dein Bot folgende Berechtigungen hat:
- `Send Messages`
- `Connect` (Voice)
- `Speak` (Voice)
- `Use Voice Activity`
- `Embed Links`
- `Attach Files`
- `Read Message History`

### 6. Bot starten
```bash
python main.py
```

## ⚙️ Erweiterte Konfiguration

### Auto-Meme Feature
```json
{
    "meme_settings": {
        "auto_meme": true,
        "meme_interval_minutes": 180,
        "meme_chance": 0.2,
        "max_memes_per_day": 5,
        "daily_reset_hour": 6,
        "allowed_channels": [1234567890, 9876543210]
    }
}
```

### Berechtigungen
Der Bot hat ein eingebautes Moderator-System für administrative Befehle.

## 🔒 Öffentliche vs. Premium Version

### Öffentliche Version (Diese)
- ✅ Vollständige Musik-Funktionalität
- ✅ Basic Meme & NSFW Support
- ✅ SFW Anime Content
- ❌ Erweiterte NSFW Features
- ❌ Premium API Integration

### Premium Features (API Keys erforderlich)
- **Rule34 API Integration** - Erweiterte NSFW Features
  - 🔗 **API verfügbar unter:** https://api.rule34.xxx
  - Ermöglicht unbegrenzte Tag-Suche und erweiterte NSFW Commands
  - Zugang zu erweiterten Character-Search Funktionen
- **Erweiterte Character Search** - Detaillierte Anime-Charaktersuche
- **Video Content APIs** - Zusätzliche Video-Quellen
- **Unbegrenzte Tag-Suche** - Ohne Rate Limits

### 🔑 API Setup für Premium Features

Um die erweiterten NSFW Features zu nutzen, füge folgende Konfiguration zu deiner `config.json` hinzu:

```json
{
    "bot_token": "DEIN_BOT_TOKEN",
    "rule34_api": {
        "enabled": true,
        "base_url": "https://api.rule34.xxx"
    },
    "meme_settings": {
        "auto_meme": false
    }
}
```

**Hinweis:** Die Rule34 API erfordert möglicherweise eine Registrierung oder API-Schlüssel je nach Nutzung.

## 🐛 Problembehandlung

### Musik funktioniert nicht
1. **FFmpeg installiert?**
   ```bash
   ffmpeg -version
   ```

2. **Opus Library Fehler:**
   - macOS: `brew install opus`
   - Linux: `sudo apt install libopus0`
   - Windows: Opus sollte mit FFmpeg kommen

3. **Bot kann nicht Voice Channel beitreten:**
   - Überprüfe Bot-Berechtigungen
   - Stelle sicher, dass du in einem Voice Channel bist

### Bot startet nicht
1. **Token korrekt?** Überprüfe `config.json`
2. **Abhängigkeiten installiert?** `pip install -r requirements.txt`
3. **Python Version?** Mindestens Python 3.8

### NSFW Befehle funktionieren nicht
1. **Channel ist NSFW?** Aktiviere NSFW in Channel-Einstellungen
2. **Bot-Berechtigungen?** `Embed Links` erforderlich

## 🤝 Beiträge & Support

- **GitHub:** https://github.com/MSCgameplayer/Discord-Bot
- **Issues:** Melde Bugs über GitHub Issues
- **Entwickler:** MSCgameplayer
- **KI-Assistent:** GitHub Copilot

## 📜 Lizenz & Attribution

Dieses Projekt steht unter der MIT Lizenz. Siehe LICENSE Datei für Details.

### 🙏 **Wenn du diesen Bot als Basis verwendest:**
**Bitte gib Credits an den ursprünglichen Entwickler!** Das bedeutet:

1. **Verweise auf dieses Projekt** in deiner README oder Dokumentation
2. **Erwähne MSCgameplayer** als ursprünglichen Entwickler  
3. **Verlinke zurück** zu diesem Repository

**Beispiel Attribution:**
```markdown
## Credits
Basiert auf Simple Discord Bot von MSCgameplayer
Original Projekt: https://github.com/MSCgameplayer/Simple_discord_bot
```

**Warum Credits wichtig sind:**
Dieses Projekt stellt bedeutende Entwicklungsarbeit dar. Attribution unterstützt den 
ursprünglichen Entwickler und hilft anderen, das Quellprojekt für Updates zu finden.

## 🙏 Credits

- **Entwickelt von:** MSCgameplayer
- **KI-Unterstützung:** GitHub Copilot
- **APIs:** Reddit, Nekos.life, Safebooru
- **Libraries:** discord.py, yt-dlp, aiohttp

---

**⚠️ Hinweis:** Dies ist die öffentliche Version ohne API Keys. Für erweiterte Features sind eigene API-Schlüssel erforderlich.