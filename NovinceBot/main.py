import asyncio
from asyncio import events
import time
from datetime import datetime
from vkbottle import Bot, Message
from vkbottle.rule import ChatActionRule
from modules import member, connector, database


"""

    Разработчик: vk.com/fanepka

"""

config = connector.JWORK("config.json").openj()
client = Bot(config['token'], group_id=config['group_id'], loop=asyncio.get_event_loop())
db = database.DataBase(config['db'])
date = datetime.fromtimestamp

# : Доп. системы

async def send(event, message, disable_mentions = False, peer_id = None):
    if not peer_id: await event(message = message, disable_mentions = disable_mentions)
    else: await client.api.messages.send(peer_id = peer_id, message = message, disable_mentions=disable_mentions, random_id=0)

async def getMember(id, nick = None):
    try: 
        member = (await client.api.users.get(user_ids=id))[0]
        return f"[id{member.id}|{member.first_name} {member.last_name}]" if not nick else f"[id{member.id}|🚀]"
    except: 
        group = (await client.api.groups.get_by_id(group_id=id*-1))[0]
        return f"[club{group.id}|{group.name}]" if not nick else f"[club{group.id}|🚀]"

async def getChat(chat):
    return await db.request(f"SELECT * FROM chats WHERE pid = {chat}")

async def inChat(id, chat):
    result = [i for i in (await client.api.messages.get_conversation_members(peer_id = chat, group_id = config['group_id'])).items if i.member_id == id]
    if len(result) > 0: return result[0]
    else: return None

async def getCommands(lvl):
    commands = config['commands']
    lvl_1 = '🛡 Команды модератора:\n'
    lvl_1 += ''.join([f"/{i} - {commands['lvl_1'][i]}\n" for i in commands['lvl_1']])
    lvl_1 += '\n'
    if lvl == 1: return lvl_1

    lvl_2 = '💥 Команды администратора:\n'
    lvl_2 += ''.join([f"/{i} - {commands['lvl_2'][i]}\n" for i in commands['lvl_2']])
    lvl_2 += '\n'
    if lvl == 2: return f"{lvl_1}{lvl_2}"

    lvl_3 = '💎 Команды спец.администратора:\n'
    lvl_3 += ''.join([f"/{i} - {commands['lvl_3'][i]}\n" for i in commands['lvl_3']])
    lvl_3 += '\n'
    if lvl == 3: return f"{lvl_1}{lvl_2}{lvl_3}"

    lvl_4 = '👑 Команды основателя:\n'
    lvl_4 += ''.join([f"/{i} - {commands['lvl_4'][i]}\n" for i in commands['lvl_4']])
    lvl_4 += '\n'
    if lvl >= 4: return f"{lvl_1}{lvl_2}{lvl_3}{lvl_4}"

def getStatus(member: member.Member):
    if member.db['admin'] == 0: return 'Пользователь'
    elif member.db['admin'] == 1: return 'Модератор'
    elif member.db['admin'] == 2: return 'Администратор'
    elif member.db['admin'] == 3: return 'Спец.Администратор'
    elif member.db['admin'] >= 4: return 'Создатель'

async def isChatBlocked(member: member.Member):
    is_muted = await db.request(f"SELECT * FROM mutes WHERE mid = {member.id} AND pid = {member.peer_id}")
    if is_muted: return f'есть | Конец {date(is_muted["time"]).strftime("%d.%m.%y в %H:%M")}'
    return 'нет'

# : События

@client.on.chat_message(ChatActionRule(['chat_invite_user']))
async def invite_user(event: Message):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author, user = member.Member(domain = event.from_id, peer_id = event.peer_id), member.Member(domain = event.action.member_id, peer_id = event.peer_id)
    await author.getUser()
    await user.getUser()
    if not (await author.conversation()).is_admin and await author.admin < 1 and (await db.request(f"SELECT * FROM settings WHERE pid = {event.peer_id}")['invite']) == 0:
        await client.api.messages.remove_chat_user(chat_id = event.peer_id - 2e9, member_id = event.action.member_id)
        await client.api.messages.remove_chat_user(chat_id = event.peer_id - 2e9, member_id = author.id)
        await user.deleteUser()
        await author.deleteUser()
        return
    if await user.getBans():
        await event(f"У участника {await user.mention} есть блокировки в беседе", disable_mentions=1)
        await client.api.messages.remove_chat_user(chat_id = event.peer_id - 2e9, member_id = event.action.member_id)
        await user.deleteUser()
        return
    chat = await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}")
    greeting = ''
    if chat['greet']: greeting = (await db.request(f"SELECT * FROM greetings WHERE id = {chat['greet']}"))['text']
    await event(f"Приветствие нового пользователя - {await user.mention}\n\n{greeting}")
    await user.update(type = 'm_time', data = time.time())

@client.on.chat_message(ChatActionRule(['chat_invite_user_by_link']))
async def invite_user_by_link(event: Message):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    user = member.Member(domain = event.from_id, peer_id = event.peer_id)
    await user.getUser()
    if await user.getBans():
        await event(f"У участника {await user.mention} есть блокировки в беседе", disable_mentions=1)
        await client.api.messages.remove_chat_user(chat_id = event.peer_id - 2e9, member_id = event.action.member_id)
        await user.deleteUser()
        return
    chat = await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}")
    greeting = ''
    if chat['greet']: greeting = (await db.request(f"SELECT * FROM greetings WHERE id = {chat['greet']}"))['text']
    await event(f"Приветствие нового пользователя - {await user.mention}\n\n{greeting}")
    await user.update(type = 'm_time', data = time.time())

@client.on.chat_message(ChatActionRule(["chat_kick_user"]))
async def chat_leave(event: Message):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    if (await db.request(f"SELECT * FROM settings WHERE pid = {event.peer_id}"))['leave'] == 0: return
    user = member.Member(domain = event.action.member_id, peer_id = event.peer_id)
    await user.getUser()
    await user.deleteUser()
    if not (await user.conversation()).is_owner: await client.api.messages.remove_chat_user(chat_id = event.peer_id - 2e9, member_id=user.id)

