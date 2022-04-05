from re import S
import discord, time, config

from discord.ext.commands.core import dm_only
from samp_client.models import ServerInfo
from discord import embeds
from datetime import datetime
from plugins import utils

def timestamp(local_time):
    return datetime.fromtimestamp(local_time - 10800)


class MemberKicked():

    def __init__(self, author, member, reason, a_id, icon):
        self.author = author
        self.member = member
        self.reason = reason
        self.a_id = a_id
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = ':tangerine: Успешное выполнение команды')
        embed.description = f"▹ Участник {self.member.mention} исключен"
        embed.add_field(name = 'Команду выполнил', value=f'▹ {self.author.mention}')
        embed.color = config.COLOR
        if self.reason: embed.add_field(name = 'Причиной тому стало', value=f"{self.reason}", inline=True)
        embed.set_footer(text = f"Действие (ID): {self.a_id}", icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

class MemberKickedLs():

    def __init__(self, author, member, reason, a_id, icon):
        self.author = author
        self.member = member
        self.reason = reason
        self.a_id = a_id
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = f':worried: Наказание с сервера {self.member.guild.name}')
        embed.description = f"▹ Вы были исключены из гильдии"
        embed.add_field(name = 'Выдал', value=f'▹ {self.author.mention}')
        embed.color = config.COLOR
        if self.reason: embed.add_field(name = 'Причиной тому стало', value=f"{self.reason}", inline=True)
        embed.set_footer(text = f"Действие (ID): {self.a_id}", icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

class MemberBanned():

    def __init__(self, author, member, reason, a_id, icon, tm: int):
        self.author = author
        self.member = member
        self.reason = reason
        self.a_id = a_id
        self.icon = icon
        self.tm = tm

    def get(self):
        embed = discord.Embed(title = ':tangerine: Успешное выполнение команды')
        embed.description = f"▹ Пользователь {self.member.mention} заблокирован"
        embed.add_field(name = 'Команду выполнил', value=f'▹ {self.author.mention}')
        embed.add_field(name = 'Время', value=f"{'{0} д.'.format(self.tm)  if self.tm > 0 else 'навсегда'}")
        embed.color = config.COLOR
        if self.reason: embed.add_field(name = 'Причиной тому стало', value=f"{self.reason}", inline=True)
        embed.set_footer(text = f"Действие (ID): {self.a_id}", icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

class MemberBannedLocal():

    def __init__(self, author, member, reason, a_id, icon, tm: int):
        self.author = author
        self.member = member
        self.reason = reason
        self.a_id = a_id
        self.icon = icon
        self.tm = tm

    def get(self):
        embed = discord.Embed(title = ':tangerine: Успешное выполнение команды')
        embed.description = f"▹ Пользователь {self.member.mention} заблокирован во всех гильдиях"
        embed.add_field(name = 'Команду выполнил', value=f'▹ {self.author.mention}')
        embed.add_field(name = 'Время', value=f"{'{0} д.'.format(self.tm)  if self.tm > 0 else 'навсегда'}")
        embed.color = config.COLOR
        if self.reason: embed.add_field(name = 'Причиной тому стало', value=f"{self.reason}", inline=True)
        embed.set_footer(text = f"Действие (ID): {self.a_id}", icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

class MuteEnd():

    def __init__(self, member, icon):
        self.member = member
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = ':partying_face: Ошибки в прошлом...')
        embed.description = f"▹ Участник {self.member.mention} разблокирован в каналах системой"
        embed.color = config.COLOR
        embed.add_field(name = 'Бот', value=f"▹ Больше не нарушай :wink:", inline=True)
        embed.set_footer(text = f"Orion RP | 2021", icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

class MuteEndByAdmin():

    def __init__(self, author: discord.Member, member: discord.Member, icon, tp: str):
        self.author = author
        self.member = member
        self.icon = icon
        self.type = tp

    def get(self):
        embed = discord.Embed(title = ':partying_face: Амнистия')
        embed.description = f"▹ Участник {self.member.mention} разблокирован в {'текстовых' if self.type == 'Mute' else 'голосовых'} каналах администратором"
        embed.add_field(name = 'Пожалел', value=f"{self.author.mention}", inline=True)
        embed.set_footer(text = f"Orion RP | 2021", icon_url=self.icon)
        embed.color = config.COLOR
        embed.timestamp = timestamp(time.time())
        return embed

class BanEnd():

    def __init__(self, member, icon):
        self.member = member
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = ':partying_face: Ошибки в прошлом...')
        embed.description = f"▹ Участник {self.member.mention} разблокирован в гильдии"
        embed.color = config.COLOR
        embed.add_field(name = 'Бот', value=f"▹ Больше не нарушай :wink:", inline=True)
        embed.set_footer(text = f"Orion RP | 2021", icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

class LogsBan():

    def __init__(self, member, icon):
        self.member = member
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = ':bookmark_tabs: Логирование действий')
        embed.description = f"▹ Участник `{self.member}` заблокирован в гильдии"
        embed.color = config.COLOR
        embed.set_footer(text = f"Orion RP | 2021", icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

class LogsVoice():

    def __init__(self, text, icon):
        self.icon = icon
        self.text = text

    def get(self):
        embed = discord.Embed(title = ':bookmark_tabs: Логирование действий голос.каналов')
        embed.description = f"▹ {self.text}"
        embed.color = config.COLOR
        embed.set_footer(text = f"Orion RP | 2021", icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

class LogsNick():

    def __init__(self, text, old: str, new: str, icon):
        self.icon = icon
        self.text = text
        self.old = old
        self.new = new

    def get(self):
        embed = discord.Embed(title = ':bookmark_tabs: Логирование ник-неймов')
        embed.description = f"▹ {self.text}"
        embed.add_field(name = 'Старый ник-нейм', value = self.old if self.old else 'Отсутствует')
        embed.add_field(name = 'Новый ник-нейм', value = self.new if self.new else 'Отсутствует')
        embed.color = config.COLOR
        embed.set_footer(text = f"Orion RP | 2021", icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

class LogsUnban():

    def __init__(self, member, icon):
        self.member = member
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = ':bookmark_tabs: Логирование действий')
        embed.description = f"▹ Участник `{self.member}` разблокирован в гильдии"
        embed.color = config.COLOR
        embed.set_footer(text = f"Orion RP | 2021", icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

class BanEndByAdmin():

    def __init__(self, author: discord.Member, member: discord.Member, icon):
        self.author = author
        self.member = member
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = ':partying_face: Амнистия')
        embed.description = f"▹ Участник {self.member.mention} разблокирован в гильдии"
        embed.add_field(name = 'Пожалел', value=f"{self.author.mention}", inline=True)
        embed.set_footer(text = f"Orion RP | 2021", icon_url=self.icon)
        embed.color = config.COLOR
        embed.timestamp = timestamp(time.time())
        return embed


class BanEndByAdminLocal():

    def __init__(self, author: discord.Member, member: discord.Member, icon):
        self.author = author
        self.member = member
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = ':partying_face: Амнистия')
        embed.description = f"▹ Участник {self.member.mention} разблокирован во всех гильдиях"
        embed.add_field(name = 'Пожалел', value=f"{self.author.mention}", inline=True)
        embed.set_footer(text = f"Orion RP | 2021", icon_url=self.icon)
        embed.color = config.COLOR
        embed.timestamp = timestamp(time.time())
        return embed

class BanEndByAdminLs():

    def __init__(self, author: discord.Member, member: discord.Member, icon):
        self.author = author
        self.member = member
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = f':partying_face: Автоматическое снятие наказания на сервере {self.member.guild.name}')
        embed.description = f"▹ Вы разблокированы в гильдии администратором"
        embed.add_field(name = 'Пожалел', value=f"{self.author.mention}", inline=True)
        embed.set_footer(text = f"Orion RP | 2021", icon_url=self.icon)
        embed.color = config.COLOR
        embed.timestamp = timestamp(time.time())
        return embed


class BanEndByAdminLocalLs():

    def __init__(self, author: discord.Member, member: discord.Member, icon):
        self.author = author
        self.member = member
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = f':partying_face: Автоматическое снятие наказания на сервере {self.member.guild.name}')
        embed.description = f"▹ Вы разблокированы во всех гильдиях"
        embed.add_field(name = 'Пожалел', value=f"{self.author.mention}", inline=True)
        embed.set_footer(text = f"Orion RP | 2021", icon_url=self.icon)
        embed.color = config.COLOR
        embed.timestamp = timestamp(time.time())
        return embed

class MemberMuted():

    def __init__(self, author, member, tm, reason, a_id, icon):
        self.author = author
        self.member = member
        self.tm = tm
        self.reason = reason
        self.a_id = a_id
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = ':tangerine: Успешное выполнение команды')
        embed.description = f"▹ Участник {self.member.mention} получил блокировку в текстовых каналах"
        embed.add_field(name = 'Команду выполнил', value=f'▹ {self.author.mention}', inline=True)
        embed.add_field(name = 'Время', value=f"{utils.translateTime(self.tm)}")
        if self.reason: embed.add_field(name = 'Причиной тому стало', value=f"▹ {self.reason}", inline=False)
        embed.set_footer(text = f"Действие (ID): {self.a_id}", icon_url=self.icon)
        embed.color = config.COLOR
        embed.timestamp = timestamp(time.time())
        return embed

