import discord, config
from discord.ext import commands
from plugins import simplemysql, embeds, connect

class LogsUpdateVoiceChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)
        self.cn = connect.DataBase(self.db)


    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        guild = self.db.request(f'SELECT * FROM guilds WHERE guild = "{member.guild.id}"')
        if not guild: return
        if before.channel and not after.channel:
            return self.cn.endVoiceChannel(member.id, guild['id'], before.channel.id)
        if not before.channel and after.channel:
            return self.cn.startVoiceChannel(member.id, guild['id'], after.channel.id)
        if before.channel and after.channel:
            if before.channel.id == after.channel.id:
                ch_id = after.channel.id
                if after.deaf and not before.deaf: return self.cn.updateVoiceData(member.id, guild['id'], ch_id, "откл. наушники")
                if after.self_deaf and not before.self_deaf: return self.cn.updateVoiceData(member.id, guild['id'], ch_id, "откл. наушники")
                
                if after.self_stream and not before.self_stream: return self.cn.updateVoiceData(member.id, guild['id'], ch_id, "вкл. стрим")
                
                if after.mute and not before.mute: return self.cn.updateVoiceData(member.id, guild['id'], ch_id, "откл. микрофон")
                if after.self_mute and not before.self_mute: return self.cn.updateVoiceData(member.id, guild['id'], ch_id, "откл. микрофон")


                if not after.self_mute and before.self_mute: return self.cn.updateVoiceData(member.id, guild['id'], ch_id, "вкл. микрофон")
                if not after.mute and before.mute: return self.cn.updateVoiceData(member.id, guild['id'], ch_id, "вкл. микрофон")
                
                if not after.deaf and before.deaf: return self.cn.updateVoiceData(member.id, guild['id'], ch_id, "вкл. наушники")
                if not after.self_deaf and before.self_deaf: return self.cn.updateVoiceData(member.id, guild['id'], ch_id, "вкл. наушники")
                
                if not after.self_stream and before.self_stream: return self.cn.updateVoiceData(member.id, guild['id'], ch_id, "выкл. стрим")
            
            self.cn.endVoiceChannel(member.id, guild['id'], before.channel.id)
            return self.cn.startVoiceChannel(member.id, guild['id'], after.channel.id)


def setup(client):
    client.add_cog(LogsUpdateVoiceChannel(client))