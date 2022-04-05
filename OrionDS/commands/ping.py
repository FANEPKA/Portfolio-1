import discord, config, asyncio
from discord.ext import commands
from collections import Counter
from plugins import simplemysql, utils, embeds

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)


    @commands.command()
    async def ping(self, ctx: commands.Context):
        await ctx.reply("ПОНГ...")
        
        
        """
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = {ctx.guild.id}")
        result = self.db.request(f"SELECT * FROM BotPings WHERE mid = {ctx.author.id} AND guild = {guild['id']}", 'result')
        if result > 2:
            self.db.request(f"DELETE FROM BotPings WHERE mid = {ctx.author.id} AND guild = {guild['id']}")
            await ctx.reply("Да ты надоел")
            [await ctx.send(ctx.author.mention) for i in range(0, 4)]
            await asyncio.sleep(1.5)
            return await ctx.send("Понравилось?")
        await ctx.reply("ПОНГ...")
        self.db.request(f"INSERT INTO BotPings(guild, mid) VALUES({guild['id']}, '{ctx.author.id}')")
        """

def setup(client):
    client.add_cog(Ping(client))