class MemberWarned():

    def __init__(self, author, member, warn, reason, a_id, icon):
        self.author = author
        self.member = member
        self.wn = warn
        self.reason = reason
        self.a_id = a_id
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = ':tangerine: Успешное выполнение команды')
        embed.description = f"▹ Участник {self.member.mention} получил предупреждение"
        embed.add_field(name = 'Команду выполнил', value=f'▹ {self.author.mention}', inline=True)
        embed.add_field(name = 'Кол-во', value=f"{self.wn}")
        if self.reason: embed.add_field(name = 'Причиной тому стало', value=f"▹ {self.reason}", inline=False)
        embed.set_footer(text = f"Действие (ID): {self.a_id}", icon_url=self.icon)
        embed.color = config.COLOR
        embed.timestamp = timestamp(time.time())
        return embed

class MemberUnWarned():

    def __init__(self, author, member, warn, reason, a_id, icon):
        self.author = author
        self.member = member
        self.wn = warn
        self.reason = reason
        self.a_id = a_id
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = ':tangerine: Успешное выполнение команды')
        embed.description = f"▹ Участнику {self.member.mention} снято предупреждение"
        embed.add_field(name = 'Команду выполнил', value=f'▹ {self.author.mention}', inline=True)
        embed.add_field(name = 'Кол-во', value=f"{self.wn}")
        if self.reason: embed.add_field(name = 'Причиной тому стало', value=f"▹ {self.reason}", inline=False)
        embed.set_footer(text = f"Действие (ID): {self.a_id}", icon_url=self.icon)
        embed.color = config.COLOR
        embed.timestamp = timestamp(time.time())
        return embed

