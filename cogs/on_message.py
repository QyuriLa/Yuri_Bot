import discord
from discord.ext import commands

from utils import default, pingpong


class OnMessage(commands.Cog):
    def __init__(self, bot):
        self.config = default.config()
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not isinstance(message.channel, discord.TextChannel):
            return

        await react_to_chito(message)

        if message.author.id in self.config["bot_whitelist"]:
            await listen_to_bot(message, self.bot)


async def react_to_chito(message):
    chito = ['치토', '치이짱', '치이쨩']
    for i in chito:
        if i in message.content:
            await message.add_reaction('❤')


async def listen_to_bot(message, bot):
    ctx = await bot.get_context(message)
    await bot.invoke(ctx)


def setup(bot):
    bot.add_cog(OnMessage(bot))
