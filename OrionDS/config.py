import time
import discord
from datetime import datetime

"""

    Конфинг бота Orion
    Version: 0.1
    Owner: https://vk.com/fanepka

"""


TOKEN = 'ODk4NjI2OTYxMjE0MTUyNzQ3.YWm9kw.HNJBXATpmhBRNKUWRcf_OGZWDks'
ID = 898238202584899584


OWNER_BOT = 383958826245816321

DB_HOST = 'localhost'
DB_USER = "phpmyadmin"
DB_PASS = "admin"
DB_NAME = "OrionDS"

VERSION = '0.1'

#DISCORD_SERVER = 'mwu5PhudrE'
#ERROR_CHANNEL = 877866920139960370

XP_FOR_UP_RANK = 100
XP_PER_MESSAGE = 5


BETA = False
GUILDS = [746825333289779221, 600582866707021824]

COLOR = discord.Color.blue()

DELETE_AFTER = 15

END_TIME_FOR_BANS = 5*60
END_TIME_FOR_ROLES = 1*60

IF_BANS = 3
IF_ROLES = 5

VMUTE_NAME = 'VMute'
MUTE_NAME = 'Mute'


LOGS = {

    "messages": 'сообщениям',
    "bans": "блокировкам",
    "mutes": "мутам",
    "welcome": 'приветствиям',
    "voice": "войсами",
    "nicks": "никами",
    "role": "группами ролей"

}

TYPES_LOGS = ['messages', 'mutes', 'bans', 'welcome', 'voice', 'nicks', 'role']
TYPES_WELCOME = ['new', 'get', 'remove']

LVL_NAMES = {

    1: "Мл.Модератор",
    2: "Модератор",
    3: "Администратор",
    4: "Спец.Администратор",
    5: "Создатель",

}


COMMANDS = {
    
    "help": {"lvl": 1, "description": "список команд администрации", "prime": False},
    "kick": {"lvl": 2, "description": "исключить участника из гильдии", "prime": False},
    "mute": {"lvl": 1, "description": "выдать блокировку текстовых каналах участнику", "prime": False},
    "vmute": {"lvl": 1, "description": "выдать блокировку в голосовых каналах участнику", "prime": False},
    "unmute": {"lvl": 1, "description": "снять блокировку в голос./текс. каналах", "prime": False},
    "admins": {"lvl": 1, "description": "список администрации гильдии", "prime": False},
    "get": {"lvl": 2, "description": "информация об участнике", "prime": False},
    "setadm": {"lvl": 4, "description": "установить права администратора участнику", "prime": False},
    "cmds": {"lvl": 6, "description": "управления командами бота", "prime": False},
    "events": {"lvl": 6, "description": "управления событиями бота", "prime": False},
    "ban": {"lvl": 3, "description": "заблокировать участника в гильдии", "prime": False},
    "unban": {"lvl": 3, "description": "разблокировать участника в гильдии", "prime": False},
    "lban": {"lvl": 4, "description": "заблокировать участника во всех гильдиях", "prime": False},
    "unlban": {"lvl": 4, "description": "разблокировать участника во всех гильдиях", "prime": False},
    "prefix": {"lvl": 5, "description": "настройки префикса бота", "prime": False},
    "logs": {"lvl": 5, "description": "установка логов на канал", "prime": False},
    "rlogs": {"lvl": 5, "description": "удаление логов с канала", "prime": False},
    "lvlname": {"lvl": 5, "description": "настройка имен уровней", "prime": False},
    "clear": {"lvl": 1, "description": "очистить сообщения", "prime": False},
    "welcome": {"lvl": 5, "description": "настройка приветствия", "prime": False},
    "local": {"lvl": 5, "description": "настройка локализации", "prime": False},
    "say": {"lvl": 1, "description": "отправить сообщение от имени бота", "prime": False},
    "warn": {"lvl": 2, "description": "выдать предупреждение участнику", "prime": False},
    "unwarn": {"lvl": 2, "description": "снять предупреждение участнику", "prime": False},
    "roles": {"lvl": 4, "description": "настройки группы ролей", "prime": True},
    "role": {"lvl": 0, "description": "подача заявки на роль", "prime": True},
    "войс": {"lvl": 4, "description": "настройка голосовых комнат", "prime": False},
    
}