class MemberBanned():

    def __init__(self, author, member, reason, a_id, icon, tm: int):
        self.author = author
        self.member = member
        self.reason = reason
        self.a_id = a_id
        self.icon = icon
        self.tm = tm

    def get(self):
        embed = discord.Embed(title = ':tangerine: Успешное выполнение команды')
        embed.description = f"▹ Пользователь {self.member.mention} заблокирован"
        embed.add_field(name = 'Команду выполнил', value=f'▹ {self.author.mention}')
        embed.add_field(name = 'Время', value=f"{'{0} д.'.format(self.tm)  if self.tm > 0 else 'навсегда'}")
        embed.color = config.COLOR
        if self.reason: embed.add_field(name = 'Причиной тому стало', value=f"{self.reason}", inline=True)
        embed.set_footer(text = f"Действие (ID): {self.a_id}", icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

class MemberBannedLocalLs():

    def __init__(self, author, member, reason, a_id, icon, tm: int, guild):
        self.author = author
        self.member = member
        self.reason = reason
        self.a_id = a_id
        self.icon = icon
        self.tm = tm
        self.guild = guild

    def get(self):
        embed = discord.Embed(title = f':tangerine: Наказание с сервера `{self.guild.name}`')
        embed.description = f"▹ Вы были заблокированы во всех гильдиях"
        embed.add_field(name = 'Выдал', value=f'▹ {self.author.mention}')
        embed.add_field(name = 'Время', value=f"{'{0} д.'.format(self.tm)  if self.tm > 0 else 'навсегда'}")
        embed.color = config.COLOR
        if self.reason: embed.add_field(name = 'Причиной тому стало', value=f"{self.reason}", inline=True)
        embed.set_footer(text = f"Действие (ID): {self.a_id}", icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

class MemberBannedLs():

    def __init__(self, author, member, reason, a_id, icon, tm: int, guild):
        self.author = author
        self.member = member
        self.reason = reason
        self.a_id = a_id
        self.icon = icon
        self.tm = tm
        self.guild = guild

    def get(self):
        embed = discord.Embed(title = f':tangerine: Наказание с сервера `{self.guild.name}`')
        embed.description = f"▹ Вы были заблокированы в гильдии"
        embed.add_field(name = 'Выдал', value=f'▹ {self.author.mention}')
        embed.add_field(name = 'Время', value=f"{'{0} д.'.format(self.tm)  if self.tm > 0 else 'навсегда'}")
        embed.color = config.COLOR
        if self.reason: embed.add_field(name = 'Причиной тому стало', value=f"{self.reason}", inline=True)
        embed.set_footer(text = f"Действие (ID): {self.a_id}", icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

class MuteEndLs():

    def __init__(self, member, icon):
        self.member = member
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = f':partying_face: Окончание времени наказания на сервере `{self.member.guild.name}`')
        embed.description = f"▹ Участник {self.member.mention} разблокирован в текстовых каналах системой"
        embed.color = config.COLOR
        embed.add_field(name = 'Бот', value=f"▹ Больше не нарушай :wink:", inline=True)
        embed.set_footer(text = f"Orion RP | 2021", icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

class CreateRoomPanel():

    def __init__(self, text, icon):
        self.icon = icon
        self.text = text

    def get(self):
        embed = discord.Embed(title = f':gear: Настройка комнат')
        embed.description = f"▹ {self.text}"
        embed.color = config.COLOR
        embed.set_footer(text = f"Orion RP | 2021", icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

class MuteEndByAdminLs():

    def __init__(self, author: discord.Member, member: discord.Member, icon, tp: str):
        self.author = author
        self.member = member
        self.icon = icon
        self.type = tp

    def get(self):
        embed = discord.Embed(title = f':partying_face: Окончание времени наказания на сервере `{self.member.guild.name}`')
        embed.description = f"▹ Вы разблокированы в {'текстовых' if self.type == 'Mute' else 'голосовых'} каналах администратором"
        embed.add_field(name = 'Пожалел', value=f"{self.author.mention}", inline=True)
        embed.set_footer(text = f"Orion RP | 2021", icon_url=self.icon)
        embed.color = config.COLOR
        embed.timestamp = timestamp(time.time())
        return embed

class BanEndLs():

    def __init__(self, member, icon):
        self.member = member
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = ':partying_face: Окончание времени наказания на сервере `{self.member.guild.name}`')
        embed.description = f"▹ Вы разблокированы в гильдии"
        embed.color = config.COLOR
        embed.add_field(name = 'Бот', value=f"▹ Больше не нарушай :wink:", inline=True)
        embed.set_footer(text = f"Orion RP | 2021", icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

class MemberWarnedLs():

    def __init__(self, author, member, warns, reason, a_id, icon):
        self.author = author
        self.member = member
        self.wn = warns
        self.reason = reason
        self.a_id = a_id
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = f':worried: Наказание с сервера `{self.member.guild.name}`')
        embed.description = f"▹ Вы получили предупреждение"
        embed.add_field(name = 'Выдал', value=f'▹ {self.author.mention}', inline=True)
        embed.add_field(name = 'Кол-во', value=f"{self.wn}")
        if self.reason: embed.add_field(name = 'Причиной тому стало', value=f"▹ {self.reason}", inline=False)
        embed.set_footer(text = f"Действие (ID): {self.a_id}", icon_url=self.icon)
        embed.color = config.COLOR
        embed.timestamp = timestamp(time.time())
        return embed

class MemberUnWarnedLs():

    def __init__(self, author, member, warns, reason, a_id, icon):
        self.author = author
        self.member = member
        self.wn = warns
        self.reason = reason
        self.a_id = a_id
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = f':worried: Наказание с сервера `{self.member.guild.name}`')
        embed.description = f"▹ Вам сняли предупреждение"
        embed.add_field(name = 'Снял', value=f'▹ {self.author.mention}', inline=True)
        embed.add_field(name = 'Кол-во', value=f"{self.wn}")
        if self.reason: embed.add_field(name = 'Причиной тому стало', value=f"▹ {self.reason}", inline=False)
        embed.set_footer(text = f"Действие (ID): {self.a_id}", icon_url=self.icon)
        embed.color = config.COLOR
        embed.timestamp = timestamp(time.time())
        return embed


class MemberVMutedLs():

    def __init__(self, author, member, tm, reason, a_id, icon):
        self.author = author
        self.member = member
        self.tm = tm
        self.reason = reason
        self.a_id = a_id
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = f':worried: Наказание с сервера `{self.member.guild.name}`')
        embed.description = f"▹ Вы были наказаны блокировкой в голосовых каналах"
        embed.add_field(name = 'Команду выполнил', value=f'▹ {self.author.mention}', inline=True)
        embed.add_field(name = 'Время', value=f"{utils.translateTime(self.tm)}")
        if self.reason: embed.add_field(name = 'Причиной тому стало', value=f"▹ {self.reason}", inline=False)
        embed.set_footer(text = f"Действие (ID): {self.a_id}", icon_url=self.icon)
        embed.color = config.COLOR
        embed.timestamp = timestamp(time.time())
        return embed

class MemberMutedLs():

    def __init__(self, author, member, tm, reason, a_id, icon):
        self.author = author
        self.member = member
        self.tm = tm
        self.reason = reason
        self.a_id = a_id
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = f':worried: Наказание с сервера `{self.member.guild.name}`')
        embed.description = f"▹ Вы были наказаны блокировкой в текстовых каналах"
        embed.add_field(name = 'Команду выполнил', value=f'▹ {self.author.mention}', inline=True)
        embed.add_field(name = 'Время', value=f"{utils.translateTime(self.tm)}")
        if self.reason: embed.add_field(name = 'Причиной тому стало', value=f"▹ {self.reason}", inline=False)
        embed.set_footer(text = f"Действие (ID): {self.a_id}", icon_url=self.icon)
        embed.color = config.COLOR
        embed.timestamp = timestamp(time.time())
        return embed

class MemberVMuted():

    def __init__(self, author, member, tm, reason, a_id, icon):
        self.author = author
        self.member = member
        self.tm = tm
        self.reason = reason
        self.a_id = a_id
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = ':tangerine: Успешное выполнение команды')
        embed.description = f"▹ Участник {self.member.mention} получил блокировку в голосовых каналах"
        embed.add_field(name = 'Команду выполнил', value=f'▹ {self.author.mention}', inline=True)
        embed.add_field(name = 'Время', value=f"{utils.translateTime(self.tm)}")
        if self.reason: embed.add_field(name = 'Причиной тому стало', value=f"▹ {self.reason}", inline=False)
        embed.set_footer(text = f"Действие (ID): {self.a_id}", icon_url=self.icon)
        embed.color = config.COLOR
        embed.timestamp = timestamp(time.time())
        return embed


class SelfPH():

    def __init__(self, member):
        self.member = member

    def get(self):
        embed = discord.Embed(title = 'Информация')
        embed.description = f"▹ Вы не можете наказать самого себя!"
        embed.color = config.COLOR
        embed.set_footer(text = f"Отправлено: {self.member} | Orion RP | 2021", icon_url=self.member.avatar_url)
        embed.timestamp = timestamp(time.time())
        return embed

class SelfInteraction():

    def __init__(self, member):
        self.member = member

    def get(self):
        embed = discord.Embed(title = 'Информация')
        embed.description = f"▹ Вы не можете взаимодействовать с самим собой!"
        embed.color = config.COLOR
        embed.set_footer(text = f"Отправлено: {self.member} | Orion RP | 2021", icon_url=self.member.avatar_url)
        embed.timestamp = timestamp(time.time())
        return embed

class TmError():

    def __init__(self, member):
        self.member = member

    def get(self):
        embed = discord.Embed(title = ':confused: Что-то пошло не так')
        embed.description = f"▹ Вы указали неверное время. Это должно быть число от 1 до 1440"
        embed.color = 0xe9931c
        embed.set_footer(text = f"Отправлено: {self.member} | Orion RP | 2021", icon_url=self.member.avatar_url)
        embed.timestamp = timestamp(time.time())
        return embed

class GroupRolesNotFound():

    def __init__(self, member):
        self.member = member

    def get(self):
        embed = discord.Embed(title = ':confused: Что-то пошло не так')
        embed.description = f"▹ У гильдии отсутствуют группы ролей"
        embed.color = 0xe9931c
        embed.set_footer(text = f"Отправлено: {self.member} | Orion RP | 2021", icon_url=self.member.avatar_url)
        embed.timestamp = timestamp(time.time())
        return embed

