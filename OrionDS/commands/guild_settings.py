import discord, config, typing
from discord.ext import commands
from plugins import simplemysql, utils, embeds

class GuildSettingsCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)


    @commands.command()
    async def prefix(self, ctx: commands.Context, new_prefix: str = None):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        lvl = utils.get_command('prefix', guild['id'])['lvl']
        aid = ctx.author.id
        if not self.db.request(f"SELECT * FROM members WHERE mid = {aid} AND guild = {guild['id']} AND admin >= {lvl}"): return await ctx.reply("У вас нет доступа к данной команде")
        if not new_prefix: return await ctx.send('Укажите новый префикс для бота')
        try: self.db.request(f"UPDATE guilds SET prefix = '{new_prefix}' WHERE id = {guild['id']}")
        except: return await ctx.send("Макс. кол-во символов префикса - 3")
        await ctx.send(f'Префикс бота обновлен на `{new_prefix}`')

    @commands.command()
    async def logs(self, ctx: commands.Context, channel: commands.Greedy[discord.TextChannel] = None, tp: str = None):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        lvl = utils.get_command('logs', guild['id'])['lvl']
        aid = ctx.author.id
        if not self.db.request(f"SELECT * FROM members WHERE mid = {aid} AND guild = {guild['id']} AND admin >= {lvl}"): return await ctx.reply("У вас нет доступа к данной команде")
        if not channel: return await ctx.send(embed = embeds.LogsForm(ctx.prefix, self.bot.user.avatar_url).get())
        if not tp: return await ctx.send(embed = embeds.GetTypesLog(self.bot.user.avatar_url).get())
        if tp not in config.TYPES_LOGS: return await ctx.send(embed = embeds.GetTypesLog(self.bot.user.avatar_url).get())
        ch = [i for i in channel][0]
        row = self.db.request(f"SELECT * FROM channels WHERE type = '{tp}_logs' AND guild = {guild['id']}")
        if row: return await ctx.send("Как я должен одни и те же логи присвоить одному и тому же каналу?")
        self.db.request(f"INSERT INTO channels(guild, type, channel) VALUES({guild['id']}, '{tp}_logs', '{ch.id}')")
        await ctx.send(f"Теперь я воспринимаю канал {ch.mention}, как логи по {config.LOGS[tp]}")

    @commands.command()
    async def rlogs(self, ctx: commands.Context, channel: commands.Greedy[discord.TextChannel] = None, tp: str = None):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        lvl = utils.get_command('rlogs', guild['id'])['lvl']
        aid = ctx.author.id
        if not self.db.request(f"SELECT * FROM members WHERE mid = {aid} AND guild = {guild['id']} AND admin >= {lvl}"): return await ctx.reply("У вас нет доступа к данной команде")
        if not channel: return await ctx.send(embed = embeds.RlogsForm(ctx.prefix, self.bot.user.avatar_url).get())
        if not tp: return await ctx.send(embed = embeds.GetTypesLog(self.bot.user.avatar_url).get())
        if tp not in config.TYPES_LOGS: return await ctx.send(embed = embeds.GetTypesLog(self.bot.user.avatar_url).get())
        ch = [i for i in channel][0]
        row = self.db.request(f"SELECT * FROM channels WHERE type = '{tp}_logs' AND guild = {guild['id']}")
        if not row: return await ctx.send(f"У канала {ch.mention} нет данного типа логов")
        self.db.request(f"DELETE FROM channels WHERE id = {row['id']}")
        await ctx.send(f"Теперь я не воспринимаю канал {ch.mention}, как логи по {config.LOGS[tp]}")

    @commands.command()
    async def lvlname(self, ctx: commands.Context, lvl: int = None, *, name: str = None):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        alvl = utils.get_command('lvlname', guild['id'])['lvl']
        aid = ctx.author.id
        if not self.db.request(f"SELECT * FROM members WHERE mid = {aid} AND guild = {guild['id']} AND admin >= {alvl}"): return await ctx.reply("У вас нет доступа к данной команде")
        if not lvl: return await ctx.send(embed = embeds.LvlNameForm(ctx.prefix, self.bot.user.avatar_url).get())
        if lvl < 1 or lvl > 5: return await ctx.send(embed = embeds.SmallInt(ctx.author).get())
        if not name: return await ctx.send("Укажите новое название уровня")
        self.db.request(f"INSERT INTO lvlNames(guild, lvl, name) VALUES({guild['id']}, {lvl}, '{name}')")
        await ctx.send(f"Уровень `{config.LVL_NAMES[lvl]}` переименован в `{name}`")

    @commands.command()
    async def welcome(self, ctx: commands.Context, tp: str = None, *, text = None):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        alvl = utils.get_command('welcome', guild['id'])['lvl']
        aid = ctx.author.id
        if not self.db.request(f"SELECT * FROM members WHERE mid = {aid} AND guild = {guild['id']} AND admin >= {alvl}"): return await ctx.reply("У вас нет доступа к данной команде")
        if not tp: return await ctx.send(embed = embeds.WelcomForm(ctx.prefix, self.bot.user.avatar_url).get())
        if tp == 'new' and self.db.request(f"SELECT * FROM Greetings WHERE guild = {guild['id']}"): return await ctx.send(f'У гильдии уже уставнолено приветствие. Удалите его -> `{ctx.prefix}welcome remove`')
        if tp not in config.TYPES_WELCOME: return await ctx.send(embed = embeds.GetTypesWelcome(self.bot.user.avatar_url).get())
        if not text and tp == 'new': return await ctx.reply('Укажите текст')
        if tp == 'new':
            self.db.request(f"INSERT INTO Greetings(guild, text) VALUES({guild['id']}, 'f\"{text}\"')")
            greet = self.db.request(f"SELECT * FROM Greetings WHERE guild = {guild['id']}")
            self.db.request(f"UPDATE guilds SET greeting = {greet['id']} WHERE id = {guild['id']}")
            return await ctx.send(f"Приветствие нового участника установлено. Чтобы проверить, пропишите `{ctx.prefix}welcome get`")

        if tp == 'get':
            greet = self.db.request(f"SELECT * FROM Greetings WHERE id = {guild['greeting']}")
            if not greet: return await ctx.send('Приветствие не установлено')
            return await ctx.send(embed = embeds.WelcomeMember(ctx.author, greet['text']).get())

        if tp == 'remove':
            greet = self.db.request(f"SELECT * FROM Greetings WHERE id = {guild['greeting']}")
            if not greet: return await ctx.send('Приветствие не установлено')
            self.db.request(f"UPDATE guilds SET greeting = NULL WHERE id = {guild['id']}")
            self.db.request(f"DELETE FROM Greetings WHERE id = {greet['id']}")
            return await ctx.send(f"Приветствие нового участника удалено.")

    @commands.group(invoke_without_command = True)
    async def roles(self, ctx: commands.Context):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        roles = self.db.request(f"SELECT * FROM groupRoles WHERE guild = {guild['id']}", 'fetchall')
        if not roles: return await ctx.send(embed = embeds.GroupRolesNotFound(ctx.author).get())
        text = '\n'.join(
            f"▹ {n}. `{i['name']}`"

            for n, i in enumerate(roles, 1)
            if ctx.guild.get_role(int(i['role']))
        )
        await ctx.send(embed = embeds.GroupRoles(text, self.bot.user.avatar_url).get())

    @roles.command()
    async def add(self, ctx: commands.Context, role: typing.Union[discord.Role, None], *, name: str = None):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        alvl = utils.get_command('roles', guild['id'])['lvl']
        aid = ctx.author.id
        if not self.db.request(f"SELECT * FROM members WHERE mid = {aid} AND guild = {guild['id']} AND admin >= {alvl}"): return await ctx.reply("У вас нет доступа к данному параметру команды")
        if not role: return await ctx.send(embed = embeds.GroupForm(ctx.prefix, self.bot.user.avatar_url).get())
        if not name: return await ctx.send("Укажите название группы")
        groups = self.db.request(f"SELECT * FROM groupRoles WHERE guild = {guild['id']}", 'fetchall')
        id = max([i['group_id'] for i in groups]) + 1 if groups else 1
        self.db.request(f"INSERT INTO groupRoles(guild, group_id, role, name) VALUES({guild['id']}, {id}, '{role.id}', '{name}')")
        await ctx.send(embed = embeds.GroupRole(f"Роль {role.mention} добавлена в группу ролей с названием `{name}` под ID: `{id}`", self.bot.user.avatar_url).get())

    @roles.command()
    async def remove(self, ctx: commands.Context, id: int):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        alvl = utils.get_command('roles', guild['id'])['lvl']
        aid = ctx.author.id
        if not self.db.request(f"SELECT * FROM members WHERE mid = {aid} AND guild = {guild['id']} AND admin >= {alvl}"): return await ctx.reply("У вас нет доступа к данному параметру команды")
        if not id: return await ctx.send(embed = embeds.GroupForm(ctx.prefix, self.bot.user.avatar_url).get())
        group = self.db.request(f"SELECT * FROM groupRoles WHERE guild = {guild['id']} AND group_id = {id}")
        if not group: return await ctx.send("Группа с данным ID не найдена") 
        self.db.request(f"DELETE FROM groupRoles WHERE id = {group['id']}")
        await ctx.send(embed = embeds.GroupRole(f"Группа роли с ID `{id}` удалена из группы", self.bot.user.avatar_url).get())

    @roles.command()
    async def edit(self, ctx: commands.Context, id: int = None, *, data: typing.Union[discord.Role, str] = None):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        alvl = utils.get_command('roles', guild['id'])['lvl']
        aid = ctx.author.id
        if not self.db.request(f"SELECT * FROM members WHERE mid = {aid} AND guild = {guild['id']} AND admin >= {alvl}"): return await ctx.reply("У вас нет доступа к данному параметру команды")
        role = data if type(data) != str else None
        name = data if type(data) == str else None
        if not id: return await ctx.send(embed = embeds.GroupFormEdit(ctx.prefix, self.bot.user.avatar_url).get())
        if not role and not name: return await ctx.send(embed = embeds.GroupFormEdit(ctx.prefix, self.bot.user.avatar_url).get())
        group = self.db.request(f"SELECT * FROM groupRoles WHERE guild = {guild['id']} AND group_id = {id}")
        if not group: return await ctx.send("Группа с данным ID не найдена") 
        self.db.request(f"UPDATE groupRoles SET role = '{role.id}' WHERE id = {group['id']}") if role else self.db.request(f"UPDATE groupRoles SET name = '{name}' WHERE id = {group['id']}") 
        await ctx.send(embed = embeds.GroupRole(f"{'Название' if name else 'Роль'} группы `{group['name']}` изменен{'о' if name else ''} на {role.mention if role else name}", self.bot.user.avatar_url).get())

    #@commands.group(name = 'кмд', invoke_without_command = True)
    async def _cmd(self, ctx: commands.Context):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        alvl = utils.get_command('кмд', guild['id'])['lvl']
        aid = ctx.author.id
        if not self.db.request(f"SELECT * FROM members WHERE mid = {aid} AND guild = {guild['id']} AND admin >= {alvl}"): return await ctx.reply("У вас нет доступа к данному параметру команды")
        await ctx.send(embed = embeds.CmdAccessForm(ctx.prefix, self.bot.user.avatar_url).get())

    #@_cmd.command()
    async def выдать(self, ctx: commands.Context, member: discord.Member = None, command: str = None, tm: str = None):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        if guild['boosts'] == 0: return await ctx.send("У гильдии отсутствует статус PRIME")
        alvl = utils.get_command('кмд', guild['id'])['lvl']
        aid = ctx.author.id
        if not self.db.request(f"SELECT * FROM members WHERE mid = {aid} AND guild = {guild['id']} AND admin >= {alvl}"): return await ctx.reply("У вас нет доступа к данному параметру команды")
        if not member: return await ctx.send(embed = embeds.CmdAccessGiveForm(ctx.prefix, self.bot.user.avatar_url).get())
        if not command: return await ctx.send(embed = embeds.CmdAccessGiveForm(ctx.prefix, self.bot.user.avatar_url).get())
        if self.db.request(f"SELECT * FROM accessCommands WHERE mid = {member.id} AND guild = {guild['id']} AND command = '{command}'"): return await ctx.send(embed = embeds.MemberIsHaveCommand(member).get())
        tm = int(tm.split()[0])*86400 if tm.split()[1] == 'д' else int(tm.split()[0])*3600
        self.db.request(f"INSERT INTO accessCommands(guild, command, mid, time) VALUES({guild['id']}, '{command}', {tm})")


def setup(client):
    client.add_cog(GuildSettingsCommands(client))   