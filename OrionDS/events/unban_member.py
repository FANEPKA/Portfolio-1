import time
import discord, config
from discord.message import Message
from discord.ext import commands
from plugins import simplemysql, embeds

class LogsUnbanMember(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        gd = self.db.request(f'SELECT * FROM guilds WHERE guild = "{guild.id}"')
        if not gd: return
        self.db.request(f"DELETE FROM bans WHERE guild = {gd['id']} AND mid = '{user.id}'")
        banLogs = self.db.request(f"SELECT * FROM channels WHERE guild = {gd['id']} AND type = 'bans_logs'")
        if not banLogs: return
        channel: discord.TextChannel = guild.get_channel(int(banLogs['channel']))
        await channel.send(embed=embeds.LogsUnban(user, self.bot.user.avatar_url).get())
        #try: await user.send(embed = embeds.MemberBannedLs(ban.user, user, ban.reason, -1, self.bot.user.avatar_url, 0, guild))
        #except: pass


def setup(client):
    client.add_cog(LogsUnbanMember(client))