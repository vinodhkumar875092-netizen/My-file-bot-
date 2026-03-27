import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from motor.motor_asyncio import AsyncIOMotorClient
from pyrogram.errors import UserNotParticipant
import os

# Env Variables (Koyeb par set karenge)
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
MONGO_URL = os.environ.get("MONGO_URL")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

# Links
TG_CHANNEL = "YourUsername"
YT_VIDEO_LIKE = "https://youtube.com/watch?v=your_video_id" # Like karne wali video

app = Client("FileBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
db = AsyncIOMotorClient(MONGO_URL).FileStoreBot.files

def get_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{TG_CHANNEL}")],
        [InlineKeyboardButton("👍 Like Video", url=YT_VIDEO_LIKE)],
        [InlineKeyboardButton("✅ Done / Check", callback_data="check_subs")]
    ])

@app.on_message(filters.command("start") & filters.private)
async def start(c, m):
    if len(m.command) > 1:
        try:
            await c.get_chat_member(TG_CHANNEL, m.from_user.id)
        except:
            return await m.reply_text("❌ Pehle Channel Join aur Video Like karein!", reply_markup=get_buttons())
        
        file = await db.find_one({"_id": m.command[1]})
        if file:
            msg = await c.send_cached_media(m.chat.id, file["file_id"], caption="8 min mein delete ho jayega!")
            await asyncio.sleep(480)
            await msg.delete()
    else:
        await m.reply_text("Admin, send file.")

@app.on_message((filters.document | filters.video) & filters.user(ADMIN_ID))
async def upload(c, m):
    fid = m.document.file_id if m.document else m.video.file_id
    res = await db.insert_one({"file_id": fid})
    me = await c.get_me()
    await m.reply_text(f"Link: `https://t.me/{me.username}?start={res.inserted_id}`")

app.run()
