# -*- coding: utf-8 -*-
"""
Minecraft Modlari Telegram Boti
--------------------------------
"""

import os
import uuid
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from mods_data import MODS
import balances

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

DEFAULT_BOT_TOKEN = "8925751397:AAE0hdfPDERIdZl0gnVwKN2jNaYpX7G3d2E"

ADMIN_ID = 8642218989
MOD_PRICE = 5000  

BACK_BUTTON = "⬅️ Orqaga"
ALL_MODS_BUTTON = "📋 Barcha modlar"
BALANCE_BUTTON = "💰 Balansim"
TOPUP_BUTTON = "➕ Hisobni to'ldirish"

MAIN_MENU_CHUNK = 1
MOD_LIST_CHUNK = 2

PENDING_TOPUPS: dict = {}


# --- RENDER UCHUN MAJBURIY HTTP SERVER (WEB SERVICE REJIMI UCHUN) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot ishlayapti!")

    def log_message(self, format, *args):
        return  # Loglarni ortiqcha yozuvlar bilan to'ldirmaslik uchun

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    logger.info(f"Render health-check serveri {port}-portda ishga tushdi.")
    server.serve_forever()
# -----------------------------------------------------------------


def _chunk(items, size):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


def build_main_keyboard() -> ReplyKeyboardMarkup:
    titles = [cat["title"] for cat in MODS.values()]
    rows = list(_chunk(titles, MAIN_MENU_CHUNK))
    rows.append([ALL_MODS_BUTTON])
    rows.append([BALANCE_BUTTON, TOPUP_BUTTON])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def build_category_keyboard(category_key: str) -> ReplyKeyboardMarkup:
    names = [m["name"] for m in MODS[category_key]["mods"]]
    rows = list(_chunk(names, MOD_LIST_CHUNK))
    rows.append([BACK_BUTTON])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def build_all_mods_keyboard() -> ReplyKeyboardMarkup:
    names = []
    for cat in MODS.values():
        names.extend(m["name"] for m in cat["mods"])
    rows = list(_chunk(names, MOD_LIST_CHUNK))
    rows.append([BACK_BUTTON])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def title_to_category_key(title: str):
    for key, cat in MODS.items():
        if cat["title"] == title:
            return key
    return None


def build_name_lookup() -> dict:
    lookup = {}
    for key, cat in MODS.items():
        for mod in cat["mods"]:
            lookup[mod["name"]] = mod
    return lookup


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop("awaiting_topup_amount", None)
    user = update.effective_user
    admin_note = "\n\n🔑 Siz admin sifatida barcha modlarni bepul ko'rasiz." if is_admin(user.id) else ""
    text = (
        "👋 Salom! Bu bot orqali mashhur *Minecraft modlari* haqida "
        f"ma'lumot olishingiz mumkin.\n\nHar bir mod — {MOD_PRICE} so'm."
        f"{admin_note}\n\nQuyidagi tugmalardan birini tanlang:"
    )
    await update.message.reply_text(
        text, reply_markup=build_main_keyboard(), parse_mode=ParseMode.MARKDOWN
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "ℹ️ *Yordam*\n\n"
        f"Har bir mod ma'lumoti — {MOD_PRICE} so'm. Balansingizni "
        "'➕ Hisobni to'ldirish' tugmasi orqali to'ldirishingiz mumkin.\n\n"
        "/start — bosh menyu\n"
        "/help — shu yordam matni"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def show_balance(update: Update) -> None:
    user = update.effective_user
    if is_admin(user.id):
        await update.message.reply_text("🔑 Siz adminsiz — balans cheklovisiz, hammasi bepul.")
        return
    bal = balances.get_balance(user.id)
    await update.message.reply_text(f"💰 Balansingiz: *{bal} so'm*", parse_mode=ParseMode.MARKDOWN)


async def ask_topup_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["awaiting_topup_amount"] = True
    await update.message.reply_text(
        "💵 Hisobni qancha summaga to'ldirmoqchisiz? Summani raqamda kiriting (masalan: 20000):"
    )


async def handle_topup_amount(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    context.user_data.pop("awaiting_topup_amount", None)
    cleaned = text.replace(" ", "").replace(",", "")
    if not cleaned.isdigit() or int(cleaned) <= 0:
        await update.message.reply_text(
            "❗ Iltimos, to'g'ri musbat son kiriting (masalan: 20000)."
        )
        return

    amount = int(cleaned)
    user = update.effective_user
    request_id = uuid.uuid4().hex[:12]
    PENDING_TOPUPS[request_id] = (user.id, amount)

    admin_keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"topup_ok:{request_id}"),
                InlineKeyboardButton("❌ Rad etish", callback_data=f"topup_no:{request_id}"),
            ]
        ]
    )
    username_display = f"@{user.username}" if user.username else user.full_name

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"💳 *Yangi to'ldirish so'rovi*\n\n"
            f"Foydalanuvchi: {username_display} (ID: `{user.id}`)\n"
            f"Summa: *{amount} so'm*"
        ),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=admin_keyboard,
    )

    await update.message.reply_text(
        "✅ So'rovingiz qabul qilindi. Admin tasdiqlashini kuting."
    )


