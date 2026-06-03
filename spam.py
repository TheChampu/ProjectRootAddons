"""
✘ Commands Available -
• `{i}spam <no of msgs> <your msg>`
  `{i}spam <no of msgs> <reply message>`
    spams chat, the current limit for this is from 1 to 99.

• `{i}bigspam <no of msgs> <your msg>`
  `{i}bigspam <no of msgs> <reply message>`
    Spams chat, the current limit is above 100.

• `{i}delayspam <delay time> <count> <msg>`
    Spam chat with delays..

• `{i}tspam <text>`
    Spam Chat with One-One Character..
"""

import asyncio

from . import *


def _spam_reply_payload(reply):
    if not reply:
        return None
    if reply.media:
        return reply
    text = (reply.message or reply.raw_text or reply.text or "").strip()
    if text:
        return text
    return reply


async def _send_spam_payload(event, payload):
    if hasattr(payload, "media") and payload.media:
        return await event.client.send_file(
            event.chat_id,
            file=payload.media,
            caption=(payload.message or payload.raw_text or payload.text or None),
        )
    return await event.client.send_message(event.chat_id, payload)


@champu_cmd(pattern="tspam")
async def tmeme(e):
    tspam = str(e.text[7:])
    message = tspam.replace(" ", "")
    for letter in message:
        await e.respond(letter)
    await e.delete()


@champu_cmd(pattern="spam")
async def spammer(e):
    message = e.text
    reply = await e.get_reply_message() if e.reply_to else None
    if e.reply_to:
        if not len(message.split()) >= 2:
            return await eod(e, "`Use in Proper Format`")
        spam_message = _spam_reply_payload(reply)
    else:
        if not len(message.split()) >= 3:
            return await eod(e, "`Reply to a Message or Give some Text..`")
        spam_message = message.split(maxsplit=2)[2]
    counter = message.split()[1]
    try:
        counter = int(counter)
        if counter >= 100:
            return await eod(e, "`Use bigspam cmd`")
    except BaseException:
        return await eod(e, "`Use in Proper Format`")
    tasks = [asyncio.create_task(_send_spam_payload(e, spam_message)) for _ in range(counter)]
    await asyncio.wait(tasks)
    await e.delete()


@champu_cmd(pattern="bigspam", fullsudo=True)
async def bigspam(e):
    message = e.text
    reply = await e.get_reply_message() if e.reply_to else None
    if e.reply_to:
        if not len(message.split()) >= 2:
            return await eod(e, "`Use in Proper Format`")
        spam_message = _spam_reply_payload(reply)
    else:
        if not len(message.split()) >= 3:
            return await eod(e, "`Reply to a Message or Give some Text..`")
        spam_message = message.split(maxsplit=2)[2]
    counter = message.split()[1]
    try:
        counter = int(counter)
    except BaseException:
        return await eod(e, "`Use in Proper Format`")
    tasks = [asyncio.create_task(_send_spam_payload(e, spam_message)) for _ in range(counter)]
    await asyncio.wait(tasks)
    await e.delete()


@champu_cmd(pattern="delayspam ?(.*)")
async def delayspammer(e):
    reply = await e.get_reply_message() if e.reply_to else None
    try:
        args = e.text.split(" ", 3)
        delay = float(args[1])
        count = int(args[2])
        msg = str(args[3])
    except BaseException:
        if reply:
            try:
                args = e.text.split()
                delay = float(args[1])
                count = int(args[2])
                msg = _spam_reply_payload(reply)
            except BaseException:
                return await e.edit(
                    f"**Usage :** {HNDLR}delayspam <delay time> <count> <msg/reply>"
                )
        else:
            return await e.edit(
                f"**Usage :** {HNDLR}delayspam <delay time> <count> <msg/reply>"
            )
    await e.delete()
    try:
        for i in range(count):
            await _send_spam_payload(e, msg)
            await asyncio.sleep(delay)
    except Exception as u:
        await e.respond(f"**Error :** `{u}`")