@client.on.chat_message(ChatActionRule(["chat_title_update"]))
async def title(event: Message):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    user = member.Member(domain = event.from_id, peer_id = event.peer_id)
    print(event)
    await user.getUser()
    if (await db.request(f"SELECT * FROM settings WHERE pid = {event.peer_id}"))['title'] == 1 or (await user.conversation()).is_admin or await user.admin > 0: 
        await db.request(f"UPDATE chats SET title = '{event.action.text}' WHERE pid = {event.peer_id}")
        return
    title = (await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"))['title']
    await client.api.messages.remove_chat_user(chat_id = event.peer_id - 2e9, member_id = user.id)
    await user.deleteUser()
    await client.api.messages.edit_chat(chat_id = event.peer_id - 2e9, title = title)

@client.on.chat_message(ChatActionRule(["chat_pin_message"]))
async def pin(event: Message):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    user = member.Member(domain = event.action.member_id, peer_id = event.peer_id)
    await user.getUser()
    if (await db.request(f"SELECT * FROM settings WHERE pid = {event.peer_id}"))['pin'] == 1 or (await user.conversation()).is_admin or await user.admin > 0: 
        await db.request(f"UPDATE chats SET message = {event.action.conversation_message_id} WHERE pid = {event.peer_id}")
        return
    pin_id = (await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"))['message']
    await client.api.messages.remove_chat_user(chat_id = event.peer_id - 2e9, member_id = user.id)
    await user.deleteUser()
    await client.api.request('messages.unpin', {'peer_id': event.peer_id, 'group_id': config['group_id']})
    if pin_id: await client.api.request('messages.pin', {'peer_id': event.peer_id, 'conversation_message_id': pin_id})

@client.on.chat_message(ChatActionRule(["chat_unpin_message"]))
async def unpin(event: Message):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    user = member.Member(domain = event.action.member_id, peer_id = event.peer_id)
    await user.getUser()
    if (await db.request(f"SELECT * FROM settings WHERE pid = {event.peer_id}"))['pin'] == 1 or (await user.conversation()).is_admin or await user.admin > 0: 
        await db.request(f"UPDATE chats SET message = NULL WHERE pid = {event.peer_id}")
        return
    pin_id = (await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"))['message']
    await client.api.messages.remove_chat_user(chat_id = event.peer_id - 2e9, member_id = user.id)
    await user.deleteUser()
    if pin_id: await client.api.request('messages.pin', {'peer_id': event.peer_id, 'conversation_message_id': pin_id})

# : Команды бота

@client.on.chat_message(text = '/start')
async def start(event: Message):
    if await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return await send(event, "Конференция уже имеет метку \"зарегистрирована\"")
    try:
        peer = (await client.api.messages.get_conversations_by_id(peer_ids = event.peer_id, group_id = config['group_id'])).items[0].chat_settings
        title = peer.title.replace('"', "'")
        await db.request(f'INSERT INTO chats(pid, owner, title) VALUES({event.peer_id}, {peer.owner_id}, "{title}")')
        await db.request(f"INSERT INTO settings(pid) VALUE({event.peer_id})")
        await db.request(f"INSERT INTO members(mid, pid, admin) VALUES({peer.owner_id}, {event.peer_id}, 4)")
        await event(f"Конференция зарегистрирована")
    except: await event(f"Ошибка доступа к конференции. Выдайте права администратора")

@client.on.chat_message(text = ['/kick', '/kick <domain> <reason>', '/kick <domain>'])
async def kick(event: Message, domain = None, reason = None):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 1: return
    if event.reply_message:
        if domain != '-': reason = f"{domain} {reason}" if reason else domain
        domain = event.reply_message.from_id
    if event.fwd_messages != []:
        if domain != '-': reason = f"{domain} {reason}" if reason else domain
        domain = event.fwd_messages[0].from_id
    if not domain: return await send(event, "Укажите ID пользователя")
    user = member.Member(domain = domain, peer_id = event.peer_id)
    if not await user.getUser(): return await send(event, "Пользователь не найден")
    if user.id == -config['group_id']: return await send(event, "Вы не можете исключить меня")
    if not await user.conversation(): 
        await user.deleteUser()
        return await send(event, f'Участник {await user.mention} не состоит в беседе', True)
    if user.id == author.id: return await send(event, "Вы не можете исключить самого себя")
    admin = (await user.conversation()).is_admin if await user.conversation() else False 
    if admin or await user.admin > await author.admin: 
        await user.deleteUser()
        return await send(event, f"У участника {await user.mention} права администратора выше/равны вашим", True)
    reason = f'\nПричина: {reason}' if reason else ''
    await send(event, f"Участник {await user.mention} исключен из конференции{reason}", True)
    await client.api.messages.remove_chat_user(chat_id = event.peer_id - 2e9, member_id = user.id)
    await user.deleteUser()

@client.on.chat_message(text = ['/gkick', '/gkick <domain> <reason>', '/gkick <domain>'])
async def gkick(event: Message, domain = None, reason = None):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 3: return
    if event.reply_message:
        if domain != '-': reason = f"{domain} {reason}" if reason else domain
        domain = event.reply_message.from_id
    if event.fwd_messages != []:
        if domain != '-': reason = f"{domain} {reason}" if reason else domain
        domain = event.fwd_messages[0].from_id
    if not domain: return await send(event, "Укажите ID пользователя")
    user = member.Member(domain = domain, peer_id = event.peer_id)
    if not await user.getUser(): return await send(event, "Пользователь не найден")
    if user.id == -config['group_id']: return await send(event, "Вы не можете исключить меня")
    if user.id == author.id: return await send(event, "Вы не можете исключить самого себя")
    admin = (await user.conversation()).is_admin if await user.conversation() else False 
    if admin or await user.admin > await author.admin: 
        await user.deleteUser()
        return await send(event, f"У участника {await user.mention} права администратора выше/равны вашим", True)
    reason = f'\nПричина: {reason}' if reason else ''
    await send(event, f"Участник {await user.mention} исключен из всех конференций{reason}", True)
    if await user.conversation(): await client.api.messages.remove_chat_user(chat_id = event.peer_id - 2e9, member_id = user.id)
    await user.deleteUser()
    [f"{await send(event, peer_id = i['pid'], message = f'Участник {await user.mention} исключен из беседы')} {await client.api.messages.remove_chat_user(chat_id = i['pid'] - 2e9, member_id = user.id)} {await user.deleteUser(i['pid'])}" for i in await db.request(f"SELECT * FROM chats", 'fetchall') if await user.conversation(i['pid']) and event.peer_id != i['pid']]


@client.on.chat_message(text = '/help')
async def help(event: Message):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 1: return 'У вас нет доступа к данной команде'
    await event(f"Доступные команды\n\n{await getCommands(await author.admin)}")

@client.on.chat_message(text = ['/приветствие', '/приветствие <text>', '/greeting', '/greeting <text>'])
async def greeting(event: Message, text = None):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 4: return
    if event.reply_message: text = event.reply_message.text
    if event.fwd_messages != []: text = event.fwd_messages[0].text
    chat = await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}")
    if not text and not chat['greet']: return await send(event, 'Введите текст приветствия (макс. 1000 симв.)')
    if not text and chat['greet']:
        await db.request(f"UPDATE chats SET greet = NULL WHERE id = {chat['id']}")
        return await send(event, 'Приветствие было удалено')

    if '"' in text: await db.request(f"INSERT INTO greetings(text) VALUES('{text}')")
    if "'" in text: await db.request(f'INSERT INTO greetings(text) VALUES("{text}")')
    else: await db.request(f'INSERT INTO greetings(text) VALUES("{text}")')
    greet = (await db.request(f"SELECT * FROM greetings", type = 'fetchall'))[-1]
    await db.request(f"UPDATE chats SET greet = {greet['id']}")
    await event(f"Приветствие установлено.")

@client.on.chat_message(text = '/staff')
async def staff(event: Message):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id)
    await author.getUser()
    if await author.admin < 1: return
    a1 = [f"— {await getMember(i['mid'])}" for i in await db.request(f"SELECT * FROM members WHERE pid = {event.peer_id} AND admin = 1", 'fetchall')]
    a2 = [f"— {await getMember(i['mid'])}" for i in await db.request(f"SELECT * FROM members WHERE pid = {event.peer_id} AND admin = 2", 'fetchall')]
    a3 = [f"— {await getMember(i['mid'])}" for i in await db.request(f"SELECT * FROM members WHERE pid = {event.peer_id} AND admin = 3", 'fetchall')]
    a4 = [f"— {await getMember(i['mid'])}" for i in await db.request(f"SELECT * FROM members WHERE pid = {event.peer_id} AND admin = 4", 'fetchall')]
    a1, a2 = '\n'.join(a1) if len(a1) > 0 else ' — отсутствуют', '\n'.join(a2) if len(a2) > 0 else ' — отсутствуют'
    a3, a4 = '\n'.join(a3) if len(a3) > 0 else ' — отсутствуют', '\n'.join(a4) if len(a4) > 0 else ' — отсутствуют'
    await event(f"Администрация беседы\n\n"
                f"👑 Основатель беседы:\n{a4}\n\n"
                f"💎 Спец.Администратор(-ы):\n{a3}\n\n"
                f"💥 Администратор(-ы):\n{a2}\n\n"
                f"🛡 Модератор(-ы):\n{a1}\n\n", disable_mentions=1) 

@client.on.chat_message(text = ['/ban', '/ban <domain> <reason>', '/ban <domain>'])
async def ban(event: Message, domain = None, reason = None):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 2: return
    if event.reply_message:
        if domain != '-': reason = f"{domain} {reason}" if reason else domain
        domain = event.reply_message.from_id
    if event.fwd_messages != []:
        if domain != '-': reason = f"{domain} {reason}" if reason else domain
        domain = event.fwd_messages[0].from_id
    if not domain: return await send(event, "Укажите ID пользователя")
    user = member.Member(domain = domain, peer_id = event.peer_id)
    if not await user.getUser(): return await send(event, "Пользователь не найден")
    if await user.getBans('ban'): 
        await user.deleteUser()
        return await send(event, "Участник уже заблокирован в конференции")
    if user.id == -config['group_id']: return await send(event, "Вы не можете заблокировать меня")
    if user.id == author.id: return await send(event, "Вы не можете заблокировать самого себя")
    admin = (await user.conversation()).is_admin if await user.conversation() else False 
    if admin or await user.admin > await author.admin: 
        await user.deleteUser()
        return await send(event, f"У участника {await user.mention} права администратора выше/равны вашим", True)
    await user.ban(author.id, reason = reason)
    reason = f'\nПричина: {reason}' if reason else ''
    await send(event, f"Участник {await user.mention} заблокирован в конференции{reason}", True)
    if await user.conversation(): await client.api.messages.remove_chat_user(chat_id = event.peer_id - 2e9, member_id = user.id)

@client.on.chat_message(text = ['/unban', '/unban <domain>'])
async def unban(event: Message, domain = None):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 2: return
    if event.reply_message: domain = event.reply_message.from_id
    if event.fwd_messages != []: domain = event.fwd_messages[0].from_id
    if not domain: return await send(event, "Укажите ID пользователя")
    user = member.Member(domain = domain, peer_id = event.peer_id)
    if not await user.getUser(): return await send(event, "Пользователь не найден")
    if not await user.getBans('ban'): 
        await user.deleteUser()
        return await send(event, "Участник не заблокирован в конференции")
    if user.id == -config['group_id']: return await send(event, "Вы не можете взаимодействовать со мной")
    if user.id == author.id: return await send(event, "Вы не можете разблокировать самого себя")
    await send(event, f"Участник {await user.mention} разблокирован в конференции", True)
    await user.unban()

@client.on.chat_message(text = ['/gban', '/gban <domain> <reason>', '/gban <domain>'])
async def gban(event: Message, domain = None, reason = None):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 4: return
    if event.reply_message:
        if domain != '-': reason = f"{domain} {reason}" if reason else domain
        domain = event.reply_message.from_id
    if event.fwd_messages != []:
        if domain != '-': reason = f"{domain} {reason}" if reason else domain
        domain = event.fwd_messages[0].from_id
    if not domain: return await send(event, "Укажите ID пользователя")
    user = member.Member(domain = domain, peer_id = event.peer_id)
    if not await user.getUser(): return await send(event, "Пользователь не найден")
    if await user.getBans('gban'): 
        await user.deleteUser()
        return await send(event, "Участник уже заблокирован в конференциях")
    if user.id == -config['group_id']: return await send(event, "Вы не можете заблокировать меня")
    if user.id == author.id: return await send(event, "Вы не можете заблокировать самого себя")
    admin = (await user.conversation()).is_admin if await user.conversation() else False 
    if admin or await user.admin > await author.admin: 
        await user.deleteUser()
        return await send(event, f"У участника {await user.mention} права администратора выше/равны вашим", True)
    await user.ban(author.id, reason = reason, type = 'gban')
    reason = f'\nПричина: {reason}' if reason else ''
    await send(event, f"Участник {await user.mention} заблокирован во всех конференциях{reason}", True)
    if await user.conversation(): await client.api.messages.remove_chat_user(chat_id = event.peer_id - 2e9, member_id = user.id)
    [f"{await send(event, peer_id = i['pid'], message = f'Участник {await user.mention} исключен из беседы')} {await client.api.messages.remove_chat_user(chat_id = i['pid'] - 2e9, member_id = user.id)} {await user.deleteUser(i['pid'])}" for i in await db.request(f"SELECT * FROM chats", 'fetchall') if await user.conversation(i['pid']) and event.peer_id != i['pid']]

@client.on.chat_message(text = ['/ungban', '/ungban <domain>'])
async def ungban(event: Message, domain = None):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 4: return
    if event.reply_message: domain = event.reply_message.from_id
    if event.fwd_messages != []: domain = event.fwd_messages[0].from_id
    if not domain: return await send(event, "Укажите ID пользователя")
    user = member.Member(domain = domain, peer_id = event.peer_id)
    if not await user.getUser(): return await send(event, "Пользователь не найден")
    if not await user.getBans('gban'): 
        await user.deleteUser()
        return await send(event, "Участник не заблокирован в конференциях")
    if user.id == -config['group_id']: return await send(event, "Вы не можете взаимодействовать со мной")
    if user.id == author.id: return await send(event, "Вы не можете разблокировать самого себя")
    await send(event, f"Участник {await user.mention} разблокирован в конференциях", True)
    await user.unban('gban')


@client.on.chat_message(text = ['/getban', '/getban <domain>'])
async def getban(event: Message, domain = None):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 1: return
    if event.reply_message: domain = event.reply_message.from_id
    if event.fwd_messages != []: domain = event.fwd_messages[0].from_id
    if not domain: return await send(event, "Укажите ID пользователя")
    user = member.Member(domain = domain, peer_id = event.peer_id)
    if not await user.getUser(): return await send(event, "Пользователь не найден")
    if user.id == -config['group_id']: return await send(event, "Вы не можете взаимодействовать со мной")
    if not await user.getBans(): 
        await user.deleteUser()
        return await send(event, f"У участника {await user.mention} отсутствуют блокировки", disable_mentions=1)
    bans = await db.request(f"SELECT * FROM bans WHERE mid = {user.id}", type = 'fetchall')
    gban = await db.request(f"SELECT * FROM gbans WHERE mid = {user.id}")
    banlist = ''.join([f"{n}. Блокировка в беседе <<{(await getChat(i['pid']))['title']}>>, выдал: {await getMember(i['admin'])}, дата: {datetime.fromtimestamp(i['time']).strftime('%d.%m.%y %H:%M')}, причина: {i['reason'] if i['reason'] != 'None' else 'не указана'}\n" for n, i in enumerate(bans, 1)])
    banlist += f"{len(bans)+1}. Блокировка во всех беседах, выдал: {await getMember(gban['admin'])}, дата: {date(gban['time']).strftime('%d.%m.%y %H:%M')}, причина: {gban['reason'] if gban['reason'] != 'None' else 'не указана'}" if gban else ''
    await event(f"Блокировки участника {await user.mention}\n\n{banlist}", disable_mentions=1)
    await user.deleteUser()

@client.on.chat_message(text = ['/banlist', '/banlist <page>'])
async def banlist(event: Message, page = 1, ric = config['ric']):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 1: return
    bans = [f"{n}. {await getMember(i['mid'])}\n" for n, i in enumerate(await db.request(f"SELECT * FROM bans WHERE pid = {event.peer_id}", type = 'fetchall'), 1)]
    ni0,ni1,ni2 = page*ric-ric,page*ric,round(len(bans)/ric,1)
    ni1 = len(bans) if ni1 > len(bans) else ni1
    ni2 = int(ni2)+1 if str(ni2)[-1] != '0' else int(ni2)
    if page <= ni2 and page > 0:
        messages = ''.join(f'{bans[n]}' for n in range(ni0,ni1))
        return await send(event, f"Список заблокированных участников:\n<<Страница: {page}/{ni2}>>\n\n{messages}", disable_mentions=1)
    if ni2 == 0: return await send(event, "Участники с блокировками отсутствуют")
    else: await event("Страница не найдена")

@client.on.chat_message(text = ['/stats', '/stats <domain>'])
async def stats(event: Message, domain = None):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 1: return
    user = member.Member(domain = domain, peer_id = event.peer_id)
    if not await user.getUser(): return await send(event, "Пользователь не найден")
    if not await user.conversation(): 
        await user.deleteUser()
        return await send(event, f"Информация об участнике {await user.mention}\n\n"
                                                        f"Дата регистрации: {await user.dtime_created}\n"
                                                        f"Статус: Пользователь\n", True)
    await event(f"Информация об участнике {await user.mention}\n\n"
                f"Дата регистрации: {await user.dtime_created}\n"
                f"Статус пользователя: {getStatus(user)}\n"
                f"Предупреждений: {await user.warns}/3\n"
                f"Блокировка чата: {await isChatBlocked(user)}\n"
                f"Никнейм: {user.db['nick'] if user.db['nick'] else 'не установлен'}\n"
                f"Отправлено сообщений: {await user.messages}\n"
                f"Последнее сообщение: {date(await user.m_time).strftime('%d.%m.%y %H:%M')}", disable_mentions=1)

@client.on.chat_message(text = ['/warn', '/warn <domain> <reason>', '/warn <domain>'])
async def warn(event: Message, domain = None, reason = None):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 2: return
    if event.reply_message:
        if domain != '-': reason = f"{domain} {reason}" if reason else domain
        domain = event.reply_message.from_id
    if event.fwd_messages != []:
        if domain != '-': reason = f"{domain} {reason}" if reason else domain
        domain = event.fwd_messages[0].from_id
    if not domain: return await send(event, "Укажите ID пользователя")
    user = member.Member(domain = domain, peer_id = event.peer_id)
    if not await user.getUser(): return await send(event, "Пользователь не найден")
    if not await user.conversation(): 
        await user.deleteUser()
        return await send(event, f"Участник {await user.mention} не состоит в конференции", True)
    if user.id == -config['group_id']: return await send(event, "Вы не можете взаимодействовать со мной")
    if user.id == author.id: return await send(event, "Вы не можете взаимодействовать с самим собой")
    if (await user.conversation()).is_admin or await user.admin > await author.admin: 
        await user.deleteUser()
        return await send(event, f"У участника {await user.mention} права администратора выше/равны вашим", True)
    await db.request(f"INSERT INTO warns(mid, pid, count, admin, time, reason) VALUES({user.id}, {event.peer_id}, +1, {author.id}, {time.time()}, '{reason}')")
    await user.update('warns', await user.warns + 1)
    if await user.warns >= 3:
        await event(f"Участник {await user.mention} получил 3/3 предупреждений и был исключен из беседы", disable_mentions=1)
        await client.api.messages.remove_chat_user(chat_id = event.peer_id - 2e9, member_id = user.id)
        return await user.deleteUser()
    reason = f'\nПричина: {reason}' if reason else ''
    await send(event, f"Участник {await user.mention} получил предупреждение{reason}\nКоличество предупреждений: {await user.warns}/3", True)

@client.on.chat_message(text = ['/unwarn', '/unwarn <domain>'])
async def unwarn(event: Message, domain = None):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 2: return
    if event.reply_message: domain = event.reply_message.from_id
    if event.fwd_messages != []: domain = event.fwd_messages[0].from_id
    if not domain: return await send(event, "Укажите ID пользователя")
    user = member.Member(domain = domain, peer_id = event.peer_id)
    if not await user.getUser(): return await send(event, "Пользователь не найден")
    if not await user.conversation(): 
        await user.deleteUser()
        return await send(event, f"Участник {await user.mention} не состоит в конференции", True)
    if user.id == -config['group_id']: return await send(event, "Вы не можете взаимодействовать со мной")
    if user.id == author.id: return await send(event, "Вы не можете взаимодействовать с самим собой")
    if (await user.conversation()).is_admin or await user.admin > await author.admin: 
        await user.deleteUser()
        return await send(event, f"У участника {await user.mention} права администратора выше/равны вашим", True)
    await db.request(f"INSERT INTO warns(mid, pid, count, admin, time, reason) VALUES({user.id}, {event.peer_id}, -1, {author.id}, {time.time()}, 'None')")
    await user.update('warns', await user.warns - 1)
    if await user.warns < 0:
        await user.update('warns', 0)
        return await send(event, f"У участника {await user.mention} нет предупреждений", disable_mentions=1)
    await send(event, f"Участнику {await user.mention} снято предупреждение\nКоличество предупреждений: {await user.warns}/3", True)
    
@client.on.chat_message(text = ['/warnlist', '/warnlist <page>'])
async def warnlist(event: Message, page = 1, ric = config['ric']):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 1: return
    warns = [f"{n}. {await getMember(i['mid'])} - {i['warns']} пред.\n" for n, i in enumerate(await db.request(f"SELECT * FROM members WHERE pid = {event.peer_id} AND warns > 0", type = 'fetchall'), 1)]
    ni0,ni1,ni2 = page*ric-ric,page*ric,round(len(warns)/ric,1)
    ni1 = len(warns) if ni1 > len(warns) else ni1
    ni2 = int(ni2)+1 if str(ni2)[-1] != '0' else int(ni2)
    if page <= ni2 and page > 0:
        messages = ''.join(f'{warns[n]}' for n in range(ni0,ni1))
        return await send(event, f"Список участников с предупреждениями:\n<<Страница: {page}/{ni2}>>\n\n{messages}", disable_mentions=1)
    if ni2 == 0: return await send(event, "Участники с предупреждениями отсутствуют")
    else: await event("Страница не найдена")

@client.on.chat_message(text = ['/mute', '/mute <domain> <tm> <reason>', '/mute <domain> <tm>', '/mute <domain>'])
async def mute(event: Message, domain = None, tm = None, reason = None):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 1: return
    if event.reply_message:
        if domain != '-': reason, tm = f"{tm} {reason}" if reason else tm, domain
        domain = event.reply_message.from_id
    if event.fwd_messages != []:
        if domain != '-': reason, tm = f"{tm} {reason}" if reason else tm, domain
        domain = event.fwd_messages[0].from_id
    if not domain: return await send(event, "Укажите ID пользователя")
    if not tm: return await send(event, "Укажите время мута")
    user = member.Member(domain = domain, peer_id = event.peer_id)
    if not await user.getUser(): return await send(event, "Пользователь не найден")
    if await db.request(f"SELECT * FROM mutes WHERE mid = {user.id} AND pid = {event.peer_id}"): return await send(event, f"Участник {await user.mention} уже замучен", disable_mentions=1)
    if not await user.conversation(): 
        await user.deleteUser()
        return await send(event, f"Участник {await user.mention} не состоит в конференции", True)
    if user.id == -config['group_id']: return await send(event, "Вы не можете взаимодействовать со мной")
    if user.id == author.id: return await send(event, "Вы не можете взаимодействовать с самим собой")
    if (await user.conversation()).is_admin or await user.admin > await author.admin: 
        await user.deleteUser()
        return await send(event, f"У участника {await user.mention} права администратора выше/равны вашим", True)
    try: 
        if int(tm) < 1 and int(tm) > 360: return await send(event, "Время должно быть больше 0 и меньше/равно 360 мин.")
    except IndexError: return await send(event, "Указано невалидное число")
    await db.request(f"INSERT INTO mutes(mid, pid, time) VALUES({user.id}, {event.peer_id}, {time.time() + int(tm)*60})")
    reason = f'\nПричина: {reason}' if reason else ''
    await send(event, f"Участник {await user.mention} получил мут на {tm} мин.{reason}", True)

@client.on.chat_message(text = ['/unmute', '/unmute <domain>'])
async def unmute(event: Message, domain = None):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 1: return
    if event.reply_message: domain = event.reply_message.from_id
    if event.fwd_messages != []: domain = event.fwd_messages[0].from_id
    if not domain: return await send(event, "Укажите ID пользователя")
    user = member.Member(domain = domain, peer_id = event.peer_id)
    if not await user.getUser(): return await send(event, "Пользователь не найден")
    if not await db.request(f"SELECT * FROM mutes WHERE mid = {user.id} AND pid = {event.peer_id}"): return await send(event, f"Участник {await user.mention} не замучен", disable_mentions=1)
    if not await user.conversation(): 
        await user.deleteUser()
        return await send(event, f"Участник {await user.mention} не состоит в конференции", True)
    if user.id == -config['group_id']: return await send(event, "Вы не можете взаимодействовать со мной")
    if user.id == author.id: return await send(event, "Вы не можете взаимодействовать с самим собой")
    if (await user.conversation()).is_admin or await user.admin > await author.admin: 
        await user.deleteUser()
        return await send(event, f"У участника {await user.mention} права администратора выше/равны вашим", True)
    await db.request(f"DELETE FROM mutes WHERE mid = {user.id} AND pid = {event.peer_id}")
    await send(event, f"Участник {await user.mention} размучен", True)

@client.on.chat_message(text = ['/addmoder', '/addmoder <domain>'])
async def addmoder(event: Message, domain = None):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 3: return
    if event.reply_message: domain = event.reply_message.from_id
    if event.fwd_messages != []: domain = event.fwd_messages[0].from_id
    if not domain: return await send(event, "Укажите ID пользователя")
    user = member.Member(domain = domain, peer_id = event.peer_id)
    if not await user.getUser(): return await send(event, "Пользователь не найден")
    if not await user.conversation(): 
        await user.deleteUser()
        return await send(event, f"Участник {await user.mention} не состоит в конференции", True)
    if user.id == -config['group_id']: return await send(event, "Вы не можете взаимодействовать со мной")
    if user.id == author.id: return await send(event, "Вы не можете взаимодействовать с самим собой")
    if await user.admin > await author.admin: return await send(event, f"У участника {await user.mention} права администратора выше/равны вашим", True)
    if await user.admin == 1: return await send(event, "Участник уже является модератором")
    await user.update('admin', 1)
    await send(event, f"Участнику {await user.mention} выданы права модератора", True)

@client.on.chat_message(text = ['/addadmin', '/addadmin <domain>'])
async def addadmin(event: Message, domain = None):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 3: return
    if event.reply_message: domain = event.reply_message.from_id
    if event.fwd_messages != []: domain = event.fwd_messages[0].from_id
    if not domain: return await send(event, "Укажите ID пользователя")
    user = member.Member(domain = domain, peer_id = event.peer_id)
    if not await user.getUser(): return await send(event, "Пользователь не найден")
    if not await user.conversation(): 
        await user.deleteUser()
        return await send(event, f"Участник {await user.mention} не состоит в конференции", True)
    if user.id == -config['group_id']: return await send(event, "Вы не можете взаимодействовать со мной")
    if user.id == author.id: return await send(event, "Вы не можете взаимодействовать с самим собой")
    if await user.admin > await author.admin: return await send(event, f"У участника {await user.mention} права администратора выше/равны вашим", True)
    if await user.admin == 1: return await send(event, "Участник уже является администратором")
    await user.update('admin', 2)
    await send(event, f"Участнику {await user.mention} выданы права администратора", True)

@client.on.chat_message(text = ['/addspec', '/addspec <domain>'])
async def addspec(event: Message, domain = None):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 4: return
    if event.reply_message: domain = event.reply_message.from_id
    if event.fwd_messages != []: domain = event.fwd_messages[0].from_id
    if not domain: return await send(event, "Укажите ID пользователя")
    user = member.Member(domain = domain, peer_id = event.peer_id)
    if not await user.getUser(): return await send(event, "Пользователь не найден")
    if not await user.conversation(): 
        await user.deleteUser()
        return await send(event, f"Участник {await user.mention} не состоит в конференции", True)
    if user.id == -config['group_id']: return await send(event, "Вы не можете взаимодействовать со мной")
    if user.id == author.id: return await send(event, "Вы не можете взаимодействовать с самим собой")
    if await user.admin > await author.admin: return await send(event, f"У участника {await user.mention} права администратора выше/равны вашим", True)
    if await user.admin == 1: return await send(event, "Участник уже является спец.администратором")
    await user.update('admin', 3)
    await send(event, f"Участнику {await user.mention} выданы права спец.администратора", True)

@client.on.chat_message(text = ['/removerole', '/removerole <domain>'])
async def removerole(event: Message, domain = None):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 3: return
    if event.reply_message: domain = event.reply_message.from_id
    if event.fwd_messages != []: domain = event.fwd_messages[0].from_id
    if not domain: return await send(event, "Укажите ID пользователя")
    user = member.Member(domain = domain, peer_id = event.peer_id)
    if not await user.getUser(): return await send(event, "Пользователь не найден")
    if not await user.conversation(): 
        await user.deleteUser()
        return await send(event, f"Участник {await user.mention} не состоит в конференции", True)
    if user.id == -config['group_id']: return await send(event, "Вы не можете взаимодействовать со мной")
    if user.id == author.id: return await send(event, "Вы не можете взаимодействовать с самим собой")
    if await user.admin > await author.admin: return await send(event, f"У участника {await user.mention} права администратора выше/равны вашим", True)
    if await user.admin == 1: return await send(event, "Участник уже является пользователем")
    await user.update('admin', 0)
    await send(event, f"Участнику {await user.mention} сняты права администратора", True)

@client.on.chat_message(text = ['/mt', '/mt <text>'])
async def mt(event: Message, text = None):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 2: return
    if not text: return await send(event, "Введите причину вызова")
    members = ''.join([await getMember(i['mid'], nick = True) for i in (await db.request(f"SELECT * FROM members WHERE pid = {event.peer_id} AND mid > 0", "fetchall")) if i['mid'] != author.id])
    await event(f"Вызов пользователей администратором:\n\n{members}\n\nСообщение: {text}")

@client.on.chat_message(text = ['ping', 'пинг'])
async def жив(event: Message):
    from pythonping import ping as pg
    await event('Проверка задержки API...')
    await asyncio.sleep(1)
    await client.api.request('messages.edit', {"peer_id": event.peer_id, "conversation_message_id": event.conversation_message_id + 1, "group_id": config['group_id'], "message": f"Пинг: {round(pg('api.vk.com').rtt_avg_ms)} мс."})


@client.on.chat_message(text = ['/silence'])
async def silence(event: Message):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 2: return
    chat = await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}")
    amode = 1 if chat['amode'] == 0 else 0
    await db.request(f"UPDATE chats SET amode = {amode} WHERE pid = {event.peer_id}")
    await event(f"В беседе {'активирован' if amode == 1 else 'деактивирован'} режим тишины")

