import asyncio
import requests
from twitchio.ext import commands
import os

# Your existing setup code
TWITCH_CLIENT_ID = 'p063h8nr6c7i7w8zcn96489x6e26pv'
TWITCH_ACCESS_TOKEN = os.environ['token']
BROADCASTER_ID = os.environ['id']
DISCORD_WEBHOOK_URL = os.environ['webhook_discord']
CHANNEL_VIEW = os.environ['channel_suspect']
MEDIA_name = os.environ['MEDIA_name']
static_member = "<@244135967378767872> <#690851125511061515>"
rainbow = "<@&697172798845485137> <@&697172317872324648>"

class Bot(commands.Bot):

    def __init__(self):
        super().__init__(
            token=TWITCH_ACCESS_TOKEN,
            client_id=TWITCH_CLIENT_ID,
            client_secret=os.environ['client_secret'],  # новый параметр
            bot_id=os.environ['bot_id'],                # новый параметр
            prefix='!',
            initial_channels=[CHANNEL_VIEW]
        )

    async def event_ready(self):
        print(f'✅ Бот запущен как {self._user.name}')
        print(f'Watching channel: {CHANNEL_VIEW}')

    async def event_message(self, message):
        # Ignore messages sent by the bot itself
        if message.echo:
            return

        # Crucial: Check if message.author is None
        # This prevents the AttributeError for messages without a valid author.
        if message.author is None:
            print(f"Received a message with no identifiable author: {message.content}")
            return

        # Proceed to handle commands only if there's a valid author
        await self.handle_commands(message)

    @commands.command(name='report')
    async def form(self, ctx: commands.Context):
        content = ctx.message.content.strip() # Use .strip() to remove leading/trailing whitespace
        if not content:
            await ctx.reply("Ошибка: пустое сообщение.")
            return

        # Only split once by space to correctly capture the reason
        # Example: !report id,id,id reason for report
        # We need to find the first space after the command and then the first space after the IDs.
        # Let's refine the parsing to be more robust.

        # Find the first space to get the command part, then the rest of the message
        parts_full = content.split(' ', 1)
        if len(parts_full) < 2: # Check if there's anything after '!report'
            await ctx.reply("Неверный формат. Используй: !report {id,id,id} {reason}")
            return

        # Now, split the remaining part to separate IDs from the reason
        args_str = parts_full[1] # This is "{id,id,id} {reason}"
        arg_parts = args_str.split(' ', 1) # Split into ID part and reason part

        if len(arg_parts) < 2:
            await ctx.reply(" blemb6Cop = Ничего не произошло = blemb6Cop")
            return

        form_id = arg_parts[0] # This is "{id,id,id}"
        reason = arg_parts[1]  # This is "{reason}"

        print(f"Command received from {ctx.author.name}: {ctx.message.content}")

        clip_url = await self.create_clip()
        if not clip_url:
            await ctx.reply("❌ Ошибка при создании клипа.")
            return

        await ctx.reply("blemb6Cop")
        print(f"Clip URL: {clip_url}")

        messageby = f"-# message by {ctx.author.mention}"
        discord_content = f"{static_member}\n```{MEDIA_name}\n{form_id} - {reason}\n{clip_url}\n{rainbow}```\n{messageby}"

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
            "has_delay": True # Request a clip with a short delay for better chance of creation
        }

        try:
            response = requests.post(url, headers=headers, json=data) # Use json=data for dict
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

            if response.status_code == 202:
                clip_data = response.json().get("data", [])
                if clip_data and "id" in clip_data[0]:
                    clip_id = clip_data[0]["id"]
                    # Give Twitch a bit more time to process the clip, maybe 10-15 seconds
                    await asyncio.sleep(10)
                    return f"https://clips.twitch.tv/{clip_id}"
            else:
                print(f"Ошибка создания клипа (HTTP {response.status_code}): {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Network or API error when creating clip: {e}")
        except Exception as e:
            print(f"Unexpected error when creating clip: {e}")

        return None

# Запуск бота
bot = Bot()
bot.run()
