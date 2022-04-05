# coding: utf-8
from vkbottle import Bot, Message
from vkbottle.keyboard import Keyboard, Text
import settings, datetime, time, random
from pythonping import ping
from modules import member
from vkbottle.rule import ChatActionRule
from plugins.events import function, database

bot = Bot(tokens=settings.TOKEN, group_id=settings.GROUP_ID, log_to_path='logs.txt')
db = database.DataBase(connect=settings.DB)

q = []
keyboard = Keyboard(inline=True)
keyboard.add_row()
keyboard.add_button(Text(label="Выйти"))
keyboard.add_button(Text(label="Отмена"))

@bot.on.chat_message(text=['/info', '/info <user>'])
async def info(ans: Message, user=None):
	peer = chat.Chat(ans=ans, peer_id=ans.peer_id)
	print(peer.sql)

@bot.on.chat_message(text='/active', lower=True)
async def active(ans: Message):
	try:
		if function.get_peer(ans.peer_id) is None:
			await ans(f"{function.create_chat(ans, ans.peer_id)}", disable_mentions=1)

		else:
			await ans('Беседа уже зарегистрирована')

	except IndexError:
		await ans('Нет прав администратора, выдайте')

@bot.on.message(text='/check_gban', lower=True)
async def check_ban(ans: Message):
	if ans.from_id < 2000000000:
		author = member.Member(ans=ans, member=ans.from_id)
		author.createMember()
		connect = db.connection()
		try:
			with connect.cursor() as cursor:
				result = cursor.execute(f"SELECT * FROM localban WHERE mid={ans.from_id}")
				if result == 1:
					row = cursor.fetchone()
					await ans(f"Информация о блокировках:\n\nВыдал: {member.Member(member=row['by']).mention}\nДата: {row['dtime']}\nПричина: {row['reason']}", disable_mentions=1)

				else:
					await ans("Блокировки отсутствуют")

		finally:
			connect.commit()
			connect.close()

@bot.on.chat_message(ChatActionRule(["chat_pin_message", "chat_unpin_message"]))
async def unpin(ans: Message):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id)
		author.createMember()
		if author.sql['admin'] >= 1 or function.chat_settings(ans.peer_id)['pin'] == 1 or author.is_admin:
			connect = db.connection()
			try:
				with connect.cursor() as cursor:
					if ans.action.type == 'chat_pin_message':
						cursor.execute(f"UPDATE settings SET pin_message={ans.action.conversation_message_id} WHERE pid={ans.peer_id}")

					else:
						cursor.execute(f"UPDATE settings SET pin_message=0 WHERE pid={ans.peer_id}")

			finally:
				connect.commit()
				connect.close()

		else:
			vk, longpoll = settings.session()
			await bot.api.messages.remove_chat_user(chat_id=ans.peer_id - 2000000000, member_id=author.id)
			vk.messages.pin(peer_id=ans.peer_id, conversation_message_id=function.chat_settings(ans.peer_id)['pin_message'])

@bot.on.chat_message(ChatActionRule(["chat_kick_user"]))
async def chat_leave(ans: Message):
	if function.get_peer(ans.peer_id):
		print(ans.action.member_id != ans.from_id)
		if ans.action.member_id == ans.from_id:
			print(1)
			function.kicked(mid=ans.from_id, pid=ans.peer_id)    
		
		elif ans.action.member_id != ans.from_id:
			print(2)
			function.user_delete(pid=ans.peer_id, mid=ans.action.member_id)
		
		await bot.api.messages.remove_chat_user(chat_id=ans.peer_id - 2000000000, member_id=ans.action.member_id)

@bot.on.chat_message(ChatActionRule(["chat_title_update"]))
async def title(ans: Message):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id)
		author.createMember()
		if author.sql['admin'] >= 1 or function.chat_settings(ans.peer_id)['title'] == 1 or author.is_admin:
			connect = db.connection()
			try:
				with connect.cursor() as cursor:
					cursor.execute(f"UPDATE chats SET title='{ans.action.text}' WHERE pid={ans.peer_id}")

			finally:
				connect.commit()
				connect.close()

		else:
			await bot.api.messages.remove_chat_user(chat_id=ans.peer_id - 2000000000, member_id=author.id)
			await bot.api.messages.edit_chat(peer_id=ans.peer_id, title=function.get_peer(ans.peer_id)['title'])

@bot.on.chat_message(ChatActionRule(["chat_photo_update"]))
async def title(ans: Message):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id)
		author.createMember()
		if author.sql['admin'] == 0 or function.chat_settings(ans.peer_id)['avatar'] == 0 or author.is_admin is None:
			await bot.api.messages.remove_chat_user(chat_id=ans.peer_id - 2000000000, member_id=author.id)



@bot.on.chat_message(ChatActionRule(["chat_invite_user", "chat_invite_user_by_link"]))
async def invite(ans: Message):
	if function.get_peer(ans.peer_id):
		if ans.action.type == 'chat_invite_user':
			author = member.Member(ans=ans, member=ans.from_id)
			author.createMember()
			if author.sql['admin'] >= 1 or function.chat_settings(ans.peer_id)['invite'] == 1 or author.is_admin:
				user = member.Member(ans=ans, member=ans.action.member_id)
				user.createMember()
				if user.id > 0:
					if function.check_ban(user.id, ans.peer_id) is None and function.check_lban(user.id, function.get_peer(ans.peer_id)['lid']) is None:
						user.changeNcase(name_case='gen')
						function.kicked(types=0, mid=user.id, pid=ans.peer_id)   
						if function.get_peer(ans.peer_id)['greeting'] != 'null':
							return f"Уведомление для {user.mention}:\n\n{function.get_peer(ans.peer_id)['greeting']}"

						else:
							return f"Уведомление для {user.mention}:\n\n - В беседе не установлено приветствие"

					else:
						lid = function.get_peer(ans.peer_id)['lid']
						bans = ''
						if function.check_lban(user.id, lid):
							bans += f"Тип: gban\nЗаблокировал: {member.Member(ans=ans, member=function.check_lban(user.id, lid)['by']).mention}\nДата: {function.check_lban(user.id, lid)['dtime']}\nПричина: {function.check_lban(user.id, lid)['reason']}\n\n"
						
						if function.check_ban(user.id, ans.peer_id):
							bans += f"Тип: ban\nЗаблокировал: {member.Member(ans=ans, member=function.check_ban(user.id, ans.peer_id)['by']).mention}\nДата: {function.check_ban(user.id, ans.peer_id)['dtime']}\nПричина: {function.check_ban(user.id, ans.peer_id)['reason']}"
						
						await bot.api.messages.remove_chat_user(chat_id=ans.peer_id - 2000000000, member_id=user.id)
						return f"{user.mention} был исключен, так как заблокирован в беседе\n\n{bans}"

				else:
					if function.chat_settings(ans.peer_id)['group_invite'] == 0 and author.sql['admin'] == 0 and author.is_admin and None:
						await bot.api.messages.remove_chat_user(chat_id=ans.peer_id - 2000000000, member_id=user.id)

					else:
						function.kicked(types=0, mid=ans.from_id, pid=ans.peer_id)   

			else:
				await bot.api.messages.remove_chat_user(chat_id=ans.peer_id - 2000000000, member_id=user.id)
				await bot.api.messages.remove_chat_user(chat_id=ans.peer_id - 2000000000, member_id=author.id)

		else:
			user = member.Member(ans=ans, member=ans.from_id)
			user.createMember()
			if function.check_ban(user.id, ans.peer_id) is None and function.check_lban(user.id, function.get_peer(ans.peer_id)['lid']) is None:
				user.changeNcase(name_case='gen')
				function.kicked(types=0, mid=ans.from_id, pid=ans.peer_id)   
				if function.get_peer(ans.peer_id)['greeting'] != 'null':
					return f"Уведомление для {user.mention}:\n\n{function.get_peer(ans.peer_id)['greeting']}"

				else:
					return f"Уведомление для {user.mention}:\n\n - В беседе не установлено приветствие"

			else:
				by = member.Member(ans=ans, member=function.check_ban(user.id, ans.peer_id)['by'])
				await bot.api.messages.remove_chat_user(chat_id=ans.peer_id - 2000000000, member_id=user.id)
				return f"{user.mention} был исключен, так как заблокирован в беседе\n\nЗаблокировал: {by.mention}\nДата: {function.check_ban(user.id, ans.peer_id)['dtime']}\nПричина: {function.check_ban(user.id, ans.peer_id)['reason']}"


@bot.on.chat_message(text=['/help', '/help <lvl>', '/ahelp', '/ahelp <lvl>', '/cmds', '/cmds <lvl>'], lower=True)
async def help(ans: Message, lvl: int = 0):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id)
		author.createMember()
		info = author.sql
		if info['admin'] > 0:
			if int(lvl) > 0:
				if info['admin'] >= 1 and int(lvl) == 1:
					await ans(f"Список команд администратора 1 уровня:\n\n"
							   "/help - список команд\n"
							   "/mute - выдать блокировку чата\n"
							   "/unmute - снять блокировку чата\n"
							   "/admins - список администрации беседы\n"
							   "/setnick - установить ник пользователю\n"
							   "/comments - комментарии пользователя\n"
							   "/rnick - удалить ник пользователю\n"
							   "/nicks - список пользователей с никнейнами\n"
							   "/pm - отправить сообщение в глобальную беседу\n"
							   "/editchat - изменить название беседы\n"
							   "/top - список топ пользователей по сообщениям\n", disable_mentions=1)

				elif info['admin'] >= 2 and int(lvl) == 2:
					await ans(f"Список команд администратора 2 уровня:\n\n"
							   "/kick - исключить пользователя из беседы\n"
							   "/mt - упомянуть пользователей\n"
							   "/get - информация о пользователе\n"
							   "/ban - выдать блокировку пользователю в беседе\n"
							   "/comments - закомментировать пользователя\n"
							   "/rcomment - удалить комментарий пользователя\n"
							   "/warn - выдать предупреждение пользователю\n"
							   "/unwarn - снять предупреждение пользователю\n"
							   "/unban - разблокировать пользователя в беседе\n"
							   "/warnlist - список пользователей с предупреждениями\n"
							   "/warnings - инфорамация о предупреждениях пользователя\n"
							   "/getban - блокировки пользователя в беседе\n"
							   "/amode - включить режим тишины\n"
							   "/blist - заблокированные пользователи в беседе\n", disable_mentions=1)

				elif info['admin'] >= 3 and int(lvl) == 3:
					await ans(f"Список команд администратора 3 уровня:\n\n"
							   "/gkick - исключить пользователя из локальных бесед\n"
							   "/search - поиск пользователя\n"
							   "/greeting - настройки приветствия\n"
							   "/filter - настройка фильтрации слов в беседе\n", disable_mentions=1)

				elif info['admin'] >= 4 and int(lvl) == 4:
					await ans(f"Список команд администратора 4 уровня:\n\n"
							   "/gban - заблокировать пользователя в локальных беседах\n"
							   "/ungban - разблокировать пользователя в локальных беседах\n"
							   "/arang - выдать права администратора пользователю\n"
							   "/settings - настройки беседы\n"
							   "/global create - создать глобальную связку\n"
							   "/global add - добавить беседу в глобальную связку\n"
							   "/global remove - удалить беседу из глобальной связки\n"
							   "/global info - информация о глобальной связке\n", disable_mentions=1)


			else:
				text = ans.text.split()[0] 
				if info['admin'] == 1:
					await ans(f"Пример: {text} <<1-1>>")

				elif info['admin'] == 2:
					await ans(f"Пример: {text} <<1-2>>")

				elif info['admin'] == 3:
					await ans(f"Пример: {text} <<1-3>>")

				elif info['admin'] == 4:
					await ans(f"Пример: {text} <<1-4>>")

		else:
			m = "/pm - отправить сообщение в локальную беседу\n" if function.chat_settings(ans.peer_id)['command_pm'] == 1 else ''
			await ans(f"Список команд для пользователей:\n\n"
					   "/help - список команд для пользователей\n"
					   f"{m}"
					   "/q - выйти из беседы\n\n", disable_mentions=1)


