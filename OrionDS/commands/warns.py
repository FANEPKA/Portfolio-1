import discord, config
from discord import guild
from discord.ext import commands
from plugins import simplemysql, utils, embeds

class WarnsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)


    @commands.command()
    async def warns(self, ctx: commands.Context):
        await ctx.reply("ПОНГ...")


def setup(client):
    client.add_cog(WarnsCommand(client))