import time
from vkbottle import Bot
from modules.database import DataBase
from modules.connector import JWORK

class MemberError(Exception):

    def __init__(self, text):
        self.text = text


class MemberDB:

    async def getInfo(self, db, call) -> any:   
        result = [item for key, item in db.items() if key == call]
        return result[0]

    async def getUser(self, mid, pid, create) -> dict:
        db = DataBase() if pid > 2e9 else None 
        if db:
            row = await db.request(f'SELECT * FROM members WHERE mid = {mid} AND pid = {pid}')
            if row: return row
            else:
                if not create: return None
                else: 
                    await db.request(F"INSERT INTO members(mid, pid) VALUES({mid}, {pid})")
                    return await db.request(f'SELECT * FROM members WHERE mid = {mid} AND pid = {pid}')
        else: return None

class MemberGet:
    def getid(self, member) -> list:
        if type(member) is int: return member, 0
        if 'vk.com/' in member: return member.split('vk.com/')[1], 0            
        elif '[id' in member: return member.split('|')[0].replace('[', ''), 0
        elif '[club' in member: return member.split('|')[0].replace('[club', ''), 1
        elif 'club' in member: return member.replace('club', ''), 1
        else: return member, 0


class Member:

    def __init__(self, domain: str, peer_id: int = 0, fields: str = None, name_case = 'nom'):
        self.domain, self.type = MemberGet().getid(str(domain))
        self.name_case = name_case
        self.fields = fields
        self.id = 0
        self.peer_id = peer_id
        self.options = None
        self.first_name = None
        self.last_name = None
        self.is_user = False

    def __str__(self) -> str:
        if self.options:
            if self.is_user: return f"Is User: True, Options: {self.options}"
            else: return f"Is User: False, Options: {self.options}"
        else: return "Error: User not found"


    async def getUser(self, create: bool = True) -> bool:
        self.bot = Bot(tokens = JWORK().openj()['token'])
        try:
            if self.type == 0:
                user = (await self.bot.api.users.get(user_ids = self.domain, fields = self.fields, name_case = self.name_case))[0]
                self.id, self.first_name, self.last_name = user.id, user.first_name, user.last_name
                self.is_user = True
                self.options = user
                self.sex = self.options.sex
                self.db = await MemberDB().getUser(self.id, self.peer_id, create)
                return True
            else: int('да да, я спецом вызываю ошибку')
        except:
            if self.domain.startswith('-'): self.domain = -1*int(self.domain)
            group = (await self.bot.api.groups.get_by_id(group_id = self.domain))[0]
            if group.screen_name == str(self.domain) or str(group.id) in str(self.domain):
                self.id, self.first_name = -group.id, group.name
                self.options = group
                self.sex = 1
                self.db = await MemberDB().getUser(self.id, self.peer_id, create)
                return True
            else: return False

    async def getBans(self, type = 'all'):
        db = DataBase()
        if type == 'all' or type == 'ban' and await db.request(f"SELECT * FROM bans WHERE mid = {self.id} AND pid = {self.peer_id}"): return await db.request(f"SELECT * FROM bans WHERE mid = {self.id} AND pid = {self.peer_id}")
        if type == 'all' or type == 'gban' and await db.request(f"SELECT * FROM gbans WHERE mid = {self.id}"): return await db.request(f"SELECT * FROM gbans WHERE mid = {self.id}")

    async def ban(self, aid, type: str = 'ban', reason = 'NULL'):
        db = DataBase()
        await self.deleteUser()
        if type == 'ban': await db.request(f"INSERT INTO bans(mid, pid, admin, `time`, reason) VALUES({self.id}, {self.peer_id}, {aid}, {time.time()}, '{reason}')")
        elif type == 'gban': await db.request(f"INSERT INTO gbans(mid, admin, `time`, reason) VALUES({self.id}, {aid}, {time.time()}, '{reason}')")

    async def unban(self, type: str = 'ban'):
        db = DataBase()
        await self.deleteUser()
        if type == 'ban': await db.request(f"DELETE FROM bans WHERE mid = {self.id} AND pid = {self.peer_id}")
        elif type == 'gban': await db.request(f"DELETE FROM gbans WHERE mid = {self.id}")
        
    async def changeNcase(self, name_case: str = 'nom') -> str:
        if self.is_user:
            user = (await self.bot.api.users.get(user_ids = self.id, name_case = name_case))[0]
            self.first_name, self.last_name = user.first_name, user.last_name
            return f'{self.first_name} {self.last_name}'

    async def aNick(self, text: str) -> str:
        if self.db['nick']: return f"{text} [id{self.id}|{self.db['nick']}]" if self.is_user else f"{text} [club{self.options.id}|{self.db['nick']}]"
        else: return await self.mention

    async def deleteUser(self, peer_id = None) -> bool:
        db = DataBase()
        if not await self.conversation():
            if not peer_id: peer_id = self.peer_id
            await db.request(f'DELETE FROM members WHERE mid = {self.id} AND pid = {peer_id}')
            await db.request(f"DELETE FROM warns WHERE mid = {self.id} AND pid = {peer_id}")

    async def conversation(self, peer_id: int = None):
        if not peer_id: peer_id = self.peer_id
        result = [i for i in (await self.bot.api.messages.get_conversation_members(peer_id = peer_id, group_id = self.bot.group_id)).items if i.member_id == self.id]
        if result == []: return
        return result[0]

    async def update(self, type: str, data: any):
        db = DataBase()
        await db.request(f"UPDATE members SET {type} = {data} WHERE mid = {self.id} AND pid = {self.peer_id}")

    async def __getattr__(self, call: str) -> any:
        if call == 'dtime_created':
            if not self.is_user: return 
            import urllib.request
            import re
            import datetime

            vk_link = f"https://vk.com/foaf.php?id={self.id}"
            with urllib.request.urlopen(vk_link) as response: vk_xml = response.read().decode("windows-1251")
            parsed_xml = re.findall(r'ya:created dc:date="(.*)"', vk_xml)
            item = ''.join(item for item in parsed_xml)
            dt = datetime.datetime.fromisoformat(item)
            return datetime.datetime.fromtimestamp(dt.timestamp()).strftime("%d.%m.%Y %H:%M") 

        elif call == 'mention':
            if self.is_user: return f"[id{self.id}|{self.first_name} {self.last_name}]"
            else: return f"[club{-1*self.id}|{self.first_name}]"

        elif call == 'nick':
            if self.db['nick']: return f"[id{self.id}|{self.db['nick']}]" if self.is_user else f"[club{self.options.id}|{self.db['nick']}]"
            else: return await self.mention

        else:
            try: return await MemberDB().getInfo(await MemberDB().getUser(self.id, self.peer_id, False), call)
            except: raise MemberError(f"{call} not found in module")