@bot.on.chat_message(text=['/admins', '/adms', '/адмс'], lower=True)
async def admins(ans: Message):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id, name_case='ins')
		author.createMember()
		if author.sql['admin'] >= 1:
			connect = db.connection()
			messages = ''
			number = 0
			try:
				with connect.cursor() as cursor:     
					result = cursor.execute(f'SELECT * FROM members WHERE pid={ans.peer_id}')
					row = cursor.fetchall()
					lvl = [i['admin'] for i in row if i['admin'] != 0 and i['kicked'] == 0]
					user_ids = ','.join(str(i['mid']) for i in row if i['admin'] != 0 and i['mid'] > 0 and i['kicked'] == 0)
					group_ids = ','.join(str(i['mid']).replace('-', '') for i in row if i['admin'] != 0 and i['mid'] < 0 and i['kicked'] == 0)
					users = (await bot.api.users.get(user_ids=user_ids))
					users = [f'[id{usr.id}|{list(usr.first_name)[0]}. {usr.last_name}]' for usr in users]
					groups = (await bot.api.groups.get_by_id(group_ids=group_ids))
					users += [f'[club{grp.id}|{grp.name}]' for grp in groups]
					sortedData = sorted(zip(lvl, users), key=lambda n: int(n[0]), reverse=True)
					messages = '\n'.join(f'{i}. {n[1]} | уровень: {n[0]}' for i, n in enumerate(sortedData, 1))
					if messages != '':
						await ans(f"Список администрации беседы:\n\n{messages}", disable_mentions=1)

					else:
						await ans(f"Администраторы беседы отсутствуют.")


			finally:
				connect.close()

@bot.on.chat_message(text=['/search', '/search <user>'], lower=True)
async def search(ans: Message, user=None):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id, name_case='ins')
		author.createMember()
		if author.sql['admin'] >= 3:
			if user:
				connect = db.connection()
				messages = ''
				number = 0
				try:
					with connect.cursor() as cursor:     
						result = cursor.execute(f'SELECT * FROM members')
						row = cursor.fetchall()
						user_ids = ','.join(str(i['mid']) for i in row if i['mid'] > 0)
						users = (await bot.api.users.get(user_ids=user_ids))
						users = [f'[id{usr.id}|{usr.first_name} {usr.last_name}] (ID: {usr.id})' for usr in users if user in f"{usr.first_name} {usr.last_name}"]
						messages = '\n'.join(f"{i}. {n}" for i, n in enumerate(users, 1))

						if messages != '':
							await ans(f"Результаты поиска '{user}'\n\n{messages}", disable_mentions=1)

						else:
							await ans(f"Результаты поиска '{user}'\n\nДанные не найдены")


				finally:
					connect.close()

			else:
				await ans(f"Пример: /search <<Инициалы>>", disable_mentions=1)


@bot.on.chat_message(text=['/mt', '/mt <types> <reason>', '/mt <types>', '/упом <types> <reason>', '/упом', '/упом <types>'], lower=True)
async def an(ans: Message, types=None, reason=None):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id, name_case='ins')
		author.createMember()
		if author.sql['admin'] >= 2:
			if types and reason:
				if types == '0':
					users = (await bot.api.messages.get_conversation_members(peer_id=ans.peer_id, group_id=settings.GROUP_ID))		
					user_ids = ','.join(str(x.member_id) for x in users.items if x.member_id > 0)
					users = (await bot.api.users.get(user_ids=user_ids))
					an_users = ', '.join(f"[id{x.id}|{list(x.first_name)[0]}. {x.last_name}]" for x in users if function.row(x.id, ans.peer_id) == 0)
					if len(list(an_users.split(','))) < 30: 
						if an_users != '': 
							an_users += '.'
							await ans(f"Упоминание пользователей {author.name}:\n\n"
									f"{an_users}\n"
									f"Сообщение: {reason}")

						else:
							await ans(f"В беседе нет пользователей")

					else:
						from math import ceil
						def parting(xs, parts):
							part_len = ceil(len(xs)/parts)
							return [xs[part_len*k:part_len*(k+1)] for k in range(parts)]

						answer = parting(list(an_users.split(',')), 2)
						users = ', '.join(i for i in answer[0])
						users += '.'
						await ans(f"Упоминание пользователей {author.name}:\n\n"
								f"{users}")
						users = ''
						users = ', '.join(i for i in answer[1])
						users += '.'
						await ans(f"{users}\n"
									f"Сообщение: {reason}")


				elif types == '1':
					users = (await bot.api.messages.get_conversation_members(peer_id=ans.peer_id, group_id=settings.GROUP_ID))		
					user_ids = ','.join(str(x.member_id) for x in users.items if x.member_id > 0)
					users = (await bot.api.users.get(user_ids=user_ids))
					an_users = ', '.join(f"[id{x.id}|{list(x.first_name)[0]}. {x.last_name}]" for x in users if function.row(x.id, ans.peer_id) > 0 and x.id != author.id)
					if an_users != '':
						an_users += '.'
						await ans(f"Упоминание администрации {author.name}:\n\n"
								   f"{an_users}\n"
								   f"Сообщение:{reason}")

					else:
						await ans(f"В беседе нет пользователей с правами администратора")

				elif types == 'all':
					users = (await bot.api.messages.get_conversation_members(peer_id=ans.peer_id, group_id=settings.GROUP_ID))		
					user_ids = ','.join(str(x.member_id) for x in users.items if x.member_id > 0)
					users = (await bot.api.users.get(user_ids=user_ids))
					an_users = ', '.join(f"[id{x.id}|{list(x.first_name)[0]}. {x.last_name}]" for x in users if x.id != author.id)
					if len(list(an_users.split(','))) < 30: 
						if an_users != '': 
							an_users += '.'
							await ans(f"Упоминание всех пользователей {author.name}:\n\n"
									f"{an_users}\n"
									f"Сообщение: {reason}")

						else:
							await ans(f"В беседе нет пользователей")

					else:
						from math import ceil
						def parting(xs, parts):
							part_len = ceil(len(xs)/parts)
							return [xs[part_len*k:part_len*(k+1)] for k in range(parts)]

						answer = parting(list(an_users.split(',')), 2)
						users = ', '.join(i for i in answer[0])
						users += '.'
						await ans(f"Упоминание всех пользователей {author.name}:\n\n"
								f"{users}")
						users = ''
						users = ', '.join(i for i in answer[1])
						users += '.'
						await ans(f"{users}\n"
									f"Сообщение: {reason}")


				else:
					await ans("Такого метода не существует, проверьте правильность написания")

			elif types:
				await ans(f"Укажите причину вызова")

			else:
				text = ans.text.split()[0]
				await ans(f"Пример: {text} <<Тип>> <<Причина вызова>>\n\n"
							"Типы:\n"
							" - 0 - упомнять пользователей\n"
							" - 1 - упомнять администрацию\n"
							" - all - упомянуть всех пользователей беседы\n\n")


@bot.on.chat_message(text='/nicks', lower=True)
async def nicks(ans: Message):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id, name_case='ins')
		author.createMember()
		if author.sql['admin'] >= 1:
			connect = db.connection()
			messages = ''
			number = 0
			try:
				with connect.cursor() as cursor:     
					result = cursor.execute(f'SELECT * FROM members WHERE pid={ans.peer_id}')
					row = cursor.fetchall()
					nicks = [i['nick'] for i in row if i['nick'] != "null" and i['mid'] > 0 and i['kicked'] == 0]
					user_ids = ','.join(str(i['mid']) for i in row if i['nick'] != "null" and i['mid'] > 0 and i['kicked'] == 0)
					group_ids = ','.join(str(i['mid']).replace('-', '') for i in row if i['nick'] != "null" and i['mid'] < 0 and i['kicked'] == 0)
					users = (await bot.api.users.get(user_ids=user_ids))
					users = [f'[id{usr.id}|{list(usr.first_name)[0]}. {usr.last_name}]' for usr in users]
					groups = (await bot.api.groups.get_by_id(group_ids=group_ids))
					users += [f'[club{grp.id}|{grp.name}]' for grp in groups]
					nicks += [i['nick'] for i in row if i['nick'] != "null" and i['mid'] < 0 and i['kicked'] == 0]
					messages = '\n'.join(f'{i}. {n[1]} | {n[0]}' for i, n in enumerate(zip(nicks, users), 1))
					if messages != '':
						await ans(f"Пользователи с никами:\n\n{messages}", disable_mentions=1)

					else:
						await ans(f"Пользователи с никами отсутствуют.")

			finally:
				connect.close()

@bot.on.chat_message(text=['/q <tag>', '/q', '/в', '/quit', '/выйти', '.й', 'Выйти', 'Отмена'])
async def q(ans: Message, tag=None):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id)
		author.changeNcase(name_case='dat')
		if 'Отмена' in ans.text.split():
			if author.id in settings.Q:
				settings.Q.remove(author.id)
				await ans(f"Выход отменен\n\nОтправлено -> {author.mention}", disable_mentions=1)

		elif 'Выйти' in ans.text.split():
			if author.id in settings.Q:
				settings.Q.remove(author.id)
				if author.is_admin is None:
					await bot.api.messages.remove_chat_user(chat_id=ans.peer_id - 2000000000, member_id=author.id)
					function.user_delete(mid=author.id, pid=ans.peer_id)

				else:
					await ans(f"Я не могу Вас исключить, т.к. Вы администратор беседы")
		
		else:
			if tag == '-c':
				if author.is_admin is None:
					await bot.api.messages.remove_chat_user(chat_id=ans.peer_id - 2000000000, member_id=author.id)
					function.user_delete(mid=author.id, pid=ans.peer_id)

				else:
					await ans(f"Я не могу Вас исключить, т.к. Вы администратор беседы")


			else:
				settings.Q.append(ans.from_id)
				await ans(f'Вы хотите покинуть беседу?\n\nОтправлено -> {author.mention}', disable_mentions=1, keyboard=keyboard.generate())

