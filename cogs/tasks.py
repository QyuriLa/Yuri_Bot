import datetime as dt
import aiohttp
import io

import discord
from discord.ext import commands, tasks

from utils import default


class Tasks(commands.Cog):
    def __init__(self, bot):
        self.config = default.config()
        self.bot = bot

    @tasks.loop(hours=1)
    async def archive_pins(self):
        for ids in self.config["pin_backup_channels"]:
            channels = [self.bot.get_channel(x) for x in ids]
            pins = await channels[0].pins()
            exceptions = self.config["pin_backup_except_msgs"]
            for msg in pins:
                # config에 등록된 제외 메시지는 제외
                if exceptions and msg.id in exceptions:
                    return

                new_msg = await _archive_message(channels[1], msg)

                # 첨부파일 개수가 같을 때만 unpin() 실행
                if new_msg and len(new_msg.attachments) == len(msg.attachments):
                    await msg.unpin()
                else:
                    await channels[0].send(
                        f'이런, 고정 메시지 아카이빙 중에 문제가 생겼어! '
                        '고정 해제는 하지 않을게―',
                        embed=discord.Embed(title='해당 메시지로 바로가기',
                                            colour=discord.Color.red,
                                            url=msg.jump_url)
                    )


async def _archive_message(dest, message):
    # 첨부파일 다운로드
    files = []
    for file in message.attachments:
        files.append(await _get_attachment(file, message))

    # 메시지에 덧붙일 타임스탬프 생성
    msg_timestamp = dt.datetime.timestamp(
        message.created_at + dt.timedelta(hours=9)
    )

    # 메시지 전송 및 전송한 메시지 반환
    return await dest.send(
        content=message.content +
                f'\n||「{message.author.mention}, '
                f'<t:{int(msg_timestamp)}:R>」||',
        files=files or None,
        allowed_mentions=discord.AllowedMentions.none()
    )


async def _get_attachment(attachment, message):
    # Ref: https://discordpy.readthedocs.io/en/latest/faq.html#how-do-i-upload-an-image
    async with aiohttp.ClientSession() as session:
        async with session.get(attachment.proxy_url) as resp:
            if resp.status != 200:
                await message.channel.send(
                    '고정 메시지 백업 실패 - 첨부파일 다운로드 실패\n'
                    f'대상: {message.jump_url}'
                )
                return None
            return discord.File(io.BytesIO(await resp.read()),
                                attachment.filename,
                                spoiler=attachment.is_spoiler())


def setup(bot):
    bot.add_cog(Tasks(bot))
