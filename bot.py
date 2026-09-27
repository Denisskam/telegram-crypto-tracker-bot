import asyncio
import os
import httpx
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from services_for_bot import get_crypto, get_fiat

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Error: BOT_TOKEN not found in .env!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

class ConvertState(StatesGroup):
    waiting_for_amount = State()

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Cryptocurrency exchange rate")],
        [KeyboardButton(text="💵 Exchange rate (NBU)")],
        [KeyboardButton(text="🧮 Conversion calculator")],
    ],
    resize_keyboard=True,
    persistent=True
)

@dp.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Welcome! I am a bot for tracking currency and cryptocurrency rates.\n"
        "Choose an option below 👇",
        reply_markup=main_keyboard
    )

@dp.message(F.text == "📊 Cryptocurrency exchange rate")
async def crypto_handler(message: types.Message):
    async with httpx.AsyncClient() as client:
        prices = await get_crypto(client)

    if not prices:
        await message.answer("⚠️ The CoinGecko service is temporarily unavailable. Try again later.")
        return

    text = (
        "<b>📊 Current exchange rate of cryptocurrencies:</b>\n\n"
        f"🪙 Bitcoin (BTC): <b>${prices['BTC']:,.2f}</b>\n"
        f"💎 Ethereum (ETH): <b>${prices['ETH']:,.2f}</b>\n"
        f"🟣 Solana (SOL): <b>${prices['SOL']:,.2f}</b>"
    )
    await message.answer(text, parse_mode="HTML")

@dp.message(F.text == "💵 Exchange rate (NBU)")
async def fiat_handler(message: types.Message):
    async with httpx.AsyncClient() as client:
        fiat_rates = await get_fiat(client)

    if not fiat_rates:
        await message.answer("⚠️ The NBU service is temporarily unavailable. Try again later.")
        return

    text = (
        "<b>💵 Official exchange rate (NBU):</b>\n\n"
        f"🇺🇸 USD: <b>{fiat_rates.get('USD', 0.0):.2f} UAH</b>\n"
        f"🇪🇺 EUR: <b>{fiat_rates.get('EUR', 0.0):.2f} UAH</b>"
    )
    await message.answer(text, parse_mode="HTML")

@dp.message(F.text == "🧮 Conversion calculator")
async def calc_start_handler(message: types.Message, state: FSMContext):
    await state.set_state(ConvertState.waiting_for_amount)
    await message.answer("🧮 Enter the amount in <b>USD</b> to convert (e.g. <code>250</code>):", parse_mode="HTML")


@dp.message(ConvertState.waiting_for_amount)
async def calc_process_amount(message: types.Message, state: FSMContext):

    try:
        usd_amount = float(message.text.replace(",", "."))
        if usd_amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer("⚠️ Please enter a valid positive number (e.g. <code>100</code> or <code>50.5</code>):", parse_mode="HTML")
        return

    async with httpx.AsyncClient() as client:
        crypto_prices, fiat_rates = await asyncio.gather(
            get_crypto(client),
            get_fiat(client)
        )

    if not crypto_prices or not fiat_rates:
        await message.answer("⚠️ Exchange rate services are temporarily unavailable. Try again in a minute.")
        await state.clear()
        return

    usd_to_uah = fiat_rates.get("USD", 0.0)
    btc_price = crypto_prices.get("BTC", 0.0)

    uah_total = usd_amount * usd_to_uah
    btc_total = usd_amount / btc_price if btc_price else 0.0
    satoshi_total = int(btc_total * 100_000_000)

    result_text = (
        f"<b>🧮 Conversion results for ${usd_amount:,.2f} USD:</b>\n\n"
        f"🇺🇦 <b>{uah_total:,.2f} UAH</b> (at NBU rate: {usd_to_uah:.2f})\n"
        f"🪙 <b>{btc_total:.8f} BTC</b> (~{satoshi_total:,} satoshi)"
    )
    await message.answer(result_text, parse_mode="HTML")
    await state.clear()

async def main():
    print("Bot successfully launched and listens to messages ;)")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())