class GroupRoles():

    def __init__(self, text, icon):
        self.icon = icon
        self.text = text

    def get(self):
        embed = discord.Embed(title = ':dividers: Список групп ролей')
        embed.description = self.text
        embed.color = 0xe9931c
        embed.set_footer(text = f"Orion RP | 2021", icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

class GroupForm(): 

    def __init__(self, prefix: str, icon: str):
        self.p = prefix
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = 'Группы ролей')
        embed.description = f"▹ Добавляйте группы ролей, чтобы участник мог подавать на роль"
        embed.add_field(name = 'Как всегда легко', 
                        value=f'▹ `{self.p}roles add @<роль> <название>`\n'
                                '  **┗** `<роль>` - может принимать упоминание или ID роли. *Обязательный параметр*\n'
                                '  **┗** `<название>` - принимает текст. *Обязательный параметр*\n')
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.set_thumbnail(url = 'https://image.flaticon.com/icons/png/512/845/845838.png')
        embed.timestamp = timestamp(time.time())
        return embed

class GroupFormEdit(): 

    def __init__(self, prefix: str, icon: str):
        self.p = prefix
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = 'Группы ролей')
        embed.description = f"▹ Изменяйте параметры группы ролей"
        embed.add_field(name = 'Как всегда легко', 
                        value=f'▹ `{self.p}roles edit <id группы> <дата>`\n'
                                '  **┗** `<id группы>` - принимает ID группы. *Обязательный параметр*\n'
                                '  **┗** `<дата>` - принимает новое название группы или новую роль (упоминание или ID роли). *Обязательный параметр*\n')
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.set_thumbnail(url = 'https://image.flaticon.com/icons/png/512/845/845838.png')
        embed.timestamp = timestamp(time.time())
        return embed

class GroupRole(): 

    def __init__(self, text: str, icon: str):
        self.text = text
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = 'Группы ролей')
        embed.description = f"▹ {self.text}"
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed


class LvlError():

    def __init__(self, member, max_lvl):
        self.max_lvl = max_lvl
        self.member = member

    def get(self):
        embed = discord.Embed(title = ':confused: Что-то пошло не так')
        embed.description = f"▹ Вы указали неверный уровень. Это должно быть число от 0 до {self.max_lvl}"
        embed.color = 0xe9931c
        embed.set_footer(text = f"Отправлено: {self.member} | Orion RP | 2021", icon_url=self.member.avatar_url)
        embed.timestamp = timestamp(time.time())
        return embed

class MemberIsMuted():

    def __init__(self, member):
        self.member = member

    def get(self):
        embed = discord.Embed(title = ':confused: Что-то пошло не так')
        embed.description = f"▹ Упс, участник уже заблокирован в данных каналах"
        embed.color = config.COLOR
        embed.set_footer(text = f"Отправлено: {self.member} | Orion RP | 2021", icon_url=self.member.avatar_url)
        embed.timestamp = timestamp(time.time())
        return embed

class MemberIsBanned():

    def __init__(self, member):
        self.member = member

    def get(self):
        embed = discord.Embed(title = ':confused: Что-то пошло не так')
        embed.description = f"▹ Упс, участник уже заблокирован в гильдии"
        embed.color = config.COLOR
        embed.set_footer(text = f"Отправлено: {self.member} | Orion RP | 2021", icon_url=self.member.avatar_url)
        embed.timestamp = timestamp(time.time())
        return embed

class EditMessage():

    def __init__(self, before: discord.Message, after: discord.Message, icon):
        self.before = before
        self.after = after
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = ':pencil: Редактирование сообщения')
        embed.description = f"▹ Отредактировано сообщение в канале {self.before.channel.mention} автором {self.before.author.mention}"
        embed.add_field(name = 'Старое сообщение', value=self.before.content)
        embed.add_field(name = 'Отредактированое сообщение', value=self.after.content)
        embed.color = config.COLOR
        embed.set_footer(text = f"Orion RP | 2021", icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

class DeleteMessage():

    def __init__(self, message: discord.Message, icon):
        self.message = message
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = ':clipboard: Корзина сообщений')
        embed.description = f"▹ Удалено сообщение в канале {self.message.channel.mention}"
        embed.add_field(name = 'Сообщение', value=self.message.content)
        embed.color = config.COLOR
        embed.set_footer(text = f"Orion RP | 2021", icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

class NotFoundActive():

    def __init__(self, author, member, dtime):
        self.member = member
        self.author = author
        self.dtime = dtime

    def get(self):
        embed = discord.Embed(title = ':confused: Что-то пошло не так')
        embed.description = f"▹ Упс, участник {self.member.mention} за {self.dtime} не участвовал в голосовых баталиях"
        embed.color = config.COLOR
        embed.set_footer(text = f"Отправлено: {self.author} | Orion RP | 2021", icon_url=self.member.avatar_url)
        embed.timestamp = timestamp(time.time())
        return embed

class MemberIsNotMuted():

    def __init__(self, member):
        self.member = member

    def get(self):
        embed = discord.Embed(title = ':confused: Что-то пошло не так')
        embed.description = f"▹ Упс, участник не заблокирован в данных каналах"
        embed.color = config.COLOR
        embed.set_footer(text = f"Отправлено: {self.member} | Orion RP | 2021", icon_url=self.member.avatar_url)
        embed.timestamp = timestamp(time.time())
        return embed

class MemberIsNotBanned():

    def __init__(self, member):
        self.member = member

    def get(self):
        embed = discord.Embed(title = ':confused: Что-то пошло не так')
        embed.description = f"▹ Упс, участник не заблокирован в гильдии"
        embed.color = config.COLOR
        embed.set_footer(text = f"Отправлено: {self.member} | Orion RP | 2021", icon_url=self.member.avatar_url)
        embed.timestamp = timestamp(time.time())
        return embed

class SmallTime():

    def __init__(self, member, a: int = 1, b: int = 1440):
        self.member = member
        self.a, self.b = a, b

    def get(self):
        embed = discord.Embed(title = ':confused: Что-то пошло не так')
        embed.description = f"▹ Время должно быть больше/равно {self.a} и меньше/равно {self.b}"
        embed.color = config.COLOR
        embed.set_footer(text = f"Отправлено: {self.member} | Orion RP | 2021", icon_url=self.member.avatar_url)
        embed.timestamp = timestamp(time.time())
        return embed

class WelcomeMember():
    def __init__(self, member: discord.Member, greeting: str):
        self.member = member
        self.greeting = greeting

    def get(self):
        embed = discord.Embed(title = ':smiley: Приветствие участника')
        member = self.member
        embed.description = f"▹ " + eval(self.greeting)
        embed.color = config.COLOR
        embed.set_footer(text = f"Отправлено: {self.member}", icon_url=self.member.avatar_url)
        embed.timestamp = timestamp(time.time())
        return embed

class SmallInt():

    def __init__(self, member, a: int = 1, b: int = 5):
        self.member = member
        self.a, self.b = a, b

    def get(self):
        embed = discord.Embed(title = ':confused: Что-то пошло не так')
        embed.description = f"▹ Число должно быть больше/равно {self.a} и меньше/равно {self.b}"
        embed.color = config.COLOR
        embed.set_footer(text = f"Отправлено: {self.member} | Orion RP | 2021", icon_url=self.member.avatar_url)
        embed.timestamp = timestamp(time.time())
        return embed

class GuildOwnerPH():

    def __init__(self, member: discord.Member):
        self.member = member

    def get(self):
        embed = discord.Embed(title = ':confused: Что-то пошло не так')
        embed.description = f"▹ Вы не можете наказать создателя гильдии!"
        embed.color = config.COLOR
        embed.set_footer(text = f"Отправлено: {self.member} | Orion RP | 2021", icon_url=self.member.avatar_url)
        embed.timestamp = timestamp(time.time())
        return embed

class GuildOwnerInteraction():

    def __init__(self, member: discord.Member):
        self.member = member

    def get(self):
        embed = discord.Embed(title = ':confused: Что-то пошло не так')
        embed.description = f"▹ Вы не можете взаимодействовать с создателем гильдии"
        embed.color = config.COLOR
        embed.set_footer(text = f"Отправлено: {self.member} | Orion RP | 2021", icon_url=self.member.avatar_url)
        embed.timestamp = timestamp(time.time())
        return embed

class TypeNotFound():

    def __init__(self, member: discord.Member):
        self.member = member

    def get(self):
        embed = discord.Embed(title = ':confused: Что-то пошло не так')
        embed.description = f"▹ Вы указали неверный тип"
        embed.add_field(name = 'Типы', value=' **┗** `mute` - разблокировать в текстовых каналах\n'
                                             ' **┗** `vmute` - разблокировать в голосовых каналах')
        embed.color = config.COLOR
        embed.set_footer(text = f"Отправлено: {self.member} | Orion RP | 2021", icon_url=self.member.avatar_url)
        embed.timestamp = timestamp(time.time())
        return embed

class GetTypesLog():
    def __init__(self, icon: str):
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = ':confused: Что-то пошло не так')
        embed.description = f"▹ Вы указали некорректный тип для логов"
        embed.add_field(name = 'Типы', 
                        value='**┗** `bans` - логи для банов/разбанов\n'
                                '**┗** `mutes` - логи для мутов/размутов\n'
                                '**┗** `messages` - логи редактирования/удаления сообщений\n'
                                '**┗** `welcome` - канал для приветствия участника\n'
                                '**┗** `voice` - логи голосовых каналов\n'
                                '**┗** `nicks` - логи никнеймов\n'
                                '**┗** `role` - логи ролей\n')
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