@client.on.chat_message(text = ['/snick', '/snick <domain> <nick>', '/snick <domain>'])
async def snick(event: Message, domain = None, nick = None):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 2: return
    if event.reply_message:
        if domain != '-': nick = f"{domain} {nick}" if nick else domain
        domain = event.reply_message.from_id
    if event.fwd_messages != []:
        if domain != '-': nick = f"{domain} {nick}" if nick else domain
        domain = event.fwd_messages[0].from_id
    if not domain: return await send(event, "Укажите ID пользователя")
    if not nick: return await send(event, "Укажите ник")
    user = member.Member(domain = domain, peer_id = event.peer_id)
    if not await user.getUser(): return await send(event, "Пользователь не найден")
    if not await user.conversation(): 
        await user.deleteUser()
        return await send(event, f"Участник {await user.mention} не состоит в конференции")
    if user.db['nick']: return await send(event, "Участнику уже установлен ник")
    if user.id == -config['group_id']: return await send(event, "Вы не можете взаимодействовать со мной")
    await send(event, f"Участнику {await user.mention} установлен ник <<{nick}>>", True)
    await db.request(f"UPDATE members SET nick = '{nick}' WHERE mid = {user.id} AND pid = {event.peer_id}")

@client.on.chat_message(text = ['/rnick', '/rnick <domain>'])
async def rnick(event: Message, domain = None):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 2: return
    if event.reply_message: domain = event.reply_message.from_id
    if event.fwd_messages != []: domain = event.fwd_messages[0].from_id
    if not domain: return await send(event, "Укажите ID пользователя")
    user = member.Member(domain = domain, peer_id = event.peer_id)
    if not await user.getUser(): return await send(event, "Пользователь не найден")
    if not await user.conversation(): 
        await user.deleteUser()
        return await send(event, f"Участник {await user.mention} не состоит в конференции")
    if not user.db['nick']: return await send(event, "У участника не установлен ник")
    if user.id == -config['group_id']: return await send(event, "Вы не можете взаимодействовать со мной")
    await send(event, f"Участнику {await user.mention} удален ник", True)
    await db.request(f"UPDATE members SET nick = NULL WHERE mid = {user.id} AND pid = {event.peer_id}")

