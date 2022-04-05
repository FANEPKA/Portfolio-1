from aiogram import types
from aiogram.types import message
from database import DBCommands

db = DBCommands()

async def start_keyboard(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    profile = types.KeyboardButton('👤 Мой профиль')
    automate_in = types.KeyboardButton('↪️ Пополнить через бота')
    automate_out = types.KeyboardButton('↩️ Вывести средства через бота')
    operator = types.KeyboardButton('📝 Тех. поддержка')
    bonus = types.KeyboardButton('🤑 Получить бонусные 300 рублей!!!')
    about = types.KeyboardButton('💬 Информация о нашем боте')
    help = types.KeyboardButton('🆘 Инструкция')
    
    user_info = await db.get_user_info(message.chat.id)
    
    markup.row(profile)
    markup.row(automate_in,automate_out)
    markup.row(about,operator)
    markup.row(help)
    
    if user_info.is_activated_promo == False:
        markup.row(bonus)
        
    return markup

def replenishment_options():
    markup = types.InlineKeyboardMarkup(row_width=2)

    qiwi = types.InlineKeyboardButton("QIWI", callback_data="qiwi_replenishment")
    btc = types.InlineKeyboardButton("BTC BANKER", callback_data="btc_replenishment")

    markup.add(qiwi, btc)
    return markup


def withdraw_options():
    markup = types.InlineKeyboardMarkup(row_width=2)

    qiwi = types.InlineKeyboardButton("QIWI", callback_data="qiwi_withdraw")
    btc = types.InlineKeyboardButton("BTC BANKER", callback_data="btc_withdraw")

    markup.add(qiwi, btc)
    return markup

def withdraw_admin_check():
    markup = types.InlineKeyboardMarkup(row_width=2)

    confirm = types.InlineKeyboardButton("Подтвердить", callback_data="admin_confirm_withdraw")
    abort = types.InlineKeyboardButton("Отклонить", callback_data="admin_abort_withdraw")

    markup.add(confirm, abort)
    return markup

def pay_url_keyboard(url):
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("↪ Пополнить", url=url)
    markup.add(button)

    return markup


def check_pay_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("✅ Проверить оплату")
    markup.add("◀️ Отменить")

    return markup

def payments_check_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)

    replenishment = types.InlineKeyboardButton("Мои депозиты", callback_data="user_replenishment")
    withdrawal = types.InlineKeyboardButton("Мои выводы", callback_data="user_withdrawal")

    markup.row(replenishment, withdrawal)
    return markup