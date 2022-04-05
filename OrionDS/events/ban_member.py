import discord, config, time, asyncio
from discord.message import Message
from discord.ext import commands
from plugins import simplemysql, embeds

class LogsBanMember(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        gd = self.db.request(f'SELECT * FROM guilds WHERE guild = "{guild.id}"')
        if not gd: return
        await asyncio.sleep(1)
        ban = (await guild.audit_logs(limit = 1, action=discord.AuditLogAction.ban, oldest_first = False).flatten())[0]
        if ban.user.id == config.ID: return
        banInfo = self.db.request(f"SELECT * FROM bans WHERE guild = {gd['id']} AND mid = '{user.id}'")
        if not banInfo: self.db.request(f"INSERT INTO bans(guild, mid, type, time, admin, reason) VALUES({gd['id']}, '{user.id}', 'ban', 0, '{ban.user.id}', '{ban.reason}')")
        banLogs = self.db.request(f"SELECT * FROM channels WHERE guild = {gd['id']} AND type = 'bans_logs'")
        if not banLogs: return
        channel: discord.TextChannel = guild.get_channel(int(banLogs['channel']))
        await channel.send(embed=embeds.LogsBan(user, self.bot.user.avatar_url).get())
        try: await user.send(embed = embeds.MemberBannedLs(ban.user, user, ban.reason, -1, self.bot.user.avatar_url, 0, guild))
        except: pass


def setup(client):
    client.add_cog(LogsBanMember(client))