from datetime import datetime, time, timedelta
from aiogram.types.input_media import InputMedia, InputMediaPhoto, MediaGroup
from assets import qiwi_in,btc_check_popoln,qiwi_out,btc_check_vivod,is_digit,check_mail
import logging
from aiogram import Dispatcher, executor, types
from aiogram.dispatcher.filters import state
from aiogram.types import message
from config import cashier
import keyboards
from database import DBCommands,create_db
from config import bot
from states import QiwiIn,BtcIn,QiwiOut,EmailCheck
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from api import get_total_transactions,get_terminal_link,terminal_deposit,get_user_balance,get_terminal_transactions,agent_deposit_subagent
import time

logging.basicConfig(level=logging.INFO)


dp = Dispatcher(bot,storage=MemoryStorage())

db = DBCommands()

@dp.message_handler(commands=['user'])
async def send_welcome(message: types.Message):

    await message.answer(types.User.get_current())

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await db.add_user()
    
    await message.answer('Выберите опцию', reply_markup= await keyboards.start_keyboard(message))

@dp.message_handler(content_types=['text'])
async def text_keyboard(message : types.Message):
    await db.add_user()
    if message.text == "↪️ Пополнить через бота":
        photo = open("static/пополнение.png", "rb")
        await bot.send_photo(message.chat.id, photo, caption = "Выберите метод пополнения", reply_markup=keyboards.replenishment_options())
    
    elif message.text == "↩️ Вывести средства через бота":
        photo = open("static/вывод.png", "rb")
        user_info = await db.get_user_info(message.chat.id)
        if user_info.email == None:
            await message.answer("Введите свой Email для вывода средств")  
        
            await EmailCheck.email.set()
        else:
            await bot.send_photo(message.chat.id, photo ,"Выберите метод вывода", reply_markup=keyboards.withdraw_options())
        
    elif message.text == "◀️ Отменить":
        await message.answer("Платеж отменен", reply_markup= await keyboards.start_keyboard(message))
        
    elif message.text == "👤 Мой профиль":
        await db.add_user()
        user_info = await db.get_user_info(message.chat.id)
        user_login = user_info.user_login
        user_pass = user_info.user_pass
        nick = user_info.nick
        reg_date = user_info.reg_date
        reg_date = reg_date.strftime('%Y-%m-%d %H:%M')
        balance = get_user_balance(user_info.terminal_id)
        permanent_link = get_terminal_link(user_info.terminal_id)
        
        photo = open("static/профиль.png", "rb")
        await bot.send_photo(message.chat.id, photo, caption = f" Ник: @{nick}\nЛогин для входа: {user_login}\nПароль: {user_pass}\nТекущий баланс: {balance} ₽\nВаша ссылка для входа: {permanent_link}\nДата регистрации: {reg_date}\n➖➖➖➖➖➖➖➖➖➖➖\nНЕ нажимайте CASHOUT находясь в терминале, все выводы средств делайте строго через нашего бота", reply_markup=keyboards.payments_check_keyboard())

    
    elif message.text == "🆘 Инструкция":
        media_arr = ["static/guide1.png","static/guide2.png","static/guide3.png","static/guide4.png"]
        await message.answer("Краткая инструкция по использованию")
        await bot.send_media_group(message.chat.id,[InputMediaPhoto(open(photo,'rb')) for photo in media_arr])
    
    elif message.text == "✅ Проверить оплату":
        bill_id = await db.get_user_bill_id(message.chat.id)
        if bill_id is None:
            await message.answer("❌ Вы не начинали оплату!")
            return
        print(bill_id)
        bill_status = cashier.check_bill(bill_id)

        if bill_status.is_paid:
            amount = bill_status.amount.value
            user_info = await db.get_user_info(message.chat.id)
            new_balance = user_info.balance + float(amount)
            terminal_deposit(message.chat.id, new_balance)
            await db.edit_balance(message.chat.id)
            await db.create_payment(message.from_user.username, amount, "Пополнение QIWI")
            await message.answer(f"Успешное пополнение на {amount}₽!",
                             reply_markup= await keyboards.start_keyboard(message))
            await db.reset_bill_id(message.chat.id)

        else:
           await message.answer("Вы не оплатили счёт!❌")    
    
    elif message.text == "🤑 Получить бонусные 300 рублей!!!":
        user_info = await db.get_user_info(message.chat.id)
    
        if user_info.is_activated_promo == False:
            amount = 300
            agent_deposit_subagent(8738,300)
            terminal_deposit(user_info.user_login,amount)
            await db.activate_promo(message.chat.id)
            await db.create_payment(message.from_user.username, amount, "Бонусное пополнение")
            await message.answer("Вам успешно зачислено 300 бонусных рублей")
        else:
            await message.answer("Вы уже получили бонус!")    
    
    elif message.text == "💬 Информация о нашем боте":
        photo = open("static/Информация.png", "rb")
        await bot.send_photo(message.chat.id, photo,'''ВНИМАНИЕ❗️❗️❗️

👋🏻Тебя приветствует Лицензионное Наземное-Казино. "Golden Alex" 🥇

🆓Каждому новому игроку при регистрации мы дарим бесплатно 300 руб.

💥Казино-Одобренное свыше 2 330 721  пользователями!

🔥Здесь, Ты можешь бесплатно и быстро пройти Регистрацию через нашего бота @GOLDEN_ALEX_BANKER_BOT

⚡️Представляем твоему вниманию на удивление огромный выбор игр,среди которых ты найдешь как Популярные слоты так и Новинки.

💫Быстрая работа сайта позволит погрузиться в мир захватывающей игры сосредоточив внимание на тактике!

🤑Чудесные, не передаваемые, эмоции обеспечены!

💰Для тебя мы приготовили Отличные Бонусы и Акции!! Плюс Эксклюзивные Подарки на Депозит !!!''')
    
    elif message.text == "📝 Тех. поддержка":
        photo = open("static/помощь.png", "rb")
        await bot.send_photo(message.chat.id, photo, "ℹ ️По всем вопросам писать: @ledi456 \n")
        # await message.answer("Мы связали вас с оператором, пришлите ему свое сообщение")
        # await bot.send_message(operators_id[0], f"Вам пишет @{message.from_user.username}")
        # await SupportUser.first()
    
