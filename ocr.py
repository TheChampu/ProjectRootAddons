"""
✘ Commands Available -

• `{i}ocr <language code><reply to a photo>`
    text recognition service.
"""


from telegraph import upload_file as uf

from . import *

TE = f"API not found, Please get it from ocr.space and set\n\ncommand `{HNDLR}setdb OCR_API your-api-key`"


@champu_cmd(pattern="ocr ?(.*)")
async def ocrify(ult):
    if not ult.is_reply:
        return await ult.eor("`Reply to Photo...`")
    msg = await ult.eor("`Processing..`")
    OAPI = udB.get_key("OCR_API")
    if not OAPI:
        return await msg.edit(TE)
    pat = ult.pattern_match.group(1)
    repm = await ult.get_reply_message()
    if not (repm.media and repm.media.photo):
        return await msg.edit("`Not a Photo..`")
    dl = await repm.download_media()
    atr = ""
    if pat:
        atr = f"&language={pat}"
    tt = uf(dl)
    li = "https://telegra.ph" + tt[0]
    gr = await async_searcher(
        f"https://api.ocr.space/parse/imageurl?apikey={OAPI}{atr}&url={li}",
        re_json=True,
    )
    trt = gr["ParsedResults"][0]["ParsedText"]
    await msg.edit(f"**🎉 OCR PORTAL\n\nRESULTS ~ ** `{trt}`")
