import discord, config
from discord import embeds
from discord.ext import commands
from Cybernator import Paginator as pg
from plugins import simplemysql, utils, connect

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)
        self.cn = connect.DataBase(self.db)
        self.bot.remove_command('help')

    @commands.command(usage = lambda ctx: f"{ctx.prefix}help")
    async def help(self, ctx: commands.Context):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        cmds = [embeds.Embed(title = f"Список команд {i} уровня", description = f"{utils.get_commands(i, ctx.prefix)}") for i in range(1, 6)]
        message = await ctx.send(embed = cmds[0])
        page = pg(ctx = self.bot, message=message, embeds=cmds)
        await page.start()
        
        
def setup(client):
    client.add_cog(Help(client))