#@bot.on.chat_message(text=['/gip', '/gip <ip1> <ip2>', '/gip <ip1>', '/get_ip', '/get_ip <ip1> <ip2>', '/get_ip <ip1>'])
async def gip(ans: Message, ip1=None, ip2=None):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id)
		if author.sql['admin'] >= 3 or function.chat_settings(ans.peer_id)['gip'] == 1:
			if ip1 and ip2:
				async def result(domain1,domain2):
					try:
						import aiohttp
						from bs4 import BeautifulSoup as bs
						text = ''
						link = "https://2ip.ua/ru/services/information-service/site-distance"
						params = {'a': 'act', 'ip': domain1, 'ip2': domain2}
						async with aiohttp.ClientSession() as session:
							async with session.post(link, data=params) as r:
								data = bs(await r.text(), 'html.parser')

								soup = data.find('table', class_='table')
								domain1 = ''
								domain2 = ''
								for i in soup.findAll('tr'):
									domain1 += f"{i.findAll('td')[0].text} {i.findAll('td')[1].text}\n"
									domain2 += f"{i.findAll('td')[0].text} {i.findAll('td')[2].text}\n"

								text += f"Информация об IP: {ip1}\n\n{domain1}\n\n"
								text += f"Информация об IP: {ip2}\n\n{domain2}\n\n"
								text += f"Расстояние: {data.find('table', class_='table table-striped').findAll('tr')[1].findAll('td')[1].text} км"
								await ans(text) 

					except Exception as e:
						print(e)
						await ans(f"Некорректно указан IP адрес")


				await result(ip1, ip2)

			elif ip1:
				await ans(f"Укажите второй IP адрес")

			else:
				text = ans.text.split()[0]
				await ans(f"Пример: {text} <<IP: 1>> <<IP: 2>>")
		


@bot.on.chat_message(text=['/settings <types>', '/settings'])
async def setting(ans: Message, types=None):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id)
		author.createMember()
		if author.sql['admin'] >= 4:
			info = function.chat_settings(ans.peer_id)
			if types:
				try:
					if info[types] == 1:
						function.types(pid=ans.peer_id, types=types, on=0)
						await ans(f'Тип <<{types}>> был отключен для пользователей')

					elif info[types] == 0:
						function.types(pid=ans.peer_id, types=types, on=1)
						await ans(f'Тип <<{types}>> был включен для пользователей')

				except:
					await ans(f'Тип <<{types}>> не найден, попробуйте написать правильно')

			else:
				avatar = '✅' if info['avatar'] == 1 else '🚫'
				invite = '✅' if info['invite'] == 1 else '🚫'
				pin = '✅' if info['pin'] == 1 else '🚫'
				message = '✅' if info['messages'] == 1 else '🚫'
				title = '✅' if info['title'] == 1 else '🚫'
				m = '✅' if info['command_m'] == 1 else '🚫'
				group_invite = '✅' if info['group_invite'] == 1 else '🚫'
				mention = '✅' if info['mention'] == 1 else '🚫'
				await ans('Настройки беседы: /settings <<Параметр>> <<true/false(необязательно)>>\n\n'
						  f'Разрешить менять аватарку беседы(avatar): {avatar}\n'
						  f'Разрешить приглашать в беседу пользователей(invite): {invite}\n'
						  f'Разрешить закреплять/откреплять сообщения(pin): {pin}\n'
						  f'Разрешить менять название беседы(title): {title}\n'
						  f'Разрешить пользователям использовать /pm(command_m): {m}\n'
						  f'Разрешить пользователям упоминать online/all(mention): {mention}\n'
						  f'Разрешить писать больше {info["messages_block"]} симв.(messages): {message}\n'
						  f'Разрешить приглашать ботов в беседу(group_invite): {group_invite}\n\n'
						  f'Чтобы изменить параметр -> /settings <<Тип>>')

@bot.on.chat_message(text = ['/chat'])
async def chat(ans: Message):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id)
		author.createMember()
		if author.sql['admin'] >= 4:
			pass

@bot.on.chat_message(text=['/pm', '/pm <lid> <message>', '/pm <lid>'])
async def m(ans: Message, lid=None, message=None, tag=None):
	try:
		if function.get_peer(ans.peer_id):
			author = member.Member(ans=ans, member=ans.from_id)
			author.createMember()
			if author.sql['admin'] >= 1 or function.chat_settings(ans.peer_id)['command_m'] == 1:
				if function.get_peer(ans.peer_id)['lid'] > 0:
					if lid and message:
						if int(lid) != -1:
							lids = [x['pid'] for x in function.get_lids(function.get_peer(ans.peer_id)['lid'])]
							if int(lid) + 2000000000 in lids:
								if int(lid) != ans.peer_id - 2000000000:
									await bot.api.messages.send(peer_id=int(lid) + 2000000000, message=f"Уведомление из беседы {function.get_peer(ans.peer_id)['title']}:\n\n"
																							f"Отправитель: [id{author.id}|{author.name[0]}. {author.name.split()[1]}]\n"
																							f"Сообщение: {message}\n\n"
																							f"Чтобы отправить в ответ -> /pm {ans.peer_id - 2000000000} <<Сообщение>>", disable_mentions=1, random_id=0)

									await ans(f"Сообщение было отправлено в беседу <<{function.get_peer(int(lid) + 2000000000)['title']}>>")

								else:
									await ans(f"Вы не можете отправить сообщение в эту же беседу")

							else:
								await ans(f"Беседа с таким ID не подключена к вашей локализации")

					elif lid:
						await ans(f"Напишите сообщение")

					else:
						lids = [x for x in function.get_lids(function.get_peer(ans.peer_id)['lid'])]
						chats = ''.join(f"<<{x['title']}>> | [ID: {x['pid'] - 2000000000}]\n" for x in lids if x['pid'] != ans.peer_id)
						if chats != []:
							await ans(f"Список глобальных бесед:\n\n{chats}\n\nЧтобы отправить сообщение -> /pm <<ID Беседы>> <<Сообщение>>")

						else:
							await ans(f"У локализации нет ни одной беседы")

				else:
					await ans(f"Беседа не подключена ни к одной локализации")

	except ValueError:
		await ans(f"Укажите корректный ID беседы")

@bot.on.chat_message(text=['/mute', '/mute <user> <times> <reason>', '/mute <user> <times>', '/mute <user>'], lower=True)
async def mute(ans: Message, user=None, times=None, reason=None):
	print(settings)
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id, name_case='ins')
		author.createMember()
		if author.sql['admin'] >= 1:
			if ans.fwd_messages != []:
				if user != '-':
					reason = f"{times} {reason}" if reason else times
					times = user
				user = ans.fwd_messages[0].from_id

			if ans.reply_message:
				if user != '-':
					reason = f"{times} {reason}" if reason else times
					times = user
				user = ans.reply_message.from_id


			if user and times:
				user = member.Member(ans=ans, member=user)
				user.createMember()
				if str(user) == 'member':
					user.createMember()
					if function.check_mute(mid=user.id, pid=ans.peer_id) is None:
						if user.id != author.id:
							print(settings)
							if user.id != -settings.GROUP_ID:
								if user.in_chat:
									if author.sql['admin'] > user.sql['admin']:
										if user.is_admin is None or user.is_admin == []:
											if reason:
												if user.id > 0:
													timess = datetime.datetime.fromtimestamp(int(times)*60+time.time())
													await ans(f"{user.mention} получил блокировку чата {author.mention} на {times} мин.\n\nОкончание мута: {timess.strftime('%Y-%m-%d %H:%M:%S')}\nПричина: {reason}", disable_mentions=1)
													function.mutes(types=1, mid=user.id, pid=ans.peer_id, times=int(times)*60+time.time(), by=author.id, reason=reason)

												else:
													timess = datetime.datetime.fromtimestamp(int(times)*60+time.time())
													await ans(f"{user.mention} получила блокировку чата {author.mention} на {times} мин.\n\nОкончание мута: {timess.strftime('%Y-%m-%d %H:%M:%S')}\nПричина: {reason}", disable_mentions=1)
													function.mutes(types=1, mid=user.id, pid=ans.peer_id, times=int(times)*60+time.time(), by=author.id, reason=reason)

											else:
												if user.id > 0:
													timess = datetime.datetime.fromtimestamp(int(times)*60+time.time())
													await ans(f"{user.mention} получил блокировку чата {author.mention} на {times} мин.\n\nОкончание мута: {timess.strftime('%Y-%m-%d %H:%M:%S')}", disable_mentions=1)
													function.mutes(types=1, mid=user.id, pid=ans.peer_id, times=int(times)*60+time.time(), by=author.id, reason='Причина не указана')

												else:
													timess = datetime.datetime.fromtimestamp(int(times)*60+time.time())
													await ans(f"{user.mention} получила блокировку чата {author.mention} на {times} мин.\n\nОкончание мута: {timess.strftime('%Y-%m-%d %H:%M:%S')}", disable_mentions=1)
													function.mutes(types=1, mid=user.id, pid=ans.peer_id, times=int(times)*60+time.time(), by=author.id, reason='Причина не указана')

										else:
											await ans(f"{user.mention} является администратором беседы", disable_mentions=1)

									else:
										await ans(f"{user.mention} имеет права администратора равные или вышех ваших", disable_mentions=1)

								else:
									await ans(f"{user.mention} не существует в данной беседе", disable_mentions=1)
							else:
								if settings.USE_STICKER:
									await bot.api.messages.send(peer_id=ans.peer_id, sticker_id=random.choice(settings.STICKERS), random_id=0)

								else:
									await ans(settings.IF_BOT)

						else:
							await ans(f"Ты шо, дурачок?", disable_mentions=1)

					else:
						await ans(f"{user.mention} уже имеет блокировку чата", disable_mentions=1)

				else:
					await ans(f"Пользователь не найден", disable_mentions=1)

			elif user:
				await ans(f"Укажите время блокировки чата")

			else:
				await ans(f"Пример: /mute <<Пользователь>> <<Время(до 1440 мин.)>> <<Причина(необязательно)>>")

@bot.on.chat_message(text=['/unmute', '/unmute <user>'], lower=True)
async def unmute(ans: Message, user=None):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id, name_case='ins')
		author.createMember()
		if author.sql['admin'] >= 1:
			if ans.fwd_messages != []:
				user = ans.fwd_messages[0].from_id

			if ans.reply_message:
				user = ans.reply_message.from_id

			if user:
				user = member.Member(ans=ans, member=user)
				if str(user) == 'member':
					user.createMember()
					if function.check_mute(mid=user.id, pid=ans.peer_id):
						if user.in_chat:
							if user.is_admin is None or user.is_admin == []:
								by = member.Member(ans=ans, member=function.check_mute(mid=user.id, pid=ans.peer_id)['by'])
								if by.sql['admin'] <= author.sql['admin']:
									if user.id > 0:
										await ans(f"{user.mention} разглушен в беседе {author.mention}", disable_mentions=1)
										function.mutes(types=0, mid=user.id, pid=ans.peer_id)

									else:
										await ans(f"{user.mention} разглушена в беседе {author.mention}", disable_mentions=1)
										function.mutes(types=0, mid=user.id, pid=ans.peer_id)

								else:
									times = datetime.datetime.fromtimestamp(function.check_mute(mid=user.id, pid=ans.peer_id)['dtime'])
									await ans(f"Вы не можете разблокировать чат данному пользователю, так как его наказал администратор выше по уровню. \n\nВыдал: {by.mention}\nВыдано до: {times.strftime('%Y-%m-%d %H:%M:%S')}\nПричина: {function.check_mute(mid=user.id, pid=ans.peer_id)['reason']}", disable_mentions=1)

							else:
								await ans(f"{user.mention} является администратором беседы", disable_mentions=1)

						else:
							await ans(f"{user.mention} не существует в данной беседе", disable_mentions=1)

					else:
						await ans(f"{user.mention} не имеет блокировки чата", disable_mentions=1)

				else:
					await ans(f"Пользователь не найден", disable_mentions=1)

			else:
				await ans(f"Пример: /unmute <<Пользователь>>")


