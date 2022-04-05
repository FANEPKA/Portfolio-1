from time import time
import discord, config, random
from datetime import datetime
from discord import guild
from discord.ext import commands
from plugins import simplemysql, utils, embeds

class BoostCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)


    @commands.group(aliases = ['boost', 'prime'], invoke_without_command = True)
    async def _boost(self, ctx: commands.Context):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        await ctx.send("```Список методов команды\n\n"
                       f"{ctx.prefix}boost check - проверить статус гильдии\n"
                       f"{ctx.prefix}boost buy - приобрести PRIME статус\n```")

    @_boost.command()
    async def check(self, ctx: commands.Context):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        if guild['boosts'] == 0: return await ctx.send(f"```У гильдии отсутствует PRIME статус. Преобрести можно его командой {ctx.prefix}boost buy```")
        await ctx.send("```У гильдии присутствует PRIME статус\n\n"
                        f"Дата окончания: {datetime.fromtimestamp(guild['end_boost']).strftime('%d.%m.%y %H:%M')}```")

    @_boost.command()
    async def buy(self, ctx: commands.Context):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        payments = self.db.request(f"SELECT * FROM Payments WHERE guild = {guild['id']} AND success = 0", 'fetchall')
        if payments: return await ctx.send("```У вас уже выстален счет. Оплатите его для продолжения```")
        from pyqiwip2p import QiwiP2P
        self.p2p = QiwiP2P(config.QIWI_PRIV_KEY, 99)
        new_bill = self.p2p.bill(bill_id=random.randint(1, 999999999), lifetime=15, comment=f"{guild['id']}")
        self.db.request(f"INSERT INTO Payments(guild, bill, time) VALUES({guild['id']}, '{new_bill.bill_id}', {time()})")
        payments = self.db.request(f"SELECT * FROM Payments", 'result')
        await ctx.send(f'Счет #{payments} выставлен.\nСсылка на оплату: {new_bill.pay_url}\n\nПосле зачисления пропишите `{ctx.prefix}boost payments`')

    @_boost.command()
    async def payments(self, ctx: commands.Context):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        payments = self.db.request(f"SELECT * FROM Payments WHERE guild = {guild['id']} AND success = 0", 'fetchall')
        if not payments: return await ctx.send('```Вы не выставили счет```')
        if self.p2p.check(payments[-1]['bill']).status != 'PAID': return await ctx.send("Вы не оплатили счет")
        self.db.request(f"UPDATE guilds SET boosts = 1, end_boost = {guild['end_boost'] + (time() + 2591999)} WHERE id = {guild['id']}")
        self.db.request(f"UPDATE Payments SET success = 1 WHERE id = {payments[-1]['id']}")
        await ctx.send("```Вы успешно оплатили счет! PRIME статус получен```")

def setup(client):
    client.add_cog(BoostCommands(client))