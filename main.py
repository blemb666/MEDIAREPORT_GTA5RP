import os
import asyncio
from twitchio.ext import commands
import discord
from discord import Intents, Embed

# Twitch config
TWITCH_TOKEN = os.getenv("token")
CHANNEL_NAME = os.getenv("channel_suspect")

# Discord config
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("id"))
SERVER_NAME = os.getenv("server_name", "GTA5RP")

MEDIA_NAME = os.getenv("MEDIA_name", "Unknown")

# Discord bot client
discord_client = discord.Client(intents=Intents.default())

# Twitch bot
class Bot(commands.Bot):
    def __init__(self):
        super().__init__(token=TWITCH_TOKEN, prefix="!", initial_channels=[CHANNEL_NAME])

    async def event_ready(self):
        print(f"Twitch bot connected as {self.nick}")

    async def event_message(self, message):
        await self.handle_commands(message)

    @commands.command(name="report")
    async def report(self, ctx):
        try:
            parts = ctx.message.content.split(maxsplit=2)
            if len(parts) < 3:
                await ctx.send("⚠️ Использование: !report {ID} {Причина}")
                return

            report_id = parts[1]
            reason = parts[2]

            content = f"{MEDIA_NAME}\n{report_id} - {reason}\n{SERVER_NAME}"
            await send_report_to_discord(content)

            await ctx.send(f"📩 Жалоба на {report_id} отправлена.")
        except Exception as e:
            await ctx.send("❌ Ошибка при отправке жалобы.")
            print("Error:", e)

# Discord report sender
async def send_report_to_discord(content):
    await discord_client.wait_until_ready()
    channel = discord_client.get_channel(DISCORD_CHANNEL_ID)
    if channel:
        embed = Embed(title=f"Жалоба", description=content, color=0xff0000)
        await channel.send(embed=embed)
    else:
        print("❌ Канал Discord не найден")

async def main():
    twitch_bot = Bot()

    await asyncio.gather(
        discord_client.start(DISCORD_TOKEN),
        twitch_bot.start()
    )

if __name__ == "__main__":
    asyncio.run(main())