async def admin_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        await query.answer("Bu tugma faqat admin uchun.", show_alert=True)
        return

    data = query.data
    action, _, request_id = data.partition(":")
    pending = PENDING_TOPUPS.pop(request_id, None)

    if pending is None:
        await query.edit_message_text("⚠️ Bu so'rov allaqachon ko'rib chiqilgan yoki topilmadi.")
        return

    user_id, amount = pending

    if action == "topup_ok":
        new_balance = balances.add_balance(user_id, amount)
        await query.edit_message_text(
            f"✅ Tasdiqlandi. Foydalanuvchi (ID: {user_id}) balansiga {amount} so'm qo'shildi."
        )
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"✅ Hisobingiz *{amount} so'm* ga to'ldirildi.\n"
                f"💰 Joriy balans: *{new_balance} so'm*"
            ),
            parse_mode=ParseMode.MARKDOWN,
        )
    elif action == "topup_no":
        await query.edit_message_text(
            f"❌ Rad etildi. Foydalanuvchi (ID: {user_id}) so'rovi: {amount} so'm."
        )
        await context.bot.send_message(
            chat_id=user_id,
            text="❌ Hisobni to'ldirish so'rovingiz admin tomonidan rad etildi.",
        )


async def send_mod(update: Update, mod: dict) -> None:
    caption = f"🔧 *{mod['name']}*\n\n{mod['desc']}\n\n🔗 [Rasmiy sahifa]({mod['link']})"
    await update.message.reply_text(
        caption, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=False
    )


async def handle_mod_request(update: Update, mod: dict) -> None:
    user = update.effective_user

    if is_admin(user.id):
        await send_mod(update, mod)
        await update.message.reply_text("🔑 Admin sifatida bepul yubordim.")
        return

    bal = balances.get_balance(user.id)
    if bal < MOD_PRICE:
        needed = MOD_PRICE - bal
        await update.message.reply_text(
            f"❗ Balansingiz yetarli emas.\n\n"
            f"💰 Joriy balans: {bal} so'm\n"
            f"💵 Mod narxi: {MOD_PRICE} so'm\n"
            f"➕ Yana kamida {needed} so'm kerak.\n\n"
            f"'{TOPUP_BUTTON}' tugmasi orqali hisobingizni to'ldiring."
        )
        return

    balances.deduct_balance(user.id, MOD_PRICE)
    new_balance = bal - MOD_PRICE
    await send_mod(update, mod)
    await update.message.reply_text(f"💰 Balansingizdan {MOD_PRICE} so'm yechildi. Qoldiq: {new_balance} so'm.")


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text

    if context.user_data.get("awaiting_topup_amount"):
        await handle_topup_amount(update, context, text)
        return

    if text == BACK_BUTTON:
        await update.message.reply_text(
            "📂 Kategoriyalardan birini tanlang:", reply_markup=build_main_keyboard()
        )
        return

    if text == ALL_MODS_BUTTON:
        await update.message.reply_text(
            "📋 Barcha modlar ro'yxati:", reply_markup=build_all_mods_keyboard()
        )
        return

    if text == BALANCE_BUTTON:
        await show_balance(update)
        return

    if text == TOPUP_BUTTON:
        await ask_topup_amount(update, context)
        return

    category_key = title_to_category_key(text)
    if category_key:
        await update.message.reply_text(
            f"{MODS[category_key]['title']}\n\nModlardan birini tanlang:",
            reply_markup=build_category_keyboard(category_key),
        )
        return

    lookup = build_name_lookup()
    if text in lookup:
        await handle_mod_request(update, lookup[text])
        return

    await update.message.reply_text(
        "Iltimos, pastdagi tugmalardan birini tanlang. /start orqali qayta boshlashingiz mumkin."
    )


def main() -> None:
    token = os.environ.get("BOT_TOKEN") or DEFAULT_BOT_TOKEN
    if not token:
        raise RuntimeError("Bot tokeni topilmadi.")

    # 1. Render talab qilayotgan portni alohida oqimda (Thread) ochamiz
    server_thread = threading.Thread(target=run_health_server, daemon=True)
    server_thread.start()

    # 2. Telegram botni standart polling usulida boshlaymiz
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(admin_callback_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    logger.info("Bot ishga tushmoqda...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
