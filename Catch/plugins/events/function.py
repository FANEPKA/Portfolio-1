import settings, time
from modules import member
from plugins.events import database


vk, longpoll = settings.session()
db = database.DataBase(connect=settings.DB)

def get_user(member=None, name_case=None, ans=None):
	if '#' in str(member):
		user = member.replace('#', '')
		row = get_w_nick(nick=user, pid=ans.peer_id)
		if row:
			if row['mid'] > 0:
				user = vk.users.get(user_ids=row['mid'], name_case=name_case)[0]
				return int(user['id']), user['first_name'], user['last_name']

			else:
				group = vk.groups.getById(group_id=row['mid'])[0]
				return -int(group['id']), group['name'], None

		else:
			return 0, None, None


	if type(member) is int: 
		if member > 0:
			user = vk.users.get(user_ids=member, name_case=name_case)[0]
			return int(user['id']), user['first_name'], user['last_name']

		else:
			group = vk.groups.getById(group_id=str(member).replace('-', ''))[0]
			return -int(group['id']), group['name'], None


	if "vk.com/" in member or 'https://vk.com/' in member:
		user = member.replace('https://vk.com/', '')
		user = user.replace('vk.com/', '')
		print(user)
		try:
			user = vk.users.get(user_ids=user, name_case=name_case)[0]
			return int(user['id']), user['first_name'], user['last_name']

		except:
			group = vk.groups.getById(group_id=user)[0]
			return -int(group['id']), group['name'], None


	if "[id" in member:
		user = member.split("|")[0]
		user = vk.users.get(user_ids=user.replace("[id", ""), name_case=name_case)[0]
		return int(user['id']), user['first_name'], user['last_name']

	elif "[club" in member:
		group = member.split("|")[0]
		group = vk.groups.getById(group_id=group.replace('[club', ''))[0]
		return -int(group['id']), group['name'], None

	else:
		if r'id' in member:
			user = vk.users.get(user_ids=member.replace("id", ""), name_case=name_case)[0]
			return int(user['id']), user['first_name'], user['last_name']

		elif r'club' in member or r'public' in member:
			group = vk.groups.getById(group_id=member.replace('club', ''))[0]
			return -int(group['id']), group['name'], None

		try:
			user = vk.users.get(user_ids=member, name_case=name_case)[0]
			return int(user['id']), user['first_name'], user['last_name']

		except:
			group = vk.groups.getById(group_id=member.replace('-', ''))[0]
			if int(group['id']) != settings.GROUP_ID: 
				return -int(group['id']), group['name'], None

			else:
				return 0, None, None


