import pymysql
from modules.connector import JWORK

class DataBase(object):

    def __init__(self, connect: dict = JWORK().openj()['db']):
        self.connect = connect

    async def connection(self):
        connection = pymysql.connect(host=self.connect['host'], user=self.connect['user'], password=self.connect['password'], db=self.connect['db'], cursorclass=pymysql.cursors.DictCursor)
        return connection

    def sync_connection(self):
        connection = pymysql.connect(host=self.connect['host'], user=self.connect['user'], password=self.connect['password'], db=self.connect['db'], cursorclass=pymysql.cursors.DictCursor)
        return connection

    async def request(self, request: str, type: str = 'fetchone', size: int = 0):
        """

        fethcone: - возвращает 1 элемент (default)
        fetchall: - возвращает все элементы
        fetchmany: - возвращает n-ое кол-во элементов
        result: - кол-во элементов

        """
        connect = await self.connection()
        try:
            with connect.cursor() as cursor:
                result = cursor.execute(request)
                if type == 'fetchone': return cursor.fetchone()
                elif type == 'fetchall': return cursor.fetchall()
                elif type == 'fetchmany': return cursor.fetchmany(size=size)
                elif type == 'result': return result

        finally:
            connect.commit()
            connect.close()

    def cursor(self, request: str, type: str = 'fetchone', size: int = 0):
        """

        fethcone: - возвращает 1 элемент (default)
        fetchall: - возвращает все элементы
        fetchmany: - возвращает n-ое кол-во элементов
        result: - кол-во элементов

        """
        connect = self.sync_connection()
        try:
            with connect.cursor() as cursor:
                result = cursor.execute(request)
                if type == 'fetchone': return cursor.fetchone()
                elif type == 'fetchall': return cursor.fetchall()
                elif type == 'fetchmany': return cursor.fetchmany(size=size)
                elif type == 'result': return result

        finally:
            connect.commit()
            connect.close()

    async def get_command_lvl(self, command: str, pid: int):
        commands = (await JWORK('config.json').open_json())['commands']
        result = await self.request(f"SELECT * FROM commands WHERE pid = {pid} AND command = '{command}'")
        if result: 
            if not commands[command]['hide']: return result['lvl']
            else: return 5
        else:
            if not commands[command]['hide']: return commands[command]['lvl']
            else: return 5


    def get_sql_member(self, mid: int, pid: int):
        result = self.cursor(f"SELECT * FROM members WHERE mid = {mid} AND pid = {pid}")
        if result: return result
        else:
            self.cursor(f"INSERT INTO members(mid, pid) VALUES({mid}, {pid})")
            return self.cursor(f"SELECT * FROM members WHERE mid = {mid} AND pid = {pid}")

    async def member(self, mid: int, pid: int):
        result = await self.request(f"SELECT * FROM members WHERE mid = {mid} AND pid = {pid}")
        if result: return result
        else:
            await self.request(f"INSERT INTO members(mid, pid) VALUES({mid}, {pid})")
            return await self.request(f"SELECT * FROM members WHERE mid = {mid} AND pid = {pid}")
