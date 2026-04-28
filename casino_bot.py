"""
🎰 Telegram Stars Casino Bot
Требования: pip install python-telegram-bot==20.7
Запуск: python casino_bot.py
"""

import logging
import random
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    PreCheckoutQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ──────────────────────────────────────────────
# НАСТРОЙКИ — замени на свои значения
# ──────────────────────────────────────────────
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"   # токен от @BotFather

# ──────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ─── Хранилище балансов (в памяти; для продакшна используй БД)
user_balances: dict[int, int] = {}

SLOT_SYMBOLS = ["🍒", "🍋", "🍊", "🍇", "⭐", "💎", "7️⃣"]
SLOT_WINS = {
    ("💎", "💎", "💎"): 50,
    ("7️⃣", "7️⃣", "7️⃣"): 30,
    ("⭐", "⭐", "⭐"): 20,
    ("🍇", "🍇", "🍇"): 10,
    ("🍊", "🍊", "🍊"): 8,
    ("🍋", "🍋", "🍋"): 6,
    ("🍒", "🍒", "🍒"): 5,
}


def get_balance(user_id: int) -> int:
    return user_balances.get(user_id, 0)


def add_balance(user_id: int, amount: int) -> int:
    user_balances[user_id] = get_balance(user_id) + amount
    return user_balances[user_id]


def spend_balance(user_id: int, amount: int) -> bool:
    """Списывает звёзды. Возвращает True при успехе."""
    if get_balance(user_id) >= amount:
        user_balances[user_id] = get_balance(user_id) - amount
        return True
    return False


# ─── /start ──────────────────────────────────
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    text = (
        f"🎰 Добро пожаловать в <b>Stars Casino</b>, {user.first_name}!\n\n"
        f"💫 Ваш баланс: <b>{get_balance(user.id)} ⭐</b>\n\n"
        "Пополните баланс звёздами и испытайте удачу!\n\n"
        "📋 <b>Команды:</b>\n"
        "/balance — текущий баланс\n"
        "/deposit — пополнить (5 ⭐)\n"
        "/slots — слоты (ставка 2 ⭐)\n"
        "/roulette — рулетка (ставка 3 ⭐)\n"
        "/coin — монетка (ставка 1 ⭐)\n"
        "/help — справка"
    )
    await update.message.reply_html(text)


# ─── /balance ────────────────────────────────
async def balance(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    await update.message.reply_html(
        f"💰 Ваш баланс: <b>{get_balance(uid)} ⭐</b>"
    )


# ─── /deposit — выставляем инвойс на 5 звёзд ─
async def deposit(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await ctx.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title="Пополнение баланса казино",
        description="Добавит 5 ⭐ на ваш игровой счёт",
        payload="deposit_5_stars",
        currency="XTR",           # валюта Telegram Stars
        prices=[LabeledPrice("5 звёзд", 5)],
        provider_token="",         # для Stars оставляем пустым
    )


# ─── Pre-checkout (обязательно подтверждаем) ─
async def precheckout(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.pre_checkout_query
    await query.answer(ok=True)


# ─── Получение оплаты ────────────────────────
async def successful_payment(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    payment = update.message.successful_payment
    stars = payment.total_amount           # уже в Stars (целых единицах)
    new_bal = add_balance(uid, stars)
    await update.message.reply_html(
        f"✅ Оплата получена! +{stars} ⭐\n"
        f"💰 Новый баланс: <b>{new_bal} ⭐</b>"
    )


# ─── /coin — монетка ─────────────────────────
BET_COIN = 1

async def coin(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    if not spend_balance(uid, BET_COIN):
        await update.message.reply_text(
            f"❌ Недостаточно звёзд! Нужно {BET_COIN} ⭐.\n"
            "Пополните баланс: /deposit"
        )
        return

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👑 Орёл", callback_data="coin_heads"),
            InlineKeyboardButton("🦅 Решка", callback_data="coin_tails"),
        ]
    ])
    await update.message.reply_html(
        f"🪙 Ставка: <b>{BET_COIN} ⭐</b>\n"
        f"💰 Баланс после ставки: <b>{get_balance(uid)} ⭐</b>\n\n"
        "Выберите сторону монеты:",
        reply_markup=keyboard,
    )


async def coin_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    choice = query.data  # coin_heads / coin_tails

    result = random.choice(["coin_heads", "coin_tails"])
    result_emoji = "👑 Орёл" if result == "coin_heads" else "🦅 Решка"

    if choice == result:
        win = BET_COIN * 2
        add_balance(uid, win)
        text = (
            f"🪙 Выпало: <b>{result_emoji}</b>\n\n"
            f"🎉 Победа! +{win} ⭐\n"
            f"💰 Баланс: <b>{get_balance(uid)} ⭐</b>"
        )
    else:
        text = (
            f"🪙 Выпало: <b>{result_emoji}</b>\n\n"
            f"😔 Вы проиграли {BET_COIN} ⭐\n"
            f"💰 Баланс: <b>{get_balance(uid)} ⭐</b>"
        )

    await query.edit_message_text(text, parse_mode="HTML")


# ─── /slots ───────────────────────────────────
BET_SLOTS = 2

async def slots(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    if not spend_balance(uid, BET_SLOTS):
        await update.message.reply_text(
            f"❌ Недостаточно звёзд! Нужно {BET_SLOTS} ⭐.\n/deposit"
        )
        return

    reels = [random.choice(SLOT_SYMBOLS) for _ in range(3)]
    combo = tuple(reels)
    multiplier = SLOT_WINS.get(combo, 0)

    display = " | ".join(reels)

    if multiplier:
        win = BET_SLOTS * multiplier
        add_balance(uid, win)
        result_text = f"🎉 ДЖЕКПОТ! x{multiplier} → +{win} ⭐"
    elif reels[0] == reels[1] or reels[1] == reels[2]:
        # 2 одинаковых — возвращаем ставку
        add_balance(uid, BET_SLOTS)
        result_text = f"🤏 Два одинаковых — ставка возвращена ({BET_SLOTS} ⭐)"
    else:
        result_text = f"😔 Не повезло, потеряно {BET_SLOTS} ⭐"

    await update.message.reply_html(
        f"🎰 <b>[ {display} ]</b>\n\n"
        f"{result_text}\n"
        f"💰 Баланс: <b>{get_balance(uid)} ⭐</b>\n\n"
        "Сыграть ещё: /slots"
    )


# ─── /roulette ────────────────────────────────
BET_ROULETTE = 3

async def roulette(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    if not spend_balance(uid, BET_ROULETTE):
        await update.message.reply_text(
            f"❌ Недостаточно звёзд! Нужно {BET_ROULETTE} ⭐.\n/deposit"
        )
        return

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔴 Красное (x2)", callback_data="rou_red"),
            InlineKeyboardButton("⚫ Чёрное (x2)", callback_data="rou_black"),
        ],
        [
            InlineKeyboardButton("🟢 Зеро (x14)", callback_data="rou_zero"),
        ],
    ])
    await update.message.reply_html(
        f"🎡 Рулетка! Ставка: <b>{BET_ROULETTE} ⭐</b>\n"
        f"💰 Баланс: <b>{get_balance(uid)} ⭐</b>\n\n"
        "Сделайте ставку:",
        reply_markup=keyboard,
    )


