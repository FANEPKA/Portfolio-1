import discord, config, time
from datetime import datetime
from discord import guild
from discord.ext import commands
from plugins import simplemysql, utils, embeds, connect

class Setadm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)
        self.cn = connect.DataBase(self.db)

    @commands.command()
    async def setadm(self, ctx: commands.Context, member: discord.Member = None, lvl: int = 0):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        aid = ctx.author.id
        clvl = utils.get_command('setadm', guild['id'])['lvl']
        alvl = self.cn.member(ctx.author.id, guild['id'])['admin']
        if not self.db.request(f"SELECT * FROM members WHERE mid = {aid} AND guild = {guild['id']} AND admin >= {clvl}"): return await ctx.reply("У вас нет доступа к команде")
        if not member: return await ctx.send(embed=embeds.SetadmForm(ctx.prefix, self.bot.user.avatar_url, alvl - 1).get())
        self.cn.createMember(member.id, guild['id'])
        if member.id == ctx.guild.owner.id: return await ctx.send(embed = embeds.GuildOwnerInteraction(ctx.author).get())
        if member.id == ctx.author.id: return await ctx.send(embed = embeds.SelfInteraction(ctx.author).get())
        if member.id == config.ID: return await ctx.send(embed = embeds.BotInteraction(ctx.author).get())
        mlvl = self.cn.member(member.id, guild['id'])['admin']
        if self.cn.member(aid, guild['id'])['admin'] <= mlvl: return await ctx.reply(f"{member.display_name} ({member.mention}) имеет права администратора схожие с вашими")
        if lvl < 0 or lvl > alvl - 1: return await ctx.send(embed = embeds.LvlError(ctx.author, alvl).get())
        embed = embeds.AdminForm(ctx.author, member, self.bot.user.avatar_url, guild['id'], lvl)
        embedLs = embeds.AdminFormLs(ctx.author, member, self.bot.user.avatar_url, guild['id'], lvl)
        self.cn.updateAdmin(member.id, guild['id'], lvl)
        data = str({"admin": ctx.author.id, "member": member.id, "lvl": lvl})
        if lvl != mlvl: utils.insertAdminHistory(guild['id'], 'setadm', data)
        if lvl == 0 and mlvl > 0: 
            try:await member.send(embed = embedLs.remove())
            except: pass
            return await ctx.send(embed = embed.remove())
        if lvl > 0 and lvl > mlvl: 
            try:await member.send(embed = embedLs.up())
            except: pass
            return await ctx.send(embed = embed.up())
        if lvl > 0 and lvl < mlvl: 
            try: await member.send(embed = embedLs.down())
            except: pass
            return await ctx.send(embed = embed.down())
        if lvl == mlvl: return await ctx.send(embed = embed.error()) 


    @setadm.error
    async def error(self, ctx, error):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        lvl = self.cn.member(ctx.author.id, guild['id'])['admin'] - 1
        if str(error) == 'Converting to "int" failed for parameter "lvl".': return await ctx.send(embed = embeds.LvlError(ctx.author, lvl).get())
        if 'not found.' in str(error): return await ctx.send(embed = embeds.MemberNotFound(ctx.author).get())
        print(utils.Colors.red(text=error, text_one="SetAdmError:"))

def setup(client):
    client.add_cog(Setadm(client))