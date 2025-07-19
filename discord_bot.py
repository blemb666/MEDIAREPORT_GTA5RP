import discord
from discord.ext import commands
import json
import os

MEDIA_name = os.environ.get('MEDIA_name', 'DefaultMedia')
role_id = os.environ.get('role_id', None)
logs_channel_id = None  # Устанавливается командой /channel_logs

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix='/', intents=intents)

db_path = 'db.json'

def load_db():
    try:
        with open(db_path, 'r') as f:
            return json.load(f)
    except Exception:
        return {"clips": [], "MEDIA_name": MEDIA_name}

def save_db(data):
    with open(db_path, 'w') as f:
        json.dump(data, f, indent=4)

db = load_db()

@bot.event
async def on_ready():
    print(f'✅ Discord бот запущен как {bot.user}')

@bot.command()
@commands.has_role(int(role_id) if role_id else 0)
async def nickname(ctx, *, new_name: str):
    db["MEDIA_name"] = new_name
    save_db(db)
    await ctx.send(f"MEDIA_name изменено на: **{new_name}**")

@bot.command()
@commands.has_role(int(role_id) if role_id else 0)
async def channel_logs(ctx, channel: discord.TextChannel):
    global logs_channel_id
    logs_channel_id = channel.id
    await ctx.send(f"Канал для логов установлен: {channel.mention}")

@bot.event
async def on_message(message):
    await bot.process_commands(message)

@bot.event
async def on_raw_reaction_add(payload):
    if payload.emoji.name != '✏️':
        return

    if payload.user_id == bot.user.id:
        return

    if not logs_channel_id:
        return

    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    if message.author != bot.user:
        return

    # Логика редактирования причины клипа
    def check(m):
        return m.author.id == payload.user_id and m.channel.id == channel.id

    await channel.send(f"<@{payload.user_id}>, напишите новую причину:")

    try:
        reply = await bot.wait_for('message', timeout=60.0, check=check)
    except:
        await channel.send("Время на ввод истекло.")
        return

    content = reply.content.strip()

    # Обновляем clip reason в базе по ID, предполагается что ID есть в сообщении
    # Пример парсинга (надо под твой формат)

    # Для простоты заменим всю причину на новую в сообщении
    new_content = message.content.split('\n')
    # Предположим, что вторая строка с формой: form_id - reason
    if len(new_content) > 1 and '-' in new_content[1]:
        form_id = new_content[1].split('-')[0].strip()
        new_content[1] = f"{form_id} - {content}"

        new_message = "\n".join(new_content)
        await message.edit(content=new_message)
        await channel.send(f"Причина обновлена на: {content}")
    else:
        await channel.send("Не удалось найти строку с причиной для редактирования.")

bot.run(os.environ['DISCORD_TOKEN'])
