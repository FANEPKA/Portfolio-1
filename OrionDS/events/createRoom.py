import discord, config
from discord.ext import commands
from plugins import simplemysql, embeds, connect, utils

class CreateRommSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)
        self.cn = connect.DataBase(self.db)

    
    @commands.group(invoke_without_command = True)
    async def войс(self, ctx: commands.Context):
        guild = self.db.request(f'SELECT * FROM guilds WHERE guild = "{ctx.guild.id}"')
        if not guild: return
        lvl = utils.get_command('войс', guild['id'])['lvl']
        aid = ctx.author.id
        if not self.db.request(f"SELECT * FROM members WHERE mid = {aid} AND guild = {guild['id']} AND admin >= {lvl}"): return await ctx.reply("У вас нет доступа к команде")
        await ctx.send(embed = embeds.VoiceForm(ctx.prefix, self.bot.user.avatar_url).get())

    @войс.command()
    async def вкл(self, ctx: commands.Context):
        guild = self.db.request(f'SELECT * FROM guilds WHERE guild = "{ctx.guild.id}"')
        if not guild: return
        lvl = utils.get_command('войс', guild['id'])['lvl']
        aid = ctx.author.id
        if not self.db.request(f"SELECT * FROM members WHERE mid = {aid} AND guild = {guild['id']} AND admin >= {lvl}"): return await ctx.reply("У вас нет доступа к команде")
        info = utils.getLogsChannel(ctx.guild, guild['id'], 'room', '')
        if info: return await ctx.send(embed = embeds.CreateRoomPanel("Система комнат уже включена", self.bot.user.avatar_url).get())
        channel: discord.VoiceChannel = await ctx.guild.create_voice_channel(":|: Создать комнату")
        self.db.request(f"INSERT INTO channels(guild, type, channel) VALUES({guild['id']}, 'room', '{channel.id}')")
        await ctx.send(embed = embeds.CreateRoomPanel("Голосовой канал, для создания комнат создан", self.bot.user.avatar_url).get())

    @войс.command()
    async def выкл(self, ctx: commands.Context):
        guild = self.db.request(f'SELECT * FROM guilds WHERE guild = "{ctx.guild.id}"')
        if not guild: return
        lvl = utils.get_command('войс', guild['id'])['lvl']
        aid = ctx.author.id
        if not self.db.request(f"SELECT * FROM members WHERE mid = {aid} AND guild = {guild['id']} AND admin >= {lvl}"): return await ctx.reply("У вас нет доступа к команде")
        channel = utils.getLogsChannel(ctx.guild, guild['id'], 'room', '')
        if not channel: return await ctx.send(embed = embeds.CreateRoomPanel("Система комнат не включена", self.bot.user.avatar_url).get())
        self.db.request(f"DELETE FROM channels WHERE guild = {guild['id']} AND channel = '{channel.id}'")
        await channel.delete()
        await ctx.send(embed = embeds.CreateRoomPanel("Система комнат отключена", self.bot.user.avatar_url).get())

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        guild = self.db.request(f'SELECT * FROM guilds WHERE guild = "{member.guild.id}"')
        if not guild: return
        if before.channel and not after.channel or before.channel and after.channel:
            channel = self.db.request(f"SELECT * FROM Rooms WHERE guild = {guild['id']} AND channel = '{before.channel.id}'")
            if not channel: return
            if len(before.channel.members) > 0: return
            self.db.request(f"DELETE FROM Rooms WHERE id = {channel['id']}")
            await before.channel.delete(reason = 'Отсутствуют участники в комнате')

        if not after.channel: return
        channel = utils.getLogsChannel(member.guild, guild['id'], 'room', '')
        if not channel: return
        if after.channel.id != int(channel.id): return
        gd: discord.Guild = member.guild
        voice_channel: discord.VoiceChannel = await gd.create_voice_channel(f"Канал участника {member.display_name}")
        self.db.request(f"INSERT INTO Rooms(guild, channel) VALUES({guild['id']}, '{voice_channel.id}')")
        await voice_channel.set_permissions(member, move_members=True, mute_members=True)
        await member.move_to(voice_channel, reason="Создание голосового канала")


def setup(client):
    client.add_cog(CreateRommSystem(client))