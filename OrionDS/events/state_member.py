import discord, config
from discord.ext import commands
from plugins import simplemysql, embeds, connect

class StateMember(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)
        self.cn = connect.DataBase(self.db)


    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = self.db.request(f'SELECT * FROM guilds WHERE guild = "{member.guild.id}"')
        if not guild: return
        logs_channel = self.db.request(f"SELECT * FROM channels WHERE guild = {guild['id']} AND type = 'welcome_logs'")
        mdb = self.cn.member(member.id, guild['id'])
        if not mdb: self.cn.createMember(member.id, guild['id'])
        if not guild['greeting']: return
        getGreeting = self.db.request(f"SELECT * FROM Greetings WHERE id = {guild['greeting']}")
        try: await member.send(embed = embeds.WelcomeMember(member, getGreeting['text']).get())
        except: pass
        if not logs_channel: return
        channel: discord.TextChannel = member.guild.get_channel(int(logs_channel['channel']))
        await channel.send(embed = embeds.WelcomeMember(member, getGreeting['text']).get())

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild = self.db.request(f'SELECT * FROM guilds WHERE guild = "{member.guild.id}"')
        if not guild: return
        mdb = self.cn.member(member.id, guild['id'])
        if not mdb: return
        self.db.request(f"DELETE FROM members WHERE id = {mdb['id']}")

    
def setup(client):
    client.add_cog(StateMember(client))