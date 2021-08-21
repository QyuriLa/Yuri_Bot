from datetime import datetime as dt
import io
import aiohttp

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

        if message.channel.id in self.config["pingpong_channels"]:
            await pingpong_chat(message)

    @commands.Cog.listener()
    async def on_guild_channel_pins_update(self, channel, last_pin):
        for i in self.config["pin_backup_channels"]:
            if self.bot.get_channel(i[0]) == channel:
                await pin_backup(self.bot.get_channel(i[0]),
                                 self.bot.get_channel(i[1]))


async def react_to_chito(message):
    chito = ['치토', '치이짱', '치이쨩']
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


async def pin_backup(origin, dest):
    pins = await origin.pins()


    for msg in pins:
        # 첨부파일 다운로드 및 첨부
        files = []
        if msg.attachments:
            for file in msg.attachments:
                files.append(await _get_attachment(file, msg))

        new_msg = await dest.send(
            content=msg.content +
                    f'\n||「{msg.author.mention}, '
                    f'<t:{int(dt.timestamp(msg.created_at))}:R>」||',
            files=files or None,
            allowed_mentions=discord.AllowedMentions.none()
        )

        if new_msg and len(new_msg.attachments) == len(msg.attachments):
            await msg.unpin()


async def _get_attachment(attachment, message):
    # Ref: https://discordpy.readthedocs.io/en/latest/faq.html#how-do-i-upload-an-image
    async with aiohttp.ClientSession() as session:
        async with session.get(attachment.proxy_url) as resp:
            if resp.status != 200:
                return await message.channel.send(
                    f'고정 메시지 백업 실패 - {message.jump_url}\n'
                    '사유: 파일 다운로드 실패'
                )
            return discord.File(io.BytesIO(await resp.read()),
                                attachment.filename,
                                spoiler=attachment.is_spoiler())


def setup(bot):
    bot.add_cog(OnMessage(bot))