class GetTypesWelcome():
    def __init__(self, icon: str):
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = ':confused: Что-то пошло не так')
        embed.description = f"▹ Вы указали некорректный тип для приветствия"
        embed.add_field(name = 'Типы', 
                        value='**┗** `new` - установить приветствие\n'
                                '**┗** `get` - проверить приветствие\n'
                                '**┗** `remove` - удалить приветствие\n')
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

class BotPH():

    def __init__(self, member):
        self.member = member

    def get(self):
        embed = discord.Embed(title = ':confused: Что-то пошло не так')
        embed.description = f"▹ Мои же наказания не действуют на меня"
        embed.color = config.COLOR
        embed.set_footer(text = f"Отправлено: {self.member} | Orion RP | 2021", icon_url=self.member.avatar_url)
        embed.timestamp = timestamp(time.time())
        return embed

class MemberIsHaveCommand():

    def __init__(self, member):
        self.member = member

    def get(self):
        embed = discord.Embed(title = ':confused: Что-то пошло не так')
        embed.description = f"▹ Участник {self.member.mention} уже имеет доступ к данной команде"
        embed.color = config.COLOR
        embed.set_footer(text = f"Orion RP | 2021")
        embed.timestamp = timestamp(time.time())
        return embed

class EndPrime():

    def __init__(self, prefix):
        self.p = prefix

    def get(self):
        embed = discord.Embed(title = ':confused: Технические уведомления')
        embed.description = f"▹ PRIME статус для данного сервера закончился. Приобрести вы можете командой `{self.p}boost buy` в любой момент"
        embed.color = config.COLOR
        embed.set_footer(text = f"Orion RP | 2021")
        embed.timestamp = timestamp(time.time())
        return embed

class BotInteraction():

    def __init__(self, member):
        self.member = member

    def get(self):
        embed = discord.Embed(title = ':confused: Что-то пошло не так')
        embed.description = f"▹ Вы не можете взаимодействовать со мной"
        embed.color = config.COLOR
        embed.set_footer(text = f"Отправлено: {self.member} | Orion RP | 2021", icon_url=self.member.avatar_url)
        embed.timestamp = timestamp(time.time())
        return embed

class MemberNotFound():

    def __init__(self, member):
        self.member = member

    def get(self):
        embed = discord.Embed(title = ':confused: Что-то пошло не так')
        embed.description = f"▹ Я не знаком с таким участником. Возможно его не существует или он Вампус :face_with_raised_eyebrow:"
        embed.color = config.COLOR
        embed.set_footer(text = f"Отправлено: {self.member} | Orion RP | 2021", icon_url=self.member.avatar_url)
        embed.timestamp = timestamp(time.time())
        return embed

class KickForm(): 

    def __init__(self, prefix: str, icon: str):
        self.p = prefix
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = 'Исключить из гильдии')
        embed.description = f"▹ У вас есть возможность изгнать участника, но при этом у него останется возможность вернуться обратно."
        embed.add_field(name = 'Легок в использовании...', 
                        value=f'▹ `{self.p}kick @<участник> <причина>`\n'
                                '  **┗** `<участник>` - может принимать цифровой ID участника или упоминание его. *Обязательный параметр*\n'
                                '  **┗** `<причина>` - *Необязательный параметр*')
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.set_thumbnail(url = 'https://image.flaticon.com/icons/png/512/531/531317.png')
        embed.timestamp = timestamp(time.time())
        return embed

class GetForm(): 

    def __init__(self, prefix: str, icon: str):
        self.p = prefix
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = 'Информация об участнике гильдии')
        embed.description = f"▹ Узнай информацию об участнике гильдии. Во что он играет, что случает и т.д."
        embed.add_field(name = 'Как всегда легко', 
                        value=f'▹ `{self.p}get @<участник>`\n'
                                '  **┗** `<участник>` - может принимать цифровой ID участника или упоминание его. *Обязательный параметр*\n')
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.set_thumbnail(url = 'https://image.flaticon.com/icons/png/512/845/845838.png')
        embed.timestamp = timestamp(time.time())
        return embed

class SayForm(): 

    def __init__(self, prefix: str, icon: str):
        self.p = prefix
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = 'Сообщения от имени бота')
        embed.description = f"▹ Отправляйте сообщения от имени бота"
        embed.add_field(name = 'Пример', 
                        value=f'▹ `{self.p}say <текст>`\n'
                                '  **┗** `<текст>` - принимает текст. *Обязательный параметр*\n')
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.set_thumbnail(url = 'https://image.flaticon.com/icons/png/512/4253/4253333.png')
        embed.timestamp = timestamp(time.time())
        return embed

