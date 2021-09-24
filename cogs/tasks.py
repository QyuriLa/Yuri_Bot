import asyncio
import datetime as dt
import aiohttp
import io
import random
import re
from typing import Optional

import discord
from discord.ext import commands, tasks
from PIL import Image, ImageDraw, ImageFont

from utils import default


KST = dt.timezone(dt.timedelta(hours=9))


class Tasks(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.config = default.config()
        self.bot = bot
        self.archive_pins.start()
        self.daily_arrest.start()

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

                try:
                    new_msg = await _archive_msg(self.bot, channels[1], msg)
                except Exception as exc:
                    print(f'고정 아카이브 중 예외 발생: {type(exc)}: {exc}')
                else:
                    await msg.unpin()

    @archive_pins.before_loop
    async def before_archive_pins(self):
        await self.bot.wait_until_ready()
        now = dt.datetime.now()
        timedelta = default.next_sharp_datetime(now, 1, 10) - now
        await asyncio.sleep(timedelta.total_seconds())

    @tasks.loop(time=dt.time(hour=21, minute=35, tzinfo=KST))
    async def daily_arrest(self):
        channel: Optional[discord.TextChannel] = None
        for id_ in self.config["daily_arrest_channels"]:
            if self.bot.get_channel(id_):
                channel = self.bot.get_channel(id_)
                break
        if not channel:
            return
        guild = channel.guild
        member = random.choice([x for x in guild.members if not x.bot])

        # 이미지 생성
        with Image.open('data/daily_arrest-in.jpg') as img:
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype('data/NanumSquareB.ttf', 90)
            draw.text((1420, 950), f'{member.display_name}',
                      font=font, anchor='rs', stroke_width=5, stroke_fill=0)
            img.save(f'data/daily_arrest-out.jpg', 'JPEG')

        now = dt.datetime.now().strftime('%y%m%d')
        message = await channel.send(member.mention, file=discord.File(
                f'data/daily_arrest-out.jpg', f'{now}.jpg'
            ))

        # 체포 역할 생성
        arrested_role = await guild.create_role(
            name='체포', color=discord.Color.darker_gray(), hoist=True
        )
        temp_roles = []
        for role in member.roles:
            if role.is_assignable() and not role.is_default():
                temp_roles.append(role)
                await member.remove_roles(role)
        await member.add_roles(arrested_role)
        for ch in guild.channels:
            if ch.permissions_for(arrested_role).send_messages:
                await ch.set_permissions(arrested_role,
                                         send_messages=False,
                                         manage_permissions=False)

        # 10분 경과 후 역할 복구 및 체포 역할 삭제
        await asyncio.sleep(600)
        for role in temp_roles:
            await member.add_roles(role)
        await arrested_role.delete()
        await message.edit(content=member.mention+' (석방됨)')


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
            if resp.status == 200:
                return discord.File(io.BytesIO(await resp.read()),
                                    attachment.filename,
                                    spoiler=attachment.is_spoiler())

        # proxy_url에서 파일을 받아오지 못한 경우 (보통 non-media)
        async with session.get(attachment.url) as resp:
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
