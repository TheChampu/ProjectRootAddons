# Champu - UserBot
# Copyright (C) 2021-2026 TheChampu
#
# This file is a part of < https://github.com/TheChampu/ProjectRootAddons/ >
# Please read the GNU Affero General Public License in
# <https://www.github.com/TheChampu/ProjectRoot/blob/main/LICENSE/>.
"""
Universal Multi-Format Text Encoder & Decoder Addon for UserBot.

✘ Commands Available -

• `{i}encode` or `{i}encoder` [format] <text / reply>
    Encodes text into Base64 (default), Base32, Hexadecimal, Binary, ROT13, URL, or Morse.
    Includes a direct 1-tap link to interactively switch algorithms in the Assistant Bot!

• `{i}decode` or `{i}decoder` [format] <text / reply>
    Intelligent Auto-Detect Decoder! Automatically decodes Base64, Hex, Binary, Base32,
    ROT13, URL-encoded strings, or Morse Code into clean text.
"""

import html
import io
import os
from contextlib import suppress

from telethon.tl.types import MessageMediaDocument

from assistant.encoder import (
    ALGO_NAMES,
    _store_cache,
    decode_text,
    encode_text,
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


@champu_cmd(pattern=r"(?:encode|encoder)(?:\s+(.*))?$")
async def ub_encode_addon(event):
    """Encodes text using Base64, Hex, Binary, Base32, ROT13, URL, or Morse."""
    raw_input = (event.pattern_match.group(1) or "").strip()
    target_fmt = "b64"
    text_content = ""

    parts = raw_input.split(maxsplit=1)
    if parts and parts[0].lower() in ALGO_NAMES:
        target_fmt = parts[0].lower()
        if len(parts) > 1:
            text_content = parts[1].strip()
    else:
        text_content = raw_input

    if not text_content:
        text_content = await _extract_text(event, "")

    if not text_content:
        return await event.eor(
            "<blockquote>🔐 <b>CHAMPU CIPHER &amp; ENCODER STUDIO</b> 🔐</blockquote>\n\n"
            "<b>Usage:</b>\n"
            "• <code>.encode &lt;text&gt;</code> (Base64 by default)\n"
            "• <code>.encode &lt;format&gt; &lt;text&gt;</code>\n"
            "• Or reply to any message with <code>.encode</code>\n\n"
            "<b>Supported Formats:</b>\n"
            "<code>b64</code>, <code>hex</code>, <code>bin</code>, <code>b32</code>, <code>b85</code>, <code>rot13</code>, <code>atbash</code>, <code>rev</code>, <code>url</code>, <code>morse</code>, <code>hash</code>",
            parse_mode="html",
        )

    algo_title = ALGO_NAMES.get(target_fmt, "Base64")
    encoded_val = encode_text(text_content, target_fmt)
    cache_id = _store_cache(text_content, target_fmt, event.sender_id)

    in_len = len(text_content)
    out_len = len(encoded_val)

    asst_uname = getattr(asst.me, "username", None) if asst and getattr(asst, "me", None) else None
    bot_link_str = f'\n\n🔗 <a href="https://t.me/{asst_uname}?start=cipher_{cache_id}"><b>[ 🤖 Open in Assistant Bot Studio ]</b></a>' if asst_uname else ""

    if len(encoded_val) > 3500:
        file_bio = io.BytesIO(encoded_val.encode("utf-8"))
        file_bio.name = f"encoded_{target_fmt}.txt"
        caption = (
            f"<blockquote>🔐 <b>CHAMPU CIPHER &amp; ENCODER STUDIO</b> 🔐\n"
            f"⚙️ <b>Algorithm:</b> <code>{algo_title}</code>\n"
            f"📊 <b>Stats:</b> Input: {in_len} chars | Output: {out_len} chars</blockquote>"
            f"{bot_link_str}"
        )
        return await event.reply(file=file_bio, caption=caption, parse_mode="html")

    msg_html = (
        f"<blockquote>🔐 <b>CHAMPU CIPHER &amp; ENCODER STUDIO</b> 🔐\n"
        f"⚙️ <b>Algorithm:</b> <code>{algo_title}</code>\n"
        f"📊 <b>Stats:</b> Input: {in_len} chars | Output: {out_len} chars</blockquote>\n\n"
        f"<b>Encoded Output:</b>\n"
        f"<code>{html.escape(encoded_val)}</code>"
        f"{bot_link_str}"
    )
    await event.eor(msg_html, parse_mode="html")


@champu_cmd(pattern=r"(?:decode|decoder)(?:\s+(.*))?$")
async def ub_decode_addon(event):
    """Decodes text with intelligent automatic format detection or manual format override."""
    raw_input = (event.pattern_match.group(1) or "").strip()
    target_fmt = "auto"
    text_content = ""

    parts = raw_input.split(maxsplit=1)
    if parts and parts[0].lower() in ALGO_NAMES:
        target_fmt = parts[0].lower()
        if len(parts) > 1:
            text_content = parts[1].strip()
    else:
        text_content = raw_input

    if not text_content:
        text_content = await _extract_text(event, "")

    if not text_content:
        return await event.eor(
            "<blockquote>🔓 <b>CHAMPU CIPHER &amp; DECODER STUDIO</b> 🔓</blockquote>\n\n"
            "<b>Usage:</b>\n"
            "• <code>.decode &lt;encoded_text&gt;</code> (Auto-Detect!)\n"
            "• <code>.decode &lt;format&gt; &lt;text&gt;</code> (Manual override)\n"
            "• Or reply to any message with <code>.decode</code>\n\n"
            "<b>Auto-Supported:</b> Base64, Hex, Binary, Morse, Base32, Base85, ROT13, Atbash, URL",
            parse_mode="html",
        )

    decoded_val, detected_algo = decode_text(text_content, target_fmt)
    cache_id = _store_cache(decoded_val, detected_algo.lower(), event.sender_id)

    in_len = len(text_content)
    out_len = len(decoded_val)

    asst_uname = getattr(asst.me, "username", None) if asst and getattr(asst, "me", None) else None
    bot_link_str = f'\n\n🔗 <a href="https://t.me/{asst_uname}?start=cipher_{cache_id}"><b>[ 🤖 Open in Assistant Bot Studio ]</b></a>' if asst_uname else ""

    if len(decoded_val) > 3500:
        file_bio = io.BytesIO(decoded_val.encode("utf-8"))
        file_bio.name = "decoded_plaintext.txt"
        caption = (
            f"<blockquote>🔓 <b>CHAMPU CIPHER &amp; DECODER STUDIO</b> 🔓\n"
            f"🎯 <b>Detected Algorithm:</b> <code>{detected_algo}</code>\n"
            f"📊 <b>Stats:</b> Input: {in_len} chars | Decoded: {out_len} chars</blockquote>"
            f"{bot_link_str}"
        )
        return await event.reply(file=file_bio, caption=caption, parse_mode="html")

    msg_html = (
        f"<blockquote>🔓 <b>CHAMPU CIPHER &amp; DECODER STUDIO</b> 🔓\n"
        f"🎯 <b>Detected Algorithm:</b> <code>{detected_algo}</code>\n"
        f"📊 <b>Stats:</b> Input: {in_len} chars | Decoded: {out_len} chars</blockquote>\n\n"
        f"<b>Decoded Plaintext:</b>\n"
        f"<code>{html.escape(decoded_val)}</code>"
        f"{bot_link_str}"
    )
    await event.eor(msg_html, parse_mode="html")
