import discord, config
from discord import guild
from discord.ext import commands
from events import new_guild
from plugins import simplemysql, utils, embeds

class LocationsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)


    @commands.group(invoke_without_command = True)
    async def local(self, ctx: commands.Context):
        guild = self.db.request(f'SELECT * FROM guilds WHERE guild = "{ctx.guild.id}"')
        if not guild: return
        await ctx.send(embed = embeds.LocationForm(ctx.prefix, self.bot.user.avatar_url).get())

    @local.command()
    async def create(self, ctx: commands.Context):
        guild = self.db.request(f'SELECT * FROM guilds WHERE guild = "{ctx.guild.id}"')
        if not guild: return
        aid = ctx.author.id
        lvl = utils.get_command('local', guild['id'])['lvl']
        if not self.db.request(f"SELECT * FROM members WHERE mid = {aid} AND guild = {guild['id']} AND admin >= {lvl}"): return await ctx.reply("У вас нет доступа к команде")
        if guild['lid']: return await ctx.send(f"Гильдия `{ctx.guild.name}` уже подключена к одной из локализаций")
        last_local = self.db.request(f"SELECT * FROM guilds WHERE lid > 0 and local_owner = 1", 'fetchall') 
        last_lid = max([i['lid'] for i in last_local]) if last_local else 0
        self.db.request(f"UPDATE guilds SET lid = {last_lid + 1}, local_owner = 1 WHERE id = {guild['id']}")
        await ctx.send(embed = embeds.CreateLocation(last_lid + 1, self.bot.user.avatar_url).get())

    @local.command()
    async def delete(self, ctx: commands.Context):
        guild = self.db.request(f'SELECT * FROM guilds WHERE guild = "{ctx.guild.id}"')
        if not guild: return
        aid = ctx.author.id
        lvl = utils.get_command('local', guild['id'])['lvl']
        if not self.db.request(f"SELECT * FROM members WHERE mid = {aid} AND guild = {guild['id']} AND admin >= {lvl}"): return await ctx.reply("У вас нет доступа к команде")
        if not guild['lid']: return await ctx.send(f"Гильдия `{ctx.guild.name}` не подключена к локализации")
        if guild['local_owner'] == 0: return await ctx.send("Данная гильдия не является главной. Доступ к команде ограничен")
        self.db.request(f"UPDATE guilds SET lid = NULL, local_owner = 0 WHERE id = {guild['id']}")
        self.db.request(f"UPDATE guilds SET lid = NULL WHERE lid = {guild['lid']}")
        await ctx.send(embed = embeds.DeleteLocation(self.bot.user.avatar_url).get())

    @local.command()
    async def add(self, ctx: commands.Context, guild: discord.Guild = None):
        sl = 0
        gd = self.db.request(f'SELECT * FROM guilds WHERE guild = "{ctx.guild.id}"')
        if not gd: return
        aid = ctx.author.id
        lvl = utils.get_command('local', gd['id'])['lvl']
        if not self.db.request(f"SELECT * FROM members WHERE mid = {aid} AND guild = {gd['id']} AND admin >= {lvl}"): return await ctx.reply("У вас нет доступа к команде")
        if not gd['lid']: return await ctx.send(f"Гильдия `{ctx.guild.name}` не подключена к локализации")
        if gd['local_owner'] == 0: return await ctx.send("Данная гильдия не является главной. Доступ к команде ограничен")
        if not guild: return await ctx.send(embed = embeds.LocationError(ctx.author).get())
        lenLocal = len(self.db.request(f"SELECT * FROM guilds WHERE lid = {gd['lid']}", 'fetchall'))
        if lenLocal == 2 and gd['boosts'] == 0: return await ctx.send(f"Вы не можете добавить больше 2-ух гильдий в одну локализацию без PRIME статуса гильдии.\n\nОформить премиум статус -> `{ctx.prefix}boost`")
        if guild.owner.id != ctx.guild.owner.id: return await ctx.send("Вы не являетесь создателем данной гильдии")
        in_db = self.db.request(f"SELECT * FROM guilds WHERE guild = '{guild.id}'")
        if not in_db: await new_guild.NewGuild(self.bot).guild_join(guild)
        in_db = self.db.request(f"SELECT * FROM guilds WHERE guild = '{guild.id}'")
        if in_db['lid']: return await ctx.send("Данная гильдия уже подключена к одной из локализаций")
        self.db.request(f"UPDATE guilds SET lid = {gd['lid']} WHERE guild = '{guild.id}'")
        await ctx.send(embed = embeds.AddGuildToLocation(guild, self.bot.user.avatar_url).get())

    @local.command()
    async def remove(self, ctx: commands.Context, guild: discord.Guild = None):
        gd = self.db.request(f'SELECT * FROM guilds WHERE guild = "{ctx.guild.id}"')
        if not gd: return
        aid = ctx.author.id
        lvl = utils.get_command('local', gd['id'])['lvl']
        if not self.db.request(f"SELECT * FROM members WHERE mid = {aid} AND guild = {gd['id']} AND admin >= {lvl}"): return await ctx.reply("У вас нет доступа к команде")
        if not gd['lid']: return await ctx.send(f"Гильдия `{ctx.guild.name}` не подключена к локализации")
        if gd['local_owner'] == 0: return await ctx.send("Данная гильдия не является главной. Доступ к команде ограничен")
        if not guild: return await ctx.send(embed = embeds.LocationError(ctx.author).get())
        if guild.owner.id != ctx.guild.owner.id: return await ctx.send("Вы не являетесь создателем данной гильдии")
        in_db = self.db.request(f"SELECT * FROM guilds WHERE guild = '{guild.id}'")
        if in_db:
            if not in_db['lid']: return await ctx.send("Данная гильдия не подключена ни к одной из локализаций")
        self.db.request(f"UPDATE guilds SET lid = NULL WHERE guild = '{guild.id}'")
        await ctx.send(embed = embeds.RemoveGuildToLocation(guild, self.bot.user.avatar_url).get())


def setup(client):
    client.add_cog(LocationsCommand(client))