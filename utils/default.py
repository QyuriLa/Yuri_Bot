import datetime as dt
import time
import json
import discord
import traceback
import timeago as timesince

from io import BytesIO

import hjson


def config(filename: str = "config"):
    """ Fetch default config file """
    try:
        with open(f'data/{filename}.hjson', encoding='utf8') as f:
            return hjson.loads(f.read())
    except FileNotFoundError:
        raise FileNotFoundError("JSON file wasn't found")


def traceback_maker(err, advance: bool = True):
    """ A way to debug your code anywhere """
    _traceback = ''.join(traceback.format_tb(err.__traceback__))
    error = ('```py\n{1}{0}: {2}\n```').format(type(err).__name__, _traceback, err)
    return error if advance else f"{type(err).__name__}: {err}"


def timetext(name):
    """ Timestamp, but in text form """
    return f"{name}_{int(time.time())}.txt"


def timeago(target):
    """ Timeago in easier way """
    return timesince.format(target)


def date(target, clock=True):
    """ Clock format using datetime.strftime() """
    if not clock:
        return target.strftime("%d %B %Y")
    return target.strftime("%d %B %Y, %H:%M")


def responsible(target, reason):
    """ Default responsible maker targeted to find user in AuditLogs """
    responsible = f"[ {target} ]"
    if not reason:
        return f"{responsible} no reason given..."
    return f"{responsible} {reason}"


def actionmessage(case, mass=False):
    """ Default way to present action confirmation in chat """
    output = f"**{case}** the user"

    if mass:
        output = f"**{case}** the IDs/Users"

    return f"✅ Successfully {output}"


async def prettyResults(ctx, filename: str = "Results", resultmsg: str = "Here's the results:", loop=None):
    """ A prettier way to show loop results """
    if not loop:
        return await ctx.send("The result was empty...")

    pretty = "\r\n".join([f"[{str(num).zfill(2)}] {data}" for num, data in enumerate(loop, start=1)])

    if len(loop) < 15:
        return await ctx.send(f"{resultmsg}```ini\n{pretty}```")

    data = BytesIO(pretty.encode('utf-8'))
    await ctx.send(
        content=resultmsg,
        file=discord.File(data, filename=timetext(filename.title()))
    )


def next_sharp_datetime(now, unit, cycle):
    """자정을 기준으로, 주기에 맞는 바로 다음 datetime을 반환합니다.

    Parameters
    ----------
    now: dt.datetime
    unit: int
        cycle의 시간 단위를 특정합니다.
        0: 초, 1: 분, 2: 시
    cycle: int
        unit이 0 or 1이라면 60, 2라면 24의 약수여야 합니다.

    Returns
    -------
    dt.datetime
    """
    if unit in (0, 1):
        if 60 % cycle != 0:
            raise ValueError('cycle이 60의 약수가 아닙니다.')
    elif unit == 2:
        if 24 % cycle != 0:
            raise ValueError('cycle이 24의 약수가 아닙니다.')
    else:
        raise ValueError(
            'unit 값이 유효하지 않습니다. unit은 0, 1 또는 2여야 합니다.'
        )

    new_dt: dt.datetime
    if unit == 0:
        new_second = (now.second // cycle + 1) * cycle
        new_dt = now.replace(second=new_second % 60)
        if new_second == 60:
            new_dt += dt.timedelta(minutes=1)

    elif unit == 1:
        new_minute = (now.minute // cycle + 1) * cycle
        new_dt = now.replace(minute=new_minute % 60)
        if new_minute == 60:
            new_dt += dt.timedelta(hours=1)

    elif unit == 2:
        new_hour = (now.hour // cycle + 1) * cycle
        new_dt = now.replace(hour=new_hour % 24)
        if new_hour == 24:
            new_dt += dt.timedelta(days=1)

    return new_dt.replace(minute=0 if unit == 2 else new_dt.minute,
                          second=0 if unit >= 1 else new_dt.second,
                          microsecond=0)
