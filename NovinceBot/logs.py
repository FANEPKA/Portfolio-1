import time, re
from datetime import datetime
from vkbottle import Bot, Message
from modules import member, connector, database

config = connector.JWORK("config.json").openj()
client = Bot(config['token'], group_id=config['group_id'])
db = database.DataBase(config['db'])
date = datetime.fromtimestamp


# : Функции обработки информации

async def filter(peer, text):
    words = (await db.request(f"SELECT * FROM filters WHERE pid = {peer}", "fetchall"))
    if words and text:
        result = [i for i in words if i['text'].lower() in text.lower()]
        return result != []
    else: return False

async def mention(peer, text):
    words = ["@all", '@online', '@everyone']
    if text:
        result = [i for i in text.split(' ') if i.replace(',', '') in words]
        return (await db.request(f"SELECT * FROM settings WHERE pid = {peer}"))['mention'] == 0 and result != []
    else: return False

async def mention_user(peer, text):
    regex = re.findall(r"id\d+", text)
    if regex: return await db.request(f"SELECT * FROM mentions WHERE mid = {regex[0].replace('id', '')} AND pid = {peer}")
    regex = re.findall(r"club\d+", text)
    if regex: return await db.request(f"SELECT * FROM mentions WHERE mid = {regex[0].replace('club', '-')} AND pid = {peer}")
    

# : Функция для получения сообщений пользователя, а так же обработка их

@client.on.chat_message()
async def new_message(event: Message):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id)
    await author.getUser()
    if await db.request(f"SELECT * FROM mutes WHERE mid = {event.from_id} AND pid = {event.peer_id}"):
        await event(f"Участник {await author.mention} исключен за использование чата во время мута")
        await client.api.messages.remove_chat_user(chat_id = event.peer_id, member_id = event.from_id)
        await author.deleteUser()
        return
    chat = await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}")
    if chat['amode'] == 1 and not (await author.conversation()).is_admin and await author.admin < 1:
        await event(f"Участник {await author.mention} исключен за использованию чата во время режима тишины", disable_mentions=1)
        await client.api.messages.remove_chat_user(chat_id = event.peer_id - 2e9, member_id = author.id)
        await author.deleteUser()
        return
    if await filter(event.peer_id, event.text) and not (await author.conversation()).is_admin and await author.admin < 1:
        await event(f"Участник {await author.mention} исключен за использование слов из фильтра", disable_mentions=1)
        await client.api.messages.remove_chat_user(chat_id = event.peer_id - 2e9, member_id = author.id)
        await author.deleteUser()
        return
    if await mention(event.peer_id, event.text) and not (await author.conversation()).is_admin and await author.admin < 1:
        await client.api.request("messages.delete", {"conversation_message_ids": event.conversation_message_id, "peer_id": event.peer_id, "delete_for_all": 1, "group_id": client.group_id})
        await event(f"Участник {await author.mention} исключен из беседы за использование упоминания в беседе.", disable_mentions=1)
        await client.api.messages.remove_chat_user(chat_id = event.peer_id - 2e9, member_id = author.id)
        await author.deleteUser()
        return
    if await mention_user(event.peer_id, event.text) and not (await author.conversation()).is_admin and await author.admin < 1:
        await event(f"Участник {await author.mention} исключен из беседы за упоминание пользователя", disable_mentions=1)
        await client.api.request("messages.delete", {"conversation_message_ids": event.conversation_message_id, "peer_id": event.peer_id, "delete_for_all": 1, "group_id": client.group_id})
        await client.api.messages.remove_chat_user(chat_id = event.peer_id - 2e9, member_id = author.id)
        await author.deleteUser()
        return

    await author.update('messages', await author.messages + 1)
    await author.update('m_time', time.time())

client.run_polling()