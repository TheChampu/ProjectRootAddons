#


"""
✘ Commands Available -

• `{i}tts` `LanguageCode <reply to a message>`
• `{i}tts` `LangaugeCode | text to speak`

• `{i}stt` `<reply to audio file>`
  `Convert Speech to Text...`
  `Note - Sometimes Not 100% Accurate`
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path

from contextlib import suppress

import speech_recognition as sr
from gtts import gTTS

from . import *

reco = sr.Recognizer()


@champu_cmd(
    pattern="tts ?(.*)",
)
async def _(event):
    input_str = event.pattern_match.group(1)
    start = datetime.now()
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        text = previous_message.message
        lan = input_str
    elif "|" in input_str:
        lan, text = input_str.split("|")
    else:
        await event.eor("Invalid Syntax. Module stopping.")
        return
    text = text.strip()
    lan = lan.strip()
    download_dir = Path("downloads")
    download_dir.mkdir(parents=True, exist_ok=True)
    required_file_name = download_dir / "voice.ogg"
    try:
        tts = gTTS(text, lang=lan)
        tts.save(str(required_file_name))
        command_to_execute = [
            "ffmpeg",
            "-i",
            str(required_file_name),
            "-map",
            "0:a",
            "-codec:a",
            "libopus",
            "-b:a",
            "100k",
            "-vbr",
            "on",
            str(required_file_name) + ".opus",
        ]
        try:
            subprocess.check_output(command_to_execute, stderr=subprocess.STDOUT)
        except (subprocess.CalledProcessError, NameError, FileNotFoundError) as exc:
            await event.eor(str(exc))
        else:
            with suppress(FileNotFoundError):
                os.remove(required_file_name)
            required_file_name = Path(str(required_file_name) + ".opus")
        end = datetime.now()
        ms = (end - start).seconds
        await event.reply(
            file=str(required_file_name),
        )
        with suppress(FileNotFoundError):
            os.remove(required_file_name)
        await eod(event, "Processed {} ({}) in {} seconds!".format(text[0:97], lan, ms))
    except Exception as e:
        await event.eor(str(e))


@champu_cmd(pattern="stt")
async def speec_(e):
    reply = await e.get_reply_message()
    if not (reply and reply.media):
        return await eod(e, "`Reply to Audio-File..`")
    # Not Hard Checking File Types
    download_dir = Path("downloads")
    download_dir.mkdir(parents=True, exist_ok=True)
    re = await reply.download_media(file=str(download_dir))
    re_path = Path(re)
    fn = Path(str(re_path) + ".wav")
    try:
        await bash(f'ffmpeg -i "{re_path}" -vn "{fn}"')
        with sr.AudioFile(str(fn)) as source:
            audio = reco.record(source)
        try:
            text = reco.recognize_google(audio, language="en-IN")
        except Exception as er:
            return await e.eor(str(er))
        out = "**Extracted Text :**\n `" + text + "`"
        await e.eor(out)
    finally:
        with suppress(FileNotFoundError):
            os.remove(fn)
        with suppress(FileNotFoundError):
            os.remove(re_path)
