import asyncio
import random

from . import champu_cmd


def _display_name(user):
	if not user:
		return "Someone"
	return getattr(user, "first_name", None) or getattr(user, "title", None) or "Someone"


@champu_cmd(pattern="chummi(?: |$)(.*)")
async def chummi_kiss(event):
	target = (event.pattern_match.group(1) or "").strip()

	reply = await event.get_reply_message()
	if reply:
		sender = reply.sender or await reply.get_sender()
		if sender:
			target = target or _display_name(sender)

	if not target:
		target = "Someone"

	kiss_frames = [
		f"😗 {target}",
		f"😙 {target}",
		f"😚 {target}",
		f"😘 {target}",
		f"💋 {target}",
		f"😘💋😚 {target}",
		f"💋💋💋 {target}",
		f"😂 Arre {target}, itni saari chummiyan le lo!",
	]

	msg = await event.eor("😏 Chummi loading...")

	for frame in kiss_frames:
		try:
			await msg.edit(frame)
		except Exception:
			break
		await asyncio.sleep(random.uniform(0.5, 1.0))

	await asyncio.sleep(1)
	try:
		await msg.edit(f"🥰 {target} ko pyaari si chummi delivered successfully 💋")
	except Exception:
		await event.client.send_message(
			event.chat_id,
			f"🥰 {target} ko pyaari si chummi delivered successfully 💋",
			reply_to=event.reply_to_msg_id,
		)
