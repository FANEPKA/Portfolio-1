import discord, config
from discord.ext import commands
from plugins import simplemysql, utils

class RemoveGuild(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)

    @commands.Cog.listener('on_guild_remove')
    async def guild_remove(self, guild: discord.Guild):
        gd = self.db.request(f"SELECT * FROM guilds WHERE guild = '{guild.id}'")
        if not gd: return
        self.db.request(f"DELETE FROM guilds WHERE id = {gd['id']}")
        self.db.request(f"DELETE FROM members WHERE guild = {gd['id']}")
        self.db.request(f"DELETE FROM Mutes WHERE guild = {gd['id']}")
        self.db.request(f"DELETE FROM lvlNames WHERE guild = {gd['id']}")
        self.db.request(f"DELETE FROM system_roles WHERE guild = {gd['id']}")


def setup(client):
    client.add_cog(RemoveGuild(client))