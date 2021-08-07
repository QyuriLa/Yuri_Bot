import discord
from discord.ext import commands

from utils import default
from bot import bot as bot_


class OnMessage(commands.Cog):
    def __init__(self, bot):
        self.config = default.config()

    @commands.Cog.listener()
    async def on_message(self, message):
        await react_to_chito(message)
        await listen_to_bot(message, self.config)


async def react_to_chito(message):
    chito = ['치토', '치이짱', '치이쨩']
    for i in chito:
        if i in message.content:
            await message.add_reaction('❤')


async def listen_to_bot(message, config):
    bot_whitelist = config["bot_whitelist"]
    if message.author.id in bot_whitelist:
        ctx = await bot_.get_context(message)
        await bot_.invoke(ctx)


def setup(bot):
    bot.add_cog(OnMessage(bot))
