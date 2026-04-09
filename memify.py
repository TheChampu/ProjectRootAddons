"""
✘ Commands Available -

• `{i}mmf <upper text> ; <lower text> <reply to media>`
    To create memes as sticker,
    for trying different fonts use (.mmf <text>_1)(u can use 1 to 10).

• `{i}mms <upper text> ; <lower text> <reply to media>`
    To create memes as pic,
    for trying different fonts use (.mms <text>_1)(u can use 1 to 10).

"""

import asyncio
import os
import textwrap
import uuid
from pathlib import Path

import cv2
from PIL import Image, ImageDraw, ImageFont

from . import *


def _tmp_file(ext):
    tmp_dir = Path("resources/downloads")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    return str(tmp_dir / f"memify_{uuid.uuid4().hex}{ext}")


async def _safe_remove(path, retries=5, delay=0.12):
    if not path:
        return
    for _ in range(retries):
        try:
            if os.path.exists(path):
                os.remove(path)
            return
        except PermissionError:
            await asyncio.sleep(delay)
        except FileNotFoundError:
            return
        except Exception:
            return


@champu_cmd(pattern="mmf ?(.*)")
async def ultd(event):
    ureply = await event.get_reply_message()
    msg = event.pattern_match.group(1)
    if not (ureply and (ureply.media)):
        xx = await event.eor("`Reply to any media`")
        return
    if not msg:
        xx = await event.eor("`Give me something text to write...`")
        return
    ultt = await ureply.download_media()
    file = _tmp_file(".png")
    if ultt.endswith((".tgs")):
        xx = await event.eor("`Ooo Animated Sticker 👀...`")
        cmd = ["lottie_convert.py", ultt, file]
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        stderr.decode().strip()
        stdout.decode().strip()
    elif ultt.endswith((".webp", ".png")):
        xx = await event.eor("`Processing`")
        with Image.open(ultt) as im:
            im.save(file, format="PNG", optimize=True)
    else:
        xx = await event.eor("`Processing`")
        img = cv2.VideoCapture(ultt)
        heh, lol = img.read()
        cv2.imwrite(file, lol)
        img.release()
    stick = await draw_meme_text(file, msg)
    await event.client.send_file(
        event.chat_id, stick, force_document=False, reply_to=event.reply_to_msg_id
    )
    await xx.delete()
    await _safe_remove(ultt)
    await _safe_remove(file)
    await _safe_remove(stick)


