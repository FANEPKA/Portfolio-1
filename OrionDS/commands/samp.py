import discord, config
from discord.ext import commands
from plugins import simplemysql, utils, embeds

class SampCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)


    @commands.command()
    async def samp(self, ctx: commands.Context, host: str = None, port: int = 7777):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        if not host: return await ctx.send(embed = embeds.GetSampForm(ctx.prefix, self.bot.user.avatar_url).get())
        from samp_client.client import SampClient
        with SampClient(address=host, port=port) as client:
            server = client.get_server_info()
            await ctx.send(embed = embeds.SampForm(server, self.bot.user.avatar_url).get())

    @samp.error
    async def error(self, ctx, error):
        if "TypeError: 'NoneType' object is not subscriptable" in str(error): return await ctx.send("Проект с данным IP/Портом не найден")
        if 'Converting to "int" failed for parameter' in str(error): return await ctx.send("IP/Порт должны быть числом")

def setup(client):
    client.add_cog(SampCommand(client))