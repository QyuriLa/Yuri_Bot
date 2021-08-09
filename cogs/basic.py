import time
import random
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

    @commands.command(name='말해줘')
    async def speak(self, ctx, *content):
        """대신 말해드립니다"""
        if not content:
            return
        await ctx.message.delete()

        # 스포일러(||) 보존
        content_ = ' '.join(content)
        if content_.count('||') % 2 == 1:
            idx = content_.rfind('||')
            if idx != -1:
                content_ = content_[:idx] + '\\||' + content_[idx+2:]

        await ctx.send(content_ + ' || by '+ctx.author.mention+'||')

    @commands.command(name='골라줘')
    async def choose(self, ctx, *args):
        """골라드립니다"""
        if not args:
            return

        # TODO 단어 종성에 따라 후치사 결정
        await ctx.send(f'음... **{random.choice(args)}** 쪽이 좋지 않아?')

    @commands.command(name='지워줘')
    async def delete(self, ctx, num=1):
        """싹 지워드립니다"""
        async for message in ctx.channel.history(
                limit=num, before=ctx.message.created_at):
            await message.delete()


def setup(bot):
    bot.add_cog(BasicCommands(bot))