@client.on.chat_message(text = ['/nicklist', '/nicklist <page>'])
async def nicklist(event: Message, page = 1, ric = config['ric']):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 1: return
    nicks = [f"{n}. {await getMember(i['mid'])} - {i['nick']}\n" for n, i in enumerate(await db.request(f"SELECT * FROM members WHERE pid = {event.peer_id}", type = 'fetchall'), 1) if i['nick']]
    ni0,ni1,ni2 = page*ric-ric,page*ric,round(len(nicks)/ric,1)
    ni1 = len(nicks) if ni1 > len(nicks) else ni1
    ni2 = int(ni2)+1 if str(ni2)[-1] != '0' else int(ni2)
    if page <= ni2 and page > 0:
        messages = ''.join(f'{nicks[n]}' for n in range(ni0,ni1))
        return await send(event, f"Список участников с никами:\n<<Страница: {page}/{ni2}>>\n\n{messages}", disable_mentions=1)
    if ni2 == 0: return await send(event, "Участники с никами отсутствуют")
    else: await event("Страница не найдена")

@client.on.chat_message(text = ['/top', '/top <page>'])
async def top(event: Message, page = 1, ric = config['ric']):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 2: return
    top = [f"{n}. {await getMember(i['mid'])} - {i['messages']} сообщ.\n" for n, i in enumerate(await db.request(f"SELECT * FROM members WHERE pid = {event.peer_id} AND messages > 0 ORDER BY messages DESC", type = 'fetchall'), 1)]
    ni0,ni1,ni2 = page*ric-ric,page*ric,round(len(top)/ric,1)
    ni1 = len(top) if ni1 > len(top) else ni1
    ni2 = int(ni2)+1 if str(ni2)[-1] != '0' else int(ni2)
    if page <= ni2 and page > 0:
        messages = ''.join(f'{top[n]}' for n in range(ni0,ni1))
        return await send(event, f"Топ участников по сообщениям:\n<<Страница: {page}/{ni2}>>\n\n{messages}", disable_mentions=1)
    if ni2 == 0: return await send(event, "Участники с сообщениями отсутствуют")
    else: await event("Страница не найдена")

