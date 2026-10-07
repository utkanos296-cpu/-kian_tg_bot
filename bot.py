import os
import json
import time
from pathlib import Path

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.environ["BOT_TOKEN"].strip()
ADMIN_ID = 8903515053

DATA_FILE = Path("bot_data.json")
MAX_SPAM_MESSAGES = 5


# =========================
# DATA
# =========================

def load_data():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    return {
        "users": {},
        "message_owners": {}
    }


data = load_data()


def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_user(user_id):
    uid = str(user_id)

    if uid not in data["users"]:
        data["users"][uid] = {
            "language": None,
            "age": None,
            "stage": "language",
            "waiting": False,
            "spam_count": 0,
            "spam_strikes": 0,
            "blocked_until": 0,
            "permanent_block": False,
        }

        save_data()

    # Добавляем новые поля старым пользователям
    defaults = {
        "language": None,
        "age": None,
        "stage": "language",
        "waiting": False,
        "spam_count": 0,
        "spam_strikes": 0,
        "blocked_until": 0,
        "permanent_block": False,
    }

    for key, value in defaults.items():
        if key not in data["users"][uid]:
            data["users"][uid][key] = value

    return data["users"][uid]


# =========================
# LANGUAGES
# =========================

LANGUAGE_BUTTONS = {
    "🇷🇺 Русский": "ru",
    "🇬🇧 English": "en",
    "🇩🇪 Deutsch": "de",
    "🇧🇾 Беларуская": "be",
    "🇺🇦 Українська": "uk",
}