@dp.callback_query_handler(lambda call : call.data)
async def callback_process(call):
    data = call.data
    if data == "qiwi_replenishment":
        
        await bot.delete_message(chat_id = call.message.chat.id,message_id = call.message.message_id)
        await bot.send_message(chat_id = call.message.chat.id, text = "Введите сумму пополнения (мин. 15₽)")  
        
        await QiwiIn.amount.set()
        
    elif data == "user_replenishment":
        
        user_replenishments_text = ""
        parent_id = 8738
        user_info = await db.get_user_info(call.message.chat.id)
        terminal_login = user_info.user_login
        replenishments_count = 5
        from_date = datetime(2021,6,10)
        to_date = from_date + timedelta(days=723)
        
        unix_from_date = time.mktime(from_date.timetuple())
        unix_to_date = time.mktime(to_date.timetuple())
        
        user_replenishments_amount = get_total_transactions(parent_id,terminal_login,unix_from_date,unix_to_date)['totalIn']
        
        all_replenishments = get_terminal_transactions(parent_id,terminal_login,replenishments_count,unix_from_date,unix_to_date)
        photo = open("static/пополнения.png", "rb")
        if all_replenishments['list'] != None:
            for user_replenishment in all_replenishments['list']:
                if user_replenishment['isDeposit'] == True:
                    user_replenishments_text += (
                        f"🛒ID траназакции: {user_replenishment['id']}\n"
                        f"↩️ От терминала: {user_replenishment['terminal']}\n"
                        f"💳 Сумма пополнения: {str(user_replenishment['amount'])}₽\n"
                        f"Тип платежа: Пополнение средств\n"
                        f"Дата: {datetime.fromtimestamp(user_replenishment['date'] / 1000)}\n"
                        f"➖➖➖➖➖➖➖➖➖➖➖\n"
                    )
        else:
            user_replenishments_text = "У этого пользователя еще нету выводов"
        await bot.delete_message(chat_id = call.message.chat.id,message_id = call.message.message_id)
        await bot.send_photo(call.message.chat.id, photo, caption = f"Всего пополнений на сумму: {user_replenishments_amount}\n\nПоследние пополнения:\n{user_replenishments_text}")
        
    elif data == "user_withdrawal":
        # all_withdrawals = await db.get_all_user_withdrawal(call.message.chat.id)
        
        user_withdrawal_text = ""
        parent_id = 8738
        user_info = await db.get_user_info(call.message.chat.id)
        terminal_login = user_info.user_login
        withdrawals_count = 10
        from_date = datetime(2021,6,10)
        to_date = from_date + timedelta(days=723)
        
        unix_from_date = time.mktime(from_date.timetuple())
        unix_to_date = time.mktime(to_date.timetuple())
        
        user_withdrawal_amount = get_total_transactions(parent_id,terminal_login,unix_from_date,unix_to_date)['totalOut']
        
        all_withdrawals = get_terminal_transactions(parent_id,terminal_login,withdrawals_count,unix_from_date,unix_to_date)
        
        photo = open("static/выводы.png", "rb")
        if all_withdrawals['list'] != None:
            for user_withdrawal in all_withdrawals['list']:
                
                if user_withdrawal['isDeposit'] == False:
                    user_withdrawal_text += (
                        f"🛒ID траназакции: {user_withdrawal['id']}\n"
                        f"↩️ От терминала: {user_withdrawal['terminal']}\n"
                        f"💳 Сумма вывода: {str(user_withdrawal['amount'])}₽\n"
                        f"Тип платежа: Вывод средств\n"
                        f"Дата: {datetime.fromtimestamp(user_withdrawal['date'] / 1000)}\n"
                        f"➖➖➖➖➖➖➖➖➖➖➖\n"
                    )
        else:
            user_withdrawal_text = "У этого пользователя еще нету выводов"
        
        await bot.delete_message(chat_id = call.message.chat.id,message_id = call.message.message_id)
        await bot.send_photo(call.message.chat.id,photo, f"Всего выводов на сумму: {user_withdrawal_amount}₽\n\nПоследние выводы:\n{user_withdrawal_text}")
    
    # elif data == "admin_confirm_withdraw":
    #     await make_out_admin()
    
    
    elif data == "btc_replenishment":
        await bot.delete_message(chat_id = call.message.chat.id,message_id = call.message.message_id)
        await bot.send_message(call.message.chat.id,"Пришлите чек... (принимаются только рубли!!!)")  
        
        await BtcIn.check.set()

    elif data == "qiwi_withdraw":
        await bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)

        await call.message.answer("Введите свой номер киви кошелька (+79876543210)")

        await QiwiOut.amount.set()
        
    elif data == "btc_withdraw":
        await bot.delete_message(chat_id = call.message.chat.id,message_id = call.message.message_id,)
        #await bot.send_message(call.message.chat.id,"Минимальная сумма вывода 1000₽")  
        await btc_check_vivod(call.message)
        



