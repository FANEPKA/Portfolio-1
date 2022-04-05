import asyncio
import discord, config
from discord.ext import commands
from plugins import simplemysql, embeds, connect, utils

class LogsUpdateMembersNick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)
        self.cn = connect.DataBase(self.db)


    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        guild = self.db.request(f'SELECT * FROM guilds WHERE guild = "{before.guild.id}"')
        if not guild: return
        channel: discord.TextChannel = utils.getLogsChannel(before.guild, guild['id'], 'nicks')
        if not channel: return
        if before.nick == after.nick: return
        await asyncio.sleep(1)
        logs = (await before.guild.audit_logs(limit = 1, action=discord.AuditLogAction.member_update, oldest_first = False).flatten())[0]
        text = f"Модератор {logs.user.mention} изменил ник-нейм участнику {before.mention}" if logs.user.id != before.id else f"Участник {before.mention} изменил себе ник-нейм"
        await channel.send(embed = embeds.LogsNick(text, before.nick, after.nick, self.bot.user.avatar_url).get())
        


def setup(client):
    client.add_cog(LogsUpdateMembersNick(client))