@bot.on.chat_message(text=['/greeting', '/greeting <types> <text>', '/greeting <types>'])
async def greeting(ans: Message, types=None, text=None):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id, name_case='ins')
		author.createMember()
		if author.sql['admin'] >= 3:
			if types:
				if types == 'add':
					if text:
						function.types(pid=ans.peer_id, where='chats', on=f"'{text}'", types='greeting')
						await ans('Приветствие установлено. Проверить работоспособность -> /greeting test')


					else:
						await ans('Напишите приветствие')

				elif types == 'test':
					if function.get_peer(ans.peer_id)['greeting'] != 'null':
						await ans(f'Тестовое приветствие пользователя\n\nУведомление для {member.Member(member=ans.from_id).mention}\n\n{function.get_peer(ans.peer_id)["greeting"]}')

					else:
						await ans('Приветствие не установлено. Установите его командой /greeting add <<приветствие>>')

				elif types == 'delete':
					function.types(pid=ans.peer_id, where='chats', on=f"'null'", types='greeting')
					await ans('Приветствие было удалено')

				else:
					await ans(f'Метод <<{types}>> не найден')


			else:
				await ans('Пример: /greeting <<Тип>>\n\n add <<приветствие>> - добавить приветствие\ntest - проверить работоспособность приветствия\ndelete - удалить приветствие')



@bot.on.chat_message(text='/top', lower=True)
async def msgtop(ans: Message):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id, name_case='ins')
		author.createMember()
		if author.sql['admin'] >= 1:
			connect = db.connection()
			try:
				with connect.cursor() as cursor:     
					result = cursor.execute(f'SELECT * FROM members WHERE pid={ans.peer_id}')
					row = cursor.fetchall()
					msgs = [str(i['messages']) for i in row if i['mid'] > 0 and i['messages'] > 0 and i['kicked'] == 0]
					user_ids = ','.join(str(i['mid']) for i in row if i['mid'] > 0 and i['messages'] > 0 and i['kicked'] == 0)
					users = (await bot.api.users.get(user_ids=user_ids))
					users = [f'[id{usr.id}|{list(usr.first_name)[0]}. {usr.last_name}]' for usr in users]
					msgs += [str(i['messages']) for i in row if i['mid'] < 0 and i['messages'] > 0 and i['kicked'] == 0]
					group_ids = ','.join(str(i['mid']).replace('-', '') for i in row if i['mid'] < 0 and i['messages'] > 0 and i['kicked'] == 0)
					groups = (await bot.api.groups.get_by_id(group_ids=group_ids))
					users += [f'[club{grp.id}|{grp.name}]' for grp in groups]
					sortedData = sorted(zip(msgs, users), key=lambda n: int(n[0]), reverse=True)
					if sortedData != []:
						top = '\n'.join(f'{i}. {n[1]} | {n[0]} сообщений.' for i, n in enumerate(sortedData, 1) if i <= 30)
						await ans(f'Топ пользователей по кол-ву сообщений:\n\n{top}', disable_mentions=1)

					else:
						await ans(f'Топ пользователей по кол-ву сообщений пуст.')
								  
			finally:
				connect.close()

@bot.on.chat_message(text=['/editchat', '/editchat <title>'])
async def editchat(ans: Message, title=None):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id, name_case='ins')
		author.createMember()
		if author.sql['admin'] >= 1:
			if title:
				await bot.api.messages.edit_chat(chat_id=ans.peer_id - 2000000000, title=title)
				await ans(f'Название беседы было изменено на <<{title}>>')
				function.types(where='chats', types='title', on=title)

			else:
				await ans(f'Укажите новое название беседы')

@bot.on.chat_message(text=['@all', '@online', '@all <a>', '@online <a>', '@all,', '@online,', '@all, <a>', '@online, <a>'], lower=True)
async def all(ans: Message, a=None):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id)
		author.createMember()
		if function.chat_settings(ans.peer_id)['mention'] == 0 and author.sql['admin'] == 0:
			await ans(f"{author.mention} исключен за использование упоминания в беседе", disable_mentions=1)
			await bot.api.messages.remove_chat_user(chat_id=ans.peer_id-2000000000, member_id=author.id)



@bot.on.chat_message(text=['/gc'], lower=True)
async def gc(ans: Message, web=None):
	await ans(f'Информация:\n\nPing: {ping("api.vk.com").rtt_avg_ms}ms')

@bot.on.chat_message(text=['/ban', '/ban <user> <reason>', '/ban <user>', '/бан', '/бан <user> <reason>', '/бан <user>'], lower=True)
async def ban(ans: Message, user=None, reason=None):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id, name_case='ins')
		author.createMember()
		if author.sql['admin'] >= 2:
			if ans.fwd_messages != []:
				if user != '-':
					reason = f"{user} {reason}" if reason else user
				user = ans.fwd_messages[0].from_id

			if ans.reply_message:
				if user != '-':
					reason = f"{user} {reason}" if reason else user
				user = ans.reply_message.from_id

			if user:
				user = member.Member(ans=ans, member=user)
				if str(user) == 'member':
					user.createMember()
					if function.check_ban(user.id, ans.peer_id) is None:
						if user.id != author.id:
							if user.id != -settings.GROUP_ID:
								if author.sql['admin'] > user.sql['admin']:
									if user.is_admin is None or user.is_admin == [] or user.is_admin == []:
										if reason:
											if user.id > 0:
												await ans(f"{user.mention} заблокирован в беседе {author.mention}.\nПричина: {reason}", disable_mentions=1)

											else:
												await ans(f"{user.mention} заблокирована в беседе {author.mention}.\nПричина: {reason}", disable_mentions=1)

											function.bans(types=1, mid=user.id, pid=ans.peer_id, by=author.id, reason=reason)
										
										else:
											if user.id > 0:
												await ans(f"{user.mention} заблокирован в беседе {author.mention}.", disable_mentions=1)

											else:
												await ans(f"{user.mention} заблокирована в беседе {author.mention}.", disable_mentions=1)

											function.bans(types=1, mid=user.id, pid=ans.peer_id, by=author.id, reason='Причина не указана')

										await bot.api.messages.remove_chat_user(chat_id=ans.peer_id - 2000000000, member_id=user.id)

									else:
										await ans(f"{user.mention} является администратором беседы", disable_mentions=1)

								else:
									await ans(f"{user.mention} имеет права администратора равные или выше ваших", disable_mentions=1)


							else:
								if settings.USE_STICKER:
									await bot.api.messages.send(peer_id=ans.peer_id, sticker_id=random.choice(settings.STICKERS), random_id=0)

								else:
									await ans(settings.IF_BOT)

						else:
							await ans(f"Ты шо, дурачок?", disable_mentions=1)

					else:
						await ans(f"{user.mention} уже имеет блокировку в беседе", disable_mentions=1)

				else:
					await ans(f"Пользователь не найден", disable_mentions=1)

			else:
				text = ans.text.split()[0]
				await ans(f"Пример команды: {text} <<Пользователь>> <<Причина(необязательно)>>")

@bot.on.chat_message(text=['/unban <user>', '/unban', '/разбан <user>', '/разбан'], lower=True)
async def unban(ans: Message, user=None):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id, name_case='ins')
		author.createMember()
		if author.sql['admin'] >= 2:
			if ans.fwd_messages != []:
				user = ans.fwd_messages[0].from_id

			if ans.reply_message:
				user = ans.reply_message.from_id

			if user:
				user = member.Member(ans=ans, member=user)
				if str(user) == 'member':
					user.createMember()
					if function.check_ban(user.id, ans.peer_id):
						by = member.Member(ans=ans, member=function.check_ban(mid=user.id, pid=ans.peer_id)['by'])
						if by.sql['admin'] <= author.sql['admin']:
							if user.id > 0:
								await ans(f"{user.mention} разблокирован в беседе {author.mention}.", disable_mentions=1)

							else:
								await ans(f"{user.mention} разблокирована в беседе {author.mention}.", disable_mentions=1)

							function.bans(types=0, mid=user.id, pid=ans.peer_id)

						else:
							await ans(f"Вы не можете разблокировать {user.mention}, так как его заблокировал администратор выше по уровню. \n\nВыдал: {by.mention}\nДата: {function.check_ban(mid=user.id, pid=ans.peer_id)['dtime']}\nПричина: {function.check_ban(mid=user.id, pid=ans.peer_id)['reason']}", disable_mentions=1)
							


					else:
						await ans(f"{user.mention} не имеет блокировки в беседе", disable_mentions=1)

				else:
					await ans(f"Пользователь не найден", disable_mentions=1)

			else:
				text = ans.text.split()[0]
				await ans(f"Пример команды: {text} <<Пользователь>> <<Причина(необязательно)>>")


@bot.on.chat_message(text=['/setnick', '/setnick <user> <nick>', '/setnick <user>'])
async def setnick(ans: Message, user=None, nick=None):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id, name_case='ins')
		author.createMember()
		if author.sql['admin'] >= 1:
			if ans.fwd_messages != []:
				if user != '-':
					nick = nick = f"{user} {nick}" if nick else user
				user = ans.fwd_messages[0].from_id

			if ans.reply_message:
				if user != '-':
					nick = nick = f"{user} {nick}" if nick else user
				user = ans.reply_message.from_id

			if user and nick:
				user = member.Member(ans=ans, member=user)
				if str(user) == 'member':
					user.createMember()
					if user.in_chat:
						function.nicks(types=1, mid=user.id, pid=ans.peer_id, nick=nick)
						user.changeNcase(name_case='dat')
						await ans(f'{user.mention} установлен ник <<{nick}>> {author.mention}', disable_mentions=1)

					else:
						await ans(f'{user.mention} не существует в данной беседе', disable_mentions=1)

				else:
					await ans('Пользователь не найден')

			elif user:
				await ans('Укажите никнейм')

			else:
				await ans('Пример: /setnick <<Пользователь>> <<Никнейм>>')

