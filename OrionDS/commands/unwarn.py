import discord, config, time
from discord.ext import commands
from plugins import simplemysql, connect, utils, embeds

class UnWarn(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)
        self.cn = connect.DataBase(self.db)

    @commands.command()
    async def unwarn(self, ctx: commands.Context, member: discord.Member = None, warns: commands.Greedy[int] = 1, *, reason = None):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        aid = ctx.author.id
        warns = warns[0] if type(warns) is list else warns
        if type(warns) == str: warns, reason = 1, f'{warns} {reason}' if reason else warns
        lvl = utils.get_command('warn', guild['id'])['lvl']
        if not self.db.request(f"SELECT * FROM members WHERE mid = {aid} AND guild = {guild['id']} AND admin >= {lvl}"): return await ctx.reply("У вас нет доступа к команде")
        if not member: return await ctx.send(embed=embeds.UnWarnForm(ctx.prefix, self.bot.user.avatar_url).get())
        self.cn.createMember(member.id, guild['id'])
        if member.id == ctx.guild.owner.id: return await ctx.send(embed = embeds.GuildOwnerPH(ctx.author).get())
        if member.id == ctx.author.id: return await ctx.send(embed = embeds.SelfPH(ctx.author).get())
        if member.id == config.ID: return await ctx.send(embed = embeds.BotPH(ctx.author).get())
        mem = self.cn.member(member.id, guild['id'])
        if mem['admin'] >= self.cn.member(aid, guild['id'])['admin']: return await ctx.reply(f"{member.display_name} ({member.mention}) имеет права администратора схожие с вашими")
        if warns > 3 or mem['warns'] - warns < 0: return await ctx.send(embed = embeds.SmallInt(ctx.author, b = 3 - mem['warns']).get())
        utils.insertAdminHistory(guild['id'], 'unwarn', str({"admin": ctx.author.id, "member": member.id, "reason": reason}))
        a_id = self.db.request(f"SELECT * FROM aHistory", 'fetchall')[-1]
        self.cn.updateWarns(member.id, guild['id'], mem['warns'] - warns)
        await ctx.send(embed=embeds.MemberUnWarned(ctx.author, member, warns, reason, a_id['id'], self.bot.user.avatar_url).get())
        try: await member.send(embed = embeds.MemberUnWarnedLs(ctx.author, member, warns, reason, a_id['id'], self.bot.user.avatar_url).get())
        except: pass

    @unwarn.error
    async def error(self, ctx, error):
        if str(error) == 'Converting to "int" failed for parameter "warns".': return await ctx.send(embed = embeds.TmError(ctx.author).get())
        if 'not found.' in str(error): return await ctx.send(embed = embeds.MemberNotFound(ctx.author).get())
        print(error)
def setup(client):
    client.add_cog(UnWarn(client))