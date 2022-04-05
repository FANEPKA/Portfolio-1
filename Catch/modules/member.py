import settings
from plugins.events import function, database

vk, longpoll = settings.session()
db = database.DataBase(connect=settings.DB)

class Member(object):
	#bot = Bot(tokens=settings.TOKEN, group_id=settings.GROUP_ID)

	def __init__(self, ans=None, member=None, name_case='nom'):
		id, f_name, l_name = function.get_user(member, name_case, ans)
		self.id = id
		self.first_name = f_name
		self.last_name = l_name
		self.ans = ans
		try:
			self.peer_id = ans.peer_id

		except:
			self.peer_id = None

	def __str__(self):
		if self.id > 0 or self.id < 0:
			return f"member"

		else:
			return f'None'

	def createMember(self, pid=None):
		if pid:
			self.peer_id = pid

		if self.sql is None:
			connect = db.connection()
			try:
				with connect.cursor() as cursor:
					cursor.execute(f"INSERT INTO members(mid, pid) VALUES({self.id}, {self.ans.peer_id})")

			finally:
				connect.commit()
				connect.close()
				return 1

		else:
			return 0

	def changeNcase(self, name_case=None):
		id, f_name, l_name = function.get_user(self.id, name_case)
		self.first_name = f_name
		self.last_name = l_name


	def __getattr__(self, call: str):
		if call == 'id':
			return int(self.id)

		elif call == 'name':
			if self.id > 0:
				return f"{self.first_name} {self.last_name}"

			else:
				return f"{self.first_name}"

		elif call == 'sql':
			return function.sql(mid=self.id, pid=self.peer_id)


		elif call == 'dtime_created':
			if self.id > 0:
				import urllib.request
				import re
				import datetime

				vk_link = f"https://vk.com/foaf.php?id={self.id}"
				with urllib.request.urlopen(vk_link) as response:
				   vk_xml = response.read().decode("windows-1251")

				parsed_xml = re.findall(r'ya:created dc:date="(.*)"', vk_xml)
				item = ''.join(item for item in parsed_xml)
				dt = datetime.datetime.fromisoformat(item)
				return datetime.datetime.fromtimestamp(dt.timestamp()).strftime("%Y-%m-%d %H:%M:%S") 

			else:
				return None

		elif call == 'mention':
			if self.id > 0:
				return f"[id{self.id}|{self.first_name} {self.last_name}]"

			else:
				return f"[club{str(self.id).replace('-', '')}|{self.first_name}]"

		elif call == 'in_chat':
			user = None
			user = [i for i in vk.messages.getConversationMembers(peer_id=self.ans.peer_id, group_id=settings.GROUP_ID)['items'] if i['member_id'] == self.id]
			return user

		elif call == 'is_admin':
			user = None
			try:
				user = [i['is_admin'] for i in vk.messages.getConversationMembers(peer_id=self.ans.peer_id, group_id=settings.GROUP_ID)['items'] if i['member_id'] == self.id]

			except:
				pass

			finally:
				return user
