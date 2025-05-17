import asyncio
import requests
from twitchio.ext import commands
import os
# By Sobyanin
# Sebastayn Suleimanov

# 👉 Настройки (замени на свои данные)
TWITCH_CLIENT_ID = 'p063h8nr6c7i7w8zcn96489x6e26pv' # Бот dev.twitch
TWITCH_ACCESS_TOKEN = os.environ['token']  # token twitch 
BROADCASTER_ID = os.environ['id']     # ID twitch
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1373030292209664030/dcqLOg8MCQpNlS2o6OiLjt9FffXpGSCPc0zj2T5Hq2EPcSdAIKz0sGGqywuKGxXSf3ua'
CHANNEL_VIEW = os.environ['channel_suspect']

class Bot(commands.Bot):

    def __init__(self):
        super().__init__(
            token=TWITCH_ACCESS_TOKEN,
            client_id=TWITCH_CLIENT_ID,
            prefix='!',
            initial_channels=[channel_view]  # без #
        )

    async def event_ready(self):
        print(f'✅ Бот запущен как {self.nick}')

    # async def event_message(self, message):
    #     await self.handle_commands(message)

    @commands.command(name='report')
    async def form(self, ctx: commands.Context):
        content = ctx.message.content
        if not content:
            await ctx.reply("Ошибка: пустое сообщение.")
            return

        parts = content.split(' ', 2)
        if len(parts) < 3:
            await ctx.reply("Неверный формат. Используй: !report {id,id,id} {reason}")
            return

        form_id = parts[1]
        reason = parts[2]

        clip_url = await self.create_clip()
        if not clip_url:
            await ctx.reply("❌ Ошибка при создании клипа.")
            return

        # Отправка сообщения в Twitch
        await ctx.reply("Жалоба зарегистрирована.")

        # Подготовка текста для Discord
        MEDIA_name = os.environ['MEDIA_name']
        discord_content = f"<@244135967378767872>\n```{MEDIA_name}\n{form_id}\n{reason}\n{clip_url}\n<@&697172798845485137> <@&697172317872324648>```"

        # Отправка Webhook
        try:
            requests.post(DISCORD_WEBHOOK_URL, json={"content": discord_content})
        except Exception as e:
            print("Ошибка отправки в Discord:", e)

    async def create_clip(self):
        url = "https://api.twitch.tv/helix/clips"
        headers = {
            "Client-ID": TWITCH_CLIENT_ID,
            "Authorization": f"Bearer {TWITCH_ACCESS_TOKEN}"
        }
        data = {
            "broadcaster_id": BROADCASTER_ID
        }

        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 202:
            clip_data = response.json().get("data", [])
            if clip_data and "id" in clip_data[0]:
                clip_id = clip_data[0]["id"]
                await asyncio.sleep(5)  # подождать, пока клип создастся
                return f"https://clips.twitch.tv/{clip_id}"

        print("Ошибка создания клипа:", response.text)
        return None

# 🔁 Запуск
bot = Bot()
bot.run()
