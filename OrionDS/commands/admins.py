import discord, config
from discord.colour import Color
from discord import guild
from discord.ext import commands
from plugins import simplemysql, utils
from Cybernator import Paginator as pg

class Admins(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)


    @commands.command()
    async def admins(self, ctx: commands.Context, ls: int = None):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        aid = ctx.author.id
        lvl = utils.get_command('admins', guild['id'])['lvl']
        if not self.db.request(f"SELECT * FROM members WHERE mid = {aid} AND guild = {guild['id']} AND admin >= {lvl}"): return await ctx.reply("У вас нет доступа к команде")
        admins = self.db.request(f"SELECT * FROM members WHERE admin > 0 and guild = {guild['id']}", 'fetchall')
        gid = guild['id']
        guild = ctx.guild
        embed = discord.Embed(title = ':rosette: Список администрации гильдии', color = config.COLOR)
        embed.add_field(name = utils.getLvlName(gid, 5), value=utils.getAdmin(guild, admins, 5), inline=False)
        embed.add_field(name = utils.getLvlName(gid, 4), value=utils.getAdmin(guild, admins, 4), inline=False)
        embed.add_field(name = utils.getLvlName(gid, 3), value=utils.getAdmin(guild, admins, 3), inline=False)
        embed.add_field(name = utils.getLvlName(gid, 2), value=utils.getAdmin(guild, admins, 2), inline=False)
        embed.add_field(name = utils.getLvlName(gid, 1), value=utils.getAdmin(guild, admins, 1), inline=False)
        embed.set_footer(text = f'Количество администрации: {len(admins)}', icon_url=self.bot.user.avatar_url)
        embed.set_thumbnail(url = 'https://image.flaticon.com/icons/png/512/1794/1794749.png')
        await ctx.send(embed=embed)
def setup(client):
    client.add_cog(Admins(client))