@bot.on.chat_message(text=['/comment', '/comment <user> <comment>', '/comment <user>'])
async def comment(ans: Message, user=None, comment=None):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id, name_case='ins')
		author.createMember()
		if author.sql['admin'] >= 1:
			if ans.fwd_messages != []:
				if user != '-':
					comment = f"{user} {comment}" if comment else user 
				user = ans.fwd_messages[0].from_id

			if ans.reply_message:
				if user != '-':
					comment = f"{user} {comment}" if comment else user
				user = ans.reply_message.from_id

			if user and comment:
				user = member.Member(ans=ans, member=user)
				if str(user) == 'member':
					user.createMember()
					function.comment(comment=comment, mid=user.id, by=author.id)
					await ans(f'{user.mention} был закомментрирован {author.mention}\n\nКомментарий: {comment}', disable_mentions=1)


				else:
					await ans('Пользователь не найден')

			elif user:
				await ans('Укажите комментарий')

			else:
				await ans('Пример: /comment <<Пользователь>> <<Комментарий>>')

@bot.on.chat_message(text=['/rcomment', '/rcomment <id>'])
async def rcomment(ans: Message, id=None):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id, name_case='ins')
		author.createMember()
		if author.sql['admin'] >= 1:
			if id:
				comment = function.get_comment(id)[0]
				if comment:
					user = member.Member(ans=ans, member=comment['mid'])
					user.createMember()
					function.rcomment(id=comment['id'])
					await ans(f'Комментарий <<{comment["comment"]}>> {user.mention} был удален {author.mention}', disable_mentions=1)


				else:
					await ans('Комментарий с таким ID не найден')

			else:
				await ans('Пример: /rcomment <<ID Комментария>>')

@bot.on.chat_message(text=['/comments', '/comments <user>'], lower=True)
async def comments(ans: Message, user=None):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id, name_case='ins')
		author.createMember()
		if author.sql['admin'] >= 1 or function.chat_settings(ans.peer_id)['comments'] == 1:
			if ans.fwd_messages != []:
				user = ans.fwd_messages[0].from_id

			if ans.reply_message:
				user = ans.reply_message.from_id

			if user:
				user = member.Member(ans=ans, member=user)
				if str(user) == 'member':
					user.createMember()
					user.changeNcase(name_case='gen')
					comments = '\n'.join(f"[{row['dtime']}](ID: {row['id']}): {member.Member(member=row['by']).mention} >> {row['comment']}" for row in function.comments(mid=user.id))
					if comments != '':
						await ans(f'Комментарии {user.mention}:\n\n{comments}', disable_mentions=1)

					else:
						await ans(f'Комментарии {user.mention} отсутствуют', disable_mentions=1)


				else:
					await ans('Пользователь не найден')

			else:
				await ans('Пример: /comments <<Пользователь>>')

@bot.on.chat_message(text=['/rnick', '/rnick <user>'], lower=True)
async def rnick(ans: Message, user=None, nick=None):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id, name_case='ins')
		author.createMember()
		if author.sql['admin'] >= 1:
			if ans.fwd_messages != []:
				user = ans.fwd_messages[0].from_id

			if ans.reply_message:
				user = ans.reply_message.from_id

			if user:
				user = member.Member(ans=ans, member=user)
				if str(user) == 'member':
					user.createMember()
					if user.in_chat:
						if user.sql['nick'] != 'null':
							function.nicks(types=0, mid=user.id, pid=ans.peer_id, nick=nick)
							user.changeNcase(name_case='dat')
							await ans(f'{user.mention} удален ник {author.mention}', disable_mentions=1)

						else:
							await ans(f'{user.mention} не установлен ник', disable_mentions=1)

					else:
						await ans(f'{user.mention} не существует в данной беседе', disable_mentions=1)

				else:
					await ans('Пользователь не найден')


			else:
				await ans('Пример: /rnick <<Пользователь>>')



@bot.on.chat_message(text=['/warnlist', '/warns'], lower=True)
async def warnlist(ans: Message):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id, name_case='ins')
		author.createMember()
		if author.sql['admin'] >= 2:
			connect = db.connection()
			try:
				with connect.cursor() as cursor:     
					result = cursor.execute(f'SELECT * FROM members WHERE pid={ans.peer_id}')
					row = cursor.fetchall()
					warns = [i['rebuke'] for i in row if i['rebuke'] > 0 or i['warn'] > 0 and i['mid'] > 0 and i['kicked'] == 0]
					warnings = [i['warn'] for i in row if i['rebuke'] > 0 or i['warn'] > 0 and i['mid'] > 0]
					user_ids = ','.join(str(i['mid']) for i in row if i['rebuke'] > 0 or i['warn'] > 0 and i['mid'] > 0 and i['kicked'] == 0)
					users = (await bot.api.users.get(user_ids=user_ids))
					users = [f'[id{usr.id}|{list(usr.first_name)[0]}. {usr.last_name}]' for usr in users]
					messages = '\n'.join(f'{i}. {n[2]} | {n[0]}/3 {n[1]}/2' for i, n in enumerate(zip(warns, warnings, users), 1))
					if messages != '':
						await ans(f"Пользователи с предупреждениями:\n\n{messages}", disable_mentions=1)

					else:
						await ans(f"Пользователи с предупреждениями отсутствуют.")

			finally:
				connect.close()
@bot.on.chat_message(text=['/blist'], lower=True)
async def blist(ans: Message):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id, name_case='ins')
		author.createMember()
		if author.sql['admin'] >= 2:
			connect = db.connection()
			messages = ''
			try:
				with connect.cursor() as cursor:
					cursor.execute(f'SELECT * FROM `bans` WHERE pid={ans.peer_id}')
					row = cursor.fetchall()
					
					user_ids = ','.join(str(i['mid']) for i in row if i['mid'] > 0)
					users = (await bot.api.users.get(user_ids=user_ids))
					types = ['ban' for i in row if i['mid'] > 0]
					users = [f'[id{usr.id}|{list(usr.first_name)[0]}. {usr.last_name}]' for usr in users]

					group_ids = ','.join(str(i['mid']).replace('-', '') for i in row if i['mid'] < 0)
					groups = (await bot.api.groups.get_by_id(group_ids=group_ids))
					"""
					types = ['ban' for i in row if i['mid'] < 0]
					users += [f'[club{grp.id}|{grp.name}]' for grp in groups]
					"""
					messages += '\n'.join(f'{n[0]} | {n[1]}' for n in zip(users, types))
					print(messages)

					if function.get_peer(ans.peer_id)['lid'] > 0:
						cursor.execute(f"SELECT * FROM `localban` WHERE lid={function.get_peer(ans.peer_id)['lid']}")
						row = cursor.fetchall()

						user_ids = ','.join(str(i['mid']) for i in row if i['mid'] > 0)
						users = (await bot.api.users.get(user_ids=user_ids))
						types = ['gban' for i in row if i['mid'] > 0]
						users = [f'[id{usr.id}|{list(usr.first_name)[0]}. {usr.last_name}]' for usr in users]

						"""
						group_ids = ','.join(str(i['mid']).replace('-', '') for i in row if i['mid'] < 0)
						groups = (await bot.api.groups.get_by_id(group_ids=group_ids))
						types = ['lban' for i in row if i['mid'] < 0]
						users += [f'[club{grp.id}|{grp.name}]' for grp in groups]
						"""
						messages +='\n'
						messages += '\n'.join(f'{n[0]} | {n[1]}' for n in zip(users, types))


					if messages != '':
						await ans(f'Список заблокированных пользователей:\n\n{messages}', disable_mentions=1)

					else:
						await ans('Пользователи с блокировками отсутствуют.')

			finally:
				connect.close()


@bot.on.chat_message(text=['/warnings', '/warnings <user>'])
async def warnings(ans: Message, user=None):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id, name_case='ins')
		author.createMember()
		if author.sql['admin'] >= 2:
			if ans.fwd_messages != []:
				user = ans.fwd_messages[0].from_id

			if ans.reply_message:
				user = ans.reply_message.from_id

			if user:
				user = member.Member(ans=ans, member=user)
				if str(user) == 'member':
					user.createMember()
					if user.in_chat:
						connect = db.connection()
						try:
							with connect.cursor() as cursor:
								cursor.execute(f"SELECT * FROM warns WHERE mid={user.id} AND pid={ans.peer_id}")
								row = cursor.fetchall()
								warns = '\n\n'.join(f"Выдал: {member.Member(ans=ans, member=i['by']).mention}\nДата: {i['dtime']}\nКол-во: {i['count']}\nПричина: {i['reason']}" for i in row)
								user.changeNcase(name_case='gen')
								if warns != '':
									await ans(f"Информация о предупреждениях {user.mention}\n\n{warns}\n\nКоличество: {user.sql['rebuke']}/3 {user.sql['warn']}/2", disable_mentions=1)

								else:
									await ans(f"У {user.mention} нет предупреждений", disable_mentions=1)


						finally:
							connect.close()	

					else:
						await ans(f"{user.mention} не существует в беседе")

				else:
					await ans('Пользователь не найден')
				

			else:
				await ans('Пример: /warnings <<Пользователь>>')

@bot.on.chat_message(text=['/mywarns'])
async def mywarns(ans: Message):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id)
		author.createMember() 
		if function.chat_settings(ans.peer_id)['mywarns'] == 1:
			connect = db.connection()
			try:
				with connect.cursor() as cursor:
					cursor.execute(f"SELECT * FROM warns WHERE mid={author.id} AND pid={ans.peer_id}")
					row = cursor.fetchall()
					warns = '\n\n'.join(f"Выдал: {member.Member(ans=ans, member=i['by']).mention}\nДата: {i['dtime']}\nКол-во: {i['count']}\nПричина: {i['reason']}" for i in row)
					author.changeNcase(name_case='gen')
					if warns != '':
						await ans(f"Информация о предупреждениях {author.mention}\n\n{warns}\n\nКоличество: {author.sql['rebuke']}/3 {author.sql['warn']}/2", disable_mentions=1)

					else:
						await ans(f"У вас нет предупреждений", disable_mentions=1)


			finally:
				connect.close()	

@bot.on.chat_message(text='/amode', lower=True)
async def amode(ans: Message):
	if function.get_peer(ans.peer_id):
		if settings.USE_AMODE:
			author = member.Member(ans=ans, member=ans.from_id, name_case='ins')
			author.createMember()
			if author.sql['admin'] >= 2:
				if function.get_peer(ans.peer_id)['amode'] == 1:
					function.amode(call=0, pid=ans.peer_id)
					await ans('В беседе отключен режим тишины')

				elif ans.peer_id not in settings.AMODE:
					function.amode(call=1, pid=ans.peer_id)
					await ans('В беседе включен режим тишины')

		else:
			await ans(f'Данная команда была отключена.\nКомментарий: {settings.AMODE_COMMENT}')


