import discord, config, time
from datetime import datetime
from discord import guild
from discord.ext import commands
from plugins import simplemysql, utils, embeds, connect

class Get(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)
        self.cn = connect.DataBase(self.db)

    @commands.command()
    async def get(self, ctx: commands.Context, member: discord.Member = None):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        aid = ctx.author.id
        lvl = utils.get_command('get', guild['id'])['lvl']
        if not self.db.request(f"SELECT * FROM members WHERE mid = {aid} AND guild = {guild['id']} AND admin >= {lvl}"): return await ctx.reply("У вас нет доступа к команде")
        if not member: return await ctx.send(embed=embeds.GetForm(ctx.prefix, self.bot.user.avatar_url).get())
        self.cn.createMember(member.id, guild['id'])
        user = self.cn.member(member.id, guild['id'])
        adm = '\n**Роль:** {}'.format(utils.getLvlName(guild['id'], user['admin'])) if user['admin'] > 0 else ''
        roles = [f'{i.mention}' for i in member.roles]
        roles.reverse()
        embed = discord.Embed(title=f'Информация об "{member.display_name}"', color=config.COLOR)
        embed.description=(f"**ID:** {member.id}\n"
                            f"**Логин:** {member}\n"
                            f"**Ник:** {member.display_name}"
                            f"{await utils.getActivity(member.activities)}"
                            f"\n**Статус:** {utils.getStatus(str(member.status))}"
                            f"{await utils.getUserStatus(member.activity)}"
                            f"\n**Роли участника:** {' '.join(roles)}"
                            f"{adm}"
                            f"\n**Дата присоединения к серверу:** {member.joined_at.strftime('%d.%m.%y %H:%M')}\n"
                            f"**Дата регистрации аккаунта:** {member.created_at.strftime('%d.%m.%y %H:%M')}\n"
                            f"**Предупреждений:** {user['warns']}/3\n")
        embed.timestamp = datetime.fromtimestamp(time.time() - 10800)
        embed.set_thumbnail(url=member.avatar_url)
        await ctx.send(embed = embed)

    @get.error
    async def error(self, ctx, error):
        if 'not found.' in str(error): return await ctx.send(embed = embeds.MemberNotFound(ctx.author).get())
        print(utils.Colors.red(text=error, text_one="GetError:"))
    
def setup(client):
    client.add_cog(Get(client))