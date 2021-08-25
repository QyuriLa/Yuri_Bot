import asyncio
import datetime as dt
import aiohttp
import io
import re

import discord
from discord.ext import commands, tasks

from utils import default


class Tasks(commands.Cog):
    def __init__(self, bot):
        self.config = default.config()
        self.bot = bot
        self.archive_pins.start()

    @tasks.loop(minutes=10)
    async def archive_pins(self):
        for ids in self.config["pin_backup_channels"]:
            channels = [self.bot.get_channel(x) for x in ids]
            pins = await channels[0].pins()
            exceptions = self.config["pin_backup_except_msgs"]
            for msg in pins:
                # config에 등록된 제외 메시지는 제외
                if exceptions and msg.id in exceptions:
                    continue

                new_msg = await _archive_msg(self.bot, channels[1], msg)

                # 첨부파일 개수가 같을 때만 unpin() 실행
                if new_msg and len(new_msg.attachments) == len(msg.attachments):
                    await msg.unpin()
                else:
                    await channels[0].send(
                        f'이런, 고정 메시지 아카이빙 중에 문제가 생겼어!\n'
                        '고정 해제는 하지 않을게―',
                        embed=discord.Embed(title='해당 메시지로 바로 가기',
                                            colour=discord.Color.red,
                                            url=msg.jump_url)
                    )

    @archive_pins.before_loop
    async def before_archive_pins(self):
        await self.bot.wait_until_ready()
        now = dt.datetime.now()
        timedelta = default.next_sharp_datetime(now, 1, 10) - now
        await asyncio.sleep(timedelta.total_seconds())


async def _archive_msg(bot, dest: discord.abc.Messageable,
                       message: discord.Message):
    are_there_large_files = False
    are_there_unusable_emojis = False

    # 첨부파일 다운로드 및 첨부 준비
    files = []
    large_filenames = []
    for file in message.attachments:
        if file.size < message.guild.filesize_limit:
            files.append(await _get_attachment(file, message))
        else:
            are_there_large_files = True
            large_filenames.append(file.filename)

    # 바로 가기 버튼 생성
    view = discord.ui.View()
    view.add_item(discord.ui.Button(url=message.jump_url,
                                    label='바로 가기', emoji='🔗'))

    # 사용 불가 이모지 '▪'로 교체
    new_content = message.content
    pattern = re.compile(r'<a?:\w*:(\d*)>')

    emoji_ids = set(pattern.findall(new_content))
    for id_ in emoji_ids:
        if not bot.get_emoji(id_):
            are_there_unusable_emojis = True
            new_content = re.sub(rf'<a?:\w*:{id_}>', '▪', new_content)

    before_len = len(new_content)  # 2000자 초과 검사 시 사용

    # 꼬리말 추가
    if are_there_unusable_emojis:
        new_content += ' *(외부 이모지 교체됨)*'
    if are_there_large_files:
        new_content += (
            f'\n*(누락된 용량 제한 초과 파일: `{", ".join(large_filenames)}`)*'
        )

    # new_content 끝에 타임스탬프 추가
    msg_ts = dt.datetime.timestamp(
        message.created_at  # + dt.timedelta(hours=9) : 로컬 구동 시 필요?
    )
    new_content += f'\n||「{message.author.mention}, <t:{int(msg_ts)}:R>」||'

    # new_content가 2000자 초과 시 뒤에 '…*(후략)*' 삽입
    if len(new_content) > 2000:
        omit = len(new_content) - 2000 + len('…*(후략)*')
        new_content = (new_content[:before_len-omit]
                       + '…*(후략)*'
                       + new_content[before_len:])

    # 메시지 전송 및 전송한 메시지 반환
    try:
        return await dest.send(content=new_content,
                               files=files or None,
                               allowed_mentions=discord.AllowedMentions.none(),
                               view=view)
    except discord.errors.HTTPException:
        pass


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