class WelcomForm(): 

    def __init__(self, prefix: str, icon: str):
        self.p = prefix
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = 'Настройка приветствия участника')
        embed.description = f"▹ Устанавливайте приветствие участника, чтобы было понятно :3"
        embed.add_field(name = 'Как всегда легко', 
                        value=f'▹ `{self.p}welcome <тип> <текст>`\n'
                                '  **┗** `<тип>` - принимает - new/get/remove. *Обязательный параметр*\n'
                                '  **┗** `<текст>` - принимает текст. Можно указывать переменые. Информацию смотрите в документации `Приветствие`. *Обязательный параметр*\n')
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.set_thumbnail(url = 'https://image.flaticon.com/icons/png/512/845/845838.png')
        embed.timestamp = timestamp(time.time())
        return embed

class ReferenceError:

    def __init__(self, icon: str):
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = ':confused: Что-то пошло не так')
        embed.description = '▹ Команда не найдена'
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

class ReferenceInfo:

    def __init__(self, name: str, data: dict, guild: int, icon: str):
        self.data = data
        self.icon = icon
        self.guild = guild
        self.name = name

    def get(self):
        embed = discord.Embed(title = f'Справка о команде "{self.name}"')
        embed.description = f'▹ {self.data["description"].capitalize()}'
        if self.data['lvl'] > 0: embed.add_field(name = 'Уровень модерации', value=utils.getLvlName(self.guild, self.data['lvl']))
        embed.add_field(name = 'Подписка PRIME', value='Требуется' if self.data['prime'] else 'Не требуется')
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

class ReferenceForm:

    def __init__(self, prefix: str, icon: str):
        self.p = prefix
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = 'Справка по командам')
        embed.description = '▹ Вы можете получить информацию о команде.'
        embed.add_field(name = 'Как всегда легко',
                        value = f'▹ `{self.p}справка <команда>`\n'
                                '**┗** `<команда>` - принимает название команды. *Обязательный параметр*')

        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.set_thumbnail(url = 'https://image.flaticon.com/icons/png/512/2806/2806879.png')
        embed.timestamp = timestamp(time.time())
        return embed

class MuteForm(): 

    def __init__(self, prefix: str, icon: str):
        self.p = prefix
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = 'Бан в текстовых каналах')
        embed.description = f"▹ Участник нарушает правила текстового канала? Накажите его блокировкой чата. Вы можете выдать мут от 1 минуты и до 24-ех часов"
        embed.add_field(name = 'Используйте', 
                        value=f'▹ `{self.p}mute @<участник> <время> <причина>`\n'
                                '**┗** `<участник>` - может принимать цифровой ID участника или упоминание его. *Обязательный параметр*\n'
                                '**┗** `<время>` - принимает только числа от 1 и до 1440 (24 часа). *Обязательный параметр*\n'
                                '**┗** `<причина>` - *Необязательный параметр*')
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.set_thumbnail(url = 'https://image.flaticon.com/icons/png/512/4862/4862692.png')
        embed.timestamp = timestamp(time.time())
        return embed

class CmdAccessForm(): 

    def __init__(self, prefix: str, icon: str):
        self.p = prefix
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = 'Выдача доступа к командам')
        embed.description = f"▹ Информация по команде"
        embed.add_field(name = 'Используйте', 
                        value=f'▹ `{self.p}кмд <тип>`\n'
                                '**┗** `<тип>` - может принимать типы: _выдать/забрать/список_. *Обязательный параметр*\n')
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.set_thumbnail(url = 'https://image.flaticon.com/icons/png/512/3103/3103968.png')
        embed.timestamp = timestamp(time.time())
        return embed

class CmdAccessGiveForm(): 

    def __init__(self, prefix: str, icon: str):
        self.p = prefix
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = 'Выдача доступа к командам')
        embed.description = f"▹ Вы можете выдать доступ к командам для участников"
        embed.add_field(name = 'Используйте', 
                        value=f'▹ `{self.p}кмд выдать @<участник> <команда> <время>`\n'
                                '**┗** `<участник>` - принимает ID/упоминание участника гильдии. *Обязательный параметр*\n'
                                '**┗** `<команда>` - принимает саму команду. *Обязательный параметр*\n'
                                '**┗** `<время>` - принимает время (1д/1ч). *Необязательный параметр*')
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.set_thumbnail(url = 'https://image.flaticon.com/icons/png/512/3103/3103968.png')
        embed.timestamp = timestamp(time.time())
        return embed

class VoiceForm(): 

    def __init__(self, prefix: str, icon: str):
        self.p = prefix
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = 'Настройка голосовых комант')
        embed.description = f"▹ Вы можете настроить систему комнат, чтобы участник мог создать для себя команту и там общаться"
        embed.add_field(name = 'Используйте', 
                        value=f'▹ `{self.p}войс <тип> `\n'
                                '**┗** `<тип>` - принимает параметры `вкл/выкл`. *Обязательный параметр*\n')
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.set_thumbnail(url = 'https://image.flaticon.com/icons/png/512/2282/2282210.png')
        embed.timestamp = timestamp(time.time())
        return embed

class GetSampForm(): 

    def __init__(self, prefix: str, icon: str):
        self.p = prefix
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = 'Информация о проекте мультиплеера "SAMP"')
        embed.description = f"▹ Можете узнать, какой онлайн на вашем любимом проекте"
        embed.add_field(name = 'Используйте', 
                        value=f'▹ `{self.p}samp <хост> <порт>`\n'
                                '**┗** `<хост>` - принимает IP адрес сервера в формате "x.x.x.x". *Обязательный параметр*\n'
                                '**┗** `<порт>` - принимает число. *Необязательный параметр*\n')
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.set_thumbnail(url = 'https://image.flaticon.com/icons/png/512/808/808439.png')
        embed.timestamp = timestamp(time.time())
        return embed

class WarnForm(): 

    def __init__(self, prefix: str, icon: str):
        self.p = prefix
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = 'Выдача предупреждения участнику')
        embed.description = f"▹ Выдавайте предупреждения участникам за их нарушения"
        embed.add_field(name = 'Используйте', 
                        value=f'▹ `{self.p}warn @<участник> <кол-во> <причина>`\n'
                                '**┗** `<участник>` - может принимать цифровой ID участника или упоминание его. *Обязательный параметр*\n'
                                '**┗** `<время>` - принимает только числа от 1 и до 3. *Необязательный параметр*\n'
                                '**┗** `<причина>` - *Необязательный параметр*')
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.set_thumbnail(url = 'https://image.flaticon.com/icons/png/512/1680/1680012.png')
        embed.timestamp = timestamp(time.time())
        return embed

class UnWarnForm(): 

    def __init__(self, prefix: str, icon: str):
        self.p = prefix
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = 'Снятие предупреждения участнику')
        embed.description = f"▹ Снимайте предупреждения участникам"
        embed.add_field(name = 'Используйте', 
                        value=f'▹ `{self.p}unwarn @<участник> <кол-во> <причина>`\n'
                                '**┗** `<участник>` - может принимать цифровой ID участника или упоминание его. *Обязательный параметр*\n'
                                '**┗** `<время>` - принимает только числа от 1 и до 3. *Необязательный параметр*\n'
                                '**┗** `<причина>` - *Необязательный параметр*')
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.set_thumbnail(url = 'https://image.flaticon.com/icons/png/512/1680/1680012.png')
        embed.timestamp = timestamp(time.time())
        return embed

