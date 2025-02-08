import telebot
from telebot import types

API_TOKEN = '8005415583:AAHKwLEtZ7djtzQyi9UxImSo6kYWm3PeBSI'
bot = telebot.TeleBot(API_TOKEN)

USER_STATE = {}

# Реквизиты для оплаты
PAYMENT_INFO = (
    "Внести оплату по следующим реквизитам:\n"
    "Т банк - 2200 7009 2070 9143 Олег Л.\n"
    "СберБанк - 2200 7601 6631 2391 Олег Л.\n"
    "Сумму оплаты можно узнать у мастера)"
)


@bot.message_handler(commands=['start'])
def start_command(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Запись на прием", "Оплата")
    bot.send_message(message.chat.id, "Здравствуйте! Вы попали в Телеграмм бота для записи в наш сервис EuroCardan.")
    bot.send_message(message.chat.id, "Пожалуйста, выберите опцию:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Запись на прием")
def record_appointment(message):
    bot.send_message(message.chat.id, "Пожалуйста, введите марку, модель и государственный номер вашего транспорта.")
    USER_STATE[message.chat.id] = 'awaiting_vehicle'


@bot.message_handler(func=lambda message: USER_STATE.get(message.chat.id) == 'awaiting_vehicle')
def vehicle_response(message):
    vehicle = message.text
    bot.send_message(message.chat.id, f"Вы выбрали: {vehicle}. Теперь выберите дату для записи.")

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for date in ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница (до 17:00)"]:
        markup.add(date)
    bot.send_message(message.chat.id, "Выберите дату:", reply_markup=markup)

    USER_STATE[message.chat.id] = 'awaiting_date'


@bot.message_handler(func=lambda message: USER_STATE.get(message.chat.id) == 'awaiting_date')
def date_response(message):
    appointment_date = message.text
    bot.send_message(message.chat.id, f"Вы выбрали дату: {appointment_date}. Теперь выберите время для записи.")

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for time in ["9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]:
        markup.add(time)
    bot.send_message(message.chat.id, "Выберите время:", reply_markup=markup)

    USER_STATE[message.chat.id] = 'awaiting_time'


@bot.message_handler(func=lambda message: USER_STATE.get(message.chat.id) == 'awaiting_time')
def time_response(message):
    appointment_time = message.text
    bot.send_message(message.chat.id, "Пожалуйста, оставьте свои контактные данные: имя и номер телефона.")

    # Сохраняем информацию о времени записи
    USER_STATE[message.chat.id] = {'state': 'awaiting_contact', 'time': appointment_time}


@bot.message_handler(func=lambda message: USER_STATE.get(message.chat.id, {}).get('state') == 'awaiting_contact')
def contact_response(message):
    contact_info = message.text
    appointment_time = USER_STATE[message.chat.id]['time']

    bot.send_message(message.chat.id, f"Спасибо! Вы оставили следующие данные: {contact_info}.")
    bot.send_message(message.chat.id,
                     f"Запись произошла успешно на {appointment_time}! Наш сервис находится по адресу: "
                     f"станция метро Стахановская, 1-ый вязовский проезд, дом 7")

    bot.send_message(message.chat.id, PAYMENT_INFO)

    # Удаляем состояние пользователя после завершения процесса
    USER_STATE.pop(message.chat.id, None)


@bot.message_handler(func=lambda message: message.text == "Оплата")
def payment_info(message):
    bot.send_message(message.chat.id, PAYMENT_INFO)


@bot.message_handler(content_types=['text', 'photo', 'sticker'])
def handle_message(message):
    if message.photo or message.sticker:
        bot.send_message(message.chat.id, 'U0001F9D0')

@bot.message_handler(func=lambda message: True)
def fallback_response(message):
    bot.send_message(message.chat.id, "Пожалуйста, следуйте инструкциям или выберите одну из предложенных опций.")


bot.polling()
