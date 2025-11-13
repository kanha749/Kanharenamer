import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait

# -----------------------------
#  EDIT YOUR CREDENTIALS HERE
# -----------------------------
API_ID = 21302239
API_HASH = "1560930c983fbca6a1fcc8eab760d40d"
BOT_TOKEN = "8257399725:AAG278Z_ndrdWgxTQuu7DQugXaoCdf1xW0M"

# -----------------------------
# OPTIONAL SETTINGS
# -----------------------------
DOWNLOAD_DIR = "./downloads/"

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

app = Client(
    "renamer-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)


# -----------------------------
# START COMMAND
# -----------------------------
@app.on_message(filters.command("start"))
async def start_cmd(_, m: Message):
    await m.reply_text(
        f"👋 Hello {m.from_user.first_name}!\n\n"
        "📁 Send me any file and I will rename it.\n"
        "🖼 Thumbnail supported (send /thumbnail)\n\n"
        "Made By: Kanha"
    )


# -----------------------------
# SAVE THUMBNAIL
# -----------------------------
@app.on_message(filters.command("thumbnail"))
async def set_thumb(_, m: Message):
    await m.reply_text("📸 Send me the thumbnail photo…")


@app.on_message(filters.photo & filters.reply)
async def save_thumb(_, m: Message):
    if m.reply_to_message.text and "thumbnail" in m.reply_to_message.text.lower():
        thumb_path = f"{m.from_user.id}.jpg"
        await m.download(thumb_path)
        await m.reply_text("✅ Thumbnail Saved!")


# -----------------------------
# RENAME HANDLER
# -----------------------------
@app.on_message(filters.document | filters.video | filters.audio)
async def rename_file(_, m: Message):
    media = m.document or m.video or m.audio
    file_name = media.file_name

    sent = await m.reply_text(
        f"📥 Downloading...\n\n**File:** `{file_name}`"
    )

    try:
        file_path = await m.download(DOWNLOAD_DIR)

        await sent.edit("✏️ Send me new file name (with extension):")

        # Wait for reply
        new_name_msg = await app.listen(m.chat.id, timeout=120)
        new_name = new_name_msg.text

        new_path = DOWNLOAD_DIR + new_name
        os.rename(file_path, new_path)

        await sent.edit("📤 Uploading…")

        thumb = f"{m.from_user.id}.jpg"
        if not os.path.exists(thumb):
            thumb = None

        await m.reply_document(
            new_path,
            caption=f"✅ Renamed Successfully!\n\n**New Name:** `{new_name}`",
            thumb=thumb
        )

        os.remove(new_path)

    except FloodWait as e:
        time.sleep(e.x)
    except Exception as e:
        await sent.edit(f"⚠️ Error: `{e}`")


# -----------------------------
# BOT RUN
# -----------------------------
print("🚀 Renamer Bot Started by Kanha!")
app.run()
