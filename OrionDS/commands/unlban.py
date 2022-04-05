import discord, config
from discord.ext import commands
from plugins import simplemysql, connect, utils, embeds

class UnlBan(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)
        self.cn = connect.DataBase(self.db)

    @commands.command()
    async def unlban(self, ctx: commands.Context, member: discord.User = None):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        aid = ctx.author.id
        lvl = utils.get_command('unlban', guild['id'])['lvl']
        if not self.db.request(f"SELECT * FROM members WHERE mid = {aid} AND guild = {guild['id']} AND admin >= {lvl}"): return await ctx.reply("У вас нет доступа к команде")
        if not member: return await ctx.send(embed=embeds.UnlbanForm(ctx.prefix, self.bot.user.avatar_url).get())
        isBanned = self.db.request(f"SELECT * FROM bans WHERE data = '{guild['lid']}' AND mid = '{member.id}' AND type = 'lban'")
        if not isBanned: return await ctx.send(embed = embeds.MemberIsNotBanned(ctx.author).get())
        utils.insertAdminHistory(guild['id'], 'unlban', str({"admin": ctx.author.id, "member": member.id, "lid": guild['lid']}))
        r_unban = f'Амнистия | {ctx.author}'
        local = self.db.request(f"SELECT * FROM guilds WHERE lid = {guild['lid']}", 'fetchall')
        [self.bot.get_guild(int(i['guild'])).unban(member, reason = r_unban) for i in local]
        await ctx.send(embed=embeds.BanEndByAdminLocal(ctx.author, member, self.bot.user.avatar_url).get())
        try: await member.send(embed = embeds.BanEndByAdminLocalLs(ctx.author, member, self.bot.user.avatar_url).get())
        except: pass

    @unlban.error
    async def error(self, ctx, error):
        if 'not found.' in str(error): return await ctx.send(embed = embeds.MemberNotFound(ctx.author).get())
        print(utils.Colors.red(text=error, text_one="UnLocalBanError:"))

def setup(client):
    client.add_cog(UnlBan(client))