TEXTS = {

    # 🇷🇺 RUSSIAN
    "ru": {
        "assistant":
            "👋 Hello! Я виртуальный помощник Kian.\n\n"
            "Но перед тем как продолжить, подтвердите свой возраст.\n\n"
            "🔞 Напишите свой возраст цифрами.",

        "bad_age":
            "Ваш возраст не подходит 😂😂😂",

        "age_number":
            "Пожалуйста, напишите свой возраст только цифрами 👀",

        "question":
            "Отлично 👀\n\n"
            "Что вас интересует и какой вопрос вы хотите задать Mister Kian?\n\n"
            "Пожалуйста, напишите всё одним сообщением.",

        "sent":
            "✅ Хорошо, я передам ваше сообщение Mister Kian.\n\n"
            "Как только у него появится возможность и время ответить, "
            "он обязательно вам ответит.\n\n"
            "Ожидайте 👀",

        "spam":
            "⚠️ Ваше сообщение уже передано.\n\n"
            "Пишите только по делу и одним сообщением. "
            "Не нужно спамить — дождитесь ответа Mister Kian 👀",

        "block_1h":
            "⛔ Слишком много сообщений подряд.\n\n"
            "Возможность писать боту ограничена на 1 час.",

        "block_3h":
            "⛔ Вы снова отправили слишком много сообщений подряд.\n\n"
            "В этот раз возможность писать боту ограничена на 3 часа.",

        "block_forever":
            "⛔ Доступ заблокирован.\n\n"
            "Вы неоднократно нарушили ограничение на отправку сообщений.",

        "still_blocked":
            "⏳ Возможность отправлять сообщения временно ограничена.\n\n"
            "Попробуйте позже.",

        "after_answer":
            "💬 Mister Kian ответил на ваше сообщение.\n\n"
            "Если у вас появился новый вопрос, можете написать его одним сообщением.",
    },


    # 🇬🇧 ENGLISH
    "en": {
        "assistant":
            "👋 Hello! I'm Kian's virtual assistant.\n\n"
            "Before we continue, please confirm your age.\n\n"
            "🔞 Enter your age using numbers.",

        "bad_age":
            "Your age is not suitable 😂😂😂",

        "age_number":
            "Please enter your age using numbers only 👀",

        "question":
            "Great 👀\n\n"
            "What are you interested in and what would you like to ask Mister Kian?\n\n"
            "Please write everything in one message.",

        "sent":
            "✅ Alright, I'll pass your message to Mister Kian.\n\n"
            "As soon as he has the opportunity and time to reply, "
            "he will definitely get back to you.\n\n"
            "Please wait 👀",

        "spam":
            "⚠️ Your message has already been delivered.\n\n"
            "Please keep it to the point and send everything in one message. "
            "Don't spam — wait for Mister Kian's reply 👀",

        "block_1h":
            "⛔ Too many messages were sent in a row.\n\n"
            "Messaging has been restricted for 1 hour.",

        "block_3h":
            "⛔ You have again sent too many messages in a row.\n\n"
            "This time messaging has been restricted for 3 hours.",

        "block_forever":
            "⛔ Access has been blocked.\n\n"
            "You repeatedly violated the messaging limit.",

        "still_blocked":
            "⏳ Messaging is temporarily restricted.\n\n"
            "Please try again later.",

        "after_answer":
            "💬 Mister Kian has replied to your message.\n\n"
            "If you have another question, you can send it in one message.",
    },


    # 🇩🇪 GERMAN
    "de": {
        "assistant":
            "👋 Hallo! Ich bin der virtuelle Assistent von Kian.\n\n"
            "Bevor wir fortfahren, bestätige bitte dein Alter.\n\n"
            "🔞 Schreibe dein Alter in Zahlen.",

        "bad_age":
            "Dein Alter passt leider nicht 😂😂😂",

        "age_number":
            "Bitte gib dein Alter nur in Zahlen ein 👀",

        "question":
            "Perfekt 👀\n\n"
            "Was interessiert dich und welche Frage möchtest du Mister Kian stellen?\n\n"
            "Bitte schreibe alles in einer einzigen Nachricht.",

        "sent":
            "✅ Alles klar, ich werde deine Nachricht an Mister Kian weiterleiten.\n\n"
            "Sobald er die Möglichkeit und Zeit hat zu antworten, "
            "wird er dir auf jeden Fall antworten.\n\n"
            "Bitte warte 👀",

        "spam":
            "⚠️ Deine Nachricht wurde bereits weitergeleitet.\n\n"
            "Bitte schreibe nur das Wesentliche und alles in einer Nachricht. "
            "Kein Spam — warte auf die Antwort von Mister Kian 👀",

        "block_1h":
            "⛔ Zu viele Nachrichten hintereinander.\n\n"
            "Das Senden von Nachrichten wurde für 1 Stunde eingeschränkt.",

        "block_3h":
            "⛔ Du hast erneut zu viele Nachrichten hintereinander gesendet.\n\n"
            "Diesmal wurde das Senden für 3 Stunden eingeschränkt.",

        "block_forever":
            "⛔ Der Zugriff wurde gesperrt.\n\n"
            "Du hast wiederholt gegen das Nachrichtenlimit verstoßen.",

        "still_blocked":
            "⏳ Das Senden von Nachrichten ist vorübergehend eingeschränkt.\n\n"
            "Versuche es später erneut.",

        "after_answer":
            "💬 Mister Kian hat auf deine Nachricht geantwortet.\n\n"
            "Wenn du eine neue Frage hast, kannst du sie in einer Nachricht senden.",
    },


    # 🇧🇾 BELARUSIAN
    "be": {
        "assistant":
            "👋 Прывітанне! Я віртуальны памочнік Kian.\n\n"
            "Перш чым працягнуць, пацвердзіце свой узрост.\n\n"
            "🔞 Напішыце свой узрост лічбамі.",

        "bad_age":
            "Ваш узрост не падыходзіць 😂😂😂",

        "age_number":
            "Калі ласка, напішыце свой узрост толькі лічбамі 👀",

        "question":
            "Выдатна 👀\n\n"
            "Што вас цікавіць і якое пытанне вы хочаце задаць Mister Kian?\n\n"
            "Калі ласка, напішыце ўсё адным паведамленнем.",

        "sent":
            "✅ Добра, я перадам ваша паведамленне Mister Kian.\n\n"
            "Як толькі ў яго з'явіцца магчымасць і час адказаць, "
            "ён абавязкова вам адкажа.\n\n"
            "Чакайце 👀",

        "spam":
            "⚠️ Ваша паведамленне ўжо перададзена.\n\n"
            "Пішыце толькі па справе і адным паведамленнем. "
            "Не трэба спаміць — дачакайцеся адказу Mister Kian 👀",

        "block_1h":
            "⛔ Занадта шмат паведамленняў запар.\n\n"
            "Магчымасць пісаць боту абмежавана на 1 гадзіну.",

        "block_3h":
            "⛔ Вы зноў адправілі занадта шмат паведамленняў запар.\n\n"
            "На гэты раз магчымасць пісаць боту абмежавана на 3 гадзіны.",

        "block_forever":
            "⛔ Доступ заблакіраваны.\n\n"
            "Вы неаднаразова парушылі абмежаванне на адпраўку паведамленняў.",

        "still_blocked":
            "⏳ Магчымасць адпраўляць паведамленні часова абмежавана.\n\n"
            "Паспрабуйце пазней.",

        "after_answer":
            "💬 Mister Kian адказаў на ваша паведамленне.\n\n"
            "Калі ў вас ёсць новае пытанне, можаце напісаць яго адным паведамленнем.",
    },


    # 🇺🇦 UKRAINIAN
    "uk": {
        "assistant":
            "👋 Привіт! Я віртуальний помічник Kian.\n\n"
            "Перш ніж продовжити, підтвердьте свій вік.\n\n"
            "🔞 Напишіть свій вік цифрами.",

        "bad_age":
            "Ваш вік не підходить 😂😂😂",

        "age_number":
            "Будь ласка, напишіть свій вік лише цифрами 👀",

        "question":
            "Чудово 👀\n\n"
            "Що вас цікавить і яке питання ви хочете поставити Mister Kian?\n\n"
            "Будь ласка, напишіть усе одним повідомленням.",

        "sent":
            "✅ Добре, я передам ваше повідомлення Mister Kian.\n\n"
            "Щойно в нього з'явиться можливість і час відповісти, "
            "він обов'язково вам відповість.\n\n"
            "Очікуйте 👀",

        "spam":
            "⚠️ Ваше повідомлення вже передано.\n\n"
            "Пишіть лише по суті та одним повідомленням. "
            "Не потрібно спамити — дочекайтеся відповіді Mister Kian 👀",

        "block_1h":
            "⛔ Забагато повідомлень поспіль.\n\n"
            "Можливість писати боту обмежена на 1 годину.",

        "block_3h":
            "⛔ Ви знову надіслали забагато повідомлень поспіль.\n\n"
            "Цього разу можливість писати боту обмежена на 3 години.",

        "block_forever":
            "⛔ Доступ заблоковано.\n\n"
            "Ви неодноразово порушили обмеження на надсилання повідомлень.",

        "still_blocked":
            "⏳ Можливість надсилати повідомлення тимчасово обмежена.\n\n"
            "Спробуйте пізніше.",

        "after_answer":
            "💬 Mister Kian відповів на ваше повідомлення.\n\n"
            "Якщо у вас з'явилося нове питання, можете написати його одним повідомленням.",
    },
}


