import discord, config
from discord.ext import commands
from plugins import simplemysql, connect, utils, embeds

class Unmute(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)
        self.cn = connect.DataBase(self.db)

    @commands.command()
    async def unmute(self, ctx: commands.Context, member: discord.Member = None, tp: str = None):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        aid = ctx.author.id
        lvl = utils.get_command('unmute', guild['id'])['lvl']
        if not self.db.request(f"SELECT * FROM members WHERE mid = {aid} AND guild = {guild['id']} AND admin >= {lvl}"): return await ctx.reply("У вас нет доступа к команде")
        if not member: return await ctx.send(embed=embeds.UnmuteForm(ctx.prefix, self.bot.user.avatar_url).get())
        self.cn.createMember(member.id, guild['id'])
        if tp == 'mute': tp = 'Mute'
        elif tp == 'vmute': tp = 'VMute'
        else: return await ctx.send(embed=embeds.TypeNotFound(ctx.author).get())
        role = self.db.request(f"SELECT * FROM system_roles WHERE guild = {guild['id']} AND name = '{tp}'")
        if not self.cn.isMuted(member.id, guild['id'], role['id']): return await ctx.send(embed = embeds.MemberIsNotMuted(ctx.author).get())
        if member.id == ctx.guild.owner.id: return await ctx.send(embed = embeds.GuildOwnerPH(ctx.author).get())
        if member.id == ctx.author.id: return await ctx.send(embed = embeds.SelfPH(ctx.author).get())
        if member.id == config.ID: return await ctx.send(embed = embeds.BotPH(ctx.author).get())
        self.cn.removeMute(member.id, guild['id'], role['id'])
        role = role['role_id'] if role else '0'
        roleType = await utils.getRoles(ctx.guild, role, tp.lower())
        await member.remove_roles(roleType, reason = f'Амнистия | {ctx.author}')
        utils.insertAdminHistory(guild['id'], 'unmute', str({"admin": ctx.author.id, "member": member.id}))
        await ctx.send(embed=embeds.MuteEndByAdmin(ctx.author, member, self.bot.user.avatar_url, tp).get())
        try: await member.send(embed = embeds.MuteEndByAdminLs(ctx.author, member, self.bot.user.avatar_url, tp).get())
        except: pass
    
    @unmute.error
    async def error(self, ctx, error):
        if 'not found.' in str(error): return await ctx.send(embed = embeds.MemberNotFound(ctx.author).get())
        print(utils.Colors.red(text=error, text_one="UnMuteError:"))

def setup(client):
    client.add_cog(Unmute(client))