@dp.message_handler(state=EmailCheck.email)
async def email_check(message: types.Message, state: FSMContext):
    email = message.text
    all_users_emails = await db.get_all_emails()
    email_tuple = (email,)
    
    await state.update_data(mail = email)
    
    sended_mail = await check_mail(message)
    
    if sended_mail == False:
        await message.answer("Неверный Email")
        await state.finish()
    
    elif email_tuple in all_users_emails:
        await message.answer("Пользователь с таким Email уже существует")
        await state.finish()
        

    else:
        code = sended_mail
        await state.update_data(confirm_code = code)
        await message.answer("Мы отправили письмо с кодом потдверждения вам на почту. Не забудьте проверить папку Спам")
        await message.answer("Введите код, который пришел вам на почту")
        await EmailCheck.next()


@dp.message_handler(state=EmailCheck.user_confirm_code)
async def confirm_code_check(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    code = state_data.get("confirm_code")
    email = state_data.get("mail")
    user_code = message.text
    if user_code == code:
        await db.set_user_email(message.chat.id, email) 
        await state.finish()
        await message.answer("Вы успешно подтвердили Email. И можете выводить средства")
    else:
        await state.finish()
        await message.answer("Неверный код подтверждения, попробуйте еще раз")
             
        
@dp.message_handler(state=QiwiIn.amount)
async def qiwi_in_amount(message: types.Message, state: FSMContext):
    amount = message.text
    
    await state.update_data(amount1 = amount)
    data = await state.get_data()
    #info = data.get("amount1")
    await qiwi_in(message)
    
    await state.finish()

@dp.message_handler(state=BtcIn.check)
async def btc_in_amount(message: types.Message, state: FSMContext):
    check = message.text
    
    await state.update_data(amount1 = check)
    await btc_check_popoln(message)
    
    await state.finish()    


@dp.message_handler(state=QiwiOut.amount)
async def qiwi_out_amount(message: types.Message, state: FSMContext):
    amount = message.text
    if is_digit(amount) and float(amount) < 100:
        await message.answer("Минимальная сумма вывода 100₽")
    else:    
        await state.update_data(amount1 = amount)
        await qiwi_out(message)
    
    await state.finish()


async def on_startup(dp):
    await create_db()

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)



