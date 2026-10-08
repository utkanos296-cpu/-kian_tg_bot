import os
import json
import time
import re
import logging
from pathlib import Path
from html import escape

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.environ['BOT_TOKEN'].strip()
SECOND_BOT_TOKEN = os.environ.get('SECOND_BOT_TOKEN', '').strip()
PHOTO_FILE_ID = os.environ.get('PHOTO_FILE_ID', '').strip()
ADMIN_ID = 8903515053
DATA_FILE = Path(os.environ.get('DATA_FILE', 'bot_data.json'))
MAX_SPAM_MESSAGES = 5
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('kian')

LANGUAGE_BUTTONS = {
    '🇷🇺 Русский': 'ru', '🇬🇧 English': 'en', '🇩🇪 Deutsch': 'de',
    '🇧🇾 Беларуская': 'be', '🇺🇦 Українська': 'uk',
}
LANGUAGE_NAMES = dict(zip(LANGUAGE_BUTTONS.values(), LANGUAGE_BUTTONS.keys()))

TEXTS = {
    'ru': {
        'assistant': '👋 Hello! Я виртуальный помощник Kian.\n\nНо перед тем как продолжить, подтвердите свой возраст.\n\n🔞 Напишите свой возраст цифрами.',
        'age_number': 'Пожалуйста, напишите свой возраст только цифрами 👀',
        'too_young': '🥹 Боже, ты такой пупсик 😂❤️\n\nТы ещё маленький, чтобы сюда писать 🤭',
        'young_welcome': 'Ого, какие люди пожаловали 🤭😱',
        'bad_age': 'Ваш возраст не подходит 😂😂😂',
        'question': 'Что вас интересует и какой вопрос вы хотите задать Mister Kian? 👀\n\nПожалуйста, напишите всё одним сообщением.',
        'sent': '✅ Хорошо, я передам ваше сообщение Mister Kian.\n\nКак только у него появится возможность и время ответить, он обязательно вам ответит.\n\nОжидайте 👀',
        'spam': '⚠️ Ваше сообщение уже передано. Не нужно спамить — дождитесь ответа Mister Kian 👀',
        'block_1h': '⛔ Слишком много сообщений. Возможность писать боту ограничена на 1 час.',
        'block_3h': '⛔ Повторный спам. Возможность писать боту ограничена на 3 часа.',
        'block_forever': '⛔ Доступ к боту заблокирован.',
        'still_blocked': '⏳ Возможность писать временно ограничена. Попробуйте позже.',
        'after_answer': '💬 Mister Kian ответил на ваше сообщение.\n\nЕсли у вас появился новый вопрос, можете написать его одним сообщением.',
        'insult_1': '😏 И это всё, на что ты способен?\nДавай общаться культурно, малыш 🤭\n⚠️ Предупреждение: 1/3',
        'insult_2': '😂 Серьёзно? Опять?\nФантазия у тебя, конечно, впечатляющая.\n⚠️ Последнее предупреждение: 2/3',
        'insult_3': '🚫 Ну вот и договорились 😂\nТри нарушения — и наша беседа окончена.\nДоступ к боту заблокирован.',
        'unblocked': '🔓 Ограничение снято. Вы снова можете пользоваться ботом.',
    },
    'en': {
        'assistant': "👋 Hello! I'm Kian's virtual assistant.\n\nBefore we continue, confirm your age.\n\n🔞 Enter your age using numbers.",
        'age_number': 'Please enter your age using numbers only 👀',
        'too_young': "🥹 Oh, you're such a cutie 😂❤️\n\nYou're still too young to message here 🤭",
        'young_welcome': 'Well, well... look who showed up 🤭😱',
        'bad_age': 'Your age is not suitable 😂😂😂',
        'question': 'What would you like to ask Mister Kian? 👀\n\nPlease write everything in one message.',
        'sent': "✅ I'll pass your message to Mister Kian. He'll reply when he has time. Please wait 👀",
        'spam': "⚠️ Your message has already been delivered. Don't spam — wait for Mister Kian 👀",
        'block_1h': '⛔ Too many messages. Messaging is restricted for 1 hour.',
        'block_3h': '⛔ Repeated spam. Messaging is restricted for 3 hours.',
        'block_forever': '⛔ Access to the bot has been blocked.',
        'still_blocked': '⏳ Messaging is temporarily restricted. Try again later.',
        'after_answer': '💬 Mister Kian replied. You may send another question in one message.',
        'insult_1': '😏 Is that all you can come up with?\nPlease be respectful 🤭\n⚠️ Warning: 1/3',
        'insult_2': '😂 Seriously? Again?\n⚠️ Final warning: 2/3',
        'insult_3': '🚫 Three violations. This conversation is over. Access blocked.',
        'unblocked': '🔓 The restriction has been removed. You can use the bot again.',
    },
    'de': {
        'assistant': '👋 Hallo! Ich bin Kians virtueller Assistent.\n\nBitte bestätige zuerst dein Alter.\n\n🔞 Schreibe dein Alter in Zahlen.',
        'age_number': 'Bitte gib dein Alter nur in Zahlen ein 👀',
        'too_young': '🥹 Du bist ja ein kleiner Süßer 😂❤️\n\nDu bist noch zu jung, um hier zu schreiben 🤭',
        'young_welcome': 'Oha, wen haben wir denn hier? 🤭😱',
        'bad_age': 'Dein Alter passt leider nicht 😂😂😂',
        'question': 'Was möchtest du Mister Kian fragen? 👀\n\nBitte schreibe alles in einer Nachricht.',
        'sent': '✅ Ich leite deine Nachricht an Mister Kian weiter. Er antwortet, sobald er Zeit hat. Bitte warte 👀',
        'spam': '⚠️ Deine Nachricht wurde bereits weitergeleitet. Bitte warte auf eine Antwort 👀',
        'block_1h': '⛔ Zu viele Nachrichten. Schreiben ist für 1 Stunde gesperrt.',
        'block_3h': '⛔ Erneuter Spam. Schreiben ist für 3 Stunden gesperrt.',
        'block_forever': '⛔ Der Zugriff auf den Bot wurde gesperrt.',
        'still_blocked': '⏳ Schreiben ist vorübergehend eingeschränkt. Versuche es später.',
        'after_answer': '💬 Mister Kian hat geantwortet. Du kannst eine neue Frage in einer Nachricht stellen.',
        'insult_1': '😏 Ist das alles, was dir einfällt?\nBleib bitte höflich 🤭\n⚠️ Verwarnung: 1/3',
        'insult_2': '😂 Ernsthaft? Schon wieder?\n⚠️ Letzte Verwarnung: 2/3',
        'insult_3': '🚫 Drei Verstöße. Das Gespräch ist beendet. Zugriff gesperrt.',
        'unblocked': '🔓 Die Einschränkung wurde aufgehoben. Du kannst den Bot wieder verwenden.',
    },
    'be': {
        'assistant': '👋 Прывітанне! Я віртуальны памочнік Kian.\n\nСпачатку пацвердзіце свой узрост.\n\n🔞 Напішыце ўзрост лічбамі.',
        'age_number': 'Калі ласка, напішыце ўзрост толькі лічбамі 👀',
        'too_young': '🥹 Божа, ты такі пупсік 😂❤️\n\nТы яшчэ маленькі, каб сюды пісаць 🤭',
        'young_welcome': 'Ого, якія людзі завіталі 🤭😱',
        'bad_age': 'Ваш узрост не падыходзіць 😂😂😂',
        'question': 'Што вы хочаце спытаць у Mister Kian? 👀\n\nНапішыце ўсё адным паведамленнем.',
        'sent': '✅ Я перадам паведамленне Mister Kian. Ён адкажа, калі зможа. Чакайце 👀',
        'spam': '⚠️ Паведамленне ўжо перададзена. Не спамце — дачакайцеся адказу 👀',
        'block_1h': '⛔ Занадта шмат паведамленняў. Абмежаванне на 1 гадзіну.',
        'block_3h': '⛔ Паўторны спам. Абмежаванне на 3 гадзіны.',
        'block_forever': '⛔ Доступ да бота заблакіраваны.',
        'still_blocked': '⏳ Адпраўка паведамленняў часова абмежавана.',
        'after_answer': '💬 Mister Kian адказаў. Можаце задаць новае пытанне адным паведамленнем.',
        'insult_1': '😏 І гэта ўсё, на што ты здольны?\nДавай ветліва 🤭\n⚠️ Папярэджанне: 1/3',
        'insult_2': '😂 Сур’ёзна? Зноў?\n⚠️ Апошняе папярэджанне: 2/3',
        'insult_3': '🚫 Тры парушэнні. Размова скончана. Доступ заблакіраваны.',
        'unblocked': '🔓 Абмежаванне знята. Вы зноў можаце карыстацца ботам.',
    },
    'uk': {
        'assistant': '👋 Привіт! Я віртуальний помічник Kian.\n\nСпочатку підтвердьте свій вік.\n\n🔞 Напишіть вік цифрами.',
        'age_number': 'Будь ласка, напишіть вік лише цифрами 👀',
        'too_young': '🥹 Боже, ти такий пупсик 😂❤️\n\nТи ще маленький, щоб сюди писати 🤭',
        'young_welcome': 'Ого, які люди завітали 🤭😱',
        'bad_age': 'Ваш вік не підходить 😂😂😂',
        'question': 'Що ви хочете запитати у Mister Kian? 👀\n\nНапишіть усе одним повідомленням.',
        'sent': '✅ Я передам повідомлення Mister Kian. Він відповість, коли зможе. Очікуйте 👀',
        'spam': '⚠️ Повідомлення вже передано. Не спамте — дочекайтеся відповіді 👀',
        'block_1h': '⛔ Забагато повідомлень. Обмеження на 1 годину.',
        'block_3h': '⛔ Повторний спам. Обмеження на 3 години.',
        'block_forever': '⛔ Доступ до бота заблоковано.',
        'still_blocked': '⏳ Надсилання повідомлень тимчасово обмежене.',
        'after_answer': '💬 Mister Kian відповів. Можете поставити нове питання одним повідомленням.',
        'insult_1': '😏 І це все, на що ти здатен?\nСпілкуймося ввічливо 🤭\n⚠️ Попередження: 1/3',
        'insult_2': '😂 Серйозно? Знову?\n⚠️ Останнє попередження: 2/3',
        'insult_3': '🚫 Три порушення. Розмову завершено. Доступ заблоковано.',
        'unblocked': '🔓 Обмеження знято. Ви знову можете користуватися ботом.',
    },
}

