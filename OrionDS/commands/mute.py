import discord, config, time
from discord.ext.commands.core import bot_has_any_role
from discord.ext import commands
from plugins import simplemysql, connect, utils, embeds

class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)
        self.cn = connect.DataBase(self.db)

    @commands.command()
    async def mute(self, ctx: commands.Context, member: discord.Member = None, tm: int = None, *, reason = None):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        aid = ctx.author.id
        lvl = utils.get_command('mute', guild['id'])['lvl']
        if not self.db.request(f"SELECT * FROM members WHERE mid = {aid} AND guild = {guild['id']} AND admin >= {lvl}"): return await ctx.reply("У вас нет доступа к команде")
        if not member: return await ctx.send(embed=embeds.MuteForm(ctx.prefix, self.bot.user.avatar_url).get())
        self.cn.createMember(member.id, guild['id'])
        role = self.cn.getRole(guild['id'], config.MUTE_NAME)
        if self.cn.isMuted(member.id, guild['id'], role['id']): return await ctx.send(embed = embeds.MemberIsMuted(ctx.author).get())
        if member.id == ctx.guild.owner.id: return await ctx.send(embed = embeds.GuildOwnerPH(ctx.author).get())
        if member.id == ctx.author.id: return await ctx.send(embed = embeds.SelfPH(ctx.author).get())
        if member.id == config.ID: return await ctx.send(embed = embeds.BotPH(ctx.author).get())
        m_info = {"lvl": self.cn.member(member.id, guild['id'])['admin'], "top_role": member.top_role}
        a_info = {"lvl": self.cn.member(aid, guild['id'])['admin'], "top_role": ctx.author.top_role}
        info = utils.getMemberIsAdmin(m_info, a_info, role_check=False)
        if info: return await ctx.reply(f"{member.mention} имеет {'роль администратора' if info == 'role' else 'права администратора схожие с вашими или выше'} ")
        if tm < 1 or tm > 1440: return await ctx.send(embed = embeds.SmallTime(ctx.author).get())
        utils.insertAdminHistory(guild['id'], 'mute', str({"admin": ctx.author.id, "member": member.id, "reason": reason}))
        r_mute = f'{reason} | {ctx.author}' if reason else f'не указана | {ctx.author}'
        roleType = await utils.getRoles(ctx.guild, role['role_id'] if role else '0', 'mute')
        await member.add_roles(roleType, reason=r_mute)
        role = self.cn.getRole(guild['id'], config.MUTE_NAME)
        self.db.request(F"INSERT INTO Mutes(mid, guild, role, time) VALUES ('{member.id}', {guild['id']}, {role['id']}, {time.time() + tm*60})")
        a_id = self.db.request(f"SELECT * FROM aHistory", 'fetchall')[-1]
        await ctx.send(embed=embeds.MemberMuted(ctx.author, member, tm, reason, a_id['id'], self.bot.user.avatar_url).get())
        try: await member.send(embed = embeds.MemberMutedLs(ctx.author, member, tm, reason, a_id['id'], self.bot.user.avatar_url).get())
        except: pass

    @mute.error
    async def error(self, ctx, error):
        if str(error) == 'Converting to "int" failed for parameter "tm".': return await ctx.send(embed = embeds.TmError(ctx.author).get())
        if 'not found.' in str(error): return await ctx.send(embed = embeds.MemberNotFound(ctx.author).get())
        print(utils.Colors.red(text=error, text_one="MuteError:"))
        
def setup(client):
    client.add_cog(Mute(client))