class LocationForm(): 

    def __init__(self, prefix: str, icon: str):
        self.p = prefix
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = 'Настройка локализации гильдии')
        embed.description = f"▹ Объединяйте свои гильдии в общую локализацию"
        embed.add_field(name = 'Используйте', 
                        value=f'▹ `{self.p}local <тип> <гильдия>`\n'
                                '**┗** `<тип>` - принимает create/add/remove/delete. *Обязательный параметр*\n'
                                '**┗** `<гильдия>` - принимает ID гильдии. *Необязательный параметр*\n')
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.set_thumbnail(url = 'https://image.flaticon.com/icons/png/512/745/745256.png')
        embed.timestamp = timestamp(time.time())
        return embed

class CreateLocation(): 

    def __init__(self, id: int, icon):
        self.id = id
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = ':yum: Успешное выполнение команды')
        embed.description = f"▹ :white_check_mark: Вы успешно создали локализацию с ID: `{self.id}`"
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

class AddGuildToLocation(): 

    def __init__(self, guild: discord.Guild, icon):
        self.guild = guild
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = ':yum: Успешное выполнение команды')
        embed.description = f"▹ Гильдия {self.guild.name} добавлена к локализации"
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

class RemoveGuildToLocation(): 

    def __init__(self, guild: discord.Guild, icon):
        self.guild = guild
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = ':yum: Успешное выполнение команды')
        embed.description = f"▹ Гильдия {self.guild.name} удалена из локализации"
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

class DeleteLocation(): 

    def __init__(self, icon):
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = ':yum: Успешное выполнение команды')
        embed.description = f"▹ :white_check_mark: Вы удалили локализацию"
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

class SendRequestOnRole(): 

    def __init__(self, text, icon, group, link):
        self.icon = icon
        self.text = text
        self.group = group
        self.link = link

    def get(self):
        embed = discord.Embed(title = ':yum: Новая заявка на группу роли')
        embed.description = f"▹ {self.text}"
        embed.add_field(name = 'Группа', value=f"{self.group}")
        embed.add_field(name = 'Ссылка на вложение', value=f"[Вложение]({self.link})")
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

class LocationError():

    def __init__(self, member):
        self.member = member

    def get(self):
        embed = discord.Embed(title = ':confused: Что-то пошло не так')
        embed.description = f"▹ Укажите гильдию, которую собираетесь подключить"
        embed.color = config.COLOR
        embed.set_footer(text = f"Отправлено: {self.member} | Orion RP | 2021", icon_url=self.member.avatar_url)
        embed.timestamp = timestamp(time.time())
        return embed


class LogsForm(): 

    def __init__(self, prefix: str, icon: str):
        self.p = prefix
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = 'Уставнока логов на канал')
        embed.description = f"▹ Устанавливайте логи на каналы и следите за действиями участников/модераторов"
        embed.add_field(name = 'Используйте', 
                        value=f'▹ `{self.p}logs #<канал> <тип>`\n'
                                '**┗** `<канал>` - может принимать цифровой ID канал или упоминание его. *Обязательный параметр*\n'
                                '**┗** `<тип>` - принимает типы: messages/bans/mutes/welcome/voice/nicks/role. *Обязательный параметр*\n')
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.set_thumbnail(url = 'https://image.flaticon.com/icons/png/512/2911/2911230.png')
        embed.timestamp = timestamp(time.time())
        return embed

class RoleForm(): 

    def __init__(self, prefix: str, icon: str):
        self.p = prefix
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = 'Подача заявки на группу роли')
        embed.description = f"▹ Вы можете подать заявку, чтобы получить роль"
        embed.add_field(name = 'Используйте', 
                        value=f'▹ `{self.p}role <ID группы> [вложение]`\n'
                                f'**┗** `<ID группы>` - принимает ID группы. Узнать можно здесь: `{self.p}roles`. *Обязательный параметр*\n'
                                '**┗** `[вложение]` - принимает прикрепленное фото. *Обязательный параметр*\n')
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.set_thumbnail(url = 'https://image.flaticon.com/icons/png/512/1319/1319361.png')
        embed.timestamp = timestamp(time.time())
        return embed

class LvlNameForm(): 

    def __init__(self, prefix: str, icon: str):
        self.p = prefix
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = 'Изменение имени уровню модераторов')
        embed.description = f"▹ Изменяйте имена уровней на свои"
        embed.add_field(name = 'Используйте', 
                        value=f'▹ `{self.p}lvlname <уровень> <название>`\n'
                                f'**┗** `<уровень>` - уровень модератора, для которого собираетесь изменить название *Обязательный параметр*\n'
                                '**┗** `<название>` новое название уровня - *Обязательный параметр*\n')
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.set_thumbnail(url = 'https://image.flaticon.com/icons/png/512/1082/1082440.png')
        embed.timestamp = timestamp(time.time())
        return embed

class RlogsForm(): 

    def __init__(self, prefix: str, icon: str):
        self.p = prefix
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = 'Удаление логов с канала')
        embed.description = f"▹ Промохнулись каналом для логов? Или меняете все? Удалите логи с канала"
        embed.add_field(name = 'Используйте', 
                        value=f'▹ `{self.p}rlogs #<канал> <тип>`\n'
                                '**┗** `<канал>` - может принимать цифровой ID канал или упоминание его. *Обязательный параметр*\n'
                                '**┗** `<тип>` - принимает типы: messages/bans/mutes/welcome/voice/nicks/role. *Обязательный параметр*\n')
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.set_thumbnail(url = 'https://image.flaticon.com/icons/png/512/2911/2911230.png')
        embed.timestamp = timestamp(time.time())
        return embed

class BanForm(): 

    def __init__(self, prefix: str, icon: str):
        self.p = prefix
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = 'Блокировка участника в гильдии')
        embed.description = f"▹ Участник нарушает все возможные правила сервера? Хватит терпеть! Накажите его печатью бана от 1 суток и до вечной блокировки"
        embed.add_field(name = 'Используйте', 
                        value=f'▹ `{self.p}ban @<участник> <время> <причина>`\n'
                                '**┗** `<участник>` - может принимать цифровой ID участника или упоминание его. *Обязательный параметр*\n'
                                '**┗** `<время>` - принимает только числа от 0 и до 30. *Необязательный параметр*\n'
                                '**┗** `<причина>` - *Необязательный параметр*')
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.set_thumbnail(url = 'https://image.flaticon.com/icons/png/512/1869/1869808.png')
        embed.timestamp = timestamp(time.time())
        return embed

