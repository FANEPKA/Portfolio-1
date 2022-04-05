import discord, config, asyncio
from discord.ext import commands
from plugins import simplemysql, utils, embeds

class AnekdotCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)


    @commands.command(name='анекдот')
    async def _anekdot(self, ctx: commands.Context):
        async with ctx.typing():
            pass
        anekdot = await utils.get_anekdot()
        эмбед = embeds.АнекдотФорма(self.bot.user.avatar_url, anekdot).гет()
        await ctx.send(embed = эмбед)


def setup(client):
    client.add_cog(AnekdotCommand(client))