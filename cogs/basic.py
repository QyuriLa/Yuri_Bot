import asyncio
import random
import re

import discord
from discord.ext import commands

from utils import default


class BasicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.config()

    @commands.command(name='샤를')
    async def charles(self, ctx, *, arg='보이지않아'):
        """보이지않아짐"""
        valid_emojis = []
        pattern = re.compile(r'(<a?:\w*:(\d*)>)')
        emojis_string_id = set(pattern.findall(arg))
        for emoji in emojis_string_id:
            if self.bot.get_emoji(int(emoji[1])):
                valid_emojis.append(emoji[0])
            else:
                arg = re.sub(rf'<a?:\w*:{emoji[1]}>', '▪', arg)

        actual_len = len(re.sub(r'(<a?:\w*:(\d*)>)', '0', arg))
        if actual_len > 50:
            await ctx.send('어이! 너무 길다구! `(최대 50자)`')
            return
        else:
            msg = await ctx.send(arg)

        passing_emoji = False
        for i in range(len(arg)):
            if i < len(arg) and arg[i] == '<':
                for emoji in valid_emojis:
                    if arg[i:].startswith(emoji):
                        passing_emoji = True
            elif passing_emoji and arg[i] == '>':
                passing_emoji = False

            if not passing_emoji:
                await asyncio.sleep(60 / 145)  # BPM 145
                await msg.edit(content='||'+arg[:i+1]+'||'+arg[i+1:])

    @commands.command(name='말해줘')
    async def speak(self, ctx, *content):
        """응? 따라 말해 보라고?"""
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
        """단어들을 띄어쓰기로 구분해서 입력하면 하나를 골라 줄게!"""
        if not args:
            return

        # TODO 단어 종성에 따라 후치사 결정
        await ctx.send(f'음... **{random.choice(args)}** 쪽이 좋지 않아?')

    @commands.command(name='지워줘')
    async def delete(self, ctx: commands.Context, num=1):
        """입력한 수만큼의 메시지를 가차없이 지워 줄게, 후후후..."""
        if not ctx.channel.permissions_for(ctx.author).manage_messages:
            await ctx.send('어이, 너 메시지 삭제 권한이 없잖아!')
            return

        messages = []
        async for message in ctx.channel.history(
                limit=num, before=ctx.message.created_at):
            messages.append(message)
        await ctx.channel.delete_messages(messages)

    @commands.command(name='대화하자')
    async def talk(self, ctx):
        """핑퐁 빌더 챗봇 안내 임베드를 출력해 줄게!"""
        channels = filter(lambda x: x.id in self.config["pingpong_channels"],
                          ctx.guild.channels)
        embed = discord.Embed(title='좋아, 이야기하자!', colour=14669221)
        embed.add_field(name='이용 방법',
                        value='- 지정 채널에서 말을 걸면 내가 답장을 해 줄거야!\n'
                              '- 혼잣말을 하고 싶으면 앞에 `!`를 덧붙여!\n'
                              '- 말을 너무 많이 시키면 지쳐서 답장을 못하게 될지도...\n'
                              '- 다른 봇이나 나를 위한 명령어에는 답장하지 않아!',
                        inline=False)
        embed.add_field(name='지정 채널',
                        value=' / '.join(map(lambda x: x.mention, channels))
                              or '`(발견되지 않음)`',
                        inline=False)
        embed.add_field(name='베타 안내',
                        value='지금은 챗봇 API의 샘플을 그대로 쓰고 있어서, '
                              '유리가 아니라 범용 챗봇이 이야기해주는 느낌이 들 거야.'
                              '나중에는 바뀔 테니까 기대해 줘!',
                        inline=False)
        embed.set_thumbnail(url='https://cdn.discordapp.com/avatars/738942382762098728/a33a31dae3335605c3795317a1d356c3.webp?size=1024')
        await ctx.send(embed=embed)

    @commands.command(aliases=default.config()['other_bot_cmds'])
    async def other_bot_commands(self, ctx):
        await ctx.send('뭐')


def setup(bot):
    bot.add_cog(BasicCommands(bot))
