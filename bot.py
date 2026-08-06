from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from math import radians, sin, cos, sqrt, atan2

TOKEN = '8829013760:AAFRTUSv-uGEY6Rr3YO-m9RR5Xy7yEcqhZE'

QUESTIONS = [
    {
        'riddle': '📍 Место где мы отжигали под "ДУРАКАМ ВЕЗЕТ"',
        'lat': 53.677953,
        'lon': 23.828860,
        'hint': 'ФОГЕЛЬ И ДОБРО'
    },
    {
        'riddle': '🚗 Машина с традиционной чешской выпечкой',
        'lat': 53.675053,
        'lon': 23.825597,
        'hint': 'Место где все самые крутые чуваки на тачках'
    },
    {
        'riddle': '🚻 Место где мы бегаем в туалет',
        'lat': 53.662881,
        'lon': 23.833571,
        'hint': 'Если успеваем до 23:00'
    },
    {
        'riddle': '❄️ Место где внутри тепла есть лед',
        'lat': 53.650830,
        'lon': 23.855221,
        'hint': 'Самый большой ТЦ в Гродно'
    },
    {
        'riddle': '📍 ФИНАЛ! Отправь геолокацию 53.641005, 23.863507',
        'lat': 53.641005,
        'lon': 23.863507,
        'hint': 'Координаты 53.641005, 23.863507'
    }
]

# ХРАНЕНИЕ ПРОГРЕССА ИГРОКОВ

user_progress = {}

# ФУНКЦИИ БОТА

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if user_id in user_progress and user_progress[user_id] >= len(QUESTIONS):
        await update.message.reply_text('🎉 Ты уже всё прошёл! Напиши /restart')
        return

    if user_id not in user_progress:
        user_progress[user_id] = 0

    await show_question(update, user_id)


async def show_question(update, user_id):
    q_num = user_progress[user_id]
    if q_num >= len(QUESTIONS):
        await update.message.reply_text('🏆 ПОБЕДА! Напиши /restart')
        return

    question = QUESTIONS[q_num]
    button = KeyboardButton('📍 Отправить геолокацию', request_location=True)
    markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True)

    await update.message.reply_text(
        f'🔍 ЗАГАДКА {q_num + 1}/5:\n\n{question["riddle"]}\n\n💡 Напиши "подсказка"',
        reply_markup=markup
    )


async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if user_id not in user_progress:
        await update.message.reply_text('❌ Напиши /start')
        return

    q_num = user_progress[user_id]
    if q_num >= len(QUESTIONS):
        await update.message.reply_text('🎉 Ты уже всё прошёл! /restart')
        return

    location = update.message.location
    user_lat = location.latitude
    user_lon = location.longitude

    correct_lat = QUESTIONS[q_num]['lat']
    correct_lon = QUESTIONS[q_num]['lon']

    distance = calc_distance(user_lat, user_lon, correct_lat, correct_lon)

    if distance <= 50:
        await update.message.reply_text(f'✅ ПРАВИЛЬНО! Расстояние: {distance:.0f} метров 🎉')
        user_progress[user_id] += 1

        if user_progress[user_id] >= len(QUESTIONS):
            await update.message.reply_text('🏆🏆🏆 ПОЗДРАВЛЯЮ! Ты прошёл все загадки! 🏆🏆🏆')
        else:
            await show_question(update, user_id)
    else:
        await update.message.reply_text(
            f'❌ Мимо! Ты в {distance:.0f} метрах от цели.\n🎯 Нужно попасть в 50 метров.'
        )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text.lower()

    if user_id not in user_progress:
        await update.message.reply_text('❌ Напиши /start')
        return

    q_num = user_progress[user_id]
    if q_num >= len(QUESTIONS):
        await update.message.reply_text('🎉 Ты уже всё прошёл! /restart')
        return

    if text == 'подсказка':
        hint = QUESTIONS[q_num]['hint']
        await update.message.reply_text(f'💡 {hint}')
    else:
        await update.message.reply_text('❌ Отправь геолокацию через кнопку 📍')


async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id in user_progress:
        del user_progress[user_id]
    await update.message.reply_text('🔄 Игра перезапущена! Напиши /start')


def calc_distance(lat1, lon1, lat2, lon2):
    R = 6371000
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print('🤖 Бот запущен! 🚀')
    app.run_polling()


if __name__ == '__main__':
    main()