def check_mute(mid=None, pid=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			result = cursor.execute(f"SELECT * FROM mutes WHERE mid={mid} AND pid={pid}")
			if result == 1:
				return cursor.fetchone()

			else:
				return None

	finally:
		connect.close()

def get_list_warns(mid=None, pid=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			cursor.execute(f"SELECT * FROM warns WHERE mid={mid} AND pid={pid}")
			warns = '\n'.join(f"Выдал: {member.Member(member=i['by']).mention}, Дата: {i['dtime']}\nКол-во: {i['count']}, Причина: {i['reason']}" for i in cursor.fetchall())
			return warns

	finally:
		connect.close()

def check_ban(mid=None, pid=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			result = cursor.execute(f"SELECT * FROM bans WHERE mid={mid} AND pid={pid}")
			if result == 1:
				return cursor.fetchone()

			else:
				return None

	finally:
		connect.close()

def check_amode(pid=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			cursor.execute(f"SELECT * FROM chats WHERE pid={pid}")
			return cursor.fetchone()

	finally:
		connect.close()

def amode(call=None, pid=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			cursor.execute(f"UPDATE chats SET amode={call} WHERE pid={pid}")

	finally:
		connect.commit()
		connect.close()

def chat_settings(pid=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			result = cursor.execute(f"SELECT * FROM settings WHERE pid={pid}")
			if result == 1:
				return cursor.fetchone()

			else:
				return None

	finally:
		connect.close()

def types(pid=None, types=None, on=None, where='settings'):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			cursor.execute(f"UPDATE `{where}` SET `{types}`={on} WHERE pid={pid}")

	finally:
		connect.commit()
		connect.close()

def comment(comment=None, mid=None, by=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			cursor.execute(f"INSERT INTO comments(mid, comment, `by`, dtime) VALUES({mid}, '{comment}', {by}, '{time.strftime('%Y-%m-%d %H:%M:%S')}')")

	finally:
		connect.commit()
		connect.close()

def rcomment(id=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			cursor.execute(f"DELETE FROM comments WHERE id={id}")

	finally:
		connect.commit()
		connect.close()

def comments(mid=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			cursor.execute(f"SELECT * FROM comments WHERE mid={mid}")
			return cursor.fetchall()

	finally:
		connect.commit()
		connect.close()

def get_comment(id=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			cursor.execute(f"SELECT * FROM comments WHERE id={id}")
			return cursor.fetchall()

	finally:
		connect.commit()
		connect.close()

def create_chat(ans=None, pid=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			try:
				cursor.execute(f"INSERT INTO chats(pid, title, owner_id) VALUES({ans.peer_id}, '{vk.messages.getConversationsById(peer_ids=ans.peer_id, group_id=settings.GROUP_ID)['items'][0]['chat_settings']['title']}', {vk.messages.getConversationsById(peer_ids=ans.peer_id, group_id=settings.GROUP_ID)['items'][0]['chat_settings']['owner_id']})")
			
			except:
				cursor.execute(f'INSERT INTO chats(pid, title, owner_id) VALUES({ans.peer_id}, "{vk.messages.getConversationsById(peer_ids=ans.peer_id, group_id=settings.GROUP_ID)["items"][0]["chat_settings"]["title"]}", {vk.messages.getConversationsById(peer_ids=ans.peer_id, group_id=settings.GROUP_ID)["items"][0]["chat_settings"]["owner_id"]})')

			cursor.execute(f"INSERT INTO settings(pid) VALUES({ans.peer_id})")
			user = member.Member(ans=ans, member=vk.messages.getConversationsById(peer_ids=ans.peer_id, group_id=settings.GROUP_ID)['items'][0]['chat_settings']['owner_id'])
			user.createMember()
			cursor.execute(f"UPDATE members SET admin=4 WHERE mid={user.id} AND pid={ans.peer_id}")
			connect.commit()
			chat = get_peer(ans.peer_id)
			return f"Беседа {vk.messages.getConversationsById(peer_ids=ans.peer_id, group_id=settings.GROUP_ID)['items'][0]['chat_settings']['title']} зарегистрирована под номером <<{chat['pid'] - 2000000000}>>.\nСоздатель беседы: {user.mention}"

	finally:
		connect.close()

def bans(types=None, mid=None, pid=None, by=None, reason=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			if types == 1:
				cursor.execute(f"INSERT INTO bans(mid, pid, dtime, `by`, reason) VALUES({mid}, {pid}, '{time.strftime('%Y-%m-%d %H:%M:%S')}', {by}, '{reason}')")

			else:
				cursor.execute(f"DELETE FROM bans WHERE mid={mid} AND pid={pid}")


	finally:
		connect.commit()
		connect.close()

def check_lban(mid=None, lid=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			result = cursor.execute(f"SELECT * FROM localban WHERE mid={mid} AND lid={lid}")
			if result >= 1:
				return cursor.fetchone()

			else:
				return None

	finally:
		connect.close()

def local_info(lid=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			result = cursor.execute(f"SELECT * FROM chats WHERE lid={lid}")
			owner = [i for i in cursor.fetchall() if i['owner_local'] == 'True'][0]
			return owner, result


	finally:
		connect.close()

def local_create(pid=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			result = cursor.execute(f"SELECT * FROM chats WHERE owner_local='True'")
			lid = 0
			try:
				lid = max([i['lid'] for i in cursor.fetchall()])

			except:
				lid = 0

			cursor.execute(f"UPDATE chats SET lid={lid + 1}, owner_local='True' WHERE pid={pid}")
			return lid + 1


	finally:
		connect.commit()
		connect.close()

def peer_delete(pid=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			cursor.execute(f"SELECT * FROM chats WHERE pid={pid}")
			if cursor.fetchone()['lid'] > 0:
				local_delete(lid=cursor.fetchone()['lid'])

			cursor.execute(f"DELETE FROM chats WHERE pid={pid}")
			cursor.execute(f"DELETE FROM settings WHERE pid={pid}")
			cursor.execute(f"DELETE FROM members WHERE pid={pid}")

	finally:
		connect.commit()
		connect.close()

def user_delete(mid=None, pid=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			cursor.execute(f"DELETE FROM members WHERE mid={mid} AND pid={pid}")


	finally:
		connect.commit()
		connect.close()

def w_amount(warns):
	if int(warns) == 1:
		return f'1 предупреждение'

	elif int(warns) in [2,3,4]:
		return f"{warns} предупреждения"

	else:
		return f"{warns} предупреждений"

def kicked(types=1, mid=None, pid=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			cursor.execute(f"UPDATE members SET kicked={types} WHERE mid={mid} AND pid={pid}")


	finally:
		connect.commit()
		connect.close()



def local_delete(lid=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			cursor.execute(f"SELECT * FROM chats WHERE lid={lid}")
			row = cursor.fetchall()
			for i in row: 
				if i['owner_local'] == 'True':
					cursor.execute(f"UPDATE chats SET lid=0, owner_local='False' WHERE pid={i['pid']}") 
					connect.commit()

				else:
					cursor.execute(f"UPDATE chats SET lid=0 WHERE pid={i['pid']}") 
					connect.commit()
			

	finally:
		connect.close()


def local_add(types=1, pid=None, lid=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			if types == 1:
				cursor.execute(f"UPDATE chats SET lid={lid} WHERE pid={pid}")

			else:
				cursor.execute(f"UPDATE chats SET lid=0 WHERE pid={pid}")


	finally:
		connect.commit()
		connect.close()



def lbans(types=None, mid=None, lid=None, by=None, reason=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			if types == 1:
				cursor.execute(f"INSERT INTO localban(mid, lid, dtime, `by`, reason) VALUES({mid}, {lid}, '{time.strftime('%Y-%m-%d %H:%M:%S')}', {by}, '{reason}')")

			else:
				cursor.execute(f"DELETE FROM localban WHERE mid={mid} AND lid={lid}")


	finally:
		connect.commit()
		connect.close()

def check_fw(pid=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			result = cursor.execute(f'SELECT * FROM chats WHERE pid={pid}')
			row = cursor.fetchone()
			try:
				if row['filter'] == 'null':
					return []
				else:
					return row['filter'].split(' ')

			except:
				return []

	finally:
		connect.close() 

def mutes(types=None, mid=None, pid=None, times=None, by=None, reason=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			if types == 1:
				cursor.execute(f"INSERT INTO mutes(mid, pid, dtime, `by`, reason) VALUES({mid}, {pid}, {times}, {by}, '{reason}')")

			else:
				cursor.execute(f"DELETE FROM mutes WHERE mid={mid} AND pid={pid}")


	finally:
		connect.commit()
		connect.close()


def get_lids(lid=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			result = cursor.execute(f"SELECT * FROM chats WHERE lid={lid}")
			return cursor.fetchall()

	finally:
		connect.close()

def chat_messages(pid=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			cursor.execute(f"SELECT * FROM members WHERE pid={pid}")
			messages = 0
			for i in cursor.fetchall():
				messages += i['messages']

			return messages

	finally:
		connect.close()

def warn_amount(warns: int):
	if warns == 0:
		return 0, 0

	elif warns == 1:
		return 0, 1

	elif warns == 2:
		return 1, 0

	elif warns == 3:
		return 1, 1

	elif warns == 4:
		return 2, 0

	elif warns == 5:
		return 2, 1

	elif warns == 6:
		return 3, 0

def warns(types=None, mid=None, pid=None, warns=None, by=None, reason=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			if types == 1:
				user = sql(mid, pid)
				rebuke, warn = warn_amount(int(warns) + user['rebuke']*2 + user['warn'])
				cursor.execute(f"UPDATE members SET warn={warn}, rebuke={rebuke} WHERE mid={mid} AND pid={pid}")
				cursor.execute(f"INSERT INTO warns(mid, pid, dtime, count, `by`, reason) VALUES({mid}, {pid}, '{time.strftime('%Y-%m-%d %H:%M:%S')}', {warns}, {by}, '{reason}')")

			else:
				user = sql(mid, pid)
				rebuke, warn = warn_amount(user['rebuke']*2 + user['warn'] - int(warns))
				cursor.execute(f"UPDATE members SET warn={warn}, rebuke={rebuke} WHERE mid={mid} AND pid={pid}")
				cursor.execute(f"INSERT INTO warns(mid, pid, dtime, count, `by`, reason) VALUES({mid}, {pid}, '{time.strftime('%Y-%m-%d %H:%M:%S')}', {-int(warns)}, {by}, '{reason}')")

	finally:
		connect.commit()
		connect.close()

def nicks(types=None, mid=None, pid=None, nick=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			if types == 1:
				cursor.execute(f"UPDATE members SET nick='{nick}' WHERE mid={mid} AND pid={pid}")

			else:
				cursor.execute(f"UPDATE members SET nick='null' WHERE mid={mid} AND pid={pid}")


	finally:
		connect.commit()
		connect.close()

def addAdmin(lvl=None, mid=None, pid=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			cursor.execute(f"UPDATE members SET admin={lvl} WHERE mid={mid} AND pid={pid}")


	finally:
		connect.commit()
		connect.close()

def get_peer(pid=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			result = cursor.execute(f"SELECT * FROM chats WHERE pid={pid}")
			return cursor.fetchone()

	finally:
		connect.close()

def sql(mid=None, pid=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			cursor.execute(f"SELECT * FROM members WHERE mid={mid} AND pid={pid}")
			return cursor.fetchone()

	finally:
		connect.close()

def get_w_nick(nick=None, pid=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			result = cursor.execute(f"SELECT * FROM members WHERE nick='{nick}' AND pid={pid}")
			return cursor.fetchone()

	except:
		return None

	finally:
		connect.close()

def row(mid=None, pid=None):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			result = cursor.execute(f"SELECT * FROM members WHERE mid={mid} AND pid={pid}")
			if result == 1:
				return cursor.fetchone()['admin']

			else:
				return 0

	finally:
		connect.close()