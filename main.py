import os
import discord
from discord.ext import commands as discord_commands
from twitchio.ext import commands as twitch_commands

MEDIA_name = os.getenv("MEDIA_name", "Unknown Media")

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", 0))
TWITCH_TOKEN = os.getenv("token")
TWITCH_NICK = os.getenv("MEDIA_name")
TWITCH_CHANNEL = os.getenv("channel_suspect")
SERVER_NAME = os.getenv("server", "Solana")

# Discord bot setup
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

discord_bot = discord_commands.Bot(command_prefix="!", intents=intents)

@discord_bot.event
async def on_ready():
    print(f"[Discord] Logged in as {discord_bot.user} (ID: {discord_bot.user.id})")

# Twitch bot setup
class TwitchBot(twitch_commands.Bot):
    def __init__(self):
        super().__init__(
            token=TWITCH_TOKEN,
            prefix="!",
            initial_channels=[TWITCH_CHANNEL]
        )

    async def event_ready(self):
        print(f"[Twitch] Logged in as {self.nick}")

    async def event_message(self, message):
        if message.echo:
            return
        await self.handle_commands(message)

    @twitch_commands.command(name="report")
    async def report(self, ctx):
        try:
            args = ctx.message.content.split()
            if len(args) < 3:
                await ctx.send(f"❌ Использование: !report ID причина")
                return

            player_id = args[1]
            reason = " ".join(args[2:])
            nickname = ctx.author.name

            embed = discord.Embed(
                title=f"Жалоба #{player_id}",
                description=f"```{nickname}\n{player_id} - {reason}\n{SERVER_NAME}```",
                color=discord.Color.red()
            )

            channel = discord_bot.get_channel(DISCORD_CHANNEL_ID)
            if channel:
                await channel.send(embed=embed)
                await ctx.send("✅ Жалоба отправлена.")
            else:
                print("[Discord] Канал не найден.")

        except Exception as e:
            print(f"[Error] {e}")
            await ctx.send("❌ Произошла ошибка при отправке жалобы.")

# Запуск ботов
async def main():
    import asyncio
    await asyncio.gather(
        discord_bot.start(DISCORD_TOKEN),
        TwitchBot().start()
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
