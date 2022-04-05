from logging import log
from typing import List
import discord, config
from discord.message import Message
from discord.ext import commands
from plugins import simplemysql, embeds, connect

class StateMessages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)
        self.cn = connect.DataBase(self.db)


    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        guild = self.db.request(f'SELECT * FROM guilds WHERE guild = "{message.guild.id}"')
        if not guild: return
        logs_channel = self.db.request(f"SELECT * FROM channels WHERE guild = {guild['id']} AND type = 'messages_logs'")
        if not logs_channel: return
        channel: discord.TextChannel = message.guild.get_channel(int(logs_channel['channel']))
        await channel.send(embed = embeds.DeleteMessage(message, self.bot.user.avatar_url).get())

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        guild = self.db.request(f'SELECT * FROM guilds WHERE guild = "{before.guild.id}"')
        if not guild: return
        logs_channel = self.db.request(f"SELECT * FROM channels WHERE guild = {guild['id']} AND type = 'messages_logs'")
        if not logs_channel: return
        channel: discord.TextChannel = before.guild.get_channel(int(logs_channel['channel']))
        if not before.content or not after.content: return  
        await channel.send(embed = embeds.EditMessage(before, after, self.bot.user.avatar_url).get())
        
def setup(client):
    client.add_cog(StateMessages(client))