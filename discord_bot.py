import discord
from discord import app_commands
from discord.ext import commands
import json
import os

DB_PATH = 'db.json'
ADMIN_ROLE_ID = 1373048899278995496

def load_db():
    if not os.path.exists(DB_PATH):
        return {}
    with open(DB_PATH, 'r') as f:
        return json.load(f)

def save_db(data):
    with open(DB_PATH, 'w') as f:
        json.dump(data, f, indent=4)

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Discord бот запущен как {bot.user}")

@bot.tree.command(name="nickname", description="Изменить MEDIA_name")
@app_commands.checks.has_role(ADMIN_ROLE_ID)
@app_commands.describe(name="Новое имя для MEDIA_name")
async def nickname(interaction: discord.Interaction, name: str):
    db = load_db()
    db["MEDIA_name"] = name
    save_db(db)
    await interaction.response.send_message(f"✅ MEDIA_name изменено на: `{name}`", ephemeral=True)

@bot.tree.command(name="channel_logs", description="Установить лог-канал для сообщений с Twitch")
@app_commands.checks.has_role(ADMIN_ROLE_ID)
@app_commands.describe(channel="Канал для логов")
async def channel_logs(interaction: discord.Interaction, channel: discord.TextChannel):
    db = load_db()
    db["log_channel_id"] = channel.id
    save_db(db)
    await interaction.response.send_message(f"📋 Канал логов установлен: {channel.mention}", ephemeral=True)

@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if str(payload.emoji) == "✏️" and payload.member and ADMIN_ROLE_ID in [role.id for role in payload.member.roles]:
        channel = bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        def check(m):
            return m.author.id == payload.user_id and m.channel.id == payload.channel_id

        await channel.send(f"{payload.member.mention}, отправь новое описание (reason):")

        try:
            msg = await bot.wait_for("message", timeout=60.0, check=check)
            updated_content = message.content.replace("```", "").split("\n")
            updated_content[2] = f"{updated_content[2].split(' - ')[0]} - {msg.content}"
            new_message = f"```{chr(10).join(updated_content)}```"
            await message.edit(content=new_message)
        except asyncio.TimeoutError:
            await channel.send("⏰ Время на редактирование истекло.")

bot.run(os.environ["discord_token"])
