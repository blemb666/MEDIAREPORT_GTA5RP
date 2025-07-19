import os
import asyncio
from twitchio.ext import commands as twitch_commands
import discord
from discord.ext import commands as discord_commands

# Переменные окружения
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
ROLE_ID = os.getenv("role_id", None)
MEDIA_name = os.getenv("MEDIA_name", "MediaReport")

# Twitch бот
class TwitchBot(twitch_commands.Bot):
    def __init__(self):
        super().__init__(
            token=os.getenv("token"),
            prefix="!",
            initial_channels=[os.getenv("id")]
        )

    async def event_ready(self):
        print(f"Twitch Bot готов! Logged in as | {self.nick}")

    @twitch_commands.command(name="clip")
    async def clip(self, ctx):
        await ctx.send(f"Клип от {ctx.author.name}")

# Discord бот
intents = discord.Intents.default()
intents.message_content = True
bot = discord_commands.Bot(command_prefix="!", intents=intents)

# Сброс жалоб каждый день в 00:00 по серверному времени (пример)
complaint_count = 0

@bot.event
async def on_ready():
    print(f"Discord Bot готов! Logged in as | {bot.user}")

@bot.command()
@discord_commands.has_role(int(ROLE_ID) if ROLE_ID and ROLE_ID.isdigit() else 0)
async def жалоба(ctx):
    global complaint_count
    complaint_count += 1
    embed = discord.Embed(
        title=f"Жалоба #{complaint_count} - {MEDIA_name}",
        description=f"Поступила жалоба от {ctx.author.mention}",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)

async def reset_complaint_count():
    global complaint_count
    while True:
        # Сбросить счетчик в полночь, простой вариант с таймером 24 часа
        await asyncio.sleep(24 * 3600)
        complaint_count = 0

async def main():
    twitch_bot = TwitchBot()
    await asyncio.gather(
        twitch_bot.start(),
        bot.start(DISCORD_TOKEN),
        reset_complaint_count()
    )

if __name__ == "__main__":
    asyncio.run(main())
