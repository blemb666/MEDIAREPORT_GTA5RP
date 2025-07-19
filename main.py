import os
import json
import asyncio
from datetime import datetime, timezone
import discord
from discord.ext import commands
from twitchio.ext import commands as twitch_commands

# ENV
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
TWITCH_TOKEN = os.environ['token']
TWITCH_CLIENT_ID = 'p063h8nr6c7i7w8zcn96489x6e26pv'
BROADCASTER_ID = os.environ['id']
CHANNEL_VIEW = os.environ['channel_suspect']

role_id_raw = os.environ.get('role_id')
import re
def extract_role_id(role_str):
    match = re.search(r'\d+', role_str)
    return int(match.group()) if match else None
role_id_int = extract_role_id(role_id_raw) if role_id_raw else None

intents = discord.Intents.default()
intents.message_content = True

# Discord bot
discord_bot = commands.Bot(command_prefix='/', intents=intents)

# Twitch bot
class TwitchBot(twitch_commands.Bot):
    def __init__(self):
        super().__init__(
            token=TWITCH_TOKEN,
            prefix='!',
            initial_channels=[CHANNEL_VIEW]
        )

    async def event_ready(self):
        print(f"Twitch Bot ready as {self.nick}")

    async def event_message(self, message):
        if message.echo or message.author is None:
            return
        await self.handle_commands(message)

    @twitch_commands.command(name='report')
    async def report(self, ctx: twitch_commands.Context):
        # Формат: !report <id> <причина>
        parts = ctx.message.content.strip().split(' ', 2)
        if len(parts) < 3:
            await ctx.reply("Используй: !report <id> <причина>")
            return
        form_id = parts[1]
        reason = parts[2]

        clip_url = await self.create_clip()
        if not clip_url:
            await ctx.reply("Ошибка создания клипа.")
            return

        await ctx.reply("Жалоба принята!")

        # Отправляем в Discord (через функцию)
        await send_report_to_discord(form_id, reason, clip_url, ctx.author.name)

    async def create_clip(self):
        import requests
        url = "https://api.twitch.tv/helix/clips"
        headers = {
            "Client-ID": TWITCH_CLIENT_ID,
            "Authorization": f"Bearer {TWITCH_TOKEN}"
        }
        data = {
            "broadcaster_id": BROADCASTER_ID,
            "has_delay": True
        }
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 202:
                await asyncio.sleep(10)
                clip_id = response.json().get("data", [{}])[0].get("id")
                if clip_id:
                    return f"https://clips.twitch.tv/{clip_id}"
            else:
                print(f"Clip create error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Exception creating clip: {e}")
        return None

twitch_bot = TwitchBot()

# ---- Общая база для жалоб ----
DB_FILE = "db.json"

def load_db():
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return {
            "complaints": [],
            "media_name": os.environ.get('MEDIA_name', 'DefaultMedia'),
            "last_reset_date": None
        }

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

db = load_db()

logs_channel_id = None

# --- Функция отправки жалобы в Discord ---
async def send_report_to_discord(form_id, reason, clip_url, author_name):
    global db, logs_channel_id

    # Сбросить счётчик если дата изменилась (UTC)
    today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    if db.get("last_reset_date") != today_str:
        db["complaints"] = []
        db["last_reset_date"] = today_str
        save_db(db)

    db["complaints"].append({
        "form_id": form_id,
        "reason": reason,
        "clip_url": clip_url,
        "author": author_name
    })
    save_db(db)

    number = len(db["complaints"])
    media_name = db.get("media_name", "DefaultMedia")

    embed = discord.Embed(
        title=f"Жалоба #{number} - {media_name}",
        description=f"**ID:** {form_id}\n**Причина:** {reason}\n**Клип:** [Ссылка]({clip_url})\n**Автор:** {author_name}",
        color=0xFF0000
    )
    if logs_channel_id:
        channel = discord_bot.get_channel(logs_channel_id)
        if channel:
            await channel.send(embed=embed)
        else:
            print("Канал для логов не найден")
    else:
        print("Канал для логов не установлен")

# --- Discord команды ---

@discord_bot.command()
@commands.has_role(role_id_int)
async def nickname(ctx, *, new_name: str):
    db["media_name"] = new_name
    save_db(db)
    await ctx.send(f"MEDIA_name изменено на: **{new_name}**")

@discord_bot.command()
@commands.has_role(role_id_int)
async def channel_logs(ctx, channel: discord.TextChannel):
    global logs_channel_id
    logs_channel_id = channel.id
    await ctx.send(f"Канал для логов установлен: {channel.mention}")

# Запуск двух ботов
async def main():
    await asyncio.gather(
        discord_bot.start(DISCORD_TOKEN),
        twitch_bot.start()
    )

if __name__ == '__main__':
    asyncio.run(main())