# Консервативный список очевидных оскорблений и нецензурных слов.
# Его можно расширять, но автоматическая проверка не безошибочна.
OFFENSIVE_PATTERN = re.compile(
    r'(?iu)(?<!\w)(?:'
    r'бля(?:дь|ть|ха|ха\w*|ди\w*|т)|'
    r'сука|суки|сукин|сучка|'
    r'хуй|хуя|хуе\w*|хер|'
    r'пизд\w*|еба\w*|ёба\w*|ёб\w*|ебл\w*|'
    r'мудак|мудаки|долбо[её]б\w*|идиот|дебил|тупица|'
    r'fuck\w*|shit\w*|bitch\w*|asshole\w*|motherfucker\w*|'
    r'arschloch|schei(?:ß|ss)e|wichser|hurensohn|'
    r'пiзд\w*|х[уy]й|йоб\w*|єба\w*'
    r')(?!\w)'
)


def load_data():
    default = {'users': {}, 'message_owners': {}, 'reply_photo_id': None}
    if DATA_FILE.exists():
        try:
            loaded = json.loads(DATA_FILE.read_text(encoding='utf-8'))
            if isinstance(loaded, dict):
                for key, value in default.items():
                    loaded.setdefault(key, value)
                return loaded
        except Exception:
            log.exception('Could not load bot data')
    return default