# =========================
# BLOCK CHECK
# =========================

async def check_block(update, user_data):
    language = user_data.get("language") or "ru"
    t = TEXTS[language]

    if user_data["permanent_block"]:
        await update.message.reply_text(t["block_forever"])
        return True

    blocked_until = user_data.get("blocked_until", 0)

    if blocked_until > time.time():
        await update.message.reply_text(t["still_blocked"])
        return True

    # Временная блокировка закончилась
    if blocked_until != 0:
        user_data["blocked_until"] = 0
        user_data["spam_count"] = 0
        user_data["waiting"] = False
        user_data["stage"] = "question"
        save_data()

    return False


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.id == ADMIN_ID:
        await update.message.reply_text(
            "👤 Mister Kian — режим администратора активен."
        )
        return

    user_data = get_user(user.id)

    if await check_block(update, user_data):
        return

    user_data["stage"] = "language"
    user_data["language"] = None
    user_data["age"] = None
    user_data["waiting"] = False
    user_data["spam_count"] = 0

    # ВАЖНО: spam_strikes здесь НЕ обнуляем
    save_data()

    keyboard = ReplyKeyboardMarkup(
        [
            ["🇷🇺 Русский", "🇬🇧 English"],
            ["🇩🇪 Deutsch", "🇧🇾 Беларуская"],
            ["🇺🇦 Українська"],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    await update.message.reply_text(
        "🌐 Выберите язык / Choose your language:",
        reply_markup=keyboard
    )


# =========================
# USER
# =========================

async def handle_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message
    user_data = get_user(user.id)

    if await check_block(update, user_data):
        return

    # LANGUAGE
    if user_data["stage"] == "language":

        if message.text not in LANGUAGE_BUTTONS:
            await message.reply_text(
                "🌐 Please choose your language using the buttons."
            )
            return

        language = LANGUAGE_BUTTONS[message.text]

        user_data["language"] = language
        user_data["stage"] = "age"
        save_data()

        await message.reply_text(
            TEXTS[language]["assistant"],
            reply_markup=ReplyKeyboardRemove()
        )
        return

    language = user_data["language"] or "ru"
    t = TEXTS[language]

    # AGE
    if user_data["stage"] == "age":

        try:
            age = int(message.text.strip())
        except (ValueError, AttributeError):
            await message.reply_text(t["age_number"])
            return

        # Диапазон скрыт от пользователя
        if age < 17 or age > 65:
            await message.reply_text(t["bad_age"])
            return

        user_data["age"] = age
        user_data["stage"] = "question"
        save_data()

        await message.reply_text(t["question"])
        return

    # SPAM WHILE WAITING
    if user_data["waiting"]:

        user_data["spam_count"] += 1
        save_data()

        if user_data["spam_count"] < MAX_SPAM_MESSAGES:
            await message.reply_text(t["spam"])
            return

        # Поймали очередное нарушение
        user_data["spam_strikes"] += 1
        user_data["spam_count"] = 0

        strike = user_data["spam_strikes"]

        # 1 нарушение = 1 час
        if strike == 1:
            user_data["blocked_until"] = time.time() + (60 * 60)
            save_data()

            await message.reply_text(t["block_1h"])

            await context.bot.send_message(
                ADMIN_ID,
                f"⚠️ Антиспам: блокировка на 1 час\n\n"
                f"👤 {user.full_name}\n"
                f"🆔 {user.id}"
            )
            return

        # 2 нарушение = 3 часа
        if strike == 2:
            user_data["blocked_until"] = time.time() + (3 * 60 * 60)
            save_data()

            await message.reply_text(t["block_3h"])

            await context.bot.send_message(
                ADMIN_ID,
                f"⚠️ Антиспам: блокировка на 3 часа\n\n"
                f"👤 {user.full_name}\n"
                f"🆔 {user.id}"
            )
            return

        # 3 нарушение = навсегда
        user_data["permanent_block"] = True
        user_data["blocked_until"] = 0
        save_data()

        await message.reply_text(t["block_forever"])

        await context.bot.send_message(
            ADMIN_ID,
            f"🚫 ПОЛНАЯ БЛОКИРОВКА ЗА СПАМ\n\n"
            f"👤 {user.full_name}\n"
            f"🔗 @{user.username if user.username else 'нет username'}\n"
            f"🆔 {user.id}"
        )
        return

    # QUESTION
    if user_data["stage"] == "question":

        username = f"@{user.username}" if user.username else "нет username"

        language_names = {
            "ru": "🇷🇺 Русский",
            "en": "🇬🇧 English",
            "de": "🇩🇪 Deutsch",
            "be": "🇧🇾 Беларуская",
            "uk": "🇺🇦 Українська",
        }

        header = (
            "📩 Новое обращение для Mister Kian\n\n"
            f"👤 {user.full_name}\n"
            f"🔗 {username}\n"
            f"🆔 {user.id}\n"
            f"🔞 Возраст: {user_data['age']}\n"
            f"🌐 Язык: {language_names[language]}"
        )

        info_message = await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=header
        )

        copied_message = await context.bot.copy_message(
            chat_id=ADMIN_ID,
            from_chat_id=message.chat_id,
            message_id=message.message_id
        )

        data["message_owners"][str(info_message.message_id)] = user.id
        data["message_owners"][str(copied_message.message_id)] = user.id

        user_data["waiting"] = True
        user_data["spam_count"] = 0
        save_data()

        await message.reply_text(t["sent"])
        return


# =========================
# ADMIN REPLY
# =========================

async def handle_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message.reply_to_message:
        return

    replied_id = str(message.reply_to_message.message_id)

    user_id = data["message_owners"].get(replied_id)

    if not user_id:
        await message.reply_text(
            "⚠️ Не удалось определить пользователя.\n\n"
            "Используй Reply именно на его сообщение."
        )
        return

    user_data = get_user(user_id)

    try:
        await context.bot.copy_message(
            chat_id=user_id,
            from_chat_id=message.chat_id,
            message_id=message.message_id
        )

        user_data["waiting"] = False
        user_data["spam_count"] = 0
        user_data["stage"] = "question"
        save_data()

        language = user_data["language"] or "ru"

        await context.bot.send_message(
            chat_id=user_id,
            text=TEXTS[language]["after_answer"]
        )

        await message.reply_text("✅ Ответ отправлен.")

    except Exception as e:
        await message.reply_text(
            f"❌ Не удалось отправить ответ: {e}"
        )


# =========================
# RUN
# =========================

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.User(user_id=ADMIN_ID) & ~filters.COMMAND,
            handle_admin
        )
    )

    app.add_handler(
        MessageHandler(
            ~filters.User(user_id=ADMIN_ID) & ~filters.COMMAND,
            handle_user
        )
    )

    print("Kian Assistant started...")
    app.run_polling()


if __name__ == "__main__":
    main()