@client.on.chat_message(text = ['/settings', '/settings <type>'])
async def settings(event: Message, type = None):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 4: return
    settings = {1: 'разрешено', 0: 'запрещено'}
    chat = await db.request(f"SELECT * FROM settings WHERE pid = {event.peer_id}")
    if not type: return await send(event, "Настройка беседы\n\n"
                                            f"Приглашать пользователей (не модератор и >): invite\n"
                                            f"Изменять аватарку беседы: title\n"
                                            f"Упоминать пользователей (через @оnline/@аll): mention"
                                            f"Закреплять/откреплять сообщения: pin"
                                            f"Исключать участника за выход: leave\n\n"
                                            f"Изменить настройки: /settings <<тип>>")
    try: 
        data = 1 if chat[type] == 0 else 0
        text = {1: 'включен', 0: 'отключен'}
        if type != 'leave':
            await db.request(f"UPDATE settings SET {type} = {data} WHERE pid = {event.peer_id}")
            return await send(event, f"Параметр \"{type}\" {text[data]}")
        await db.request(f"UPDATE settings SET `leave` = {data} WHERE pid = {event.peer_id}")
        return await send(event, f"Кик при выходе из беседы {text[data]}")
    except KeyError: return await send(event, "Параметр не найден")


@client.on.chat_message(text = ['/inactive', '/inactive <days>'])
async def inactive(event: Message, days = None):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 3: return
    if not days: return await send(event, "Введите количество дней [От 1 до 31 дней]")
    try:
        if int(days) < 1 and int(days) > 31: return await send(event, "Число должно быть больше 0 и меньше/равно 31")
    except ValueError: return await send(event, "Указано невалидное число")
    tm = int(days)*24*60
    members = await db.request(f"SELECT * FROM members WHERE pid = {event.peer_id} AND m_time > 0 and admin < 4 AND m_time < {tm}", "fetchall")
    if not members: return await send(event, "Участники по данным критериям не найдены")
    [await client.api.messages.remove_chat_user(chat_id = event.peer_id - 2e9, member_id = i['mid']) for i in members if not (await inChat(i['mid'], event.peer_id)).is_admin]
    await event(f"Из конференции был{'o' if len(members) > 1 else ''} исключено {len(members)} чел.")


