# Discord Bot - Public Version

A versatile Discord bot with music streaming, memes, and entertainment features.

## ⚠️ **Important Notice for Developers**

**If you use this bot as a base for your own project, please provide attribution!**  
Developing this bot was a lot of work - a small credit means a lot to me! 🙏

**Simply add to your README:**
```
Based on Simple Discord Bot by MSCgameplayer
https://github.com/MSCgameplayer/Simple_discord_bot
```

## 🚀 Features

### ✅ Fully Available (Public Version)
- **🎵 Music Bot** - YouTube, Spotify, SoundCloud support
- **🤣 Meme Generator** - Reddit & public APIs  
- **🔞 Basic NSFW** - Reddit-based content (NSFW channels only)
- **🎨 SFW Anime** - Safebooru & Nekos.life API

### ⚠️ Limited (API Keys Required)
- **Advanced NSFW Tags** - Rule34 API Premium Features
- **Video Content** - Premium APIs  
- **Extended Character Search** - API Rate Limits

## 📋 Main Commands

### 🎵 Music
- `!play [song/url]` - Plays music
- `!pause` - Pauses the music
- `!resume` - Resumes the music
- `!skip` - Skips the current song
- `!queue` - Shows the queue
- `!stop` - Stops the music
- `!join` - Bot joins voice channel
- `!leave` - Bot leaves voice channel

### 🤣 Memes & Fun
- `!meme` - Random meme
- `!nsfw` - NSFW content (NSFW channels only)
- `!figure [name]` - Search anime characters
- `!tag [tags]` - Tag-based search (SFW)

### ℹ️ Help & Info
- `!help` - Complete command list
- `!help_public` - Public version info

## 🔧 Installation & Setup

### Prerequisites
- Python 3.8+
- Discord Developer Account
- FFmpeg (for music)

### 1. Clone Repository
```bash
git clone https://github.com/MSCgameplayer/Simple_discord_bot.git
cd Simple_discord_bot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg

**Windows:**
- Download FFmpeg from https://ffmpeg.org/download.html
- Add FFmpeg to PATH

**macOS:**
```bash
brew install ffmpeg opus
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg libopus0
```

### 4. Configure Bot Token

1. Go to https://discord.com/developers/applications
2. Create a new Application
3. Go to "Bot" → "Add Bot"
4. Copy the bot token
5. Edit `config.json`:

```json
{
    "bot_token": "YOUR_BOT_TOKEN_HERE",
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

### 5. Bot Permissions

Make sure your bot has the following permissions:
- `Send Messages`
- `Connect` (Voice)
- `Speak` (Voice)
- `Use Voice Activity`
- `Embed Links`
- `Attach Files`
- `Read Message History`

### 6. Start Bot
```bash
python main.py
```

## ⚙️ Advanced Configuration

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

### Permissions
The bot has a built-in moderator system for administrative commands.

## 🔒 Public vs. Premium Version

### Public Version (This One)
- ✅ Complete music functionality
- ✅ Basic meme & NSFW support
- ✅ SFW anime content
- ❌ Advanced NSFW features
- ❌ Premium API integration

### Premium Features (API Keys Required)
- **Rule34 API Integration** - Advanced NSFW features
  - 🔗 **API available at:** https://api.rule34.xxx
  - Enables unlimited tag search and advanced NSFW commands
  - Access to extended character search functions
- **Extended Character Search** - Detailed anime character search
- **Video Content APIs** - Additional video sources
- **Unlimited Tag Search** - Without rate limits

### 🔑 API Setup for Premium Features

To use the advanced NSFW features, add the following configuration to your `config.json`:

```json
{
    "bot_token": "YOUR_BOT_TOKEN",
    "rule34_api": {
        "enabled": true,
        "base_url": "https://api.rule34.xxx"
    },
    "meme_settings": {
        "auto_meme": false
    }
}
```

**Note:** The Rule34 API may require registration or API keys depending on usage.

## 🐛 Troubleshooting

### Music Not Working
1. **FFmpeg installed?**
   ```bash
   ffmpeg -version
   ```

2. **Opus Library Error:**
   - macOS: `brew install opus`
   - Linux: `sudo apt install libopus0`
   - Windows: Opus should come with FFmpeg

3. **Bot can't join voice channel:**
   - Check bot permissions
   - Make sure you're in a voice channel

### Bot Won't Start
1. **Token correct?** Check `config.json`
2. **Dependencies installed?** `pip install -r requirements.txt`
3. **Python version?** Minimum Python 3.8

### NSFW Commands Not Working
1. **Channel is NSFW?** Enable NSFW in channel settings
2. **Bot permissions?** `Embed Links` required

## 🤝 Contributing & Support

- **GitHub:** https://github.com/MSCgameplayer/Simple_discord_bot
- **Issues:** Report bugs via GitHub Issues
- **Developer:** MSCgameplayer
- **AI Assistant:** GitHub Copilot

## 📜 License & Attribution

This project is licensed under the MIT License. See LICENSE file for details.

### 🙏 **If you use this bot as a base:**
**Please give credits to the original developer!** This means:

1. **Reference this project** in your README or documentation
2. **Mention MSCgameplayer** as the original developer  
3. **Link back** to this repository

**Example Attribution:**
```markdown
## Credits
Based on Simple Discord Bot by MSCgameplayer
Original Project: https://github.com/MSCgameplayer/Simple_discord_bot
```

**Why Credits Matter:**
This project represents significant development work. Attribution supports the 
original developer and helps others find the source project for updates.

## 🙏 Credits

- **Developed by:** MSCgameplayer
- **AI Support:** GitHub Copilot
- **APIs:** Reddit, Nekos.life, Safebooru
- **Libraries:** discord.py, yt-dlp, aiohttp

---

**⚠️ Note:** This is the public version without API keys. For advanced features, you need your own API keys.

## 🌐 Language Versions

- **🇩🇪 German:** [README.md](README.md) (Original)
- **🇺🇸 English:** [README_EN.md](README_EN.md) (This file)