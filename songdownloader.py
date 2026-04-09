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
    await doit.reply(file=sticcers[0].document)
    await a.delete()

