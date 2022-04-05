import asyncio
import discord, config, time
from discord.ext import commands
from plugins import simplemysql, embeds, connect

class AntiSlivSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)
        self.cn = connect.DataBase(self.db)


    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, member: discord.Member):
        gd = self.db.request(f"SELECT * FROM guilds WHERE guild = '{guild.id}'")
        time.sleep(1)
        bans = await guild.audit_logs(limit = 1, action=discord.AuditLogAction.ban, oldest_first = False).flatten()
        if guild.owner.id == bans[0].user.id or bans[0].user.id == config.ID: return
        row = self.db.request(f"SELECT * FROM anSys WHERE guild = {gd['id']} AND mid = '{bans[0].user.id}' AND type = 'ban'", 'fetchall')
        if not row: return self.db.request(f"INSERT INTO anSys(guild, mid, type, end_time) VALUES({gd['id']}, '{bans[0].user.id}', 'ban', {time.time() + config.END_TIME_FOR_BANS})")
        if len(row) < config.IF_BANS: return self.db.request(f"INSERT INTO anSys(guild, mid, type, end_time) VALUES({gd['id']}, '{bans[0].user.id}', 'ban', {time.time() + config.END_TIME_FOR_BANS})")
        try:
            await bans[0].user.kick(reason = 'подозрение в сливе гильдии')
            await bans[0].user.send(f'Вы были исключены с сервера `{guild.name}` по подозрению в сливе гильдии')
        except: pass
    
    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, member: discord.Member):
        gd = self.db.request(f"SELECT * FROM guilds WHERE guild = '{guild.id}'")
        await asyncio.sleep(1)
        bans = await guild.audit_logs(limit = 1, action=discord.AuditLogAction.unban, oldest_first = False).flatten()
        if guild.owner.id == bans[0].user.id or bans[0].user.id == config.ID: return
        row = self.db.request(f"SELECT * FROM anSys WHERE guild = {gd['id']} AND mid = '{bans[0].user.id}' AND type = 'ban'", 'fetchall')
        if not row: return self.db.request(f"INSERT INTO anSys(guild, mid, type, end_time) VALUES({gd['id']}, '{bans[0].user.id}', 'ban', {time.time() + config.END_TIME_FOR_BANS})")
        if len(row) < config.IF_BANS: return self.db.request(f"INSERT INTO anSys(guild, mid, type, end_time) VALUES({gd['id']}, '{bans[0].user.id}', 'ban', {time.time() + config.END_TIME_FOR_BANS})")
        try:
            await bans[0].user.kick(reason = 'подозрение в сливе гильдии')
            await bans[0].user.send(f'Вы были исключены с сервера `{guild.name}` по подозрению в сливе гильдии')
        except: pass

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if after.roles == before.roles: return
        guild = before.guild
        gd = self.db.request(f"SELECT * FROM guilds WHERE guild = '{guild.id}'")
        await asyncio.sleep(1)
        bans = await guild.audit_logs(limit = 1, action=discord.AuditLogAction.member_role_update, oldest_first = False).flatten()
        if guild.owner.id == bans[0].user.id or bans[0].user.id == config.ID: return
        row = self.db.request(f"SELECT * FROM anSys WHERE guild = {gd['id']} AND mid = '{bans[0].user.id}' AND type = 'role'", 'fetchall')
        if not row: return self.db.request(f"INSERT INTO anSys(guild, mid, type, end_time) VALUES({gd['id']}, '{bans[0].user.id}', 'role', {time.time() + config.END_TIME_FOR_ROLES})")
        if len(row) < config.IF_ROLES: return self.db.request(f"INSERT INTO anSys(guild, mid, type, end_time) VALUES({gd['id']}, '{bans[0].user.id}', 'role', {time.time() + config.END_TIME_FOR_ROLES})")
        try:
            await bans[0].user.kick(reason = 'подозрение в сливе гильдии')
            await bans[0].user.send(f'Вы были исключены с сервера `{guild.name}` по подозрению в сливе гильдии')
        except: pass

    @commands.Cog.listener()
    async def on_error(self, event_method, *args, **kwargs):
        print(event_method)
        print(args)
        print(kwargs)

def setup(client):
    client.add_cog(AntiSlivSystem(client))