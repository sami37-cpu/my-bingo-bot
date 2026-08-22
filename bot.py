import asyncio
import random
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import database as db

API_TOKEN = "8830629039:AAHz3xUENXP9GSkvC7we3_EvS-uDhRLt0LE" # የቦት ቶከንዎን እዚህ ያስገቡ

# የ6ቱ ቻናሎች Username (ወይም Chat ID)
CHANNELS = ["@alpha_bet_12", "@safarigiftti", "@safariicomgift", "@safariicom_gift", "@Big_Tech_sami", "@proofofpaymenty"]

NAMES = ["አዲሱ", "ሄኖክ", "ዳምጠው", "ኤላ", "ሳሙኤል", "መብራቱ"]
PRIZES = [850, 800, 720, 910, 630]

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

class WithdrawForm(StatesGroup):
    phone_number = State()

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
        [InlineKeyboardButton(text="🎲 Bingo ተጫወት (10 ብር)", callback_data="play_bingo")],
        [InlineKeyboardButton(text="💰 ቀሪ ሂሳብ (Balance)", callback_data="show_balance")],
        [InlineKeyboardButton(text="🔗 የጋበዙት ሰው (Referral)", callback_data="show_ref")],
        [InlineKeyboardButton(text="💸 ብር ለማውጣት (Withdraw)", callback_data="withdraw")]
    ])

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    args = message.text.split()
    ref_id = int(args[1]) if len(args) > 1 and args[1].isdigit() else None

    await db.register_user(message.from_user.id, ref_id)

    if not await check_force_join(message.from_user.id):
        await message.answer("🚨 ቦቱን ለመጠቀም እባክዎን የሚከተሉትን 6 ቻናሎች ይቀላቀሉ:", reply_markup=get_sub_keyboard())
        return

    await message.answer("እንኳን ወደ Bingo Simulation Bot በደህና መጡ! 🎁 20 ብር የጀማሪ ቦነስ ተሰጥቶዎታል።", reply_markup=main_keyboard())

@dp.callback_query(F.data == "check_join")
async def check_join_callback(call: types.CallbackQuery):
    if await check_force_join(call.from_user.id):
        await call.message.edit_text("ምዝገባዎ ተጠናቋል! ከታች ካሉት አማራጮች ይምረጡ:", reply_markup=main_keyboard())
    else:
        await call.answer("እባክዎን ሁሉንም 6 ቻናሎች ይቀላቀሉ!", show_alert=True)

@dp.callback_query(F.data == "show_balance")
async def balance_handler(call: types.CallbackQuery):
    user = await db.get_user(call.from_user.id)
    balance = user[0] if user else 0.0
    await call.message.answer(f"💳 የእርስዎ ቀሪ ሂሳብ: {balance} ብር")

@dp.callback_query(F.data == "show_ref")
async def ref_handler(call: types.CallbackQuery):
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={call.from_user.id}"
    user = await db.get_user(call.from_user.id)
    refs = user[1] if user else 0
    await call.message.answer(f"🔗 የእርስዎ የጋበዟቸው ሰዎች ብዛት: {refs}\n\nየጋበዙበት ሊንክ:\n{ref_link}\n\n1 ሰው ሲጋብዙ 10 ብር ያገኛሉ!")

@dp.callback_query(F.data == "play_bingo")
async def bingo_handler(call: types.CallbackQuery):
    if not await check_force_join(call.from_user.id):
        await call.message.answer("እባክዎን መጀመሪያ ቻናሎቹን ይቀላቀሉ!", reply_markup=get_sub_keyboard())
        return

    await db.increment_game(call.from_user.id)
    card_number = random.randint(1, 500)
    winner_name = random.choice(NAMES)
    prize_amount = random.choice(PRIZES)

    msg = f"🎟 የBingo ካርድ ቁጥርዎ: **{card_number}** (ከ 500)\n\n"
    msg += "ቁጥሮች በመውጣት ላይ ናቸው...\n"
    msg += "━━━━━━━\n"
    msg += f"🎉 Bingo! ደራሽ ደርሷል!\n"
    msg += f"👤 የአሸናፊ ስም: **{winner_name}**\n"
    msg += f"💰 የደረሰው መጠን: **{prize_amount} ብር**\n\n"
    msg += "ለእርስዎ አልደረሰዎትም። እንደገና ይሞክሩ!"

    await call.message.answer(msg, parse_mode="Markdown")

@dp.callback_query(F.data == "withdraw")
async def withdraw_handler(call: types.CallbackQuery, state: FSMContext):
    user = await db.get_user(call.from_user.id)
    if not user:
        return

    balance, refs, games = user

    if balance < 50:
        await call.answer("ዝቅተኛው የማውጫ መጠን 50 ብር ነው!", show_alert=True)
        return
    if refs < 10:
        await call.message.answer("❌ ብር ለማውጣት ቢያንስ 10 ሰው መጋበዝ አለብዎት!")
        return
    if games < 8:
        await call.message.answer("❌ ብር ለማውጣት ቢያንስ 8 ጊዜ Bingo መጫወት አለብዎት!")
        return

    await state.set_state(WithdrawForm.phone_number)
    await call.message.answer("📱 እባክዎን የTelebirr ስልክ ቁጥርዎን ያስገቡ:")

@dp.message(WithdrawForm.phone_number)
async def process_phone(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ ይቅርታ! ያሉት ቀሪ ሂሳብ ለማውጣት በቂ አይደለም።")

async def main():
    await db.init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# ቦትህ ከመነሳቱ በፊት keep_alive() ን ጥራ:
keep_alive()
