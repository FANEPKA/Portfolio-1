# -*- coding: utf-8 -*-
import time
import discord, config, os, asyncio
from plugins import simplemysql, connect, embeds
from discord.ext import commands


def get_prefix(client: discord.Client = None, message: discord.Message = None):
    guild = db.request(f"SELECT * FROM guilds WHERE guild = '{message.guild.id}'")
    if not guild: return '!'
    return guild['prefix']

intents = discord.Intents.all()
db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)
bot = commands.Bot(command_prefix=get_prefix, intents=intents)
cn = connect.DataBase(db)	

@bot.event
async def on_message(message: discord.Message):
	if not message.guild or message.author.id == config.ID: return
	guild = db.request(f"SELECT * FROM guilds WHERE guild = '{message.guild.id}'")
	if not guild: return
	if message.author.id == config.ID: return
	cn.createMember(f'{message.author.id}', guild['id'])
	cn.updateMessages(message.author.id, guild['id'])
	await bot.process_commands(message)


@bot.event
async def on_ready():
    print(f"Запустился... | {config.VERSION}")

for filename in os.listdir('./commands'):
	if filename.endswith('.py'):
		try: bot.load_extension(f"commands.{filename[:-3]}") 
		except Exception as e: print(f"Error: {e}")

for filename in os.listdir('./events'):
	if filename.endswith('.py'):
		try: bot.load_extension(f"events.{filename[:-3]}")
		except Exception as e: print(f"Error: {e}")


async def checkAnSys():
	while True:
		await asyncio.sleep(1)
		for logs in db.request(f"SELECT * FROM anSys WHERE end_time <= {time.time()}", 'fetchall'):
			db.request(f"DELETE FROM anSys WHERE id = {logs['id']}")
	

async def checkBans():
	while True:
		await asyncio.sleep(1)
		for user in db.request(f"SELECT * FROM bans WHERE time <= {time.time()} and time > 0", 'fetchall'):
			guild: discord.Guild = bot.get_guild(int(cn.getGuild(user['guild'])['guild']))
			gd = db.request(f"SELECT * FROM guilds WHERE guild = '{guild.id}'")
			if gd:
				member: discord.User = bot.get_user(int(user['mid']))
				db.request(f"DELETE FROM bans WHERE mid = '{member.id}' AND guild = {gd['id']}")
				await guild.unban(member, reason = 'Конец времени бана | Система')
				logs_channel = db.request(f"SELECt * FROM channels WHERE guild = {gd['id']} AND type = 'bans_logs'")
				if logs_channel:
					channel: discord.TextChannel = guild.get_channel(int(logs_channel['channel']))
					await channel.send(embed=embeds.BanEnd(member, bot.user.avatar_url).get())
			


async def checkMutes():
	while True:
		await asyncio.sleep(1)
		for user in db.request(f"SELECT * FROM Mutes WHERE time <= {time.time()}", 'fetchall'):
			guild: discord.Guild = bot.get_guild(int(cn.getGuild(user['guild'])['guild']))
			if guild:
				gd = db.request(f"SELECT * FROM guilds WHERE guild = '{guild.id}'")
				if gd:
					member: discord.Member = guild.get_member(int(user['mid']))
					db.request(f"DELETE FROM Mutes WHERE id = {user['id']}")
					if member: 
						roleInfo = db.request(f"SELECT * FROM system_roles WHERE id = {user['role']}")
						role = guild.get_role(int(roleInfo['role_id']))
						await member.remove_roles(role, reason='Конец времени мута | Система')
						logs_channel = db.request(f"SELECt * FROM channels WHERE guild = {gd['id']} AND type = 'mutes_logs'")
						if logs_channel:
							channel: discord.TextChannel = guild.get_channel(int(logs_channel['channel']))
							await channel.send(embed=embeds.MuteEnd(member, bot.user.avatar_url).get())
					
					else: db.request(f"DELETE FROM members WHERE guild = {user['guild']} AND mid = {user['mid']}")
			else: db.request(f"DELETE FROM Mutes WHERE guild = {user['guild']}")

bot.loop.create_task(checkBans())
bot.loop.create_task(checkAnSys())
bot.loop.create_task(checkMutes())
bot.run(config.TOKEN)