import os
import ffmpeg
from pyrogram import Client, filters
from keepalive import keep_alive

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("WebRenamerThumb", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ---------------- START ----------------
@app.on_message(filters.command("start"))
async def start(_, m):
    await m.reply(
        "**👋 Web Service Renamer + Thumbnail Bot**\n"
        "Send me any video/document.\n\n"
        "Choose: Rename / Thumbnail."
    )


# ---------------- CHOOSE ----------------
@app.on_message(filters.video | filters.document)
async def choose(_, m):
    await m.reply(
        "What do you want to do?",
        reply_markup=filters.InlineKeyboardMarkup(
            [
                [
                    filters.InlineKeyboardButton("✏ Rename", callback_data="rename"),
                    filters.InlineKeyboardButton("🖼 Thumbnail", callback_data="thumb")
                ]
            ]
        )
    )
    app.last_msg = m


# ------------- CALLBACKS --------------
@app.on_callback_query()
async def callback(app, query):
    if query.data == "rename":
        await query.message.reply("Send new file name:")
        app.waiting_rename = True

    elif query.data == "thumb":
        await query.message.reply("Send new thumbnail image:")
        app.waiting_thumb = True


# ------------- RECEIVE NEW NAME -------------
@app.on_message(filters.text)
async def rename_file(app, m):
    if not getattr(app, "waiting_rename", False):
        return

    new_name = m.text
    file = app.last_msg

    downloaded = await file.download()
    ext = os.path.splitext(downloaded)[1]
    new_file = new_name + ext

    os.rename(downloaded, new_file)

    await m.reply_document(new_file, caption="✔ File Renamed!")
    app.waiting_rename = False


# ------------- RECEIVE THUMBNAIL -------------
@app.on_message(filters.photo)
async def set_thumb(app, m):
    if not getattr(app, "waiting_thumb", False):
        return

    video = app.last_msg
    vfile = await video.download("video.mp4")
    thumb = await m.download("thumb.jpg")

    output = "output.mp4"

    try:
        ffmpeg.input(vfile).output(
            output,
            vcodec="copy",
            acodec="copy",
            **{"metadata:s:v": "title=Thumbnail Updated"}
        ).run(overwrite_output=True)
    except Exception as e:
        await m.reply(f"Error: {e}")
        return

    await m.reply_video(output, caption="✔ Thumbnail Updated!")
    app.waiting_thumb = False


# -------- START BOT + WEB SERVER --------
keep_alive()
app.run()
