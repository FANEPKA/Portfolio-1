import discord, config, time
from pkg_resources import yield_lines
import youtube_dl
import os
from os import system
from datetime import datetime as dtime
from youtube_search import YoutubeSearch
from discord import guild
from discord.utils import get
from discord.ext import commands
from plugins import simplemysql, utils, embeds

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)

    @commands.command()
    async def play(self, ctx, *, url: str = None):
        if not url:
            return await ctx.send("/play <Ссылка на ютуб>")

        channel = ctx.message.author.voice.channel
        if not channel:
            await ctx.send("Вы не подключены к голосовому каналу")
            return
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            voice = await channel.connect()
        await voice.disconnect()
        if voice and voice.is_connected():
            return await ctx.send("В одном из каналов играет музыка")
        else:
            voice = await channel.connect()

        await ctx.send("Все готово, скоро начнется воспроизведение звука")
        print("Someone wants to play music let me get that ready for them...")
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        ydl_opts = {
            'format': 'bestaudio',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '2048',
            }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                URL = info['formats'][0]['url']
            except:
                to_search = url
                results = YoutubeSearch(to_search, max_results=1).to_dict()
                NEW_URL = ("https://youtube.com" + results[0]["url_suffix"])
                info = ydl.extract_info(NEW_URL, download = False)
                URL = info['formats'][0]['url']

        voice.play(discord.FFmpegPCMAudio(URL))
        voice.volume = 60
        voice.is_playing()
    
    @commands.command()
    async def stop(self, ctx):
        channel = ctx.message.author.voice.channel
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            voice.stop()
            await voice.disconnect()
            await ctx.send(f"Музыка остановлена")
        else:
            await ctx.send("Не думайте, что я нахожусь на голосовом канале")



def setup(client):
    client.add_cog(Music(client))