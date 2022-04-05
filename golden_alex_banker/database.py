from hashlib import new
from aiogram import types
from aiogram.types.base import Boolean
from gino import Gino
from sqlalchemy import (Column, Integer, BigInteger, String,
                        Sequence, Float, Boolean, TIMESTAMP, or_, and_)
from sqlalchemy import sql
from sqlalchemy.sql.functions import current_date, user

from config import DB_NAME,DB_HOST,DB_PASS,DB_USERNAME
from datetime import datetime, timedelta
from api import get_user_balance,create_terminal,get_terminals

db = Gino()

class User(db.Model):
    __tablename__ = "Users"
    
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    tg_id = Column(BigInteger)
    terminal_id = Column(BigInteger)
    nick = Column(String(50))
    user_login = Column(String(150))
    user_pass = Column(String(100))
    email = Column(String(120))
    balance = Column(Float)
    reg_date = Column(TIMESTAMP)
    bill_id = Column(String(80))
    is_activated_promo = Column(Boolean, default=False)
    query: sql.Select
    
    def __repr__(self):
        return "<User(id='{}', nick='{}')>".format(
        self.id, self.nick)

class Payment(db.Model):
    __tablename__ = "Payments"
    
    id = Column(Integer, Sequence('payment_id_seq'), primary_key=True)
    from_user = Column(String(40))
    amount = Column(Float)
    payment_status = Column(String(40))
    payment_date = Column(TIMESTAMP)
    query: sql.Select

    
    def __repr__(self):
        return "<Payment(id='{}', amount='{}')>".format(
        self.id, str(self.amount))
    
class DBCommands:
    async def get_user_info(self,user_id):
        user = await User.query.where(User.tg_id == user_id).gino.first()

        return user
    
    async def get_all_emails(self):
        emails = await User.select('email').gino.all()

        return emails
    
    async def add_user(self):
        user = types.User.get_current()
        old_user = await self.get_user_info(user.id)
        
        if old_user:
            return old_user
        
        terminals = get_terminals(8738,"login",user.id)
        print(terminals)
        if not terminals['list']:
            created = create_terminal(8738,user.id)
            print(created)
            terminal_login = created['list'][0]['login']
            terminal_pass = created['list'][0]['password']
            terminal_id = created['list'][0]['id']
            new_user = User()
            new_user.tg_id = user.id
            new_user.nick = user.username
            new_user.user_login = terminal_login
            new_user.user_pass = terminal_pass
            new_user.terminal_id = terminal_id
            new_user.email = None
            new_user.balance = get_user_balance(terminal_id)
            new_user.reg_date = datetime.now()

            await new_user.create()
            return new_user
        else:
            terminal_login = terminals['list'][0]['login']
            terminal_pass = terminals['list'][0]['password']
            terminal_id = terminals['list'][0]['id']
            new_user = User()
            new_user.tg_id = user.id
            new_user.nick = user.username
            new_user.user_login = terminal_login
            new_user.user_pass = terminal_pass
            new_user.terminal_id = terminal_id
            new_user.email = None
            new_user.balance = get_user_balance(terminal_id)
            new_user.reg_date = datetime.now()
            
            await new_user.create()
            return new_user

        
    async def get_user_bill_id(self,user_id):
        bills = await User.select('bill_id').where(User.tg_id == user_id).gino.scalar()
        print("Bills" + str(bills))
       
        try:
            return bills
        except:
            return  None
        
    async def set_bill_id(self,user_id,bill_id):
        bills = await User.query.where(User.tg_id == user_id).gino.first()
        await bills.update(bill_id = bill_id).apply()
    
    async def reset_bill_id(self,user_id):
        bills = await User.query.where(User.tg_id == user_id).gino.first()
        await bills.update(bill_id = None).apply()
    
    async def activate_promo(self,user_id):
        user = await self.get_user_info(user_id)
        if user.is_activated_promo == False:
            await user.update(is_activated_promo = True).apply()
           
    async def edit_balance(self,user_id):
        user = await User.query.where(User.tg_id == user_id).gino.first()
        current_balance = get_user_balance(user.terminal_id)
        print("Current balance:" + str(current_balance))
        await user.update(balance = current_balance).apply()
    
    async def get_all_user_replenishment(self,user_id):
        user = await self.get_user_info(user_id)
        payments = await Payment.query.where(and_(Payment.from_user == user.nick, or_(Payment.payment_status == "Пополнение QIWI", Payment.payment_status == "Пополнение BTC"))).gino.all()

        return payments
    
    async def get_bonus_balance(self,user_id):
        user = await self.get_user_info(user_id)
        
        bonus_payments = await Payment.query.where(and_(Payment.from_user == user.nick, Payment.payment_status == "Бонусное пополнение")).gino.first()
        
        return bonus_payments or None
    
    async def get_all_user_withdrawal(self,user_id):
        user = await self.get_user_info(user_id)
        payments = await Payment.query.where(and_(Payment.from_user == user.nick, or_(Payment.payment_status == "Вывод QIWI", Payment.payment_status == "Вывод BTC"))).gino.all()
        print(payments)
        return payments
    
    
    async def set_user_email(self,user_id,email):
        user = await self.get_user_info(user_id)
        if not user.email:
            await user.update(email = email).apply()
        
        
    async def create_payment(self,from_user,amount, payment_status):
        new_payment = Payment()
        new_payment.from_user = from_user
        new_payment.amount = amount
        new_payment.payment_status = payment_status
        new_payment.payment_date = datetime.now()

        await new_payment.create()
        return new_payment
        
async def create_db():
    await db.set_bind(f'postgresql://{DB_USERNAME}:{DB_PASS}@{DB_HOST}/{DB_NAME}')     
    #await db.gino.drop_all()
    await db.gino.create_all()
            