import discord, config, uptime, pythonping, datetime
from discord import guild
from discord.ext import commands
from plugins import simplemysql, utils

class Canella(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)


    #@commands.command()
    async def canella(self, ctx: commands.Context):
        gc = pythonping.ping("discord.com").rtt_avg_ms
        info = discord.Embed(color=config.COLOR)
        dtime = datetime.datetime.fromtimestamp(uptime.uptime() - 10800).strftime("%d:%H:%M:%S")
        up = utils.getTime(dtime, days=True)
        users = "{:,}".format(len(self.bot.users)).replace(',', '.')
        emojies = "{:,}".format(len(self.bot.emojis)).replace(',', '.')
        info.add_field(name='**Статистика**', value=f'**Гильдий:** {len(self.bot.guilds)}\n'
                                                    f'**Пользователей:** {users}\n'
                                                    f"**Эмоджи:** {emojies}")

        info.add_field(name='**Система**', value=f'**Стартовал:** {up} назад\n'
                                                 f"**Библиотека:** DISCORD.PY (v{discord.__version__})\n"
                                                 f"**Соединение:** {round(gc)} ms")
        info.add_field(name = '**Версия бота: **', value=config.VERSION, inline=False)

        info.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=info)

def setup(client):
    client.add_cog(Canella(client))