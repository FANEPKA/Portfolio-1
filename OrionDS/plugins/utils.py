import re
import discord
import config, time, datetime
from plugins import simplemysql, connect

db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)


class Colors():
    
    @staticmethod
    def red(text: str, text_one: str = None):
        return f"\033[31m{text_one if text_one else ''} \033[37m{text}"

    @staticmethod
    def yellow(text: str, text_one: str = None):
        return f"\033[33m{text_one if text_one else ''} \033[37m{text}"


def getMemberIsAdmin(member: dict, author: dict, role_check = True):
    role_is_admin = member['top_role'].permissions.administrator if member['top_role'] else False
    if role_is_admin and role_check: return 'role'
    if author['lvl'] <= member['lvl']: return 'lvl'
    return False


class Emojies:

    Spotify = '<:Spotify:878359692303298570>'
    VSCode = '<:vscode:878360037427412992>'

async def get_anekdot():
    import aiohttp, random
    from bs4 import BeautifulSoup as bs
    url = 'http://anekdotov.net/anekdot/'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            data = bs(await r.text(), 'html.parser')
            rm = random.choice(data.findAll('div', class_ = "anekdot"))
            
            return rm.text

"""
async def getAsyncActivity(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]

def getAnswer(type: str, language: str = 'ru'):
    pass

"""

def get_command(name: str, guild: int):
    commands = config.COMMANDS
    #db_command = db.request(f"SELECT * FROM commandsLvl WHERE name = '{name}' AND guild = {guild}")
    #if not db_command: 
    return [commands[command] for command in commands if command == name][0]
    #return db_command

def get_commands(lvl: int, p: str):
    commands = config.COMMANDS
    #db_command = db.request(f"SELECT * FROM commandsLvl WHERE name = '{name}' AND guild = {guild}")
    #if not db_command: 
    return '\n'.join(f"{p}{command} - {commands[command]['description']}" for command in commands if commands[command]["lvl"] == lvl)
    #return db_command
     

def insertAdminHistory(guild: int, types: str, data: str):
    db.request(f'INSERT INTO aHistory(guild, type, data, time) VALUES({guild}, "{types}", "{data}", {time.time() - 10800})')


def translateTime(tm):
    if tm < 60: return f"{tm} мин."
    elif tm < 3600:
        if float(tm/60) == int(tm/60): return f"{int(tm/60)} ч"
        return f"{int(tm/60)} ч. {str(tm)[-1] if tm - 60 > 60 else tm - 60} мин."

    else:
        if float(tm/3600) == int(tm/3600): return f"{int(tm/3600)} ч"
        return f"{int(tm/3600)} ч. {str(tm)[-1] if tm - 3600 > 3600 else tm - 3600} мин."

async def getRoles(guild: discord.Guild, id, role):
    roles = guild.get_role(int(id))
    if roles: return roles
    res = await createMuteRoles(guild, role)
    if role == 'mute':
        db.request(f"UPDATE system_roles SET role_id = '{res[0].id}' WHERE role_id = '{id}'") 
        return res[0]
    elif role == 'vmute':
        db.request(f"UPDATE system_roles SET role_id = '{res[1].id}' WHERE role_id = '{id}'")
        return res[1]

def getNitroBoosters(boost: datetime.datetime):
    if not boost: return ''
    tm = boost.timestamp() + 10800
    boost = datetime.datetime.fromtimestamp(tm)
    return f"| Буст {boost.strftime('%d.%m.%y %H:%M')}"


def getTime(dtime: str, days = False):
    new_time = ''
    d, h, m, s = dtime.split(':')
    d = f"{int(d) - 1}"
    if int(d) > 0 and days: new_time += f'{d if d[0] != "0" else d[1]} д. '
    if int(h) > 0: new_time += f'{h if h[0] != "0" else h[1]} ч. '
    if int(m) > 0: new_time += f'{m if m[0] != "0" else m[1]} мин. ' 
    if int(s) > 0: new_time += f'{s if s[0] != "0" else s[1]} сек.'
    return new_time.strip() 

def getLogsChannel(guild: discord.Guild, gd: int, type: str, suffix: str = '_logs'):
    ch = db.request(f"SELECT * FROM channels WHERE type = '{type}{suffix}' AND guild = {gd}")
    if not ch: return None
    channel = guild.get_channel(int(ch['channel']))
    if not channel: return None
    return channel

def passedTime(created_at: datetime.datetime):
    result = time.time() - created_at.timestamp() - 21600
    dtime = datetime.datetime.fromtimestamp(result).strftime('%d:%H:%M:%S')
    return getTime(dtime)

