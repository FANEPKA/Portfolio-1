from aiogram import bot
from payments import get_pay_url
from config import bot,admins,api as qiwiapi
from keyboards import pay_url_keyboard,check_pay_markup,withdraw_admin_check
import os
from database import DBCommands
from SimpleQIWI.Errors import QIWIAPIError
from api import terminal_collect,get_user_balance,get_subagnet_balance,agent_deposit_subagent,get_terminal_bets_info

import smtplib
from email.message import EmailMessage
import string
import random
import re
from datetime import datetime,timedelta
import time


db = DBCommands()

async def qiwi_in(message):
    try:
        sum = float(message.text)
    except:
        await bot.send_message(message.chat.id, "❌ Сумма должна быть числом")
    else:
            if sum < 15:
                await bot.send_message(message.chat.id, "❌ Минимальная сумма пополнения 15₽")
            else:
                if sum > get_subagnet_balance(8738,1):
                    agent_deposit_subagent(8738,sum)
                invoice = get_pay_url(sum)
                pay_url = invoice[0]
                bill_id = invoice[1]
                print("Bill id" + str(bill_id))
                await db.set_bill_id(message.chat.id, bill_id)
                await bot.send_message(message.chat.id, f"Отлично, пополнить вы можете тут 👇",
                                reply_markup=pay_url_keyboard(pay_url))
                await bot.send_message(message.chat.id, 'После пополнения ОБЯЗАТЕЛЬНО нажмите "✅ Проверить оплату"',
                                reply_markup=check_pay_markup())
            
async def vivod_possible_check(message):
    user_info = await db.get_user_info(message.chat.id)
    
    if user_info.is_activated_promo == True:
        user_balance = get_user_balance(user_info.terminal_id)
        user_bonus_payment = await db.get_bonus_balance(message.chat.id)    

        from_date = user_bonus_payment.payment_date
        to_date = from_date + timedelta(days=10)
            
        unix_from_date = time.mktime(from_date.timetuple())
        unix_to_date = time.mktime(to_date.timetuple())
        
        terminal_bets = get_terminal_bets_info(user_info.terminal_id,unix_from_date,unix_to_date)
        
        bets_amount = 0
        if terminal_bets['list'] == []:
            return False
        
        for terminal_bet in terminal_bets['list']:
            bets_amount += terminal_bet['bet']
                    
        if bets_amount >= user_bonus_payment.amount or user_bonus_payment == None:
            return True
        else:
            return False
        
    return True                
            
async def qiwi_out(message):
    try:
        number = message.text
    except:
        await bot.send_message(message.chat.id, "❌ Некорректный ввод")
    else:
        user_info = await db.get_user_info(message.chat.id)
        balance = get_user_balance(user_info.terminal_id)
        if await vivod_possible_check(message) == True:
            if balance >= 15:
                try:
                    if balance >= 5000:
                        for admin in admins:
                            await bot.send_message(admin, f"Запрос на вывод\nНик:@{message.from_user.username}\nЛогин терминала:{message.chat.id}\nСумма вывода:{balance}", reply_markup=withdraw_admin_check())
                    else:        
                        qiwiapi.pay(account=number, amount=balance, comment=f'Вывод для @{message.from_user.username}')
                        terminal_collect(user_info.terminal_id)
                        await db.create_payment(message.from_user.username, balance, "Вывод QIWI")
                        await db.edit_balance(message.chat.id)
                        await bot.send_message(message.chat.id, "Деньги были отправлены!")
                except QIWIAPIError as e:
                    await bot.send_message(message.chat.id, e)
            else:
                await bot.send_message(message.chat.id, "❌ Минимальная сумма вывода 1000₽")
        else:
            await bot.send_message(message.chat.id, "Вы должны отыграть свои бонусы (общая сумма ставок должна превышать сумму бонуса)")        

# async def make_out_admin(message):
#     qiwiapi.pay(account=number, amount=balance, comment=f'Вывод для @{message.from_user.username}')
#     terminal_collect(user_info.terminal_id)
#     await db.create_payment(message.from_user.username, balance, "Вывод QIWI")
#     await db.edit_balance(message.chat.id)
#     await bot.send_message(message.chat.id, "Деньги были отправлены!")
        

async def btc_check_popoln(message):
    os.system(f"python btc.py {message.text} {message.chat.id} --in")            
    await db.edit_balance(message.chat.id)

async def btc_check_vivod(message):
    user_info = await db.get_user_info(message.chat.id)
    balance = get_user_balance(user_info.terminal_id)
    if await vivod_possible_check(message) == True:
        if balance >= 1000:
            await bot.send_message(message.chat.id, "Подождите пожалуйста...")
            os.system(f"python btc.py {balance} {message.chat.id} --out")
            await db.edit_balance(message.chat.id)
            await db.create_payment(message.from_user.username, balance, "Вывод BTC")
            terminal_collect(user_info.terminal_id)
        else:
            await bot.send_message(message.chat.id, "❌ Минимальная сумма вывода 1000₽")
    else:
        await bot.send_message(message.chat.id, "Вы должны отыграть свои бонусы (общая сумма ставок должна превышать сумму бонуса)")       

async def check_mail(message):
    letters = string.digits
    random_code = ''.join(random.choice(letters) for i in range(8))

    email = message.text

    sender = "GoldenAlex7777@gmail.com"
    
    adress_regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    if(re.search(adress_regex, email)):
        receivers = [email]
        msg = EmailMessage()

        msg["Subject"] = "Код подтверждения от Golden Alex Banker"
        msg["From"] = sender
        msg["To"] = receivers
        
        msg.set_content("Your code: {0}".format(random_code))

        
        try:
            smtpObj = smtplib.SMTP('smtp-relay.sendinblue.com',587)
            smtpObj.login('artem.logachov773@gmail.com','50Jna9rqQY4pL8bR')
            smtpObj.send_message(msg)         
        except smtplib.SMTPException as e:
            print ("Error: unable to send email" + str(e))
            
        return random_code
        
    else:
        return False

    
def is_digit(string):
    if string.isdigit():
        return True
    else:
        try:
            float(string)
            return True
        except ValueError:
            return False    
    