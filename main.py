import asyncio
import os
import json
from twitchio.ext import commands

TWITCH_CLIENT_ID = 'p063h8nr6c7i7w8zcn96489x6e26pv'
TWITCH_ACCESS_TOKEN = os.environ['token']
BROADCASTER_ID = os.environ['id']
CHANNEL_VIEW = os.environ['channel_suspect']
MEDIA_name = os.environ['MEDIA_name']

DB_PATH = 'db.json'

def save_clip_data(data):
    with open(DB_PATH, 'w') as f:
        json.dump({"pending_clip": data}, f, indent=4)

class Bot(commands.Bot):

    def __init__(self):
        super().__init__(token=TWITCH_ACCESS_TOKEN, prefix='!', initial_channels=[CHANNEL_VIEW])

    async def event_ready(self):
        print(f'✅ Twitch-бот запущен как {self.nick}')

    async def event_message(self, message):
        if message.echo or message.author is None:
            return
        await self.handle_commands(message)

    @commands.command(name='report')
    async def report(self, ctx: commands.Context):
        content = ctx.message.content.strip()
        if not content:
            await ctx.reply("Ошибка: пустое сообщение.")
            return

        parts_full = content.split(' ', 1)
        if len(parts_full) < 2:
            await ctx.reply("Неверный формат. Используй: !report ид причина")
            return

        args_str = parts_full[1]
        arg_parts = args_str.split(' ', 1)

        if len(arg_parts) < 2:
            await ctx.reply(" blemb6Cop = Ничего не произошло = blemb6Cop")
            return

        form_id, reason = arg_parts[0], arg_parts[1]
        clip_url = await self.create_clip()
        if not clip_url:
            await ctx.reply("❌ Ошибка при создании клипа.")
            return

        await ctx.reply("blemb6Cop")

        save_clip_data({
            "form_id": form_id,
            "reason": reason,
            "author": ctx.author.name,
            "clip_url": clip_url
        })
        print("🎬 Клип сохранён для отправки в Discord.")

    async def create_clip(self):
        import requests
        url = "https://api.twitch.tv/helix/clips"
        headers = {
            "Client-ID": TWITCH_CLIENT_ID,
            "Authorization": f"Bearer {TWITCH_ACCESS_TOKEN}"
        }
        data = {
            "broadcaster_id": BROADCASTER_ID,
            "has_delay": True
        }
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            clip_data = response.json().get("data", [])
            if clip_data and "id" in clip_data[0]:
                clip_id = clip_data[0]["id"]
                await asyncio.sleep(10)
                return f"https://clips.twitch.tv/{clip_id}"
        except Exception as e:
            print(f"Ошибка при создании клипа: {e}")
        return None

if __name__ == '__main__':
    bot = Bot()
    bot.run()