async def getActivity(activities: discord.BaseActivity, activity = ''):
    if activities == (): return ''
    for data in activities:
        if data.type == discord.ActivityType.listening and data.name == 'Spotify':
            activity += f'\n**Слушает Spotify: ** {Emojies.Spotify} [{data.artist} - {data.title}]({data.album_cover_url}) уже {passedTime(data.start)}'
        if data.type == discord.ActivityType.listening and data.name != 'Spotify':
            url = f"[{data.name}]({data.url})" if data.url else f'{data.name}'
            activity += f'\n**Слушает: ** {url}'
        if data.type == discord.ActivityType.playing:
            res = data.name == 'Visual Studio Code'
            activity += f'\n**Играет:**{" {}".format(Emojies.VSCode) if res else ""} {data.name} {" уже " + passedTime(data.start) if data.start else ""}'

    return activity


def getRankMember(members, member):
    lvls = [i['lvl'] for i in members]
    members = [i['id'] for i in members]
    result = sorted(zip(members, lvls), key=lambda n: int(n[1]), reverse=True)
    response = [n
        for n, i in enumerate(result, 1)
        if i[0] == member['id']
    ]
    return response

def getStatus(status):
    if status == 'online': return 'В сети'
    elif status == 'offline': return 'Не в сети'
    elif status == 'idle': return 'Не активен'
    elif status == 'dnd': return 'Не беспокоить'
            
async def getUserStatus(activity):
    try: 
        if activity.type != discord.ActivityType.custom: return ''
        return f'\n**Пользовательский статус:** {activity}'
    except: return ''

def getAdmin(guild: discord.Guild, a_list: list, lvl: int):
    gm: discord.Member = guild.get_member
    admins = '\n'.join(f"▹ {gm(int(i['mid'])).display_name} {getNitroBoosters(gm(int(i['mid'])).premium_since)}" for i in a_list if i['admin'] == lvl)
    if admins: return admins
    return '▹ Отсутствуют'

def getActivityMember(guild: dict, active: dict):
    if guild['boosts'] == 0 or not active['data']: return ''
    return f"| `{active['data']}`"

def getLvlName(guild: int, lvl: int):
    lvlNames = db.request(f"SELECT * FROM lvlNames WHERE guild = {guild} AND lvl = {lvl}", 'fetchall')
    if lvlNames: return lvlNames[-1]['name']
    try: return config.LVL_NAMES[lvl] 
    except KeyError: return 'Неизвестный чудак'


    
async def createMuteRoles(guild: discord.Guild, roles = 'all'):
    mute_per = discord.Permissions(
            send_messages = False, 
            send_tts_messages = False, 
            manage_messages=False, 
            change_nickname = True, 
            view_channel = False)
    vmute_per = discord.Permissions(
            speak = False, 
            connect = False,  
            change_nickname = True, 
            view_channel = False)
    gid = db.request(F"SELECT * FROM guilds WHERE guild = '{guild.id}'")['id']
    spec_role = db.request(f'SELECT * FROM system_roles WHERE guild = {gid} AND name = "Canella"') 
    spec_role: discord.Role = guild.get_role(int(spec_role['role_id']))
    spec_position = spec_role.position
    vmute, mute = None, None
    if roles == 'all' or roles == 'mute':
        mute = await guild.create_role(name = 'Mute', reason = 'Роль отсутствует')
        position = {mute: spec_position - 1}
        await guild.edit_role_positions(position)
        db.request(f"INSERT INTO system_roles(guild, name, role_id) VALUES({gid}, 'Mute', '{mute.id}')") 
    if roles == 'all' or roles == 'vmute':
        vmute = await guild.create_role(name = 'VMute', reason = 'Роль отсутствует')
        position = {vmute: spec_position - 1}
        await guild.edit_role_positions(position)
        db.request(f"INSERT INTO system_roles(guild, name, role_id) VALUES({gid}, 'VMute', '{vmute.id}')")

    if mute: [
        
        await i.set_permissions(mute, reason = 'Обновление ролей', send_messages = False, 
            send_tts_messages = False, 
            manage_messages=False, 
            change_nickname = True) 
        for i in guild.categories
        
        ]

    if vmute: [
        
        await i.set_permissions(vmute, reason = 'Обновление ролей',
            speak = False,  
            change_nickname = True) 
        for i in guild.categories
        
        ]

    return mute, vmute


async def help_command(lvl: int, p: str = '!', guild: int = 0):
    commands = [i for i in config.COMMANDS if config.COMMANDS[i]['lvl'] == lvl]
    #db_commands = db.request(f"SELECT * FROM commandsLvl WHERE lvl = {lvl} AND guild = {guild}", "fetchall")
    #if db_commands: 
    if len(commands) == 0: return '▹ Команды не найдены'
    return '\n'.join(f'▹ {p}{i} - {config.COMMANDS[i]["description"]}' for i in commands)
    