import discord, config, time
from datetime import datetime as dtime
from discord import guild
from discord.ext import commands
from plugins import simplemysql, utils, embeds

class Active(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)


    @commands.command()
    async def active(self, ctx: commands.Context, member: discord.Member = None, dt: str = time.strftime('%d.%m.%y')):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return
        ft = dtime.fromtimestamp
        member = member if member else ctx.author
        row = self.db.request(f"SELECT * FROM activitiesMembers WHERE mid = {member.id} AND guild = {guild['id']} AND dtime = '{dt}'", 'fetchall')
        if not row: return await ctx.send(embed = embeds.NotFoundActive(ctx.author, member, dt).get())
        channels = '\n'.join(
            
            f'┗ {ctx.guild.get_channel(int(i["channel"]))}, онлайн {utils.getTime(ft(i["end_time"] - i["start_time"] - 10800).strftime("%d:%H:%M:%S")) if i["end_time"] > 0 else utils.getTime(ft(time.time() - i["start_time"] - 10800).strftime("%d:%H:%M:%S"))} {utils.getActivityMember(guild, i)}' 
            for i in row
            
            )
        onlines = sum(
            [
            
            i['end_time'] - i['start_time'] if i['end_time'] else time.time() - i['start_time'] for i in row
            
            ]
            )


        embed = discord.Embed(title = ':floppy_disk: Актив участника')
        embed.description = f"▹ Активность участника {member.mention} за {dt}"
        embed.add_field(name = 'Голосовые каналы',
                        value=f"{channels}\n\n"
                              f"**Общий онлайн:** {utils.getTime(ft(onlines - 10800).strftime('%d:%H:%M:%S'))}")

        embed.color = config.COLOR
        embed.set_footer(text = f"Отправлено: {ctx.author} | Отважная Канелла (c) 2021", icon_url=ctx.author.avatar_url)
        embed.timestamp = dtime.fromtimestamp(time.time() - 10800)
        await ctx.send(embed = embed)
        
    @active.error
    async def error(self, ctx, error):
        if 'not found.' in str(error): return await ctx.send(embed = embeds.MemberNotFound(ctx.author).get())
        print(utils.Colors.red(text=error, text_one="ActiveError:"))

def setup(client):
    client.add_cog(Active(client))