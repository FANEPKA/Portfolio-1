import sys
from datetime import datetime

from config import bot
from time import sleep
from telethon import TelegramClient, events
from telethon.tl import functions

from database import DBCommands

from api import terminal_deposit

api_id = 2742315
api_hash = '19bcb62caaec31d25c94c684c9f322b2'
username = 'Artimidion'

client = TelegramClient(username, api_id, api_hash)

db = DBCommands()

async def main():
    
    if sys.argv[3] == "--out":
        await client.send_message('BTC_CHANGE_BOT', '💼 Кошелек')
        sleep(0.5)
        message = await client.get_messages("BTC_CHANGE_BOT")
        await message[-1].click(data=b'0|0|gift_actions')
        sleep(0.5)

        message = await client.get_messages("BTC_CHANGE_BOT")
        await message[-1].click(data=b'0|0|make_voucher')
        sleep(0.5)

        message = await client.get_messages("BTC_CHANGE_BOT")
        await message[-1].click(text="RUB")
        sleep(0.5)

        await client.send_message('BTC_CHANGE_BOT', sys.argv[1])

        sleep(1)
        date = str(datetime.now()).split(" ")[0].split("-")
        entity = await client.get_entity("BTC_CHANGE_BOT")
        result = await client(functions.messages.GetHistoryRequest(
            peer=entity,
            offset_id=0,
            add_offset=0,
            offset_date=datetime(int(date[0]), int(date[1]), int(date[2])),
            limit=1000,
            max_id=0,
            min_id=0,
            hash=0
        ))

        check = result.messages[1].message
        await bot.send_message(sys.argv[2], f"Отлично, вот ваш чек:\n"
                                          f"{check}")
    
    elif sys.argv[3] == "--in":
        try:
            url = sys.argv[1].split("?start=")[1]
            await client.send_message('BTC_CHANGE_BOT', '/start ' + url)
        except:
            pass
        sleep(0.5)

        result = await client(functions.messages.GetPeerDialogsRequest(
            peers=["BTC_CHANGE_BOT"]
        ))
        result = result.messages[-1].message

        if result != "Упс, кажется, данный чек успел обналичить кто-то другой 😟":
            try:
                in_rub = round(float(result.split(" ")[4][1:]), 2)
                terminal_deposit(sys.argv[2],in_rub)
                await bot.send_message(sys.argv[2], f"Отлично! На ваш счёт поступило {in_rub}₽")
            except Exception as e:
                print("Exce: " + str(e))
                await bot.send_message(sys.argv[2], "Чек неправильный или его уже обналичил кто-то другой 😟" + str(e))
        else:
            await bot.send_message(sys.argv[2], "Чек неправильный или его уже обналичил кто-то другой 😟")


client.start()
client.loop.run_until_complete(main())