@bot.on.chat_message(text=['/gbinfo', '/gbinfo <user>'])
async def gbinfo(ans: Message, user=None):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id, name_case='ins')
		author.createMember()
		if author.sql['admin'] >= 2 or function.chat_settings(ans.peer_id)['gbinfo'] == 1:
			if ans.fwd_messages != []:
				user = ans.fwd_messages[0].from_id

			if ans.reply_message:
				user = ans.reply_message.from_id

			if user:
				user = member.Member(ans=ans, member=user)
				if str(user) == 'member':
					user.createMember()
					connect = db.connection()
					try:
						with connect.cursor() as cursor:
							cursor.execute(f"SELECT * FROM bans WHERE mid={user.id}")
							row = cursor.fetchall()
							bans = [f"Беседа: '{function.get_peer(i['pid'])['title']} [ID: {i['pid'] - 2000000000}]', выдал: {member.Member(ans=ans, member=i['by']).mention}, дата: {i['dtime']}, причина: {i['reason']}\n\n" for i in row]
							items = len(bans)
							bans = '\n'.join(f"{i}. {n}" for i, n in enumerate(bans, 1))
							cursor.execute(f"SELECT * FROM localban WHERE mid={user.id} AND lid={function.get_peer(ans.peer_id)['lid']}")
							row = cursor.fetchall()
							lbans = [f"Беседа: [G], выдал: {member.Member(ans=ans, member=i['by']).mention}, дата: {i['dtime']}, причина: {i['reason']}\n\n" for i in row]
							bans += '\n'.join(f"{i}. {n}" for i, n in enumerate(lbans, items + 1))
							comments = f'\n\nНайден {len(function.comments(mid=user.id))} комментарий\nПроверить -> /comments https://vk.com/id{user.id}' if len(function.comments(mid=user.id)) > 0 else ''
							user.changeNcase(name_case='gen')
							if bans != '':
								await ans(f"Информация о блокировках {user.mention}\n\n{bans}{comments}", disable_mentions=1)

							else:
								user.changeNcase(name_case='gen')
								await ans(f"У {user.mention} нет блокировок{comments}", disable_mentions=1)


					finally:
						connect.close()	

				else:
					await ans('Пользователь не найден')
				

			else:
				await ans('Пример: /gbinfo <<Пользователь>>')


@bot.on.chat_message(text=['/warn', '/warn <user> <warn> <reason>', '/warn <user> <warn>', '/warn <user>'], lower=True)
async def warn(ans: Message, user=None, warn=None, reason=None):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id, name_case='ins')
		author.createMember()
		if author.sql['admin'] >= 2:
			if ans.fwd_messages != []:
				if user != '-':
					reason = f"{warn} {reason}" if reason else warn
					warn = user
				user = ans.fwd_messages[0].from_id

			if ans.reply_message:
				if user != '-':
					reason = f"{warn} {reason}" if reason else warn
					warn = user
				user = ans.reply_message.from_id

			if user and warn:
				user = member.Member(ans=ans, member=user)
				if str(user) == 'member':
					user.createMember()
					if user.id != author.id:
						if user.id != -settings.GROUP_ID:
							if user.in_chat:
								if author.sql['admin'] > user.sql['admin']:
									if user.is_admin is None or user.is_admin == [] or user.is_admin == []:
										if int(warn) >= 0:
											user.changeNcase(name_case='dat')
											if user.sql['warn'] + user.sql['rebuke']*2 + int(warn) < 6:
												if reason:
													function.warns(types=1, mid=user.id, pid=ans.peer_id, warns=warn, by=author.id, reason=reason)
													if user.id > 0:
														await ans(f"{user.mention} выдано {function.w_amount(warn)} {author.mention}.\n\nКоличество: {user.sql['rebuke']}/3 {user.sql['warn']}/2\nПричина: {reason}", disable_mentions=1)

													else:
														await ans(f"{user.mention} выдана {function.w_amount(warn)} {author.mention}.\n\nКоличество: {user.sql['rebuke']}/3 {user.sql['warn']}/2\nПричина: {reason}", disable_mentions=1)

												
												else:
													function.warns(types=1, mid=user.id, pid=ans.peer_id, warns=warn, by=author.id, reason='Причина не указана')
													if user.id > 0:
														await ans(f"{user.mention} выдано {function.w_amount(warn)} {author.mention}.\n\nКоличество: {user.sql['rebuke']}/3 {user.sql['warn']}/2", disable_mentions=1)

													else:
														await ans(f"{user.mention} выдана {function.w_amount(warn)} {author.mention}.\n\nКоличество: {user.sql['rebuke']}/3 {user.sql['warn']}/2", disable_mentions=1)

											elif user.sql['warn'] + user.sql['rebuke']*2 + int(warn) == 6:
												if reason:
													function.warns(types=1, mid=user.id, pid=ans.peer_id, warns=warn, by=author.id, reason=reason)

												else:
													function.warns(types=1, mid=user.id, pid=ans.peer_id, warns=warn, by=author.id, reason='Причина не указана')
												
												warns = function.get_list_warns(mid=user.id, pid=ans.peer_id)
												if user.id > 0:
													await ans(f"{user.mention} получил 3/3 {author.mention} и был исключен из беседы.\n\nСписок предупреждений:\n{warns}", disable_mentions=1)

												else:
													await ans(f"{user.mention} получает 3/3 {author.mention} и была исключена из беседы.\n\nСписок предупреждений:\n{warns}", disable_mentions=1)

												function.bans(types=1, mid=user.id, pid=ans.peer_id, by=-settings.GROUP_ID, reason='3/3')
												function.warns(types=0, mid=user.id, pid=ans.peer_id, warns=6, by=author.id, reason='System')
												await bot.api.messages.remove_chat_user(chat_id=ans.peer_id - 2000000000, member_id=user.id)

											else:
												await ans(f"Общая сумма предупреждений не должна привышать 6", disable_mentions=1)

										else:
											await ans(f"Количество выдаваемых предупреждений должно быть больше или равно 0", disable_mentions=1)

									else:
										await ans(f"{user.mention} является администратором беседы", disable_mentions=1)

								else:
									await ans(f"{user.mention} имеет права администратора равные или выше ваших", disable_mentions=1)

							else:
								await ans(f"{user.mention} не существует в данной беседе", disable_mentions=1)
						else:
							if settings.USE_STICKER:
								await bot.api.messages.send(peer_id=ans.peer_id, sticker_id=random.choice(settings.STICKERS), random_id=0)

							else:
								await ans(settings.IF_BOT)

					else:
						await ans(f"Ты шо, дурачок?", disable_mentions=1)


				else:
					await ans(f"Пользователь не найден")

			elif user:
				await ans(f"Укажите количество предупреждений")

			else:
				await ans(f"Пример: /warn <<Пользователь>> <<Количество>> <<Причина(необязательно)>>")


@bot.on.chat_message(text=['/unwarn', '/unwarn <user> <warn> <reason>', '/unwarn <user> <warn>', '/unwarn <user>'], lower=True)
async def unwarn(ans: Message, user=None, warn=None, reason=None):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id, name_case='ins')
		author.createMember()
		if author.sql['admin'] >= 2:
			if ans.fwd_messages != []:
				if user != '-':
					reason = f"{warn} {reason}" if reason else warn
					warn = user
				user = ans.fwd_messages[0].from_id

			if ans.reply_message:
				if user != '-':
					reason = f"{warn} {reason}" if reason else warn
					warn = user
				user = ans.reply_message.from_id

			if user and warn:
				user = member.Member(ans=ans, member=user)
				if str(user) == 'member':
					user.createMember()
					if user.id != author.id:
						if user.id != -settings.GROUP_ID:
							if user.in_chat:
								if author.sql['admin'] > user.sql['admin']:
									if user.is_admin is None or user.is_admin == [] or user.is_admin == []:
										if int(warn) >= 0:
											print(user.sql['warn'] + user.sql['rebuke']*2)
											if user.sql['warn'] + user.sql['rebuke']*2 >= int(warn):
												user.changeNcase(name_case='dat')
												if reason:
													function.warns(types=0, mid=user.id, pid=ans.peer_id, warns=warn, by=author.id, reason=reason)
													await ans(f"{user.mention} снято {function.w_amount(warn)} {author.mention}.\n\nКоличество: {user.sql['rebuke']}/3 {user.sql['warn']}/2\nПричина: {reason}", disable_mentions=1)

												
												else:
													function.warns(types=0, mid=user.id, pid=ans.peer_id, warns=warn, by=author.id, reason='Причина не указана')
													await ans(f"{user.mention} снято {function.w_amount(warn)} {author.mention}.\n\nКоличество: {user.sql['rebuke']}/3 {user.sql['warn']}/2", disable_mentions=1)


											else:
												await ans(f"У пользователя нет столько предупреждений", disable_mentions=1)

										else:
											await ans(f"Количество выдаваемых предупреждений должно быть больше или равно 0", disable_mentions=1)

									else:
										await ans(f"{user.mention} является администратором беседы", disable_mentions=1)

								else:
									await ans(f"{user.mention} имеет права администратора равные или выше ваших", disable_mentions=1)

							else:
								await ans(f"{user.mention} не существует в данной беседе", disable_mentions=1)
						else:
							if settings.USE_STICKER:
								await bot.api.messages.send(peer_id=ans.peer_id, sticker_id=random.choice(settings.STICKERS), random_id=0)

							else:
								await ans(settings.IF_BOT)

					else:
						await ans(f"Ты шо, дурачок?", disable_mentions=1)


				else:
					await ans(f"Пользователь не найден")

			elif user:
				await ans(f"Укажите количество снимаех предупреждений")

			else:
				await ans(f"Пример: /unwarn <<Пользователь>> <<Количество>> <<Причина(необязательно)>>")


