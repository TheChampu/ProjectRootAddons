# Champu - UserBot
# Copyright (C) 2021-2026 TheChampu
#
# This file is a part of < https://github.com/TheChampu/ProjectRootAddons/ >
# Please read the GNU Affero General Public License in
# <https://www.github.com/TheChampu/ProjectRoot/blob/main/LICENSE/>.
"""
International Morse Code Encoder & Decoder Addon for UserBot.

✘ Commands Available -

• `{i}mencode` <text / reply>
    Encodes English text & symbols into International Morse Code (`.-`).
    Includes a direct link to interactively decode in the Assistant Bot!

• `{i}mdecode` <morse / reply>
    Decodes International Morse Code (`.-`, `•`, `−`, `/`) back into clear text.
    Includes a direct link to interactively re-encode in the Assistant Bot!
"""

import html
import io
import os
from contextlib import suppress

from telethon.tl.types import MessageMediaDocument

from assistant.encoder import (
    _store_cache,
    decode_morse,
    encode_morse,
)
from pyChampu import asst
from . import champu_cmd


async def _extract_text(event, raw_arg: str) -> str:
    """Extracts target text from command argument, replied text, or replied text document."""
    if raw_arg and raw_arg.strip():
        return raw_arg.strip()

    reply = await event.get_reply_message()
    if reply:
        if reply.text and reply.text.strip():
            return reply.text.strip()
        if reply.media and isinstance(getattr(reply.media, "document", None), MessageMediaDocument):
            doc = reply.media.document
            mime = getattr(doc, "mime_type", "")
            if "text" in mime or any(getattr(a, "file_name", "").endswith((".txt", ".py", ".json", ".csv", ".log")) for a in getattr(doc, "attributes", [])):
                if getattr(doc, "size", 0) <= 200000:
                    fpath = await event.client.download_media(reply.media)
                    try:
                        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                            return f.read().strip()
                    finally:
                        if fpath and os.path.exists(fpath):
                            with suppress(Exception):
                                os.remove(fpath)
    return ""


@champu_cmd(pattern=r"mencode(?:\s+(.*))?$")
async def ub_mencode_addon(event):
    """Encodes text into International Morse Code."""
    text_content = (event.pattern_match.group(1) or "").strip()
    if not text_content:
        text_content = await _extract_text(event, "")

    if not text_content:
        return await event.eor(
            "<blockquote>⚡ <b>CHAMPU MORSE CODE ENCODER</b> ⚡</blockquote>\n\n"
            "<b>Usage:</b>\n"
            "• <code>.mencode &lt;text&gt;</code> (e.g. <code>.mencode Hello World!</code>)\n"
            "• Or reply to any text message with <code>.mencode</code>",
            parse_mode="html",
        )

    morse_val = encode_morse(text_content)
    cache_id = _store_cache(text_content, "morse", event.sender_id)

    dots = morse_val.count(".")
    dashes = morse_val.count("-")
    chars_cnt = len(text_content)

    asst_uname = getattr(asst.me, "username", None) if asst and getattr(asst, "me", None) else None
    bot_link_str = f'\n\n🔗 <a href="https://t.me/{asst_uname}?start=cipher_{cache_id}"><b>[ 🤖 Open in Assistant Bot Studio ]</b></a>' if asst_uname else ""

    if len(morse_val) > 3500:
        file_bio = io.BytesIO(morse_val.encode("utf-8"))
        file_bio.name = "morse_encoded.txt"
        caption = (
            f"<blockquote>⚡ <b>CHAMPU MORSE CODE ENCODER</b> ⚡\n"
            f"📊 <b>Characters:</b> {chars_cnt} | <b>Dots:</b> {dots} | <b>Dashes:</b> {dashes}</blockquote>"
            f"{bot_link_str}"
        )
        return await event.reply(file=file_bio, caption=caption, parse_mode="html")

    msg_html = (
        f"<blockquote>⚡ <b>CHAMPU MORSE CODE ENCODER</b> ⚡\n"
        f"📊 <b>Characters:</b> {chars_cnt} | <b>Dots:</b> {dots} | <b>Dashes:</b> {dashes}</blockquote>\n\n"
        f"<b>Morse Code Output:</b>\n"
        f"<code>{html.escape(morse_val)}</code>"
        f"{bot_link_str}"
    )
    await event.eor(msg_html, parse_mode="html")


@champu_cmd(pattern=r"mdecode(?:\s+(.*))?$")
async def ub_mdecode_addon(event):
    """Decodes International Morse Code into plain text."""
    text_content = (event.pattern_match.group(1) or "").strip()
    if not text_content:
        text_content = await _extract_text(event, "")

    if not text_content:
        return await event.eor(
            "<blockquote>⚡ <b>CHAMPU MORSE CODE DECODER</b> ⚡</blockquote>\n\n"
            "<b>Usage:</b>\n"
            "• <code>.mdecode &lt;morse_code&gt;</code> (e.g. <code>.mdecode ... --- ...</code>)\n"
            "• Or reply to any message containing Morse Code with <code>.mdecode</code>",
            parse_mode="html",
        )

    decoded_val = decode_morse(text_content)
    cache_id = _store_cache(decoded_val, "morse", event.sender_id)

    tokens = len(text_content.split())
    out_chars = len(decoded_val)

    asst_uname = getattr(asst.me, "username", None) if asst and getattr(asst, "me", None) else None
    bot_link_str = f'\n\n🔗 <a href="https://t.me/{asst_uname}?start=cipher_{cache_id}"><b>[ 🤖 Open in Assistant Bot Studio ]</b></a>' if asst_uname else ""

    if len(decoded_val) > 3500:
        file_bio = io.BytesIO(decoded_val.encode("utf-8"))
        file_bio.name = "morse_decoded.txt"
        caption = (
            f"<blockquote>⚡ <b>CHAMPU MORSE CODE DECODER</b> ⚡\n"
            f"📊 <b>Morse Tokens:</b> {tokens} | <b>Decoded Length:</b> {out_chars} chars</blockquote>"
            f"{bot_link_str}"
        )
        return await event.reply(file=file_bio, caption=caption, parse_mode="html")

    msg_html = (
        f"<blockquote>⚡ <b>CHAMPU MORSE CODE DECODER</b> ⚡\n"
        f"📊 <b>Morse Tokens:</b> {tokens} | <b>Decoded Length:</b> {out_chars} chars</blockquote>\n\n"
        f"<b>Decoded Plaintext:</b>\n"
        f"<code>{html.escape(decoded_val)}</code>"
        f"{bot_link_str}"
    )
    await event.eor(msg_html, parse_mode="html")