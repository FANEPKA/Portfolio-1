import discord, config, datetime, time
from discord import guild
from discord.ext import commands
from plugins import simplemysql, utils

class Clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)


    @commands.command()
    async def clear(self, ctx: commands.Context, amount = 10):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        aid = ctx.author.id
        lvl = utils.get_command('clear', guild['id'])['lvl']
        if not self.db.request(f"SELECT * FROM members WHERE mid = {aid} AND guild = {guild['id']} AND admin >= {lvl}"): return await ctx.reply("У вас нет доступа к команде")
        messages = await ctx.channel.purge(limit = amount + 1)
        embed = discord.Embed(title = f':white_check_mark: Удалено {len(messages) - 1}/{amount}.')
        embed.timestamp = datetime.datetime.fromtimestamp(time.time() - 10800)
        embed.color = config.COLOR
        await ctx.send(embed = embed)

def setup(client):
    client.add_cog(Clear(client))