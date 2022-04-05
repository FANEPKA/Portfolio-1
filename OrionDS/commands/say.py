import discord, config
from discord import guild
from discord.ext import commands
from plugins import simplemysql, utils, embeds

class Say(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)


    @commands.command()
    async def say(self, ctx: commands.Context, *, text = None):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        aid = ctx.author.id
        lvl = utils.get_command('say', guild['id'])['lvl']
        if not self.db.request(f"SELECT * FROM members WHERE mid = {aid} AND guild = {guild['id']} AND admin >= {lvl}"): return await ctx.reply("У вас нет доступа к команде")
        if not text: return await ctx.send(embed=embeds.SayForm(ctx.prefix, self.bot.user.avatar_url).get())
        await ctx.send(text)


def setup(client):
    client.add_cog(Say(client))