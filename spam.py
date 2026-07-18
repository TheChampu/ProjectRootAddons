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

from telethon.tl.custom import Message

from . import *


async def _send_spam_payload(event, payload, reply_to_id=None):
    if isinstance(payload, Message):
        try:
            if payload.sticker:
                return await event.client.send_file(
                    event.chat_id,
                    payload.media,
                    reply_to=reply_to_id,
                )
            elif payload.media:
                from telethon.tl.types import (
                    MessageMediaPoll,
                    MessageMediaGeo,
                    MessageMediaGeoLive,
                    MessageMediaContact,
                    MessageMediaVenue,
                    MessageMediaGame,
                )
                if isinstance(
                    payload.media,
                    (
                        MessageMediaPoll,
                        MessageMediaGeo,
                        MessageMediaGeoLive,
                        MessageMediaContact,
                        MessageMediaVenue,
                        MessageMediaGame,
                    ),
                ):
                    return await event.client.send_message(
                        event.chat_id,
                        payload,
                        reply_to=reply_to_id,
                    )
                else:
                    return await event.client.send_file(
                        event.chat_id,
                        payload.media,
                        caption=payload.message,
                        formatting_entities=payload.entities,
                        reply_to=reply_to_id,
                    )
            else:
                return await event.client.send_message(
                    event.chat_id,
                    payload.message,
                    formatting_entities=payload.entities,
                    reply_to=reply_to_id,
                    link_preview=False,
                )
        except Exception:
            return await event.client.send_message(
                event.chat_id,
                payload,
                reply_to=reply_to_id,
            )
    else:
        return await event.client.send_message(
            event.chat_id,
            payload,
            reply_to=reply_to_id,
        )


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
    reply_to_id = None
    if e.reply_to:
        args = message.split(maxsplit=2)
        if len(args) == 3:
            spam_message = args[2]
        else:
            spam_message = reply
        reply_to_id = reply.reply_to_msg_id or reply.id
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
    
    tasks = [
        asyncio.create_task(_send_spam_payload(e, spam_message, reply_to_id))
        for _ in range(counter)
    ]
    await asyncio.wait(tasks)
    await e.delete()


@champu_cmd(pattern="bigspam", fullsudo=True)
async def bigspam(e):
    message = e.text
    reply = await e.get_reply_message() if e.reply_to else None
    reply_to_id = None
    if e.reply_to:
        args = message.split(maxsplit=2)
        if len(args) == 3:
            spam_message = args[2]
        else:
            spam_message = reply
        reply_to_id = reply.reply_to_msg_id or reply.id
    else:
        if not len(message.split()) >= 3:
            return await eod(e, "`Reply to a Message or Give some Text..`")
        spam_message = message.split(maxsplit=2)[2]
    
    counter = message.split()[1]
    try:
        counter = int(counter)
    except BaseException:
        return await eod(e, "`Use in Proper Format`")
    
    tasks = [
        asyncio.create_task(_send_spam_payload(e, spam_message, reply_to_id))
        for _ in range(counter)
    ]
    await asyncio.wait(tasks)
    await e.delete()


@champu_cmd(pattern="delayspam ?(.*)")
async def delayspammer(e):
    reply = await e.get_reply_message() if e.reply_to else None
    reply_to_id = None
    try:
        args = e.text.split(" ", 3)
        delay = float(args[1])
        count = int(args[2])
        msg = str(args[3])
        if reply:
            reply_to_id = reply.reply_to_msg_id or reply.id
    except BaseException:
        if reply:
            try:
                args = e.text.split()
                delay = float(args[1])
                count = int(args[2])
                msg = reply
                reply_to_id = reply.reply_to_msg_id or reply.id
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
            await _send_spam_payload(e, msg, reply_to_id)
            await asyncio.sleep(delay)
    except Exception as u:
        await e.respond(f"**Error :** `{u}`")
