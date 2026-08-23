import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

API_TOKEN = "8830629039:AAHz3xUENXP9GSkvC7we3_EvS-uDhRLt0LE"  # የቦት ቶከንህን አስገባ
WEB_APP_URL = "https://sami37-cpu.github.io/my-bingo-bot/"  # የ Mini App ህ Link

CHANNELS = ["@alpha_bet_12", "@safarigiftti", "@safariicomgift", "@safariicom_gift", "@Big_Tech_sami", "@proofofpaymenty"]

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def check_force_join(user_id: int) -> bool:
    for ch in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=ch, user_id=user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception:
            return False
    return True

def get_sub_keyboard():
    buttons = [[InlineKeyboardButton(text=f"ቻናል {i+1}", url=f"https://t.me/{ch.replace('@', '')}")] for i, ch in enumerate(CHANNELS)]
    buttons.append([InlineKeyboardButton(text="አረጋግጥ ✅", callback_data="check_join")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 MY BINGO ክፈት", web_app=WebAppInfo(url=WEB_APP_URL))]
    ])

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    if not await check_force_join(message.from_user.id):
        await message.answer("🚨 ቦቱን ለመጠቀም እባክዎን የ6ቱን ቻናሎች ይቀላቀሉ:", reply_markup=get_sub_keyboard())
        return

    await message.answer(
        "እንኳን ወደ **MY BINGO** በደህና መጡ! 🎲\n\nጨዋታውን ለመጀመር ከታች ያለውን ቁልፍ ይጫኑ:",
        reply_markup=main_keyboard(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "check_join")
async def check_join_callback(call: types.CallbackQuery):
    if await check_force_join(call.from_user.id):
        await call.message.edit_text("ምዝገባዎ ተጠናቋል! ከታች ያለውን ቁልፍ ተጭነው መጫወት ይችላሉ:", reply_markup=main_keyboard())
    else:
        await call.answer("እባክዎን ሁሉንም 6 ቻናሎች ይቀላቀሉ!", show_alert=True)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
