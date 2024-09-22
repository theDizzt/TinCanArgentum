import discord
from discord.ext import commands
import yaml
import fcts.sqlcontrol as q
import fcts.etcfunctions as etc
import random
from PIL import Image, ImageDraw, ImageFont
import io
from fcts.translator import dataProcessStream
import urllib
from urllib.request import HTTPError
from config.rootdir import root_dir

with open(root_dir + '/config/config.yml',encoding='UTF-8') as f:
    keys = yaml.load(f, Loader=yaml.FullLoader)

client_id = keys['Keys']['client_id']
client_secret = keys['Keys']['client_secret']
streamInstance = dataProcessStream(client_id, client_secret)


class Miscellaneous(commands.Cog):  # Cog를 상속하는 클래스를 선언

    def __init__(self, client: commands.Bot):  # 생성자 작성
        self.client = client

    # Random [ID: 31]
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)
    @commands.hybrid_command(name='dice',
                             description="Display a random number")
    async def dice(self,
                   ctx,
                   rand: int = 99,
                   non_zero: int = 1,
                   option: int = 3):

        if option >= 3 or option < 0:
            option = random.randint(1, 3) - 1

        if non_zero == 0:
            lucky_num = random.randint(1, rand + 1) - 1
        else:
            lucky_num = random.randint(1, rand)

        rand0 = Image.open(root_dir + "/config/rand/rand1.png").convert('RGBA')
        rand1 = Image.open(root_dir + "/config/rand/rand2.png").convert('RGBA')
        rand2 = Image.open(root_dir + "/config/rand/rand3.png").convert('RGBA')

        arr_rand = [rand0, rand1, rand2]

        #duplicate image
        image = arr_rand[option].copy()
        image_width, image_height = image.size

        # create object for drawing
        draw = ImageDraw.Draw(image)

        # draw text in center

        font_rand = ImageFont.truetype(root_dir + "/font/rand.ttf", 48)

        x1 = (192 - draw.textlength(str(lucky_num), font=font_rand)) / 2 - 24
        y1 = 48 / 2

        draw.text((x1 + 3, y1 + 3),
                  str(lucky_num),
                  fill=(0, 0, 0, 255),
                  font=font_rand)
        draw.text((x1, y1),
                  str(lucky_num),
                  fill=(255, 255, 255, 255),
                  font=font_rand)

        #sending image
        buffer_output = io.BytesIO()
        image.save(buffer_output, format='PNG')
        buffer_output.seek(0)

        if rand == 222 and lucky_num == 22:
            if q.readStorage(ctx.author, 22) == 0:
                q.storageModify(ctx.author, 22, 1)
                await ctx.send(file=discord.File(root_dir + '/config/easter/22222.jpg'))

        await ctx.reply(file=discord.File(buffer_output, 'myimage.png'))

    @dice.error
    async def dice_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = '`(⩌ʌ ⩌;)` This command is ratelimited, please try again in **{:.2f} seconds**.'.format(
                error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    # Rage [ID: 36]
    @commands.cooldown(rate=1, per=20, type=commands.BucketType.user)
    @commands.hybrid_command(name='rage',
                             description="I'M F$%#^%#$%^%#% ANGRY!!!")
    #@discord.app_commands.describe(text_size="Font size",obj="User mention",rage="Write down your text")
    async def rage(self, ctx, text_size=24, obj=None, *, rage=None):

        bg = Image.open(root_dir + "/config/rage/ivory_rage.png").convert('RGBA')

        #duplicate image
        image = bg.copy()
        image_width, image_height = image.size

        # create object for drawing
        draw = ImageDraw.Draw(image)

        # draw text in center
        font_rage = ImageFont.truetype(root_dir + "/font/name.ttf", int(text_size))
        xa, ya, xb, yb = font_rage.getbbox(rage)

        tw_rage, th_rage = xb - xa, yb - ya

        x1 = (500 - tw_rage) / 2 - 92
        y1 = (500 - th_rage) / 2 - 96

        draw.text((x1, y1), rage, fill=(0, 0, 0, 255), font=font_rage)

        #sending image
        buffer_output = io.BytesIO()
        image.save(buffer_output, format='PNG')
        buffer_output.seek(0)

        await ctx.send(obj, file=discord.File(buffer_output, 'myimage.png'))

    @rage.error
    async def rage_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = '`(⩌ʌ ⩌;)` This command is ratelimited, please try again in **{:.2f} seconds**.'.format(
                error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    # Translator [ID: 39]
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    @commands.hybrid_command(name='translate',
                             description="Translate your text.")
    #@discord.app_commands.describe(lan1="Language of original text",lan2="Translation result language",text="Write your text to translate")
    async def translate(self, ctx, lan1, lan2, *, text=""):
        try:
            if text == "":
                await ctx.reply("단어 혹은 문장이 입력되지 않았어요. 다시한번 확인해주세요.")
            else:
                try:
                    resultPackage = streamInstance.returnQuery(
                        lan1, lan2, text)
                    await ctx.reply(resultPackage["data"]["tl"]["text"])
                except:
                    await ctx.reply("???")

        except HTTPError as e:
            await ctx.reply(f"Translate Failed. HTTPError Occured : {e}")

    @translate.error
    async def translate_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = '`(⩌ʌ ⩌;)` This command is ratelimited, please try again in **{:.2f} seconds**.'.format(
                error.retry_after)
            await ctx.send(msg)
        else:
            raise error


async def setup(client):
    await client.add_cog(Miscellaneous(client))
