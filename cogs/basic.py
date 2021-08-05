import time

import discord
from discord.ext import commands


class BasicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='샤를')
    async def charles(self, ctx):
        """보이지않아짐"""
        msg = await ctx.send('보이지않아')
        for i in range(3, 8):
            time.sleep(0.2)
            content = '||보이지않아'
            await msg.edit(content=content[:i]+'||'+content[i:])

def setup(bot):
    bot.add_cog(BasicCommands(bot))