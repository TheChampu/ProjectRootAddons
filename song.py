"""
✘ Commands Available -
• `{i}lyrics <search query>`
    get lyrics of song.

• `{i}songs <search query>`
    alternative song command.
"""


import random
import asyncio
from urllib.parse import quote_plus

from lyrics_extractor import SongLyrics as sl
from lyrics_extractor.lyrics import LyricScraperException as LyError
from telethon import Button, events

from . import *

API_URL = "https://shrutibots.site"
SEARCH_ENDPOINTS = (
    "song/search",
    "songs/search",
    "ytsearch",
    "youtube/search",
    "search",
    "song",
    "songs",
    "api/search",
    "music",
    "api/song",
    "api/songs",
)
DOWNLOAD_ENDPOINTS = (
    "song/download",
    "songs/download",
    "download/song",
    "download",
    "ytaudio",
    "ytmp3",
    "api/song/download",
    "api/songs/download",
    "song",
)


def _normalize_url(url):
    if not isinstance(url, str):
        return None
    if url.startswith("//"):
        return "https:" + url
    if url.startswith("/"):
        return API_URL + url
    return url


def _song_url_from_payload(payload):
    if not isinstance(payload, dict):
        return None, None, None
    direct_audio_url = (
        payload.get("url")
        or payload.get("download_url")
        or payload.get("audio_url")
        or payload.get("audio")
    )
    title = payload.get("title") or payload.get("name")
    artist = payload.get("artist") or payload.get("singer") or payload.get("channel")
    return _normalize_url(direct_audio_url), title, artist


def _extract_video_id(payload):
    if not isinstance(payload, dict):
        return None
    return (
        payload.get("id")
        or payload.get("video_id")
        or payload.get("videoId")
        or payload.get("yt_id")
    )


def _get_song_list(response):
    if isinstance(response, list):
        return response
    if not isinstance(response, dict):
        return []
    for key in ("results", "data", "result", "songs", "items", "videos"):
        value = response.get(key)
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            for nested in ("results", "items", "songs", "videos", "data"):
                nested_value = value.get(nested)
                if isinstance(nested_value, list):
                    return nested_value
    return []


def _normalize_song_item(item):
    if not isinstance(item, dict):
        return None
    title = item.get("title") or item.get("name") or item.get("song")
    artist = (
        item.get("artist")
        or item.get("channel")
        or item.get("uploader")
        or item.get("author")
    )
    duration = item.get("duration") or item.get("length") or item.get("timestamp")
    video_url = _normalize_url(
        item.get("video_url")
        or item.get("youtube_url")
        or item.get("webpage_url")
        or item.get("url")
        or item.get("link")
    )
    video_id = _extract_video_id(item)
    if not video_url and isinstance(video_id, str):
        video_url = f"https://www.youtube.com/watch?v={video_id}"
    direct_audio_url, _, _ = _song_url_from_payload(item)
    return {
        "title": title or "Unknown Title",
        "artist": artist,
        "duration": duration,
        "video_url": video_url,
        "video_id": video_id,
        "audio_url": direct_audio_url,
        "raw": item,
    }


def _extract_song_choices(response):
    songs = _get_song_list(response)
    cleaned = []
    for song in songs:
        row = _normalize_song_item(song)
        if row and row["title"]:
            cleaned.append(row)
    return cleaned


def _extract_song_data(response):
    if isinstance(response, list) and response:
        response = response[0]
    if not isinstance(response, dict):
        return None, None, None
    url, title, artist = _song_url_from_payload(response)
    if url:
        return url, title, artist
    for key in ("result", "results", "data", "song"):
        data = response.get(key)
        if isinstance(data, list) and data:
            data = data[0]
        url, title, artist = _song_url_from_payload(data)
        if url:
            return url, title, artist
    return None, None, None


async def _fetch_song_details(query):
    encoded_query = quote_plus(query)
    for endpoint in DOWNLOAD_ENDPOINTS:
        api = f"{API_URL}/{endpoint}?query={encoded_query}"
        try:
            data = await async_searcher(api, re_json=True)
        except Exception:
            continue
        song_url, title, artist = _extract_song_data(data)
        if song_url:
            return song_url, title, artist
    return None, None, None


async def _search_songs(query):
    encoded_query = quote_plus(query)
    for endpoint in SEARCH_ENDPOINTS:
        for param in ("query", "q", "search"):
            api = f"{API_URL}/{endpoint}?{param}={encoded_query}"
            try:
                data = await async_searcher(api, re_json=True)
            except Exception:
                continue
            songs = _extract_song_choices(data)
            if songs:
                return songs
    return []


def _build_song_list_text(songs):
    lines = ["**Choose a song from buttons (45s timeout):**\n"]
    for idx, song in enumerate(songs, start=1):
        detail = f"{idx}. {song['title']}"
        meta = []
        if song.get("artist"):
            meta.append(song["artist"])
        if song.get("duration"):
            meta.append(str(song["duration"]))
        if meta:
            detail += f"  -  {' | '.join(meta)}"
        lines.append(detail)
    return "\n".join(lines)


