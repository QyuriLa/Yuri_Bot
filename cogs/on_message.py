import random

import discord
from discord.ext import commands

from utils import default, pingpong


class OnMessage(commands.Cog):
    def __init__(self, bot):
        self.config = default.config()
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not isinstance(message.channel, discord.TextChannel):
            return

        await react_to_chito(message)

        if message.author.id in self.config["bot_whitelist"]:
            await listen_to_bot(message, self.bot)

        if message.channel.id in self.config["pingpong_channels"]:
            await pingpong_chat(message)

        if message.guild.id in self.config["dont_use_tq_guilds"]:
            await dont_use_tq(message)


async def react_to_chito(message):
    chito = ['치토', '치이짱', '치이쨩', '치짱', '치쨩']
    for i in chito:
        if i in message.content:
            await message.add_reaction('❤')


async def listen_to_bot(message, bot):
    ctx = await bot.get_context(message)
    await bot.invoke(ctx)


async def pingpong_chat(message):
    if message.author.bot:
        return
    for escape in ('!', '유리! '):
        if message.content.startswith(escape):
            return
    if not message.content:
        return

    session_id = message.channel.id  # TODO - ID 재설정 명령어
    await message.channel.trigger_typing()

    response = pingpong.request(message.content, session_id)
    for reply in response:
        content = None
        if reply['type'] == 'text':
            content = reply['text']
        elif reply['type'] == 'image':
            content = reply['image']['url']
        await message.channel.send(content if content else '⚠')


async def dont_use_tq(message):
    if message.content == 'ㅅㅂ' and random.random() < 0.5:
        await message.channel.send(
            file=discord.File('data/dont_use_tq.png', 'tq.png'),
            reference=message
        )


def setup(bot):
    bot.add_cog(OnMessage(bot))