@client.on.chat_message(text = ['/filter', '/filter <word>'])
async def filter(event: Message, word = None):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 3: return
    if not word: return 'Введите слово'
    if await db.request(f"SELECT * FROM filters WHERE pid = {event.peer_id} AND text = '{word}'"): return 'Данное слово уже находится в фильтре'
    await db.request(f"INSERT INTO filters(pid, text) VALUES({event.peer_id}, '{word}')")
    await event(f"В фильтр добавлено слово \"{word}\"")

@client.on.chat_message(text = ['/rfilter', '/rfilter <word>'])
async def rfilter(event: Message, word = None):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 3: return
    if not word: return 'Введите слово'
    if not await db.request(f"SELECT * FROM filters WHERE pid = {event.peer_id} AND text = '{word}'"): return 'Данного слова нет в фильтре'
    await db.request(f"DELETE FROM filters WHERE pid = {event.peer_id} AND text = '{word}'")
    await event(f"Слово \"{word}\" удалено из фильтра")

@client.on.chat_message(text = ['/flist'])
async def flist(event: Message):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 3: return
    filters = await db.request(f"SELECT * FROM filters WHERE pid = {event.peer_id}", "fetchall")
    if not filters: return 'Фильтр беседы пуст'
    result = ', '.join(f"{i['text']}" for i in filters)
    await event(f"Фильтр беседы: {result}.")
    

