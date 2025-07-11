import asyncio
import requests
from twitchio.ext import commands
import os

# Переменные среды
TWITCH_CLIENT_ID = 'p063h8nr6c7i7w8zcn96489x6e26pv'
TWITCH_ACCESS_TOKEN = os.environ['token']
BROADCASTER_ID = os.environ['id']
DISCORD_WEBHOOK_URL = os.environ['webhook_discord']
CHANNEL_VIEW = os.environ['channel_suspect']
MEDIA_name = os.environ['MEDIA_name']
static_member = "<@244135967378767872> <#690851125511061515>"
rainbow = "<@&697172798845485137> <@&697172317872324648>"
hawick = "<@&1182947880168861727> <@&1182732063221231616>"

class Bot(commands.Bot):

    def __init__(self):
        super().__init__(
            token=TWITCH_ACCESS_TOKEN,
            prefix='!',
            initial_channels=[CHANNEL_VIEW]
        )

    async def event_ready(self):
        print(f'✅ Бот запущен как {self.nick}')
        print(f'Watching channel: {CHANNEL_VIEW}')

    async def event_message(self, message):
        if message.echo or message.author is None:
            return
        await self.handle_commands(message)

    @commands.command(name='report')
    async def form(self, ctx: commands.Context):
        content = ctx.message.content.strip()
        if not content:
            await ctx.reply("Ошибка: пустое сообщение.")
            return

        parts_full = content.split(' ', 1)
        if len(parts_full) < 2:
            await ctx.reply("Неверный формат. Используй: !report {id,id,id} {reason}")
            return

        args_str = parts_full[1]
        arg_parts = args_str.split(' ', 1)

        if len(arg_parts) < 2:
            await ctx.reply(" blemb6Cop = Ничего не произошло = blemb6Cop")
            return

        form_id = arg_parts[0]
        reason = arg_parts[1]

        print(f"Command received from {ctx.author.name}: {ctx.message.content}")

        clip_url = await self.create_clip()
        if not clip_url:
            await ctx.reply("❌ Ошибка при создании клипа.")
            return

        await ctx.reply("blemb6Cop")
        print(f"Clip URL: {clip_url}")

        messageby = f"-# message by {ctx.author.mention}"
        discord_content = f"{static_member}\n```{MEDIA_name}\n{form_id} - {reason}\n{clip_url}\n{hawick}```\n{messageby}"

        try:
            requests.post(DISCORD_WEBHOOK_URL, json={"content": discord_content})
            print("Successfully sent webhook to Discord.")
        except Exception as e:
            print(f"Ошибка отправки в Discord: {e}")

    async def create_clip(self):
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

            if response.status_code == 202:
                clip_data = response.json().get("data", [])
                if clip_data and "id" in clip_data[0]:
                    clip_id = clip_data[0]["id"]
                    await asyncio.sleep(10)
                    return f"https://clips.twitch.tv/{clip_id}"
            else:
                print(f"Ошибка создания клипа (HTTP {response.status_code}): {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Network or API error when creating clip: {e}")
        except Exception as e:
            print(f"Unexpected error when creating clip: {e}")

        return None

# Запуск
if __name__ == '__main__':
    bot = Bot()
    bot.run()
