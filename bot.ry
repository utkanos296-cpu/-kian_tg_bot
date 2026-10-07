import os
import json
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

# Максимум попыток написать повторно, пока Mister Kian не ответил
MAX_SPAM_ATTEMPTS = 5


# =========================
# ХРАНЕНИЕ ДАННЫХ
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
    user_id = str(user_id)

    if user_id not in data["users"]:
        data["users"][user_id] = {
            "language": None,
            "age": None,
            "stage": "language",
            "waiting": False,
            "spam_count": 0,
            "blocked": False,
        }
        save_data()

    return data["users"][user_id]


# =========================
# ЯЗЫКИ
# =========================

LANGUAGE_BUTTONS = {
    "🇷🇺 Русский": "ru",
    "🇬🇧 English": "en",
    "🇩🇪 Deutsch": "de",
    "🇧🇾 Беларуская": "be",
    "🇺🇦 Українська": "uk",
}


TEXTS = {
    "ru": {
        "assistant":
            "👋 Hello! Я виртуальный помощник Kian.\n\n"
            "Но перед тем как продолжить, подтвердите свой возраст.\n\n"
            "🔞 Напишите свой возраст цифрами от 17 до 65.",

        "bad_age":
            "Извините, этот возраст не подходит.\n\n"
            "Продолжить могут пользователи в возрасте от 17 до 65 лет.",

        "age_number":
            "Пожалуйста, укажите возраст только цифрами.\n"
            "Например: 21",

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
            "Пожалуйста, не отправляйте сообщения по частям. "
            "Напишите один полный вопрос и дождитесь ответа Mister Kian.",

        "blocked":
            "⛔ Вы отправили слишком много сообщений подряд.\n\n"
            "Доступ к отправке новых сообщений временно заблокирован.",

        "after_answer":
            "💬 Mister Kian ответил на ваше сообщение.\n\n"
            "Если у вас появился новый вопрос, можете написать его одним сообщением.",
    },

    "en": {
        "assistant":
            "👋 Hello! I'm Kian's virtual assistant.\n\n"
            "Before we continue, please confirm your age.\n\n"
            "🔞 Enter your age using numbers from 17 to 65.",

        "bad_age":
            "Sorry, this age is not accepted.\n\n"
            "Only users between 17 and 65 can continue.",

        "age_number":
            "Please enter your age using numbers only.\n"
            "For example: 21",

        "question":
            "Great 👀\n\n"
            "What would you like to know, and what question would you like to ask Mister Kian?\n\n"
            "Please write everything in one message.",

        "sent":
            "✅ Alright, I'll pass your message to Mister Kian.\n\n"
            "As soon as he has the opportunity and time to reply, "
            "he will definitely get back to you.\n\n"
            "Please wait 👀",

        "spam":
            "⚠️ Your message has already been delivered.\n\n"
            "Please don't send your question in multiple messages. "
            "Send one complete message and wait for Mister Kian's reply.",

        "blocked":
            "⛔ You have sent too many messages in a row.\n\n"
            "Sending new messages has been temporarily blocked.",

        "after_answer":
            "💬 Mister Kian has replied to your message.\n\n"
            "If you have another question, you can send it in one message.",
    },

    "de": {
        "assistant":
            "👋 Hallo! Ich bin der virtuelle Assistent von Kian.\n\n"
            "Bevor wir fortfahren, bestätige bitte dein Alter.\n\n"
            "🔞 Schreibe dein Alter als Zahl zwischen 17 und 65.",

        "bad_age":
            "Entschuldigung, dieses Alter ist nicht zulässig.\n\n"
            "Fortfahren können Nutzer zwischen 17 und 65 Jahren.",

        "age_number":
            "Bitte gib dein Alter nur als Zahl ein.\n"
            "Zum Beispiel: 21",

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
            "Bitte sende deine Frage nicht in mehreren einzelnen Nachrichten. "
            "Schreibe eine vollständige Nachricht und warte auf die Antwort von Mister Kian.",

        "blocked":
            "⛔ Du hast zu viele Nachrichten hintereinander gesendet.\n\n"
            "Das Senden neuer Nachrichten wurde vorübergehend gesperrt.",

        "after_answer":
            "💬 Mister Kian hat auf deine Nachricht geantwortet.\n\n"
            "Wenn du eine neue Frage hast, kannst du sie in einer Nachricht senden.",
    },

    "be": {
        "assistant":
            "👋 Прывітанне! Я віртуальны памочнік Kian.\n\n"
            "Перш чым працягнуць, пацвердзіце свой узрост.\n\n"
            "🔞 Напішыце свой узрост лічбамі ад 17 да 65.",

        "bad_age":
            "Прабачце, гэты ўзрост не падыходзіць.\n\n"
            "Працягнуць могуць карыстальнікі ва ўзросце ад 17 да 65 гадоў.",

        "age_number":
            "Калі ласка, укажыце ўзрост толькі лічбамі.\n"
            "Напрыклад: 21",

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
            "Калі ласка, не адпраўляйце паведамленні па частках. "
            "Напішыце адно поўнае пытанне і дачакайцеся адказу Mister Kian.",

        "blocked":
            "⛔ Вы адправілі занадта шмат паведамленняў запар.\n\n"
            "Адпраўка новых паведамленняў часова заблакіравана.",

        "after_answer":
            "💬 Mister Kian адказаў на ваша паведамленне.\n\n"
            "Калі ў вас ёсць новае пытанне, можаце напісаць яго адным паведамленнем.",
    },

    "uk": {
        "assistant":
            "👋 Привіт! Я віртуальний помічник Kian.\n\n"
            "Перш ніж продовжити, підтвердьте свій вік.\n\n"
            "🔞 Напишіть свій вік цифрами від 17 до 65.",

        "bad_age":
            "Вибачте, цей вік не підходить.\n\n"
            "Продовжити можуть користувачі віком від 17 до 65 років.",

        "age_number":
            "Будь ласка, вкажіть вік лише цифрами.\n"
            "Наприклад: 21",

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
            "Будь ласка, не надсилайте повідомлення частинами. "
            "Напишіть одне повне питання та дочекайтеся відповіді Mister Kian.",

        "blocked":
            "⛔ Ви надіслали забагато повідомлень поспіль.\n\n"
            "Надсилання нових повідомлень тимчасово заблоковано.",

        "after_answer":
            "💬 Mister Kian відповів на ваше повідомлення.\n\n"
            "Якщо у вас з'явилося нове питання, можете написати його одним повідомленням.",
    },
}


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

    # При /start начинаем процесс заново,
    # но блокировку не снимаем.
    user_data = get_user(user.id)

    if user_data["blocked"]:
        language = user_data["language"] or "ru"
        await update.message.reply_text(TEXTS[language]["blocked"])
        return

    user_data["stage"] = "language"
    user_data["language"] = None
    user_data["age"] = None
    user_data["waiting"] = False
    user_data["spam_count"] = 0
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
# ПОЛЬЗОВАТЕЛЬ
# =========================

