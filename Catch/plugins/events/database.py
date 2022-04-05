import settings, pymysql, asyncio

class DataBase(object):

	def __init__(self, connect=None):
		self.connect = connect

	def connection(self):
		connection = pymysql.connect(host=self.connect['host'], user=self.connect['user'], password=self.connect['password'], db=self.connect['db'], cursorclass=pymysql.cursors.DictCursor)
		return connection