def _build_song_buttons(count):
    buttons = []
    row = []
    for idx in range(1, count + 1):
        row.append(Button.inline(str(idx), data=f"songsel:{idx}".encode("utf-8")))
        if len(row) == 5:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([Button.inline("Cancel", data=b"songsel:cancel")])
    return buttons


async def _resolve_audio_for_choice(song):
    if song.get("audio_url"):
        return song["audio_url"], song.get("title"), song.get("artist")
    payload = song.get("raw") or {}
    for endpoint in DOWNLOAD_ENDPOINTS:
        query_pairs = []
        if song.get("video_url"):
            query_pairs.append(("url", song["video_url"]))
            query_pairs.append(("query", song["video_url"]))
        if song.get("video_id"):
            query_pairs.append(("id", song["video_id"]))
            query_pairs.append(("video_id", song["video_id"]))
        if song.get("title"):
            query_pairs.append(("query", song["title"]))
        for key in ("url", "link", "video_url", "videoId", "video_id"):
            if isinstance(payload.get(key), str):
                query_pairs.append(("url", payload[key]))
        for key, value in query_pairs:
            api = f"{API_URL}/{endpoint}?{key}={quote_plus(str(value))}"
            try:
                data = await async_searcher(api, re_json=True)
            except Exception:
                continue
            song_url, title, artist = _extract_song_data(data)
            if song_url:
                return song_url, title or song.get("title"), artist or song.get("artist")
    return None, song.get("title"), song.get("artist")


@champu_cmd(pattern=r"lyrics ?(.*)")
async def original(event):
    if not event.pattern_match.group(1):
        return await event.eor("give query to search.")
    noob = event.pattern_match.group(1)
    ab = await event.eor("Getting lyrics..")
    dc = random.randrange(1, 3)
    if dc == 1:
        danish = "AIzaSyAyDBsY3WRtB5YPC6aB_w8JAy6ZdXNc6FU"
    elif dc == 2:
        danish = "AIzaSyBF0zxLlYlPMp9xwMQqVKCQRq8DgdrLXsg"
    else:
        danish = "AIzaSyDdOKnwnPwVIQ_lbH5sYE4FoXjAKIQV0DQ"
    extract_lyrics = sl(danish, "15b9fb6193efd5d90")
    try:
        sh1vm = await extract_lyrics.get_lyrics(noob)
    except LyError:
        return await eod(event, "No Results Found")
    a7ul = sh1vm["lyrics"]
    await event.client.send_message(event.chat_id, a7ul, reply_to=event.reply_to_msg_id)
    await ab.delete()


@champu_cmd(pattern="song ?(.*)")
async def _(event):
    champu_bot = event.client
    args = event.pattern_match.group(1)
    if not args:
        return await event.eor("`Enter song name`")
    okla = await event.eor("`Searching songs...`")
    try:
        songs = await _search_songs(args)
        if not songs:
            song_url, title, artist = await _fetch_song_details(args)
            if not song_url:
                return await okla.eor("`Song not found.`")
            caption = f"**{title or args}**"
            if artist:
                caption += f"\n__{artist}__"
            await champu_bot.send_file(
                event.chat_id,
                song_url,
                caption=caption,
                supports_streaming=True,
            )
            return await okla.delete()

        songs = songs[:10]
        picker = await okla.edit(_build_song_list_text(songs), buttons=_build_song_buttons(len(songs)))
        async with champu_bot.conversation(event.chat_id, timeout=45) as conv:
            response = await conv.wait_event(
                events.CallbackQuery(
                    chats=event.chat_id,
                    func=lambda q: q.sender_id == event.sender_id
                    and q.message_id == picker.id
                    and q.data
                    and q.data.startswith(b"songsel:"),
                )
            )
        choice = response.data.decode("utf-8").split(":", 1)[1]
        if choice == "cancel":
            await response.answer("Cancelled", alert=False)
            return await picker.edit("`Selection cancelled.`", buttons=None)
        await response.answer("Selected", alert=False)
        if not choice.isdigit():
            return await picker.edit("`Invalid selection.`", buttons=None)
        index = int(choice)
        if index < 1 or index > len(songs):
            return await picker.edit("`Choice out of range.`", buttons=None)
        selected = songs[index - 1]
        await picker.edit("`Downloading selected song...`", buttons=None)
        song_url, title, artist = await _resolve_audio_for_choice(selected)
        if not song_url:
            return await picker.edit("`Unable to fetch audio for selected song.`")
        caption = f"**{title or selected.get('title') or args}**"
        if artist:
            caption += f"\n__{artist}__"
        if selected.get("duration"):
            caption += f"\n`Duration:` {selected['duration']}"
        if selected.get("video_url"):
            caption += f"\n[YouTube Link]({selected['video_url']})"
        await champu_bot.send_file(
            event.chat_id,
            song_url,
            caption=caption,
            supports_streaming=True,
            reply_to=event.reply_to_msg_id,
        )
        await picker.delete()
    except asyncio.TimeoutError:
        return await okla.edit("`Selection timed out. Run .song again.`")
    except Exception:
        return await okla.eor("`Song not found.`")
