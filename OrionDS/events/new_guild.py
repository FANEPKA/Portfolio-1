import discord, config
from discord.ext import commands
from plugins import simplemysql, utils, embeds

class NewGuild(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)

    @commands.Cog.listener('on_message')
    async def register_new_guild(self, message: discord.Message):
        if not message.guild: return
        if self.db.request(f"SELECT * FROM guilds WHERE guild = '{message.guild.id}'"): return 
        if config.BETA and message.guild.id not in config.GUILDS: return
        self.db.request(f"INSERT INTO guilds(guild, owner) VALUES('{message.guild.id}', '{message.guild.owner.id}')")
        gid = self.db.request(f"SELECT * FROM guilds WHERE guild = '{message.guild.id}'")['id']
        role_id = [i.id for i in message.guild.roles if i.name == 'CanellaBot']
        self.db.request(f"INSERT INTO system_roles(name, guild, role_id) VALUES('Canella', {gid}, {role_id[0]})")
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{message.guild.id}'")
        self.db.request(f"INSERT INTO members(mid, guild, admin) VALUES('{message.author.id}', {guild['id']}, 5)")
        await utils.createMuteRoles(message.guild)
        if message.guild.system_channel: return await message.guild.system_channel.send(embed = embeds.WelcomeCanella(self.bot.user.avatar_url).get())
        channels = [i for i in message.guild.channels if i.type == discord.ChannelType.text]
        if len(channels) == 0: return
        await channels[0].send(embed = embeds.WelcomeCanella(self.bot.user.avatar_url).get()) 


    @commands.Cog.listener('on_guild_join')
    async def guild_join(self, guild: discord.Guild):
        if self.db.request(f"SELECT * FROM guilds WHERE guild = '{guild.id}'"): return
        if config.BETA and guild.id not in config.GUILDS: return 
        self.db.request(f"INSERT INTO guilds(guild, owner) VALUES('{guild.id}', '{guild.owner.id}')")
        gid = self.db.request(f"SELECT * FROM guilds WHERE guild = '{guild.id}'")['id']
        role_id = [i.id for i in guild.roles if i.name == 'CanellaBot']
        self.db.request(f"INSERT INTO system_roles(name, guild, role_id) VALUES('Canella', {gid}, {role_id[0]})")
        g_info = self.db.request(f"SELECT * FROM guilds WHERE guild = '{guild.id}'")
        self.db.request(f"INSERT INTO members(mid, guild, admin) VALUES('{guild.owner.id}', {g_info['id']}, 5)")
        await utils.createMuteRoles(guild)
        if guild.system_channel: return await guild.system_channel.send(embed = embeds.WelcomeCanella(self.bot.user.avatar_url).get())
        channels = [i for i in guild.channels if i.type == discord.ChannelType.text]
        if len(channels) == 0: return
        await channels[0].send(embed = embeds.WelcomeCanella(self.bot.user.avatar_url).get()) 

def setup(client):
    client.add_cog(NewGuild(client))