ROULETTE_COLORS = ["red"] * 18 + ["black"] * 18 + ["zero"]

async def roulette_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    choice = query.data  # rou_red / rou_black / rou_zero

    spin = random.choice(ROULETTE_COLORS)
    number = random.randint(0, 36)
    spin_emoji = {"red": "🔴", "black": "⚫", "zero": "🟢"}[spin]

    won = False
    multiplier = 0
    if choice == "rou_red" and spin == "red":
        won, multiplier = True, 2
    elif choice == "rou_black" and spin == "black":
        won, multiplier = True, 2
    elif choice == "rou_zero" and spin == "zero":
        won, multiplier = True, 14

    if won:
        win = BET_ROULETTE * multiplier
        add_balance(uid, win)
        result = f"🎉 Победа! x{multiplier} → +{win} ⭐"
    else:
        result = f"😔 Проигрыш {BET_ROULETTE} ⭐"

    await query.edit_message_text(
        f"🎡 Шарик упал на: {spin_emoji} <b>{number}</b>\n\n"
        f"{result}\n"
        f"💰 Баланс: <b>{get_balance(uid)} ⭐</b>",
        parse_mode="HTML",
    )


# ─── /help ───────────────────────────────────
async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(
        "🎰 <b>Stars Casino — справка</b>\n\n"
        "<b>Игры:</b>\n"
        "🪙 /coin — монетка, ставка 1 ⭐ → угадай сторону (x2)\n"
        "🎰 /slots — слоты, ставка 2 ⭐ → совпади 3 символа (x5–x50)\n"
        "🎡 /roulette — рулетка, ставка 3 ⭐ → красное/чёрное (x2), зеро (x14)\n\n"
        "<b>Баланс:</b>\n"
        "/balance — проверить\n"
        "/deposit — пополнить на 5 ⭐\n\n"
        "Удачи! 🍀"
    )


# ─── Точка входа ─────────────────────────────
def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("deposit", deposit))
    app.add_handler(CommandHandler("coin", coin))
    app.add_handler(CommandHandler("slots", slots))
    app.add_handler(CommandHandler("roulette", roulette))
    app.add_handler(CommandHandler("help", help_cmd))

    app.add_handler(CallbackQueryHandler(coin_callback, pattern="^coin_"))
    app.add_handler(CallbackQueryHandler(roulette_callback, pattern="^rou_"))

    app.add_handler(PreCheckoutQueryHandler(precheckout))
    app.add_handler(
        MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment)
    )

    logger.info("Бот запущен...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