@bot.on.chat_message(text=['/global', '/global <types> <chat>', '/global <types>'], lower=True)
async def local(ans: Message, types=None, chat=None):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id, name_case='ins')
		author.createMember()
		if author.sql['admin'] >= 4:
			if types:
				info = function.get_peer(ans.peer_id)
				if types == 'info':
					if info['lid'] > 0:
						owner, lids = function.local_info(info['lid'])
						await ans(f'Информация о глобализации беседы:\n\n'
									f"Локализация: привязан [№ {info['lid']}]\n"
									f"Основная беседа: {owner['title']} [ID: {owner['pid'] - 2000000000}]\n"
									f"ID Беседы: {info['title']} [ID: {info['pid'] - 2000000000}]\n\n"
									f"Подключено бесед: {lids}")

					else:
						await ans(f'Информация о глобализации беседы:\n\n'
									f"Локализация: не привязан [№ 0]\n"
									f"Основная беседа: отсутствуют\n"
									f"Беседа: {info['title']} [ID: {info['pid'] - 2000000000}]\n\n")

				elif types == 'create':
					if info['lid'] == 0:
						lid = function.local_create(ans.peer_id)
						await ans(f"глобальная связка успешно создана [№{lid}]!\n\n"
																		'Чтобы подключить беседу, нужно ввести /global add <<ID>>\n\n'
																		'Все действия выполняет администратор 4 уровня')


					else:
						await ans(f'Беседа уже подключена к глобализации <<№{info["lid"]}>>')

				elif types == 'add':
					if function.get_peer(ans.peer_id)['lid'] > 0:
						if chat:
							if int(chat) <= 100000000 and int(chat) > 0:
								chat = int(chat) + 2000000000
								if function.get_peer(chat):
									if function.get_peer(chat)['lid'] == 0:
										info = function.get_peer(chat)
										function.local_add(pid=chat, lid=function.get_peer(ans.peer_id)['lid'])
										await ans(f"Беседа <<{info['title']}>> была подключена к глобализации <<№ {function.get_peer(ans.peer_id)['lid']}>>")


									else:
										await ans('Беседа уже подключена к одной из глобализации')

								else:
									await ans('Беседа не зарегистрирована')


							else:
								await ans(f"ID Беседы должно быть меньше 100000001 и больше 0")

						else:
							await ans(f"Укажите ID Беседы")

					else:
						await ans('У беседы отсутствуют глобализация. Создайте ее -> /global create')



				elif types == 'remove':
					if function.get_peer(ans.peer_id)['lid'] > 0:
						if chat:
							if int(chat) <= 100000000 and int(chat) > 0:
								chat = int(chat) + 2000000000
								if function.get_peer(chat):
									if function.get_peer(chat)['lid'] > 0:
										info = function.get_peer(chat)
										function.local_add(types=0, pid=chat, lid=function.get_peer(ans.peer_id)['lid'])
										await ans(f"Беседа <<{info['title']}>> была отключена от глобальной связки")

									else:
										await ans('Беседа не подключена ни к одной глобализации')

								else:
									await ans('Беседа не зарегистрирована')


							else:
								await ans(f"ID Беседы должно быть меньше 100000001 и больше 0")

						else:
							await ans(f"Укажите ID Беседы")

					else:
						await ans('У беседы отсутствуют глобализации. Создайте ее -> /local create')

				elif types == 'delete':
					if info['lid'] > 0:
						if info['owner_local'] == 'True':
							lid = function.local_delete(info['lid'])
							await ans(f"глобализация <<№ {info['lid']}>> была удалена")

						else:
							await ans('Беседа не является ведущей по глобализации')

					else:
						await ans('У беседы отсутствуют глобализация.')


			else:
				await ans(f"Пример: /global <<Тип>>\n\ninfo - информация о глобализации\ncreate - создать глобальную связку\nadd <<ID>> - добавить беседу в глобальную связку\nremove <<ID>> - удалить беседу из глобализации")

@bot.on.chat_message(text=['/filter', '/filter <types> <word>', '/filter <types>'], lower=True)
async def filter(ans: Message, types=None, word=None):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id, name_case='ins')
		author.createMember()
		if author.sql['admin'] >= 3:
			if types:
				connect = db.connection()
				try:
					with connect.cursor() as cursor:
						result = cursor.execute(f'SELECT * FROM chats WHERE pid={ans.peer_id}')
						row = cursor.fetchone()
						if types == 'add':
							if word:
								if '"' not in list(word) and len(list(word)) < 15:
									if word not in function.check_fw(ans.peer_id):
										if str(row['filter']) == 'null':
											cursor.execute(f'UPDATE chats SET filter="{word}" WHERE pid={ans.peer_id}')
											await ans(f"Слово было добавлено в запретные слова беседы.")

										else:
											filt = f"{row['filter']} {word}"
											cursor.execute(f'UPDATE chats SET filter="{filt}" WHERE pid={ans.peer_id}')
											await ans(f"Слово было добавлено в запретные слова беседы.")

									else:
										await ans(f"Такое слово есть уже в списке")

								else:
									await ans(f"Слово не должно содержать ковычки, а также быть длиннее 15 символов")

							else:
								await ans(f"Напишите слово")

						elif types == 'list':
							fw = function.check_fw(ans.peer_id)
							text = ''
							for i in range(len(fw)):
								a = len(fw) - 1
								if i != a:
									text += f"{fw[i]}, "
								else:
									text += f"{fw[i]}."

							if text != '':
								await ans(f"Список запретных слов установленых в беседе:\n\n{text}\n\nВсего слов: {len(fw)}")
							else:
								await ans(f"В беседе не установлены запретные слова.")

						elif types == 'del':
							if '"' not in list(word):
								if str(row['filter']) == 'null':
									await ans(f"В беседе не установлено ни одного запретного слова.")

								else:
									if word in function.check_fw(ans.peer_id):
										if word == function.check_fw(ans.peer_id)[0]:
											try:
												check = function.check_fw(ans.peer_id)[1]
												filt = row['filter'].replace(f"{word.lower()} ", '')
												cursor.execute(f'UPDATE chats SET filter="{filt}" WHERE pid={ans.peer_id}')
											except IndexError:
												cursor.execute(f'UPDATE chats SET filter="null" WHERE pid={ans.peer_id}')
											await ans(f"Слово было удалено из запретных слов беседы.")
										else:
											filt = row['filter'].replace(f" {word.lower()}", '')
											cursor.execute(f'UPDATE chats SET filter="{filt}" WHERE pid={ans.peer_id}')
											await ans(f"Слово было удалено из запретных слов беседы.")

									else:
										await ans(f"Такого слова нету в списке.")


				finally:
					connect.commit()
					connect.close()

			else:
				await ans(f"Пример: /filter <<Тип>>\n\nadd <<слово>> - добавить слово\nlist - список запретных слов\ndel - удалить запретное слово")

@bot.on.chat_message(text=['/get', '/get <user>'], lower=True)
async def get(ans: Message, user=None):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id, name_case='ins')
		author.createMember()
		if author.sql['admin'] >= 2 or function.chat_settings(ans.peer_id)['c_get'] == 1:
			if ans.fwd_messages != []:
				user = ans.fwd_messages[0].from_id

			if ans.reply_message:
				user = ans.reply_message.from_id

			if user:
				user = member.Member(ans=ans, member=user)
				if str(user) == 'member':
					user.createMember()
					if user.id > 0:
						in_chat =  "состоит в беседе" if user.in_chat else 'не состоит в беседе'
						info = f'Время приглашения в беседу: {datetime.datetime.fromtimestamp(user.in_chat[0]["join_date"]).strftime("%Y-%m-%d %H:%M:%S")}\nПригласил: {member.Member(ans=ans, member=user.in_chat[0]["invited_by"]).mention}' if user.in_chat else ''
						nick = user.sql['nick'] if user.sql['nick'] != 'null' else 'никнейм отсутствуют'
						admin = user.sql['admin'] if user.sql["admin"] > 0 else 'отсутствуют'
						user.changeNcase(name_case='abl')
						text = f'Информация о {user.mention}:\n\nДата регистрации: {user.dtime_created}\nОтправлено сообщений: {user.sql["messages"]}\nСостоит в беседе: {in_chat}\nПрава администратора в беседе: {admin}\nНикнейм пользователя: {nick}\n{info}'
						await ans(f"{text}", disable_mentions=1)

					else:
						in_chat =  "состоит в беседе" if user.in_chat else 'не состоит в беседе'
						info = f'Время приглашения в беседу: {datetime.datetime.fromtimestamp(user.in_chat[0]["join_date"]).strftime("%Y-%m-%d %H:%M:%S")}\nПригласил: {member.Member(ans=ans, member=user.in_chat[0]["invited_by"]).mention}' if user.in_chat else ''
						nick = user.sql['nick'] if user.sql['nick'] != 'null' else 'никнейм отсутствуют'
						admin = user.sql['admin'] if user.sql["admin"] > 0 else 'отсутствуют'
						text = f'Информация о {user.mention}:\n\nСостоит в беседе: {in_chat}\nПрава администратора в беседе: {admin}\nНикнейм группы: {nick}\n{info}'
						await ans(f"{text}", disable_mentions=1)


				else:
					await ans(f"Пользователь не найден", disable_mentions=1)

			else:
				await ans(f"Пример команды: /get <<Пользователь>>")

@bot.on.chat_message(text=['/arang', '/arang <user> <lvl> <tag>', '/arang <user> <lvl>', '/arang <user>'], lower=True)
async def arang(ans: Message, user=None, lvl=None, tag=None):
	if function.get_peer(ans.peer_id):
		try:
			author = member.Member(ans=ans, member=ans.from_id, name_case='ins')
			author.createMember()
			if author.sql['admin'] >= 4:
				if ans.fwd_messages != []:
					if user != '-':
						tag = lvl
						lvl = user
					user = ans.fwd_messages[0].from_id

				if ans.reply_message:
					if user != '-':
						tag = lvl
						lvl = user
					user = ans.reply_message.from_id

				if user and lvl:
					user = member.Member(ans=ans, member=user)
					if str(user) == 'member':
						user.createMember()
						if user.id != author.id:
							if user.id != -settings.GROUP_ID:
								if user.in_chat or int(lvl) == 0:
									if author.sql['admin'] > user.sql['admin']:
										if user.sql['admin'] != int(lvl):
											if tag:
												if tag == '-g':
													for i in function.get_lids(function.get_peer(ans.peer_id)['lid']):
														function.addAdmin(lvl=int(lvl), mid=user.id, pid=i['pid'])
													
													user.changeNcase(name_case='dat')
													await ans(f"{user.mention} выданы права администратора {lvl} уровня во всех беседах {author.mention}", disable_mentions=1)

												else:
													await ans(f"Тэга <<{tag}>> не существует")

											else:
												user.changeNcase(name_case='dat')
												if author.sql['admin'] == 5:
													if int(lvl) > 0 and int(lvl) <= 5:
														function.addAdmin(lvl=int(lvl), mid=user.id, pid=ans.peer_id)
														await ans(f"{user.mention} выданы права администратора {lvl} уровня {author.mention}", disable_mentions=1)

													elif int(lvl) == 0:
														function.addAdmin(lvl=int(lvl), mid=user.id, pid=ans.peer_id)
														await ans(f"{user.mention} сняты права администратора {author.mention}", disable_mentions=1)

													elif int(lvl) < 0:
														await ans(f"Уровень администратора не может быть отрицательным", disable_mentions=1)

												else:
													if int(lvl) > 0 and int(lvl) <= 3:
														function.addAdmin(lvl=int(lvl), mid=user.id, pid=ans.peer_id)
														await ans(f"{user.mention} выданы права администратора {lvl} уровня {author.mention}", disable_mentions=1)

													elif int(lvl) == 0:
														function.addAdmin(lvl=int(lvl), mid=user.id, pid=ans.peer_id)
														await ans(f"{user.mention} сняты права администратора {author.mention}", disable_mentions=1)

													else:
														if int(lvl) > 0:
															await ans(f"Вы не можете выдать права администратора выше или равного своему уровню", disable_mentions=1)

														else:
															await ans(f"Уровень администратора не может быть отрицательным", disable_mentions=1)

										else:
											await ans(f"{user.mention} уже имеет данный уровень", disable_mentions=1)

									else:
										await ans(f"{user.mention} имеет права администратора равные или выше ваших", disable_mentions=1)

								else:
									await ans(f"{user.mention} не существует в данной беседе", disable_mentions=1)
							else:
								if settings.USE_STICKER:
									await bot.api.messages.send(peer_id=ans.peer_id, sticker_id=random.choice(settings.STICKERS), random_id=0)

								else:
									await ans(settings.IF_BOT)

						else:
							await ans(f"Нельзя выдать/снять себе права администратора", disable_mentions=1)

					else:
						await ans(f"Пользователь не найден", disable_mentions=1)

				elif user:
					if author.sql['admin'] == 4:
						await ans('Уровни: <<0-3>>')

					elif author.sql['admin'] == 5:
						await ans('Уровни: <<0-5>>')

				else:
					text = ans.text.split()[0]
					if settings.USE_TAG:
						await ans(f"Пример команды: {text} <<Пользователь>> <<Уровень>> <<Тэг(необязательно)>>\n\nТэг (-g): Выдача прав администратора в локальных беседах")

					else:
						await ans(f"Пример команды: {text} <<Пользователь>> <<Уровень>>")

		except ValueError:
			await ans('Уровень должен быть числом')

