from qiwi_payments.kassa import QiwiKassa
from SimpleQIWI import QApi
from aiogram import Bot
from sqlalchemy.sql import operators

BOT_TOKEN = "1627472154:AAFDvxAGl-40dr9jrrU36h1IdI7swKDuRD4"
bot = Bot(token=BOT_TOKEN)

qiwi_api_token = "d7681079506fd311d091bf599d9525f4"

cashier = QiwiKassa ("eyJ2ZXJzaW9uIjoiUDJQIiwiZGF0YSI6eyJwYXlpbl9tZXJjaGFudF9zaXRlX3VpZCI6Imo4eHAzNy0wMCIsInVzZXJfaWQiOiI3OTg3MzM1ODI2MiIsInNlY3JldCI6ImJiYjQ5NWQzNTA0MTJiZTU5MmFkZjc2MGZjMDY4YTgyYjE0YWQwYWM2ODc5YjNjZTBmZmJmZDBjNGY1MTQwZjIifX0=")

qiwi_phone = "79873358262"


api = QApi(token=qiwi_api_token, phone=qiwi_phone)

DB_NAME = "banker_bot"
DB_HOST = "localhost"
DB_USERNAME = "postgres"
DB_PASS = "artem4569"
#DB_PASS = "434264323"

admins = [488546565]