from os import stat
import discord, config
from discord.ext import commands
from PIL import Image, ImageFilter, ImageDraw, ImageFont
import io
from plugins import simplemysql, utils, embeds, connect

class RangCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = simplemysql.Pymysql(host=config.DB_HOST, user = config.DB_USER, password = config.DB_PASS, db = config.DB_NAME)
        self.cn = connect.DataBase(self.db)            

    @commands.command()
    async def ranks(self, ctx: commands.Context):
        guild = self.db.request(f"SELECT * FROM guilds WHERE guild = '{ctx.guild.id}'")
        if not guild: return 
        member = self.cn.member(ctx.author.id, guild['id'])
        members = self.db.request(f"SELECT * FROM members WHERE guild = {guild['id']}", 'fetchall')
        image = Image.open("img/font_card.jpg")
        img = image.resize([600, 160])
        idraw = ImageDraw.Draw(img)
        font = ImageFont.truetype("Montserrat-SemiBold.ttf", size=20)
        font_2 = ImageFont.truetype("Montserrat-SemiBold.ttf", size=16)
        font_3 = ImageFont.truetype("Montserrat-SemiBold.ttf", size=17)
        font_4 = ImageFont.truetype("Montserrat-SemiBold.ttf", size=32)
        async with ctx.typing():
            pass
        avatar, cirle = await self.circle_avatar(ctx, 91)
        #status, status_circle = await self.get_status(ctx)
        idraw.text((189, 60), f"{ctx.author.display_name}", font = font, fill = 'white')
        idraw.text((281, 63), f"#{ctx.author.discriminator}", font = font_2, fill = 'grey')
        idraw.text((379, 113), f"{member['xp']}", font = font_2, fill = 'white')
        idraw.text((545, 7), f"#{utils.getRankMember(members, member)[0]}", font = font_4, fill = 'white')
        idraw.text((self.dr(394, member['xp']), 113), f"/ {member['lvl']*100 + config.XP_FOR_UP_RANK}", font = font_2, fill = 'grey')
        idraw.text((self.dr2(165, member['lvl']), 86), f"{member['lvl']}", font = font_3, fill = 'white')
        img.paste(avatar, (38, 29), cirle)
        #img.paste(status, (110, 100), status_circle)
        img.save("card.jpg", quality = 5000)
        await ctx.send(file = discord.File("card.jpg"))

    @staticmethod
    def dr(w, lvl):
        if len(str(lvl)) == 1: return w
        if len(str(lvl)) == 2: return w+8
        if len(str(lvl)) == 3: return w+20
    
    @staticmethod
    def dr2(w, lvl):
        if len(str(lvl)) < 2:
            if lvl == 1: return w-2
            if lvl in [4, 8]: return w-4
            return w-3
        if str(lvl)[0] in ['9','5','2','3','7']: return w-3*2.5
        if str(lvl)[0] in ['1']: return w-3*1.4
        if str(lvl)[0] in ['4']: return w-3*3.2
        if str(lvl)[0] in ['6','8']: return w-3*3
        return w-3*2

    async def circle_avatar(self, ctx, size):
        avatar_asset = ctx.author.avatar_url_as(format='jpg', size=128)

        buffer_avatar = io.BytesIO(await avatar_asset.read())

        avatar_image = Image.open(buffer_avatar)

        avatar_image = avatar_image.resize((size, size))

        circle_image = Image.new('L', (size, size))
        circle_draw = ImageDraw.Draw(circle_image)
        circle_draw.ellipse((0, 0, size, size), fill=255)
        
        return avatar_image, circle_image

    async def get_status(self, ctx):
        size = 64

        status = ctx.author.status

        status_image = Image.open(f"img/{status}.png")
        status_image.resize((size, size))

        circle_image = Image.new('L', (size, size))
        circle_draw = ImageDraw.Draw(circle_image)
        circle_draw.ellipse((0, 0, size/2, size/2), fill=255)
        return status_image, circle_image

def setup(client):
    client.add_cog(RangCommand(client))