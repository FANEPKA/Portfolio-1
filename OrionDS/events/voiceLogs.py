import discord, config
from discord.ext import commands
from plugins import simplemysql, embeds, connect, utils

class LogsUpdateVoiceChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)
        self.cn = connect.DataBase(self.db)


    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        guild = self.db.request(f'SELECT * FROM guilds WHERE guild = "{member.guild.id}"')
        if not guild: return
        channel: discord.TextChannel = utils.getLogsChannel(member.guild, guild['id'], 'voice')
        if not channel: return
        if before.channel and not after.channel:
            return await channel.send(embed = embeds.LogsVoice(f"Участник {member.mention} покинул канал {before.channel.mention}", self.bot.user.avatar_url).get())
        if not before.channel and after.channel:
            return await channel.send(embed = embeds.LogsVoice(f"Участник {member.mention} присоединился к каналу {after.channel.mention}", self.bot.user.avatar_url).get())
        if before.channel and after.channel:
            if before.channel == after.channel:
                if after.deaf and not before.deaf: return await channel.send(embed = embeds.LogsVoice(f"Модератор отключил наушники участнику {member.mention} в канале {after.channel.mention}", self.bot.user.avatar_url).get())
                if after.self_deaf and not before.self_deaf: return await channel.send(embed = embeds.LogsVoice(f"Участник {member.mention} самостоятельно отключил наушники в канале {after.channel.mention}", self.bot.user.avatar_url).get())
                
                if after.self_stream and not before.self_stream: return await channel.send(embed = embeds.LogsVoice(f"Участник {member.mention} запустил стрим в канале {after.channel.mention}", self.bot.user.avatar_url).get())
                
                if after.mute and not before.mute: return await channel.send(embed = embeds.LogsVoice(f"Модератор отключил микрофон участнику {member.mention} в канале {after.channel.mention}", self.bot.user.avatar_url).get())
                if after.self_mute and not before.self_mute: return await channel.send(embed = embeds.LogsVoice(f"Участник {member.mention} самостоятельно отключил микрофон в канале {after.channel.mention}", self.bot.user.avatar_url).get())


                if not after.self_mute and before.self_mute: return await channel.send(embed = embeds.LogsVoice(f"Участник {member.mention} самостоятельно включил микрофон в канале {after.channel.mention}", self.bot.user.avatar_url).get())
                if not after.mute and before.mute: return await channel.send(embed = embeds.LogsVoice(f"Модератор включил микрофон участнику {member.mention} в канале {after.channel.mention}", self.bot.user.avatar_url).get())
                
                if not after.deaf and before.deaf: return await channel.send(embed = embeds.LogsVoice(f"Модератор включил наушники участнику {member.mention} в канале {after.channel.mention}", self.bot.user.avatar_url).get())
                if not after.self_deaf and before.self_deaf: return await channel.send(embed = embeds.LogsVoice(f"Участник {member.mention} самостоятельно включил наушники в канале {after.channel.mention}", self.bot.user.avatar_url).get())
                
                if not after.self_stream and before.self_stream: return await channel.send(embed = embeds.LogsVoice(f"Участник {member.mention} выключил стрим в канале {after.channel.mention}", self.bot.user.avatar_url).get())
            
            
            if before.channel != after.channel: return await channel.send(embed = embeds.LogsVoice(f"Участник {member.mention} переместился из {before.channel.mention} в {after.channel.mention}", self.bot.user.avatar_url).get())


def setup(client):
    client.add_cog(LogsUpdateVoiceChannel(client))