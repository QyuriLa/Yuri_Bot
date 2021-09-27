import os

import discord
from discord.ext import commands

from utils import default


class DevelopCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    async def refresh_config(self, ctx: commands.Context):
        if not await ctx.bot.is_owner(ctx.author):
            await ctx.message.delete()
            return await ctx.send('그건 관리자 전용 명령어야!', delete_after=5)

        os.remove('data/config.hjson')
        default.config()
        await ctx.send('config 새로고침 완료!')


def setup(bot):
    bot.add_cog(DevelopCommands(bot))
