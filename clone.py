"""
✘ Commands Available

• `{i}clone <reply/username>`
    clone the identity of user.

• `{i}revert`
    Revert to your original identity
"""
import html
import os
from pathlib import Path

from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import DeletePhotosRequest, UploadProfilePhotoRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import MessageEntityMentionName

from . import *


def _clone_key(suffix):
    return f"{champu_bot.uid}:clone:{suffix}"


def _backup_photo_path():
    backup_dir = Path("resources/startup")
    backup_dir.mkdir(parents=True, exist_ok=True)
    return str(backup_dir / f"clone_backup_{champu_bot.uid}.jpg")


def _target_photo_path(target_id):
    tmp_dir = Path("resources/downloads")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    return str(tmp_dir / f"clone_target_{target_id}.jpg")


@champu_cmd(pattern="clone ?(.*)", fullsudo=True)
async def _(event):
    eve = await event.eor("Processing...")
    reply_message = await event.get_reply_message()
    whoiam = await event.client(GetFullUserRequest(champu_bot.uid))
    # Save original profile info for revert.
    udB.set_key(_clone_key("bio"), whoiam.full_user.about or "")
    udB.set_key(_clone_key("first_name"), whoiam.users[0].first_name or "")
    udB.set_key(_clone_key("last_name"), whoiam.users[0].last_name or "")

    # Save current profile photo explicitly to avoid Telethon filename inference issues.
    my_photo = None
    try:
        my_photo = await event.client.download_profile_photo("me", file=_backup_photo_path())
    except Exception:
        my_photo = None
    udB.set_key(_clone_key("photo"), my_photo or "")

    replied_user, error_i_a = await get_full_user(event)
    if replied_user is None:
        await eve.edit(str(error_i_a))
        return
    user_id = replied_user.users[0].id
    profile_pic = None
    try:
        profile_pic = await event.client.download_profile_photo(
            replied_user.users[0], file=_target_photo_path(user_id)
        )
    except Exception:
        profile_pic = None
    first_name = html.escape(replied_user.users[0].first_name)
    if first_name is not None:
        first_name = first_name.replace("\u2060", "")
    last_name = replied_user.users[0].last_name
    if last_name is not None:
        last_name = html.escape(last_name)
        last_name = last_name.replace("\u2060", "")
    if last_name is None:
        last_name = "⁪⁬⁮⁮⁮"
    user_bio = replied_user.full_user.about or ""
    await event.client(UpdateProfileRequest(first_name=first_name))
    await event.client(UpdateProfileRequest(last_name=last_name))
    await event.client(UpdateProfileRequest(about=user_bio))
    if profile_pic:
        pfile = await event.client.upload_file(profile_pic)
        await event.client(UploadProfilePhotoRequest(file=pfile))
        if os.path.exists(profile_pic):
            os.remove(profile_pic)
    await eve.delete()
    await event.client.send_message(
        event.chat_id, f"I am {first_name} from now...", reply_to=reply_message
    )


@champu_cmd(pattern="revert$")
async def _(event):
    name = udB.get_key(_clone_key("first_name")) or OWNER_NAME
    bio = udB.get_key(_clone_key("bio"))
    lname = udB.get_key(_clone_key("last_name")) or ""
    ok = lname
    n = 1
    client = event.client

    if bio is None:
        try:
            whoiam = await event.client(GetFullUserRequest(champu_bot.uid))
            bio = whoiam.full_user.about or ""
        except Exception:
            bio = ""

    await client(
        DeletePhotosRequest(await event.client.get_profile_photos("me", limit=n))
    )
    await client(UpdateProfileRequest(about=bio))
    await client(UpdateProfileRequest(first_name=name))
    await client(UpdateProfileRequest(last_name=ok))

    # Restore original profile photo if available.
    old_photo = udB.get_key(_clone_key("photo"))
    if old_photo and os.path.exists(old_photo):
        pfile = await event.client.upload_file(old_photo)
        await event.client(UploadProfilePhotoRequest(file=pfile))

    await event.eor("Succesfully reverted to your account back !")
    udB.del_key(_clone_key("bio"))
    udB.del_key(_clone_key("first_name"))
    udB.del_key(_clone_key("last_name"))
    udB.del_key(_clone_key("photo"))


async def get_full_user(event):
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        if previous_message.forward:
            replied_user = await event.client(
                GetFullUserRequest(
                    previous_message.forward.sender_id
                    or previous_message.forward.channel_id
                )
            )
            return replied_user, None
        replied_user = await event.client(
            GetFullUserRequest(previous_message.sender_id)
        )
        return replied_user, None
    else:
        input_str = None
        try:
            input_str = event.pattern_match.group(1)
        except IndexError as e:
            return None, e
        if event.message.entities is not None:
            mention_entity = event.message.entities
            probable_user_mention_entity = mention_entity[0]
            if isinstance(probable_user_mention_entity, MessageEntityMentionName):
                user_id = probable_user_mention_entity.user_id
                replied_user = await event.client(GetFullUserRequest(user_id))
                return replied_user, None
            try:
                user_object = await event.client.get_entity(input_str)
                user_id = user_object.id
                replied_user = await event.client(GetFullUserRequest(user_id))
                return replied_user, None
            except Exception as e:
                return None, e
        elif event.is_private:
            try:
                user_id = event.chat_id
                replied_user = await event.client(GetFullUserRequest(user_id))
                return replied_user, None
            except Exception as e:
                return None, e
        else:
            try:
                user_object = await event.client.get_entity(int(input_str))
                user_id = user_object.id
                replied_user = await event.client(GetFullUserRequest(user_id))
                return replied_user, None
            except Exception as e:
                return None, e
