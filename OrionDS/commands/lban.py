import time
import discord, config
from discord.ext import commands
from plugins import simplemysql, connect, utils, embeds

class LBan(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)
        self.cn = connect.DataBase(self.db)

    @commands.command()
    async def lban(self, ctx: commands.Context, member: discord.User = None, tm: commands.Greedy[int] = 0, *, reason = None):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        aid = ctx.author.id
        tm = tm[0] if type(tm) is list else tm
        if type(tm) == str: tm, reason = 0, f'{tm} {reason}' if reason else tm
        lvl = utils.get_command('lban', guild['id'])['lvl']
        if not self.db.request(f"SELECT * FROM members WHERE mid = {aid} AND guild = {guild['id']} AND admin >= {lvl}"): return await ctx.reply("У вас нет доступа к команде")
        if not guild['lid']: return await ctx.send("У гильдии не включена система локализаций")
        if not member: return await ctx.send(embed=embeds.LbanForm(ctx.prefix, self.bot.user.avatar_url).get())
        self.cn.createMember(member.id, guild['id'])
        in_guild = ctx.guild.get_member(member.id)
        member = in_guild if in_guild else member
        if member.id == ctx.guild.owner.id: return await ctx.send(embed = embeds.GuildOwnerPH(ctx.author).get())
        if member.id == ctx.author.id: return await ctx.send(embed = embeds.SelfPH(ctx.author).get())
        if member.id == config.ID: return await ctx.send(embed = embeds.BotPH(ctx.author).get())
        m_info = {"lvl": self.cn.member(member.id, guild['id'])['admin'], "top_role": member.top_role if in_guild else None}
        a_info = {"lvl": self.cn.member(aid, guild['id'])['admin'], "top_role": ctx.author.top_role}
        info = utils.getMemberIsAdmin(m_info, a_info)
        if info: return await ctx.reply(f"{member.mention} имеет {'роль администратора' if info == 'role' else 'права администратора схожие с вашими или выше'} ")
        if self.db.request(f"SELECT * FROM bans WHERE data = '{guild['lid']}' AND mid = '{member.id}' AND type = 'lban'"): return await ctx.send(embed = embeds.MemberIsBanned(ctx.author).get())
        if tm < 0 or tm > 30: return await ctx.send(embed = embeds.SmallTime(ctx.author, 0, 30).get())
        self.db.request(f"INSERT INTO bans(guild, mid, type, time, admin, reason, data) VALUES({guild['id']}, '{member.id}', 'lban', {time.time() + tm * 3600 * 24 if tm > 0 else 0}, '{ctx.author.id}', '{reason}', {guild['lid']})")
        utils.insertAdminHistory(guild['id'], 'lban', str({"admin": ctx.author.id, "member": member.id, "lid": guild['lid'], "time": tm, "reason": reason}))
        r_ban = f'{reason} | {ctx.author}' if reason else f'не указана | {ctx.author}'
        local = self.db.request(f"SELECT * FROM guilds WHERE lid = {guild['lid']}", 'fetchall')
        [self.bot.get_guild(int(i['guild'])).ban(member, reason = r_ban) for i in local]
        a_id = self.db.request(f"SELECT * FROM aHistory", 'fetchall')[-1]
        await ctx.send(embed=embeds.MemberBannedLocal(ctx.author, member, reason, a_id['id'], self.bot.user.avatar_url, tm).get())
        try: await member.send(embed = embeds.MemberBannedLocalLs().get(ctx.author, member, reason, a_id['id'], self.bot.user.avatar_url, tm))
        except: pass

    @lban.error
    async def error(self, ctx, error):
        if 'not found.' in str(error): return await ctx.send(embed = embeds.MemberNotFound(ctx.author).get())
        print(utils.Colors.red(text=error, text_one="LocalBanError:"))

def setup(client):
    client.add_cog(LBan(client))