async def draw_meme_text(image_path, msg):
    with Image.open(image_path) as opened:
        img = opened.convert("RGBA")
    i_width, i_height = img.size
    if "_" in msg:
        text, font = msg.split("_")
    else:
        text = msg
        font = "default"
    if ";" in text:
        upper_text, lower_text = text.split(";")
    else:
        upper_text = text
        lower_text = ""
    draw = ImageDraw.Draw(img)
    m_font = ImageFont.truetype(
        f"resources/fonts/{font}.ttf", int((70 / 640) * i_width)
    )
    current_h, pad = 10, 5
    if upper_text:
        for u_text in textwrap.wrap(upper_text, width=15):
            bbox = draw.textbbox((0, 0), u_text, font=m_font)
            u_width, u_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text(
                xy=(((i_width - u_width) / 2) - 1, int((current_h / 640) * i_width)),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=(((i_width - u_width) / 2) + 1, int((current_h / 640) * i_width)),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=((i_width - u_width) / 2, int(((current_h / 640) * i_width)) - 1),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=(((i_width - u_width) / 2), int(((current_h / 640) * i_width)) + 1),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=((i_width - u_width) / 2, int((current_h / 640) * i_width)),
                text=u_text,
                font=m_font,
                fill=(255, 255, 255),
            )
            current_h += u_height + pad
    if lower_text:
        for l_text in textwrap.wrap(lower_text, width=15):
            bbox = draw.textbbox((0, 0), l_text, font=m_font)
            u_width, u_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text(
                xy=(
                    ((i_width - u_width) / 2) - 1,
                    i_height - u_height - int((80 / 640) * i_width),
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=(
                    ((i_width - u_width) / 2) + 1,
                    i_height - u_height - int((80 / 640) * i_width),
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=(
                    (i_width - u_width) / 2,
                    (i_height - u_height - int((80 / 640) * i_width)) - 1,
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=(
                    (i_width - u_width) / 2,
                    (i_height - u_height - int((80 / 640) * i_width)) + 1,
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=(
                    (i_width - u_width) / 2,
                    i_height - u_height - int((80 / 640) * i_width),
                ),
                text=l_text,
                font=m_font,
                fill=(255, 255, 255),
            )
            current_h += u_height + pad
    imag = _tmp_file(".webp")
    img.save(imag, "WebP")
    return imag


@champu_cmd(pattern="mms ?(.*)")
async def mms(event):
    ureply = await event.get_reply_message()
    msg = event.pattern_match.group(1)
    if not (ureply and (ureply.media)):
        xx = await event.eor("`Reply to any media`")
        return
    if not msg:
        xx = await event.eor("`Give me something text to write 😑`")
        return
    ultt = await ureply.download_media()
    file = _tmp_file(".png")
    if ultt.endswith((".tgs")):
        xx = await event.eor("`Ooo Animated Sticker 👀...`")
        cmd = ["lottie_convert.py", ultt, file]
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        stderr.decode().strip()
        stdout.decode().strip()
    elif ultt.endswith((".webp", ".png")):
        xx = await event.eor("`Processing`")
        with Image.open(ultt) as im:
            im.save(file, format="PNG", optimize=True)
    else:
        xx = await event.eor("`Processing`")
        img = cv2.VideoCapture(ultt)
        heh, lol = img.read()
        cv2.imwrite(file, lol)
        img.release()
    pic = await draw_meme(file, msg)
    await event.client.send_file(
        event.chat_id, pic, force_document=False, reply_to=event.reply_to_msg_id
    )
    await xx.delete()
    await _safe_remove(ultt)
    await _safe_remove(file)
    await _safe_remove(pic)


async def draw_meme(image_path, msg):
    with Image.open(image_path) as opened:
        img = opened.convert("RGBA")
    i_width, i_height = img.size
    if "_" in msg:
        text, font = msg.split("_")
    else:
        text = msg
        font = "default"
    if ";" in text:
        upper_text, lower_text = text.split(";")
    else:
        upper_text = text
        lower_text = ""
    draw = ImageDraw.Draw(img)
    m_font = ImageFont.truetype(
        f"resources/fonts/{font}.ttf", int((70 / 640) * i_width)
    )
    current_h, pad = 10, 5
    if upper_text:
        for u_text in textwrap.wrap(upper_text, width=15):
            bbox = draw.textbbox((0, 0), u_text, font=m_font)
            u_width, u_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text(
                xy=(((i_width - u_width) / 2) - 1, int((current_h / 640) * i_width)),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=(((i_width - u_width) / 2) + 1, int((current_h / 640) * i_width)),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=((i_width - u_width) / 2, int(((current_h / 640) * i_width)) - 1),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=(((i_width - u_width) / 2), int(((current_h / 640) * i_width)) + 1),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=((i_width - u_width) / 2, int((current_h / 640) * i_width)),
                text=u_text,
                font=m_font,
                fill=(255, 255, 255),
            )
            current_h += u_height + pad
    if lower_text:
        for l_text in textwrap.wrap(lower_text, width=15):
            bbox = draw.textbbox((0, 0), l_text, font=m_font)
            u_width, u_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text(
                xy=(
                    ((i_width - u_width) / 2) - 1,
                    i_height - u_height - int((20 / 640) * i_width),
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=(
                    ((i_width - u_width) / 2) + 1,
                    i_height - u_height - int((20 / 640) * i_width),
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=(
                    (i_width - u_width) / 2,
                    (i_height - u_height - int((20 / 640) * i_width)) - 1,
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=(
                    (i_width - u_width) / 2,
                    (i_height - u_height - int((20 / 640) * i_width)) + 1,
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=(
                    (i_width - u_width) / 2,
                    i_height - u_height - int((20 / 640) * i_width),
                ),
                text=l_text,
                font=m_font,
                fill=(255, 255, 255),
            )
            current_h += u_height + pad
    pics = _tmp_file(".png")
    img.save(pics, "png")
    return pics