class LbanForm(): 

    def __init__(self, prefix: str, icon: str):
        self.p = prefix
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = 'Блокировка участника во всех гильдиях')
        embed.description = f"▹ Участник нарушает все возможные правила сервера? Хватит терпеть! Накажите его печатью бана от 1 суток и до вечной блокировки"
        embed.add_field(name = 'Используйте', 
                        value=f'▹ `{self.p}lban @<участник> <время> <причина>`\n'
                                '**┗** `<участник>` - может принимать цифровой ID участника или упоминание его. *Обязательный параметр*\n'
                                '**┗** `<время>` - принимает только числа от 0 и до 30. *Необязательный параметр*\n'
                                '**┗** `<причина>` - *Необязательный параметр*')
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.set_thumbnail(url = 'https://image.flaticon.com/icons/png/512/1869/1869808.png')
        embed.timestamp = timestamp(time.time())
        return embed

class AdminForm:

    def __init__(self, author: discord.Member, member: discord.Member, icon_url: str, guild: int, lvl: int):
        self.author = author
        self.member = member
        self.icon = icon_url
        self.guild = guild
        self.lvl = lvl

    def up(self):
        embed = discord.Embed(title = 'Выдача админ-прав')
        embed.description = f"▹ Участник {self.member.mention} повышен до {utils.getLvlName(self.guild, self.lvl)}"
        embed.add_field(name = 'Команду выполнил', value=f'▹ {self.author.mention}', inline=True)
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

    def down(self):
        embed = discord.Embed(title = 'Выдача админ-прав')
        embed.description = f"▹ Участник {self.member.mention} понижен до {utils.getLvlName(self.guild, self.lvl)}"
        embed.add_field(name = 'Команду выполнил', value=f'▹ {self.author.mention}', inline=True)
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

    def remove(self):
        embed = discord.Embed(title = 'Выдача админ-прав')
        embed.description = f"▹ Участник {self.member.mention} снова становится обычным обитателем гильдии"
        embed.add_field(name = 'Команду выполнил', value=f'▹ {self.author.mention}', inline=True)
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

    def error(self):
        embed = discord.Embed(title = ':confused: Что-то пошло не так')
        embed.description = f"▹ Участник {self.member.mention} уже имеет данный уровень"
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

class AdminFormLs:

    def __init__(self, author: discord.Member, member: discord.Member, icon_url: str, guild: int, lvl: int):
        self.author = author
        self.member = member
        self.icon = icon_url
        self.guild = guild
        self.lvl = lvl

    def up(self):
        embed = discord.Embed(title = f'Уведомление из гильдии `{self.member.guild}`')
        embed.description = f"▹ Вас повысили до {utils.getLvlName(self.guild, self.lvl)}"
        embed.add_field(name = 'Команду выполнил', value=f'▹ {self.author.mention}', inline=True)
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

    def down(self):
        embed = discord.Embed(title = f'Уведомление из гильдии `{self.member.guild}`')
        embed.description = f"▹ Вас понизили до {utils.getLvlName(self.guild, self.lvl)}"
        embed.add_field(name = 'Команду выполнил', value=f'▹ {self.author.mention}', inline=True)
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed

    def remove(self):
        embed = discord.Embed(title = f'Уведомление из гильдии `{self.member.guild}`')
        embed.description = f"▹ Вы снова становитесь обычным обитателем гильдии"
        embed.add_field(name = 'Команду выполнил', value=f'▹ {self.author.mention}', inline=True)
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.timestamp = timestamp(time.time())
        return embed



class SetadmForm(): 

    def __init__(self, prefix: str, icon: str, max_lvl: int):
        self.p = prefix
        self.icon = icon
        self.max_lvl = max_lvl

    def get(self):
        embed = discord.Embed(title = 'Выдача прав администратора')
        embed.description = f"▹ Вам нужны администраторы, которые будут следить За порядком на сервере? Выдайте им права администратора"
        embed.add_field(name = 'Используйте', 
                        value=f'▹ `{self.p}setadm @<участник> <уровень>`\n'
                                '**┗** `<участник>` - может принимать цифровой ID участника или упоминание его. *Обязательный параметр*\n'
                                f'**┗** `<уровень>` - принимает только числа от 0 и до {self.max_lvl} *Обязательный параметр*\n')
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.set_thumbnail(url = 'https://image.flaticon.com/icons/png/512/2206/2206248.png')
        embed.timestamp = timestamp(time.time())
        return embed

class UnmuteForm(): 

    def __init__(self, prefix: str, icon: str):
        self.p = prefix
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = 'Размут в голос./текст. каналах')
        embed.description = f"▹ Участник осознал свою ошибку и хочет исправиться? Вы можете разблокировать ему каналы"
        embed.add_field(name = 'Используйте', 
                        value=f'▹ `{self.p}unmute @<участник> <тип>`\n'
                                '**┗** `<участник>` - может принимать цифровой ID участника или упоминание его. *Обязательный параметр*\n'
                                '**┗** `<тип>` - тип мута (vmute/mute). *Обязательный параметр*')
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.set_thumbnail(url = 'https://image.flaticon.com/icons/png/512/1041/1041916.png')
        embed.timestamp = timestamp(time.time())
        return embed

class UnbanForm(): 

    def __init__(self, prefix: str, icon: str):
        self.p = prefix
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = 'Разбан участника')
        embed.description = f"▹ Участник покаялся и не собирается нарушать правила? Разблокируйте его в гильдии"
        embed.add_field(name = 'Используйте', 
                        value=f'▹ `{self.p}unban @<участник>`\n'
                                '**┗** `<участник>` - может принимать цифровой ID участника или упоминание его. *Обязательный параметр*\n')
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.set_thumbnail(url = 'https://image.flaticon.com/icons/png/512/4428/4428998.png')
        embed.timestamp = timestamp(time.time())
        return embed

class UnlbanForm(): 

    def __init__(self, prefix: str, icon: str):
        self.p = prefix
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = 'Разбан участника во всех гильдиях')
        embed.description = f"▹ Участник покаялся и не собирается нарушать правила? Разблокируйте его в гильдии"
        embed.add_field(name = 'Используйте', 
                        value=f'▹ `{self.p}unlban @<участник>`\n'
                                '**┗** `<участник>` - может принимать цифровой ID участника или упоминание его. *Обязательный параметр*\n')
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.set_thumbnail(url = 'https://image.flaticon.com/icons/png/512/4428/4428998.png')
        embed.timestamp = timestamp(time.time())
        return embed


class VMuteForm(): 

    def __init__(self, prefix: str, icon: str):
        self.p = prefix
        self.icon = icon

    def get(self):
        embed = discord.Embed(title = 'Бан в голосовых каналах')
        embed.description = f"▹ Вы можете заблокировать голосовые каналы участнику"
        embed.add_field(name = 'Используйте', 
                        value=f'▹ `{self.p}vmute @<участник> <время> <причина>`\n'
                                '**┗** `<участник>` - может принимать цифровой ID участника или упоминание его. *Обязательный параметр*\n'
                                '**┗** `<время>` - принимает только числа от 1 и до 1440 (24 часа) *Обязательный параметр*\n'
                                '**┗** `<причина>` - *Необязательный параметр*')
        embed.color = config.COLOR
        embed.set_footer(text = 'Orion RP | 2021', icon_url=self.icon)
        embed.set_thumbnail(url = 'https://image.flaticon.com/icons/png/512/1679/1679975.png')
        embed.timestamp = timestamp(time.time())
        return embed