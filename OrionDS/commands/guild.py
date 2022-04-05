import discord, config
from discord.ext import commands
from plugins import simplemysql, utils, embeds

class GuildCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)


    @commands.command()
    async def guild(self, ctx: commands.Context):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        members_guild = ctx.guild.members
        members_total = len(members_guild)
        bots = len([i for i in members_guild if i.bot])
        members = len([i for i in members_guild if not i.bot])

        offline = len([i for i in members_guild if i.status == discord.Status.offline])
        online = len([i for i in members_guild if i.status == discord.Status.online])
        idle = len([i for i in members_guild if i.status == discord.Status.idle])

        channels_total = ctx.guild.channels
        text_channels = len([i for i in channels_total if i.type == discord.ChannelType.text])
        voice_channels = len([i for i in channels_total if i.type == discord.ChannelType.voice])

        embed = discord.Embed(title = f'Информация о гильдии "{ctx.guild.name}"')
        embed.add_field(name = "Участники", value = f"Всего: `{members_total}`\n"
                                                    f"Пользователей: `{members}`\n"
                                                    f"Ботов: `{bots}`")

        embed.add_field(name = "Статусы участников", value = f"В сети: `{online}`\n"
                                                    f"Не активны: `{idle}`\n"
                                                    f"Не в сети: `{offline}`")

        embed.add_field(name = "Каналы гильдии", value = f"Всего: `{len([i for i in channels_total if i.type != discord.ChannelType.category])}`\n"
                                                    f"Текстовых: `{text_channels}`\n"
                                                    f"Голосовых: `{voice_channels}`")

        embed.color = config.COLOR
        embed.set_thumbnail(url = ctx.guild.icon_url)
        embed.add_field(name = "Создатель", value = f"`{ctx.guild.owner}`")
        embed.add_field(name = "Локализация гильдии", value = f"{'`подключена`' if guild['lid'] else '`не подключена`'}")
        embed.add_field(name = "Дата создания гильдии", value = f"`{ctx.guild.created_at.strftime('%d.%m.%y %H:%M')}`")

        await ctx.send(embed = embed)

def setup(client):
    client.add_cog(GuildCommand(client))