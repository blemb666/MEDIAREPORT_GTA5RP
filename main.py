import os
import asyncio
from twitchio.ext import commands
import discord
from discord.ext import commands as discord_commands

# Переменные окружения
MEDIA_name = os.getenv("MEDIA_name", "BotName")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_SUSPECT = os.getenv("channel_suspect", "unknown_server")

# Twitch Bot
class TwitchBot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=os.getenv("token"),
            prefix='!',
            initial_channels=[os.getenv("id")]
        )

    async def event_ready(self):
        print(f"Twitch Bot is ready | Logged in as {self.nick}")

    async def event_message(self, message):
        if message.author and message.author.name.lower() != self.nick.lower():
            await self.handle_commands(message)

    @commands.command(name="report")
    async def report(self, ctx: commands.Context):
        try:
            args = ctx.message.content.split(" ", 2)
            if len(args) < 3:
                await ctx.send(f"{ctx.author.name}, неверный формат. Используй !report <id> <reason>")
                return

            reported_id = args[1]
            reason = args[2]
            report_text = f"{ctx.author.name}\n{reported_id} - {reason}\n{CHANNEL_SUSPECT}"
            print("Получена жалоба:", report_text)

            # Discord: добавить жалобу в очередь
            discord_bot.report_queue.append({
                "title": f"Жалоба #{len(discord_bot.report_queue) + 1}",
                "description": report_text
            })

            await ctx.send(f"{ctx.author.name}, жалоба отправлена!")

        except Exception as e:
            print("Ошибка в команде report:", e)
            await ctx.send("Произошла ошибка при отправке жалобы.")

# Discord Bot
intents = discord.Intents.default()
intents.message_content = True

discord_bot = discord_commands.Bot(command_prefix="!", intents=intents)
discord_bot.report_queue = []

@discord_bot.event
async def on_ready():
    print(f"Discord Bot is ready | Logged in as {discord_bot.user}")
    await discord_bot.change_presence(activity=discord.Game(name=MEDIA_name))
    # Периодическая отправка отчетов
    discord_bot.loop.create_task(send_daily_reports())

async def send_daily_reports():
    await discord_bot.wait_until_ready()
    while not discord_bot.is_closed():
        if discord_bot.report_queue:
            channel = discord.utils.get(discord_bot.get_all_channels(), name="reports")
            if channel:
                for report in discord_bot.report_queue:
                    embed = discord.Embed(
                        title=report["title"],
                        description=report["description"],
                        color=discord.Color.red()
                    )
                    await channel.send(embed=embed)
                discord_bot.report_queue.clear()
        await asyncio.sleep(86400)  # раз в день

# Запуск
async def main():
    await asyncio.gather(
        discord_bot.start(DISCORD_TOKEN),
        TwitchBot().start()
    )

if __name__ == "__main__":
    asyncio.run(main())
