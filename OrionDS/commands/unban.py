import discord, config
from discord.ext import commands
from plugins import simplemysql, connect, utils, embeds

class UnBan(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)
        self.cn = connect.DataBase(self.db)

    @commands.command()
    async def unban(self, ctx: commands.Context, member: discord.User = None):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        aid = ctx.author.id
        lvl = utils.get_command('unban', guild['id'])['lvl']
        if not self.db.request(f"SELECT * FROM members WHERE mid = {aid} AND guild = {guild['id']} AND admin >= {lvl}"): return await ctx.reply("У вас нет доступа к команде")
        if not member: return await ctx.send(embed=embeds.UnbanForm(ctx.prefix, self.bot.user.avatar_url).get())
        banList = [i for i in await ctx.guild.bans() if i.user.id == member.id]
        if banList == []: return await ctx.send(embed = embeds.MemberIsNotBanned(ctx.author).get())
        utils.insertAdminHistory(guild['id'], 'unban', str({"admin": ctx.author.id, "member": member.id}))
        r_unban = f'Амнистия | {ctx.author}'
        await ctx.guild.unban(member, reason = r_unban)
        await ctx.send(embed=embeds.BanEndByAdmin(ctx.author, member, self.bot.user.avatar_url).get())
        try: await member.send(embed = embeds.BanEndByAdminLs(ctx.author, member, self.bot.user.avatar_url).get())
        except: pass

    @unban.error
    async def error(self, ctx, error):
        if 'not found.' in str(error): return await ctx.send(embed = embeds.MemberNotFound(ctx.author).get())
        print(utils.Colors.red(text=error, text_one="UnBanError:"))

def setup(client):
    client.add_cog(UnBan(client))