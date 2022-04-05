import discord, config
#import sdc_api_py
from discord.message import Message
from discord.ext import commands
from plugins import simplemysql, embeds, connect

class BotSDC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.SDC_TOKEN = 'token'

    @commands.Cog.listener()
    async def on_ready(self):
        pass
        #bots = sdc_api_py.Bots(self.bot, self.SDC_TOKEN, False)
        #bots.create_loop()  
        


def setup(client):
    client.add_cog(BotSDC(client))