@bot.on.chat_message(text=['/gkick', '/gkick <user> <reason>', '/gkick <user>'], lower=True)
async def lkick(ans: Message, user=None, reason=None):
	if function.get_peer(ans.peer_id):
		if function.get_peer(ans.peer_id)['lid'] > 0:
			author = member.Member(ans=ans, member=ans.from_id, name_case='ins')
			author.createMember()
			if author.sql['admin'] >= 3:
				if ans.fwd_messages != []:
					if user != '-':
						reason = f"{user} {reason}" if reason else user
					user = ans.fwd_messages[0].from_id

				if ans.reply_message:
					if user != '-':
						reason = f"{user} {reason}" if reason else user
					user = ans.reply_message.from_id

				if user:
					user = member.Member(ans=ans, member=user)
					if str(user) == 'member':
						user.createMember()
						if user.id != author.id:
							if user.id != -settings.GROUP_ID:
								if author.sql['admin'] > user.sql['admin']:
									if user.is_admin is None or user.is_admin == []:
										if reason:
											if user.id > 0:
												await ans(f"{user.mention} исключен из глобальных бесед {author.mention}.\nПричина: {reason}", disable_mentions=1)

											else:
												await ans(f"{user.mention} исключена из глобальных бесед {author.mention}.\nПричина: {reason}", disable_mentions=1)

										else:
											if user.id > 0:
												await ans(f"{user.mention} исключен из глобальных бесед {author.mention}.", disable_mentions=1)

											else:
												await ans(f"{user.mention} исключена из глобальных бесед {author.mention}.", disable_mentions=1)

										for i in function.get_lids(function.get_peer(ans.peer_id)['lid']):
											print(i)
											try:
												function.user_delete(pid=i['pid'], mid=user.id)
												await bot.api.messages.remove_chat_user(chat_id=i['pid'] - 2000000000, member_id=user.id)

											except:
												pass


									else:
										await ans(f"{user.mention} является администратором беседы", disable_mentions=1)

								else:
									await ans(f"{user.mention} имеет права администратора равные или выше ваших", disable_mentions=1)
							else:
								if settings.USE_STICKER:
									await bot.api.messages.send(peer_id=ans.peer_id, sticker_id=random.choice(settings.STICKERS), random_id=0)

								else:
									await ans(settings.IF_BOT)

						else:
							await ans(f"Вы не можете самого себя наказать", disable_mentions=1)

					else:
						await ans(f"Пользователь не найден", disable_mentions=1)

				else:
					text = ans.text.split()[0]
					await ans(f"Пример: {text} <<Пользователь>> <<Причина(необязательно)>>")

		else:
			await ans(f"Беседа не подключена к глобализации. Подключить -> /local create")

@bot.on.chat_message(text=['/ungban <user>', '/ungban'], lower=True)
async def ungban(ans: Message, user=None):
	if function.get_peer(ans.peer_id):
		if function.get_peer(ans.peer_id)['lid'] > 0:
			author = member.Member(ans=ans, member=ans.from_id, name_case='ins')
			author.createMember()
			if author.sql['admin'] >= 5:
				if ans.fwd_messages != []:
					user = ans.fwd_messages[0].from_id

				if ans.reply_message:
					user = ans.reply_message.from_id

				if user:
					user = member.Member(ans=ans, member=user)
					if str(user) == 'member':
						user.createMember()
						if function.check_lban(user.id, function.get_peer(ans.peer_id)['lid']):
							by = member.Member(ans=ans, member=function.check_lban(mid=user.id, lid=function.get_peer(ans.peer_id)['lid'])['by'])
							if by.sql['admin'] <= author.sql['admin']:
								if user.id > 0:
									await ans(f"{user.mention} разблокирован в глобальных беседах {author.mention}.", disable_mentions=1)

								else:
									await ans(f"{user.mention} разблокирована в глобальных беседах {author.mention}.", disable_mentions=1)

								function.lbans(types=0, mid=user.id, lid=function.get_peer(ans.peer_id)['lid'])

							else:
								user.changeNcase(name_case='gen')
								await ans(f"Вы не можете разблокировать {user.mention}, так как его заблокировал администратор выше по уровню. \n\nВыдал: {by.mention}\nДата: {function.check_lban(mid=user.id, lid=function.get_peer(ans.peer_id)['lid'])['dtime']}\nПричина: {function.check_lban(mid=user.id, lid=function.get_peer(ans.peer_id)['lid'])['reason']}", disable_mentions=1)
								


						else:
							await ans(f"{user.mention} не имеет блокировок", disable_mentions=1)

					else:
						await ans(f"Пользователь не найден", disable_mentions=1)

				else:
					text = ans.text.split()[0]
					await ans(f"Пример команды: {text} <<Пользователь>> <<Причина(необязательно)>>")

			elif author.sql['admin'] < 5:
				await ans(f"Доступ запрещен")



		else:
			await ans(f"Беседа не подключена к локализации. Подключить -> /local create")

@bot.on.chat_message(text=['/gban', '/gban <user> <reason>', '/gban <user>'], lower=True)
async def lban(ans: Message, user=None, reason=None):
	if function.get_peer(ans.peer_id):
		if function.get_peer(ans.peer_id)['lid'] > 0:
			author = member.Member(ans=ans, member=ans.from_id, name_case='ins')
			author.createMember()
			if author.sql['admin'] >= 4:
				if ans.fwd_messages != []:
					if user != '-':
						reason = f"{user} {reason}" if reason else user
					user = ans.fwd_messages[0].from_id

				if ans.reply_message:
					if user != '-':
						reason = f"{user} {reason}" if reason else user
					user = ans.reply_message.from_id

				if user:
					user = member.Member(ans=ans, member=user)
					if str(user) == 'member':
						user.createMember()
						if function.check_lban(user.id, function.get_peer(ans.peer_id)['lid']) is None:
							if user.id != author.id:
								if user.id != -settings.GROUP_ID:
									if author.sql['admin'] > user.sql['admin']:
										if user.is_admin is None or user.is_admin == [] or user.is_admin == []:
											if reason:
												if user.id > 0:
													await ans(f"{user.mention} заблокирован в глобальных беседах {author.mention}.\nПричина: {reason}", disable_mentions=1)

												else:
													await ans(f"{user.mention} заблокирована в глобальных беседах {author.mention}.\nПричина: {reason}", disable_mentions=1)

												function.lbans(types=1, mid=user.id, lid=function.get_peer(ans.peer_id)['lid'], by=author.id, reason=reason)
											
											else:
												if user.id > 0:
													await ans(f"{user.mention} заблокирован в глобальных беседах {author.mention}.", disable_mentions=1)

												else:
													await ans(f"{user.mention} заблокирована в глобальных беседах {author.mention}.", disable_mentions=1)

												function.lbans(types=1, mid=user.id, lid=function.get_peer(ans.peer_id)['lid'], by=author.id, reason='Причина не указана')

											for i in function.get_lids(function.get_peer(ans.peer_id)['lid']):
												try:
													function.user_delete(pid=i['pid'], mid=user.id)
													await bot.api.messages.remove_chat_user(chat_id=i['pid'] - 2000000000, member_id=user.id)

												except:
													pass

										else:
											await ans(f"{user.mention} является администратором беседы", disable_mentions=1)

									else:
										await ans(f"{user.mention} имеет права администратора равные или выше ваших", disable_mentions=1)


								else:
									if settings.USE_STICKER:
										await bot.api.messages.send(peer_id=ans.peer_id, sticker_id=random.choice(settings.STICKERS), random_id=0)

									else:
										await ans(settings.IF_BOT)

							else:
								await ans(f"Вы не можете самого себя наказать", disable_mentions=1)

						else:
							await ans(f"{user.mention} уже имеет блокировку в беседе", disable_mentions=1)

					else:
						await ans(f"Пользователь не найден", disable_mentions=1)

				else:
					text = ans.text.split()[0]
					await ans(f"Пример команды: {text} <<Пользователь>> <<Причина(необязательно)>>")

		else:
			await ans(f"Беседа не подключена к локализации. Подключить -> /local create")


@bot.on.chat_message(text=['/kick', '/kick <user> <reason>', '/kick <user>', '/кик', '/кик <user>', '/кик <user> <reason>'], lower=True)
async def kick(ans: Message, user=None, reason=None):
	if function.get_peer(ans.peer_id):
		author = member.Member(ans=ans, member=ans.from_id, name_case='ins')
		author.createMember()
		if author.sql['admin'] >= 2:
			if ans.fwd_messages != []:
				if user != '-':
					reason = f"{user} {reason}" if reason else user
				user = ans.fwd_messages[0].from_id

			if ans.reply_message:
				if user != '-':
					reason = f"{user} {reason}" if reason else user
				user = ans.reply_message.from_id

			if user:
				user = member.Member(ans=ans, member=user)
				if str(user) == 'member':
					user.createMember()
					if user.id != author.id:
						if user.id != -settings.GROUP_ID:
							if user.in_chat:
								if author.sql['admin'] > user.sql['admin']:
									if user.is_admin is None or user.is_admin == []:
										if reason:
											if user.id > 0:
												await ans(f"{user.mention} исключен из беседы {author.mention}.\nПричина: {reason}", disable_mentions=1)

											else:
												await ans(f"{user.mention} исключена из беседы {author.mention}.\nПричина: {reason}", disable_mentions=1)

										else:
											if user.id > 0:
												await ans(f"{user.mention} исключен из беседы {author.mention}.", disable_mentions=1)

											else:
												await ans(f"{user.mention} исключена из беседы {author.mention}.", disable_mentions=1)

										function.user_delete(pid=ans.peer_id, mid=user.id)
										await bot.api.messages.remove_chat_user(chat_id=ans.peer_id - 2000000000, member_id=user.id)

									else:
										await ans(f"{user.mention} является администратором беседы", disable_mentions=1)

								else:
									await ans(f"{user.mention} имеет права администратора равные или выше ваших", disable_mentions=1)

							else:
								await ans(f"{user.mention} не существует в данной беседе", disable_mentions=1)
						else:
							if settings.USE_STICKER:
								await bot.api.messages.send(peer_id=ans.peer_id, sticker_id=random.choice(settings.STICKERS), random_id=0)

							else:
								await ans(settings.IF_BOT)

					else:
						await ans(f"Вы не можете самого себя наказать", disable_mentions=1)

				else:
					await ans(f"Пользователь не найден", disable_mentions=1)

			else:
				text = ans.text.split()[0]
				await ans(f"Пример: {text} <<Пользователь>> <<Причина(необязательно)>>")

bot.run_polling(skip_updates=True)