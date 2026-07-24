"""
✘ Commands Available -

• `{i}song <search query>`
    Inline song search and downloader.

"""

from random import choice

from addons.waifu import deEmojify

from . import champu_cmd, get_string



@champu_cmd(pattern="song ?(.*)")
async def nope(doit):
    ok = doit.pattern_match.group(1)
    replied = await doit.get_reply_message()
    a = await doit.eor(get_string("com_1"))
    if ok:
        pass
    elif replied and replied.message:
        ok = replied.message
    else:
        return await doit.eor(
            "`Sir please give some query to search and download it for you..!`",
        )
    sticcers = await doit.client.inline_query("Lybot", f"{(deEmojify(ok))}")
    if not sticcers:
        return await a.edit("❌ **No results found for your song query.**")

    result_to_send = None
    for res in sticcers:
        if getattr(res, "document", None) is not None:
            result_to_send = res
            break

    if result_to_send:
        try:
            await doit.reply(file=result_to_send.document)
            await a.delete()
        except Exception:
            try:
                await result_to_send.click(doit.chat_id, reply_to=doit.reply_to_msg_id or doit.id, hide_via=True)
                await a.delete()
            except Exception as click_err:
                await a.edit(f"❌ **Failed to send song:** `{click_err}`")
    else:
        try:
            await sticcers[0].click(doit.chat_id, reply_to=doit.reply_to_msg_id or doit.id, hide_via=True)
            await a.delete()
        except Exception as err:
            await a.edit(f"❌ **Failed to send song:** `{err}`")

