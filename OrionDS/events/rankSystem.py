import discord, config
from discord.message import Message
from discord.ext import commands
from plugins import simplemysql, embeds, connect

class RankSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)
        self.cn = connect.DataBase(self.db)


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild: return
        guild = self.db.request(f'SELECT * FROM guilds WHERE guild = "{message.guild.id}"')
        if not guild: return
        member = self.cn.member(message.author.id, guild['id'])
        if not member: return
        if member['xp'] == member['lvl']*100 + config.XP_FOR_UP_RANK:
            member['xp'] = 0
            self.cn.updateRankSystem(member['mid'], member['guild'], 'lvl', member['lvl'] + 1)
        self.db.request(f"UPDATE members SET xp = {member['xp'] + config.XP_PER_MESSAGE} WHERE mid = '{message.author.id}' AND guild = {guild['id']}")
        
        
def setup(client):
    client.add_cog(RankSystem(client))