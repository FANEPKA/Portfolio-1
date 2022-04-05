import discord, config, time
from discord.ext.commands import bot
from discord.ext import commands
from plugins import simplemysql, embeds, connect, utils

class ErroLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)
        self.cn = connect.DataBase(self.db)


    #@commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        print(f'!!!  NEW ERROR  !!!')
        print(f"Message: {error}")
        print(f"Guild: {ctx.guild} (ID: {ctx.guild.id})")
        print(f"TIME: {time.strftime('%d.%m.%y %H:%M')}\n\n")

def setup(client):
    client.add_cog(ErroLogs(client))