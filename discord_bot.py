import discord
from discord.ext import commands, tasks
import json
import os

DB_PATH = 'db.json'
ADMIN_ROLE_ID = 1373048899278995496
MEDIA_name = os.environ.get("MEDIA_name", "Solana Fliper")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

def load_db():
    if not os.path.exists(DB_PATH):
        return {}
    with open(DB_PATH, 'r') as f:
        return json.load(f)

def save_db(data):
    with open(DB_PATH, 'w') as f:
        json.dump(data, f, indent=4)

@bot.event
async def on_ready():
    await bot.tree.sync()
    check_for_clip.start()
    print(f"✅ Discord бот запущен как {bot.user}")

@tasks.loop(seconds=5)
async def check_for_clip():
    data = load_db()
    clip = data.get("pending_clip")
    if not clip:
        return

    form_id = clip["form_id"]
    reason = clip["reason"]
    author = clip["author"]
    clip_url = clip["clip_url"]

    guild = bot.guilds[0]
    log_channel = None
    for ch in guild.text_channels:
        if ch.permissions_for(guild.me).send_messages:
            log_channel = ch
            break

    if log_channel:
        msg = await log_channel.send(
            f"```{MEDIA_name}
{form_id} - {reason}
{clip_url}```
📨 by {author}"
        )
        await msg.add_reaction("✏️")
        data["last_msg_id"] = msg.id
        data["last_msg_channel"] = log_channel.id
        data.pop("pending_clip", None)
        save_db(data)

@bot.event
async def on_raw_reaction_add(payload):
    if str(payload.emoji) != "✏️" or payload.user_id == bot.user.id:
        return

    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    if not member or ADMIN_ROLE_ID not in [r.id for r in member.roles]:
        return

    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)

    def check(m):
        return m.author.id == payload.user_id and m.channel.id == payload.channel_id

    await channel.send(f"{member.mention}, введи новое описание:")

    try:
        msg = await bot.wait_for("message", timeout=60.0, check=check)
        lines = message.content.splitlines()
        if len(lines) >= 2:
            header = lines[0].strip("`")
            form_id = lines[1].split(" - ")[0]
            new_reason = msg.content
            clip_url = lines[2]
            updated = f"```{header}
{form_id} - {new_reason}
{clip_url}```
📨 by {member.name}"
            await message.edit(content=updated)
            await channel.send("✅ Обновлено.")
    except:
        await channel.send("⏰ Время на редактирование истекло.")

@bot.tree.command(name="nickname", description="Изменить MEDIA_name")
async def nickname(interaction: discord.Interaction, name: str):
    if ADMIN_ROLE_ID not in [r.id for r in interaction.user.roles]:
        await interaction.response.send_message("⛔ Нет доступа", ephemeral=True)
        return
    save_db({"MEDIA_name": name})
    await interaction.response.send_message(f"✅ MEDIA_name изменено на: {name}", ephemeral=True)

bot.run(os.environ["discord_token"])
