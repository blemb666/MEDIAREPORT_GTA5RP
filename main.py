import os
import asyncio
from twitchio.ext import commands as twitch_commands
import discord
from discord.ext import commands as discord_commands
from datetime import datetime, timedelta

# Переменные окружения
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_GUILD_ID = int(os.getenv("DISCORD_GUILD_ID", 0))  # айди сервера для изменения никнейма
ROLE_ID = int(os.getenv("ROLE_ID", 0))  # айди роли для проверки доступа к команде жалобы
MEDIA_NAME = os.getenv("MEDIA_name", "MediaReport")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", 0))  # куда отправлять жалобы
TWITCH_TOKEN = os.getenv("token")
TWITCH_CHANNEL = os.getenv("id")  # канал для Twitch бота

# Discord intents — нужен для доступа к сообщениям и членам сервера
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Discord бот
discord_bot = discord_commands.Bot(command_prefix="!", intents=intents)

# Twitch бот
class TwitchBot(twitch_commands.Bot):
    def __init__(self):
        super().__init__(token=TWITCH_TOKEN, prefix="!", initial_channels=[TWITCH_CHANNEL])

    async def event_ready(self):
        print(f"Twitch Bot готов! Logged in as | {self.nick}")

    @twitch_commands.command(name="clip")
    async def clip(self, ctx):
        await ctx.send(f"Клип от {ctx.author.name} создан!")

# Для учета жалоб
complaint_count = 0
complaints_reset_time = datetime.utcnow() + timedelta(days=1)

@discord_bot.event
async def on_ready():
    print(f"Discord Bot готов! Logged in как {discord_bot.user}")

async def reset_complaints_daily():
    global complaint_count, complaints_reset_time
    while True:
        now = datetime.utcnow()
        if now >= complaints_reset_time:
            complaint_count = 0
            complaints_reset_time = now + timedelta(days=1)
            print("Счетчик жалоб сброшен")
        await asyncio.sleep(60)  # Проверяем каждую минуту

@discord_bot.command(name="жалоба")
@discord_commands.has_role(ROLE_ID)
async def complaint(ctx, *, text: str):
    global complaint_count
    complaint_count += 1

    guild = discord_bot.get_guild(DISCORD_GUILD_ID)
    if guild:
        member = guild.get_member(ctx.author.id)
        if member:
            try:
                # Добавляем карандаш (✏️) к нику, если его нет
                if not member.nick or "✏️" not in member.nick:
                    new_nick = f"{member.nick or member.name} ✏️"
                    await member.edit(nick=new_nick)
            except Exception as e:
                print(f"Ошибка при изменении ника: {e}")

    embed = discord.Embed(
        title=f"Жалоба #{complaint_count} - {MEDIA_NAME}",
        description=f"От: {ctx.author.mention}\n\n{text}",
        color=discord.Color.red(),
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text="MEDIAREPORT")
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

    channel = discord_bot.get_channel(DISCORD_CHANNEL_ID)
    if channel:
        await channel.send(embed=embed)
    else:
        await ctx.send("Ошибка: не найден канал для отправки жалоб.")

    await ctx.message.add_reaction("✅")  # Подтверждение жалобы

async def main():
    twitch_bot = TwitchBot()
    await asyncio.gather(
        twitch_bot.start(),
        discord_bot.start(DISCORD_TOKEN),
        reset_complaints_daily()
    )

if __name__ == "__main__":
    asyncio.run(main())