@client.on.chat_message(text = ['/mention', '/mention <domain>'])
async def mention(event: Message, domain = None):
    if not await db.request(f"SELECT * FROM chats WHERE pid = {event.peer_id}"): return
    author = member.Member(domain = event.from_id, peer_id = event.peer_id, name_case = 'ins')
    await author.getUser()
    if await author.admin < 4: return
    if not domain: return 'Введите ID пользователя'
    user = member.Member(domain = domain, peer_id=event.peer_id)
    if not await user.getUser(): return 'Пользователь не найден'
    if user.id == -config['group_id']: return "Вы не можете взаимодействовать со мной"
    if await db.request(f"SELECT * FROM mentions WHERE pid = {event.peer_id} AND mid = {user.id}"):
        await db.request(f"DELETE FROM mentions WHERE pid = {event.peer_id} AND mid = {user.id}")
        await user.deleteUser()
        return await send(event, f"Участника {await user.mention} вновь разрешено упоминать", disable_mentions=1)
    await db.request(f"INSERT INTO mentions(pid, mid) VALUES({event.peer_id}, {user.id})")
    await user.deleteUser()
    await send(event, f"Участника {await user.mention} запрещено упоминать в беседе", disable_mentions=1) 


async def check_mute():
    while True:
        await asyncio.sleep(1)
        for i in await db.request(f"SELECT * FROM mutes WHERE time <= {time.time()}", "fetchall"):
            await db.request(f"DELETE FROM mutes WHERE id = {i['id']}")
            await client.api.messages.send(peer_id=i['pid'], message = f'Участник {await getMember(i["mid"])} размучен', disable_mentions=1, random_id=0)

client.loop.create_task(check_mute())
client.run_polling()