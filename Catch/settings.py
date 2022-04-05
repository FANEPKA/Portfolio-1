import vk_api
from vk_api.bot_longpoll import VkBotLongPoll

"""

	Настройки бота
	Версия 1.0
	Разработчик: https://vk.com/fanepka


"""

#Токен группы
TOKEN = '4975a3e4f626c811ed61219e23eb375435fdb04b846ff8ee941d69a4ee584c17c0c8c377713dc07764824'

#Мой токен
USER_TOKEN = ''

#ID Группы для регистрации в системе
GROUP_ID = 203898932

#Для выхода
Q = []

#Если попытаются кикнуть бота
IF_BOT = 'На меня не действуют мои же наказания'

#Беседы с режимом тишины
USE_AMODE = True
AMODE = []

#Работа тэга /arole
USE_TAG = False
TAG_COMMENT = 'команда в разработке'

#Отправлять стикеры
USE_STICKER = False
STICKERS = []

#Беседы в режиме тишины
AMODE = []

#Работа с базой данных
DB = {
	
	'host': 'localhost',
	'user': 'phpmyadmin',
	'password': 'admin',
	'db': 'Catch',
	'port': 3307

}

def session():
	vk_session = vk_api.VkApi(token=TOKEN)
	vk = vk_session.get_api()
	longpoll = VkBotLongPoll(vk_session, GROUP_ID)
	return vk, longpoll

def MySession():
	vk_session = vk_api.VkApi(token=USER_TOKEN)
	vk = vk_session.get_api()
	return vk
