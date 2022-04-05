from vk_api.bot_longpoll import VkBotEventType
import settings, datetime, time, asyncio, datetime
from modules import member
from plugins.events import function, database

vk, longpoll = settings.session()
db = database.DataBase(connect=settings.DB)

def amode(mid, pid):
	if function.get_peer(pid)['amode'] == 1:
		user = member.Member(member=mid)
		user.createMember(pid=pid)
		if user.sql['admin'] == 0:
			vk.messages.send(peer_id=pid, message=f"{user.mention} исключен за использование чата во тишины", disable_mentions=1, random_id=0)
			vk.messages.removeChatUser(chat_id=event.chat_id, member_id=user.id)
			function.kicked(mid=mid, pid=pid)


def mutes():
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			cursor.execute(f"SELECT * FROM mutes")
			for i in cursor.fetchall():
				if time.time() >= i['dtime']:
					user = member.Member(member=i['mid'])
					function.mutes(types=0, mid=user.id, pid=i['pid'])
					vk.messages.send(peer_id=i['pid'], message=f"{user.mention} разглушен в беседе системой", disable_mentions=1, random_id=0)


	finally:
		connect.commit()
		connect.close()

def message_new(mid, pid):
	connect = db.connection()
	try:
		with connect.cursor() as cursor:
			user = member.Member(member=mid)
			result = cursor.execute(f"SELECT * FROM mutes WHERE mid={mid} AND pid={pid}")
			if result == 0:
				user.createMember(pid=pid)
				if user.sql:
					cursor.execute(f"UPDATE members SET messages={user.sql['messages'] + 1} WHERE mid={mid} AND pid={pid}")

				else:
					cursor.execute(f"INSERT INTO members(mid, pid, messages) VALUES({mid}, {pid}, 1)")

			else:
				row = cursor.fetchone()
				vk.messages.send(peer_id=pid, message=f"{user.mention} исключен за использование чата во время мута\n\nВыдал: {member.Member(member=row['by'])}\nДо: {datetime.datetime.fromtimestamp(row['dtime']).strftime('%Y-%m-%d %H:%M:%S')}\nПричина: {row['reason']}", disable_mentions=1, random_id=0)
				vk.messages.removeChatUser(chat_id=event.chat_id, member_id=user.id)
				function.kicked(mid=mid, pid=pid)




	finally:
		connect.commit()
		connect.close()

def check_filter(mid, pid, message):
	user = member.Member(member=mid)
	user.createMember(pid=pid)
	stage = [i for i in message.lower().split()]
	stage = [i for i in stage if i in function.check_fw(pid)] 
	stage = True if stage != [] else False
	if stage:
		if user.sql['admin'] == 0:
			vk.messages.send(peer_id=pid, message=f"{user.mention} исключен за использование запретных слов в беседе", disable_mentions=1, random_id=0)
			vk.messages.removeChatUser(chat_id=event.chat_id, member_id=user.id)
			function.kicked(mid=mid, pid=pid)


print('Logs 1.0')
while True:
	try:
		time.sleep(1)
		for event in longpoll.listen():
			if event.type == VkBotEventType.MESSAGE_NEW:
				amode(event.raw['object']['message']['from_id'], event.raw['object']['message']['peer_id'])
				mutes()
				message_new(event.raw['object']['message']['from_id'], event.raw['object']['message']['peer_id'])
				check_filter(event.raw['object']['message']['from_id'], event.raw['object']['message']['peer_id'], event.raw['object']['message']['text'])

	except Exception as e:
		print(e)