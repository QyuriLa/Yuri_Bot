import os
import logging

import discord
from discord.ext import commands
from dotenv import load_dotenv


# Bot kwargs 초기화
bot = commands.Bot(
    command_prefix='유리! ',
    description='하나 둘 셋에 정말좋아요',
    owner_id=226671028460322818,
    allowed_mentions=discord.AllowedMentions(
        everyone=False, users=True, roles=False, replied_user=True
    ),
    intents=discord.Intents.all()
)

# 로그 Setup
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w'
)
handler.setFormatter(
    logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
)
logger.addHandler(handler)

# Cogs 로드
load_dotenv()
for file in os.listdir("cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")

# Token 로드 및 봇 실행
TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)
