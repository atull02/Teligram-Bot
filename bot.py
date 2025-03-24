from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import ffmpeg

API_ID = os.getenv("29957885")
API_HASH = os.getenv("df2f91e241c8250af285ae0569a96a74")
BOT_
TOKEN = os.getenv("8032569973:AAGlPIKFQJmA1s4nELWsADTegY8RpmfLryo")

app = Client("video_compressor_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

video_dict = {}  # यूजर के वीडियो को स्टोर करने के लिए

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("👋 नमस्ते! पहले कोई वीडियो अपलोड करें, फिर मैं आपको क्वालिटी चुनने का ऑप्शन दूंगा।")

# **यूजर से पहले वीडियो अपलोड करवाना**
@app.on_message(filters.video)
async def ask_quality(client, message):
    user_id = message.from_user.id
    video_dict[user_id] = await message.download()
    
    await message.reply_text(
        "📥 आपका वीडियो अपलोड हो गया! अब कृपया क्वालिटी चुनें:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("144p", callback_data="144p"), InlineKeyboardButton("240p", callback_data="240p")],
            [InlineKeyboardButton("360p", callback_data="360p"), InlineKeyboardButton("480p", callback_data="480p")],
            [InlineKeyboardButton("720p", callback_data="720p"), InlineKeyboardButton("1080p", callback_data="1080p")]
        ])
    )

# **यूजर की चुनी हुई क्वालिटी को स्टोर करना और वीडियो कंप्रेस करना**
@app.on_callback_query()
async def compress_video(client, callback_query):
    user_id = callback_query.from_user.id
    if user_id not in video_dict:
        await callback_query.message.edit_text("⚠ कोई वीडियो नहीं मिला! कृपया पहले वीडियो अपलोड करें।")
        return
    
    video_path = video_dict[user_id]
    quality = callback_query.data

    resolutions = {
        "144p": "256:144",
        "240p": "426:240",
        "360p": "640:360",
        "480p": "854:480",
        "720p": "1280:720",
        "1080p": "1920:1080"
    }

    if quality in resolutions:
        output_video = f"compressed_{quality}.mp4"
        
        await callback_query.message.edit_text(f"🔄 वीडियो {quality} में कंप्रेस किया जा रहा है...")

        ffmpeg.input(video_path).output(output_video, vcodec='libx264', crf=28, preset='fast', vf=f'scale={resolutions[quality]}').run()
        
        await callback_query.message.reply_text(
            "✅ कंप्रेस किया गया वीडियो डाउनलोड या शेयर करें:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬇ Download", callback_data=f"download_{output_video}")],
                [InlineKeyboardButton("🔗 Share", switch_inline_query="Check out this compressed video!")]
            ])
        )

        video_dict[user_id] = output_video  # कंप्रेस वीडियो सेव करना

# **"Download" बटन पर क्लिक करने के बाद वीडियो भेजना**
@app.on_callback_query(filters.regex("^download_"))
async def send_compressed_video(client, callback_query):
    file_name = callback_query.data.split("_")[1]
    await callback_query.message.reply_video(file_name, caption="🎬 यह रहा आपका कंप्रेस किया गया वीडियो!")
    
    os.remove(file_name)  # वीडियो भेजने के बाद डिलीट करना

app.run()
