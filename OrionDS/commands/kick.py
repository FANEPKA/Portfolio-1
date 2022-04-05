import discord, config
from discord.ext import commands
from plugins import simplemysql, connect, utils, embeds

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)
        self.cn = connect.DataBase(self.db)

    @commands.command()
    async def kick(self, ctx: commands.Context, member: discord.Member = None, *, reason = None):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        aid = ctx.author.id
        lvl = utils.get_command('kick', guild['id'])['lvl']
        if not self.db.request(f"SELECT * FROM members WHERE mid = {aid} AND guild = {guild['id']} AND admin >= {lvl}"): return await ctx.reply("У вас нет доступа к команде")
        if not member: return await ctx.send(embed=embeds.KickForm(ctx.prefix, self.bot.user.avatar_url).get())
        self.cn.createMember(member.id, guild['id'])
        if member.id == ctx.guild.owner.id: return await ctx.send(embed = embeds.GuildOwnerPH(ctx.author).get())
        if member.id == ctx.author.id: return await ctx.send(embed = embeds.SelfPH(ctx.author).get())
        if member.id == config.ID: return await ctx.send(embed = embeds.BotPH(ctx.author).get())
        m_info = {"lvl": self.cn.member(member.id, guild['id'])['admin'], "top_role": member.top_role}
        a_info = {"lvl": self.cn.member(aid, guild['id'])['admin'], "top_role": ctx.author.top_role}
        info = utils.getMemberIsAdmin(m_info, a_info, role_check = False)
        if info: return await ctx.reply(f"{member.mention} имеет {'роль администратора' if info == 'role' else 'права администратора схожие с вашими или выше'} ")
        utils.insertAdminHistory(guild['id'], 'kick', str({"admin": ctx.author.id, "member": member.id, "reason": reason}))
        r_kick = f'{reason} | {ctx.author}' if reason else f'не указана | {ctx.author}'
        await member.kick(reason=r_kick)
        a_id = self.db.request(f"SELECT * FROM aHistory", 'fetchall')[-1]
        await ctx.send(embed=embeds.MemberKicked(ctx.author, member, reason, a_id['id'], self.bot.user.avatar_url).get())
        try: await member.send(embed = embeds.MemberKickedLs(ctx.author, member, reason, a_id['id'], self.bot.user.avatar_url).get())
        except: pass

    @kick.error
    async def error(self, ctx, error):
        if 'not found.' in str(error): return await ctx.send(embed = embeds.MemberNotFound(ctx.author).get())
        print(utils.Colors.red(text=error, text_one="KickError:"))

def setup(client):
    client.add_cog(Kick(client))