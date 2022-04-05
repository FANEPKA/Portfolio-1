import discord, config
from discord import client
from discord.ext import commands
from plugins import simplemysql, utils, embeds

class RoleCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)


    @commands.command()
    async def role(self, ctx: commands.Context, group: int = None):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        if not group: return await ctx.send(embed = embeds.RoleForm(ctx.prefix, self.bot.user.avatar_url).get())
        group = self.db.request(f"SELECT * FROM groupRoles WHERE guild = {guild['id']} AND group_id = {group}")
        if not group: return await ctx.send("Группа с данным ID не найдена")
        if len(ctx.message.attachments) == 0: return await ctx.send("Вы не прикрепили вложение к сообщению")
        channel: discord.TextChannel = utils.getLogsChannel(ctx.guild, guild['id'], "role")
        if not channel: return await ctx.send("Ошибка, администратор не создал канал для подачи ролей")
        message: discord.Message = await channel.send(embed = embeds.SendRequestOnRole(f"{ctx.author.mention} подал заявку на роль", self.bot.user.avatar_url, group['name'], ctx.message.attachments[0].url).get())
        await message.add_reaction('✅')
        await message.add_reaction('❌')
        self.db.request(f"INSERT INTO groupRequest(guild, group_id, mid) VALUES({guild['id']}, {group['id']}, '{ctx.author.id}')")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{payload.guild_id}'")
        if not guild: return
        channel = await self.bot.fetch_channel(payload.channel_id)
        if payload.emoji.name == '❌':
            row = self.db.request(f"SELECT *  FROM groupRequest WHERE guild = {guild['id']} AND mid = '{payload.member.id}'")
            if not row: return 
            await payload.member.send("Ваша заявка на роль отказана")
            await channel.send(f"Заявка от участника {payload.member.mention} была отказана")
            return self.db.request(f"DELETE FROM groupRequest WHERE guild = {guild['id']} AND mid = '{payload.member.id}'")

        if payload.emoji.name == '✅':
            row = self.db.request(f"SELECT *  FROM groupRequest WHERE guild = {guild['id']} AND mid = '{payload.member.id}'")
            if not row: return
            await payload.member.send("Ваша заявка на роль одобрена")
            await channel.send(f"Заявка от участника {payload.member.mention} была одобрена")
            role = self.db.request(f"SELECT * FROM groupRoles WHERE id = {row['group_id']}")
            gd: discord.Guild = await self.bot.fetch_guild(payload.guild_id)
            role = gd.get_role(int(role['role']))
            await payload.member.add_roles(role, reason = 'Одобренная заявка на получение роли')
            return self.db.request(f"DELETE FROM groupRequest WHERE guild = {guild['id']} AND mid = '{payload.member.id}'")


def setup(client):
    client.add_cog(RoleCommands(client))