async def handle_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message
    user_data = get_user(user.id)

    if user_data["blocked"]:
        language = user_data["language"] or "ru"
        await message.reply_text(TEXTS[language]["blocked"])
        return

    # ВЫБОР ЯЗЫКА
    if user_data["stage"] == "language":

        if message.text not in LANGUAGE_BUTTONS:
            await message.reply_text(
                "🌐 Пожалуйста, выберите язык с помощью кнопки."
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

    # ВОЗРАСТ
    if user_data["stage"] == "age":

        try:
            age = int(message.text.strip())
        except (ValueError, AttributeError):
            await message.reply_text(t["age_number"])
            return

        if age < 17 or age > 65:
            await message.reply_text(t["bad_age"])
            return

        user_data["age"] = age
        user_data["stage"] = "question"
        save_data()

        await message.reply_text(t["question"])
        return

    # ЗАЩИТА ОТ СПАМА
    if user_data["waiting"]:

        user_data["spam_count"] += 1

        if user_data["spam_count"] >= MAX_SPAM_ATTEMPTS:
            user_data["blocked"] = True
            save_data()

            await message.reply_text(t["blocked"])

            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=(
                    "🚫 Пользователь автоматически заблокирован за спам.\n\n"
                    f"👤 {user.full_name}\n"
                    f"🔗 @{user.username if user.username else 'нет username'}\n"
                    f"🆔 {user.id}"
                )
            )
            return

        save_data()

        attempts_left = MAX_SPAM_ATTEMPTS - user_data["spam_count"]

        await message.reply_text(
            t["spam"] +
            f"\n\n⚠️ {user_data['spam_count']}/{MAX_SPAM_ATTEMPTS}"
        )
        return

    # ВОПРОС
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
# ОТВЕТ MISTER KIAN
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
            "Используй Reply именно на сообщение пользователя."
        )
        return

    user_data = get_user(user_id)

    try:
        await context.bot.copy_message(
            chat_id=user_id,
            from_chat_id=message.chat_id,
            message_id=message.message_id
        )

        # После ответа Mister Kian пользователь снова может написать
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
# ЗАПУСК
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
