import discord, config
from discord.ext import commands
from plugins import simplemysql

class Presence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=discord.Game(name = 'Orion Role Play'))

def setup(client):
    client.add_cog(Presence(client))