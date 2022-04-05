import time
from plugins import simplemysql


class DataBase:
    def __init__(self, db: simplemysql.Pymysql):
        self.db = db

    def member(self, member: int, guild: int, guild_ds: str = None):
        return self.db.request(f"SELECT * FROM members WHERE mid = '{member}' AND guild = {guild}")

    def createMember(self, member: int, guild: int):
        if self.member(member, guild): return 0
        return self.db.request(f"INSERT INTO members(mid, guild) VALUES('{member}', {guild})")

    def updateMessages(self, member: int, guild: int):
        sql = self.member(member, guild)
        return self.db.request(f"UPDATE members SET messages = {sql['messages'] + 1} WHERE mid = '{member}' AND guild = {guild}")

    def getGuild(self, guild: int):
        return self.db.request(f"SELECT * FROM guilds WHERE id = {guild}")

    def isMuted(self, member: int, guild: int, role: int):
        return self.db.request(f"SELECT * FROM Mutes WHERE mid = '{member}' AND guild = {guild} AND role = {role}")

    def removeMute(self, member: int, guild: int, role: int):
        return self.db.request(f"DELETE FROM Mutes WHERE mid = '{member}' AND guild = {guild} AND role = {role}")

    def getRole(self, guild: int, tp: str):
        return self.db.request(f"SELECT * FROM system_roles WHERE guild = {guild} AND name = '{tp}'")  

    def updateAdmin(self, member: int, guild: int, lvl: int):
        return self.db.request(f"UPDATE members SET admin = {lvl} WHERE mid = {member} AND guild = {guild}")

    def updateWarns(self, member: int, guild: int, warns: int):
        return self.db.request(f"UPDATE members SET warns = {warns} WHERE mid = {member} AND guild = {guild}")

    def startVoiceChannel(self, member: int, guild: int, channel: int):
        return self.db.request(f"INSERT INTO activitiesMembers(guild, mid, channel, start_time, end_time, dtime) VALUES({guild}, '{member}', '{channel}', {time.time()}, 0, '{time.strftime('%d.%m.%y')}')", 'result')

    def endVoiceChannel(self, member: int, guild: int, channel: int):
        lastActive = self.db.request(f"SELECT * FROM activitiesMembers WHERE mid = '{member}' AND guild = {guild} AND channel = '{channel}'", 'fetchall')[-1]
        self.db.request(f"UPDATE activitiesMembers SET end_time = {time.time()} WHERE id = {lastActive['id']}")
    
    def updateVoiceData(self, member: int, guild: int, channel: int, data: str):
        lastActive = self.db.request(f"SELECT * FROM activitiesMembers WHERE mid = '{member}' AND guild = {guild} AND channel = '{channel}'", 'fetchall')[-1]
        self.db.request(f"UPDATE activitiesMembers SET data = '{'{0}, {1}'.format(lastActive['data'], data) if lastActive['data'] else data}' WHERE id = {lastActive['id']}")

    def updateRankSystem(self, member: int, guild: int, tp: str, data: int):
        self.db.request(f"UPDATE members SET {tp} = {data} WHERE mid = '{member}' AND guild = {guild}")