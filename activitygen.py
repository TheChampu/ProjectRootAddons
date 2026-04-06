 """
✘ Commands Available -

• `{i}bored`
    Get some activity to do when you get bored
"""

from . import async_searcher, champu_cmd


@champu_cmd(pattern="bored$")
async def bored_cmd(event):
    msg = await event.eor("`Generating an Activity for You!`")
    content = await async_searcher(
        "https://bored-api.appbrewery.com/random", re_json=True
    )
    m = f"**Activity:** `{content['activity']}`"
    if content.get("link"):
        m += f"\n**Read More:** {content['link']}"
    if content.get("participants"):
        m += f"\n**Participants Required:** `{content['participants']}`"
    if content.get("price"):
        m += f"\n**Price:** `{content['price']}`"
    await msg.edit(m)