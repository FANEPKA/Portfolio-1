import discord, config
from discord.ext import commands
from plugins import simplemysql, utils, embeds

class ReferenceCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)


    @commands.command('справка')
    async def _reference(self, ctx: commands.Context, command: str = None):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        if not command: return await ctx.send(embed = embeds.ReferenceForm(ctx.prefix, self.bot.user.avatar_url).get())
        try: command_info = utils.get_command(command, guild['id'])
        except IndexError: return await ctx.send(embed = embeds.ReferenceError(self.bot.user.avatar_url).get())
        await ctx.send(embed = embeds.ReferenceInfo(command, command_info, guild['id'], self.bot.user.avatar_url).get())

def setup(client):
    client.add_cog(ReferenceCommand(client))