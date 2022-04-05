from warnings import resetwarnings
import discord, config, os
from discord.ext.commands.core import command
from discord.ext import commands
from plugins import simplemysql, utils

class System(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)


    @commands.command()
    async def cmds(self, ctx: commands.Context, tp: str = 'reload', command: str = None):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        lvl = utils.get_command('cmds', guild['id'])['lvl']
        if not self.db.request(f"SELECT * FROM members WHERE mid = {ctx.author.id} AND guild = {guild['id']} AND admin >= {lvl}"): return
        if command:
            if tp == 'load':
                self.bot.load_extension(f"commands.{command}")
                return await ctx.send(f'Команда: `{command}` загружена на сервер')
            if tp == 'unload':
                self.bot.unload_extension(f"commands.{command}")
                return await ctx.send(f'Команда: `{command}` разгружена с сервера')

            if tp == 'reload':
                self.bot.unload_extension(f"commands.{command}")
                self.bot.load_extension(f"commands.{command}")
                return await ctx.send(f'Команда: `{command}` перезагружена')
        for filename in os.listdir('./commands'):
            if filename.endswith('.py'):
                try: 
                    self.bot.unload_extension(f"commands.{filename[:-3]}")
                    self.bot.load_extension(f"commands.{filename[:-3]}")
                except Exception as e: print(f"Error: {e}")
        
        await ctx.send('Команды перезагружены')

    @commands.command()
    async def events(self, ctx: commands.Context, tp: str = 'reload', event: str = None):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        lvl = utils.get_command('events', guild['id'])['lvl']
        if not self.db.request(f"SELECT * FROM members WHERE mid = {ctx.author.id} AND guild = {guild['id']} AND admin >= {lvl}"): return
        if event:
            if tp == 'load':
                self.bot.load_extension(f"events.{event}")
                return await ctx.send(f'Команда: `{event}` загружена на сервер')
            if tp == 'unload':
                self.bot.unload_extension(f"events.{event}")
                return await ctx.send(f'Команда: `{event}` разгружена с сервера')

            if tp == 'reload':
                self.bot.unload_extension(f"events.{event}")
                self.bot.load_extension(f"events.{event}")
                return await ctx.send(f'Команда: `{event}` перезагружена')
        for filename in os.listdir('./events'):
            if filename.endswith('.py'):
                try: 
                    self.bot.unload_extension(f"events.{filename[:-3]}")
                    self.bot.load_extension(f"events.{filename[:-3]}")
                except Exception as e: print(f"Error: {e}")
        
        await ctx.send('События перезагружены')

    @commands.command()
    async def left(self, ctx: commands.Context, guild: discord.Guild):
        gd = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        await ctx.send(gd)
        await ctx.send(guild)
        response = await guild.leave()
        print(response)
        await ctx.send("Бот покинул гильдию")


def setup(client):
    client.add_cog(System(client))