data = load_data()


def save_data():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp = DATA_FILE.with_suffix('.tmp')
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    temp.replace(DATA_FILE)


def get_user(user_id):
    uid = str(user_id)
    defaults = {
        'language': None, 'age': None, 'stage': 'language', 'waiting': False,
        'spam_count': 0, 'spam_strikes': 0, 'insult_strikes': 0,
        'blocked_until': 0, 'permanent_block': False,
    }
    if uid not in data['users']:
        data['users'][uid] = defaults.copy()
        save_data()
    else:
        changed = False
        for key, value in defaults.items():
            if key not in data['users'][uid]:
                data['users'][uid][key] = value
                changed = True
        if changed:
            save_data()
    return data['users'][uid]


async def react(message, emoji):
    try:
        await message.set_reaction(emoji)
    except Exception:
        log.debug('Reaction unavailable', exc_info=True)


async def check_block(update, u):
    t = TEXTS.get(u.get('language'), TEXTS['ru'])
    if u['permanent_block']:
        await update.message.reply_text(t['block_forever'])
        return True
    until = u.get('blocked_until', 0)
    if until > time.time():
        minutes = max(1, int((until - time.time() + 59) // 60))
        await update.message.reply_text(t['still_blocked'] + f'\n\n⏱ {minutes} min.')
        return True
    if until:
        u['blocked_until'] = 0
        u['spam_count'] = 0
        # Сохраняем ожидание ответа, чтобы снятие бана не теряло вопрос.
        save_data()
    return False


def target_id(update, context):
    if context.args:
        try:
            return int(context.args[0])
        except ValueError:
            return None
    reply = update.message.reply_to_message
    return int(data['message_owners'].get(str(reply.message_id))) if reply and str(reply.message_id) in data['message_owners'] else None


async def setphoto(update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    reply = update.message.reply_to_message
    if not reply or not reply.photo:
        await update.message.reply_text('📸 Отправь фото, затем ответь на него командой /setphoto')
        return
    data['reply_photo_id'] = reply.photo[-1].file_id
    save_data()
    await update.message.reply_text('✅ Фото Mister Kian установлено.')


async def removephoto(update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    data['reply_photo_id'] = None
    save_data()
    await update.message.reply_text('🗑 Фото удалено.')


async def testsecond(update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    if not SECOND_BOT_TOKEN:
        await update.message.reply_text('❌ Добавь SECOND_BOT_TOKEN в Railway → Variables.')
        return
    try:
        async with Bot(token=SECOND_BOT_TOKEN) as other:
            info = await other.get_me()
        await update.message.reply_text(
            f'🧪 Второй бот\n\n✅ Токен работает\n🤖 {info.full_name}\n'
            f'🔗 @{info.username or "нет"}\n🆔 {info.id}\n\n'
            'Это проверка токена, а не доступ к базе второго бота.'
        )
    except Exception:
        log.exception('Second bot check failed')
        await update.message.reply_text('❌ Проверка второго токена не удалась. Проверь Railway Variables.')


async def unblock(update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    uid = target_id(update, context)
    if uid is None:
        await update.message.reply_text('🔓 Reply на обращение или /unblock ID')
        return
    u = get_user(uid)
    u.update(permanent_block=False, blocked_until=0, spam_count=0,
             spam_strikes=0, insult_strikes=0, waiting=False)
    u['stage'] = 'question' if u.get('age') and u.get('language') else ('age' if u.get('language') else 'language')
    save_data()
    await update.message.reply_text(f'🔓 {uid} разблокирован. Все нарушения сброшены.')
    try:
        await context.bot.send_message(uid, TEXTS.get(u['language'], TEXTS['ru'])['unblocked'])
    except Exception:
        log.info('Could not notify unblocked user %s', uid)


async def block(update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    uid = target_id(update, context)
    if uid is None:
        await update.message.reply_text('🚫 Reply на обращение или /block ID')
        return
    u = get_user(uid)
    u['permanent_block'] = True
    u['blocked_until'] = 0
    save_data()
    await update.message.reply_text(f'🚫 Пользователь {uid} заблокирован.')


async def status(update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    uid = target_id(update, context)
    if uid is None:
        await update.message.reply_text('ℹ️ Reply на обращение или /status ID')
        return
    u = get_user(uid)
    if u['permanent_block']:
        state = '🚫 Постоянный бан'
    elif u['blocked_until'] > time.time():
        state = '⏳ Временный бан'
    else:
        state = '✅ Доступен'
    await update.message.reply_text(
        f'👤 ID: {uid}\n🌐 {LANGUAGE_NAMES.get(u["language"], "Не выбран")}\n'
        f'🔞 Возраст: {u["age"] or "не указан"}\n📨 Ждёт ответа: {"Да" if u["waiting"] else "Нет"}\n'
        f'⚠️ Спам: {u["spam_strikes"]}/3\n😡 Оскорбления: {u["insult_strikes"]}/3\n🔒 {state}'
    )


async def start(update, context):
    if update.effective_user.id == ADMIN_ID:
        photo = 'да' if data.get('reply_photo_id') or PHOTO_FILE_ID else 'нет'
        second = 'есть' if SECOND_BOT_TOKEN else 'нет'
        await update.message.reply_text(
            '👤 Mister Kian — администратор\n\n'
            f'🖼 Фото: {photo}\n🤖 Второй токен: {second}\n\n'
            '/setphoto — установить фото (Reply)\n/removephoto — удалить фото\n'
            '/testsecond — проверить второй токен\n/status ID — статус\n'
            '/block ID — заблокировать\n/unblock ID — разблокировать'
        )
        return
    u = get_user(update.effective_user.id)
    if await check_block(update, u):
        return
    # /start не позволяет обойти антиспам, пока админ не ответил.
    if u['waiting']:
        await update.message.reply_text(TEXTS.get(u['language'], TEXTS['ru'])['spam'])
        return
    u.update(stage='language', language=None, age=None, spam_count=0)
    save_data()
    keyboard = ReplyKeyboardMarkup(
        [['🇷🇺 Русский', '🇬🇧 English'], ['🇩🇪 Deutsch', '🇧🇾 Беларуская'], ['🇺🇦 Українська']],
        resize_keyboard=True, one_time_keyboard=True,
    )
    await update.message.reply_text('🌐 Выберите язык / Choose your language:', reply_markup=keyboard)


async def handle_insult(update, context, u):
    msg = update.message
    lang = u.get('language') or 'ru'
    t = TEXTS[lang]
    await react(msg, '😡')
    u['insult_strikes'] += 1
    strikes = u['insult_strikes']
    if strikes >= 3:
        u['permanent_block'] = True
        u['blocked_until'] = 0
    save_data()
    await msg.reply_text(t[f'insult_{min(strikes, 3)}'])
    if strikes >= 3:
        sender = update.effective_user
        try:
            await context.bot.send_message(
                ADMIN_ID,
                f'🚫 БАН ЗА ОСКОРБЛЕНИЯ\n👤 {sender.full_name}\n'
                f'🔗 @{sender.username or "нет username"}\n🆔 {sender.id}\n'
                f'😡 Нарушения: 3/3\n🔓 /unblock {sender.id}'
            )
        except Exception:
            log.exception('Failed to notify admin about insults')


async def handle_user(update, context):
    msg = update.message
    sender = update.effective_user
    u = get_user(sender.id)
    if await check_block(update, u):
        return
    text = msg.text or msg.caption or ''
    # Проверяем грубые выражения до антиспама: категории нарушений независимы.
    if text and OFFENSIVE_PATTERN.search(text):
        await handle_insult(update, context, u)
        return
    if u['stage'] == 'language':
        if msg.text not in LANGUAGE_BUTTONS:
            await msg.reply_text('🌐 Please choose your language using the buttons.')
            return
        lang = LANGUAGE_BUTTONS[msg.text]
        await react(msg, '❤')
        u.update(language=lang, stage='age')
        save_data()
        await msg.reply_text(TEXTS[lang]['assistant'], reply_markup=ReplyKeyboardRemove())
        return
    lang = u.get('language') or 'ru'
    t = TEXTS[lang]
    if u['stage'] == 'age':
        try:
            age = int(msg.text.strip())
        except (ValueError, AttributeError):
            await msg.reply_text(t['age_number'])
            return
        if age < 17:
            await msg.reply_text(t['too_young'])
            return
        if age > 65:
            await msg.reply_text(t['bad_age'])
            return
        await react(msg, '❤')
        u.update(age=age, stage='question')
        save_data()
        if 17 <= age <= 25:
            await msg.reply_text(t['young_welcome'])
        await msg.reply_text(t['question'])
        return
    if u['waiting']:
        await react(msg, '😡')
        u['spam_count'] += 1
        if u['spam_count'] < MAX_SPAM_MESSAGES:
            save_data()
            await msg.reply_text(f'{t["spam"]}\n\n⚠️ {u["spam_count"]}/{MAX_SPAM_MESSAGES}')
            return
        u['spam_count'] = 0
        u['spam_strikes'] += 1
        strikes = u['spam_strikes']
        if strikes == 1:
            u['blocked_until'] = time.time() + 3600
            key, reason = 'block_1h', '1 час'
        elif strikes == 2:
            u['blocked_until'] = time.time() + 10800
            key, reason = 'block_3h', '3 часа'
        else:
            u['permanent_block'] = True
            key, reason = 'block_forever', 'навсегда'
        save_data()
        await msg.reply_text(t[key])
        try:
            await context.bot.send_message(
                ADMIN_ID, f'⚠️ Антиспам: {reason}\n👤 {sender.full_name}\n'
                f'🆔 {sender.id}\n⚠️ {strikes}/3\n🔓 /unblock {sender.id}'
            )
        except Exception:
            log.exception('Failed to notify admin about spam')
        return
    if u['stage'] == 'question':
        username = f'@{sender.username}' if sender.username else 'нет username'
        header = (
            '📩 Новое обращение для Mister Kian\n\n'
            f'👤 {sender.full_name}\n🔗 {username}\n🆔 {sender.id}\n'
            f'🔞 Возраст: {u["age"]}\n🌐 {LANGUAGE_NAMES.get(lang, lang)}\n'
            f'⚠️ Спам: {u["spam_strikes"]}/3\n😡 Оскорбления: {u["insult_strikes"]}/3'
        )
        try:
            info = await context.bot.send_message(ADMIN_ID, header)
            copied = await context.bot.copy_message(ADMIN_ID, msg.chat_id, msg.message_id)
        except Exception:
            log.exception('Failed to forward user question')
            await msg.reply_text('⚠️ Не удалось передать сообщение. Попробуйте позже.')
            return
        data['message_owners'][str(info.message_id)] = sender.id
        data['message_owners'][str(copied.message_id)] = sender.id
        u.update(waiting=True, spam_count=0)
        save_data()
        await react(msg, '❤')
        await msg.reply_text(t['sent'])


async def handle_admin(update, context):
    msg = update.message
    if not msg.reply_to_message:
        return
    uid = data['message_owners'].get(str(msg.reply_to_message.message_id))
    if uid is None:
        # Не выдаём ошибку на Reply к собственной фотографии/сообщению.
        return
    u = get_user(uid)
    photo = data.get('reply_photo_id') or PHOTO_FILE_ID
    try:
        if photo and msg.text:
            if len(msg.text) <= 1024:
                await context.bot.send_photo(uid, photo=photo, caption=msg.text)
            else:
                await context.bot.send_photo(uid, photo=photo)
                await context.bot.send_message(uid, msg.text)
        else:
            if photo:
                await context.bot.send_photo(uid, photo=photo)
            await context.bot.copy_message(uid, msg.chat_id, msg.message_id)
    except Exception:
        log.exception('Failed to deliver admin answer')
        await msg.reply_text('❌ Ответ не отправлен. Проверь доступность пользователя и фото.')
        return
    u.update(waiting=False, spam_count=0, stage='question')
    save_data()
    lang = u.get('language') or 'ru'
    try:
        spoiler = escape(TEXTS[lang]['after_answer'])
        await context.bot.send_message(uid, f'<tg-spoiler>{spoiler}</tg-spoiler>', parse_mode='HTML')
    except Exception:
        log.exception('Failed to send spoiler')
    await msg.reply_text('✅ Ответ отправлен.')


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    for name, handler in [
        ('start', start), ('setphoto', setphoto), ('removephoto', removephoto),
        ('testsecond', testsecond), ('unblock', unblock), ('block', block), ('status', status),
    ]:
        app.add_handler(CommandHandler(name, handler))
    app.add_handler(MessageHandler(filters.User(user_id=ADMIN_ID) & ~filters.COMMAND, handle_admin))
    app.add_handler(MessageHandler(~filters.User(user_id=ADMIN_ID) & ~filters.COMMAND, handle_user))
    print('Kian Assistant started...')
    app.run_polling()


if __name__ == '__main__':
    main()
