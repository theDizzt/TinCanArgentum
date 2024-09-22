"""
 █████  ██████   ██████  ███████ ███    ██ ████████ ██    ██ ███    ███ 
██   ██ ██   ██ ██       ██      ████   ██    ██    ██    ██ ████  ████ 
███████ ██████  ██   ███ █████   ██ ██  ██    ██    ██    ██ ██ ████ ██ 
██   ██ ██   ██ ██    ██ ██      ██  ██ ██    ██    ██    ██ ██  ██  ██ 
██   ██ ██   ██  ██████  ███████ ██   ████    ██     ██████  ██      ██ 

           Code by 혜성(dizzt, Dizzt#0116)
           Start of Development: May 20, 2017
"""

####### 0. Modules #######

# 0.1. Discord.py
import discord
from discord.ext import commands
import asyncio

# 0.2. Fuctions
from fcts.keep_alive import keep_alive
import fcts.sqlcontrol as q
import fcts.etcfunctions as etc
import fcts.koreanbreak as kb
import fcts.worddict as wd
import fcts.leaderboard as l
import fcts.lklab as lk
import fcts.tedne as ted
from config.rootdir import root_dir

# 0.2. Dir. Manager
import os

# 0.3. Dynamic Images + Buffer
from PIL import Image, ImageDraw, ImageFont
import io

# 0.4. ect.
import random as r
import math as m
import time as t
from time import sleep
import datetime
import yaml
from tqdm import tqdm

####### 1. Config #######

# 1.0. Open Config & Admin file

with open(root_dir + '/config/config.yml',encoding='UTF-8') as f:
    keys = yaml.load(f, Loader=yaml.FullLoader)

# 1.1. Discord Bot
token = keys['Bot']['token']
prefix = keys['Bot']['prefix']
Version = keys['Version']['ver']
Update_Date = keys['Version']['date']
game_mes = f"Made by Dizzt | {Version} | {Update_Date} | Type '{prefix}help' for help"

# 1.4. Event Variables
xp_multi = 1.84

####### 2.Funtions #######

# 2.0. DB Init Setting
q.initSetting()
wd.initSetting()
l.initSetting()
lk.initSetting()
ted.initSetting()

####### 3. Discord Bot Client #######

# 3.0. Create Discord Client

intents = discord.Intents.all()
client = commands.Bot(command_prefix=prefix,
                      intents=intents,
                      help_command=None,
                      sync_commands=True,
                      status=discord.Status.online,
                      activity=discord.Game(game_mes))

# 3.1. Discord Cogs Loading

# 3.2. Discord Bot Ready Events


@client.event
async def on_ready():
    print("New log in as {0.user}".format(client))


# 3.3. Voice Channel Event


# 3.3.1. Voice Leveling
@client.event
async def on_voice_state_update(member, before, after):

    if not before.channel and after.channel:
        voicetime = int(t.time())
        etc.voiceDelete(member)
        etc.voiceWrite(member, voicetime)
        print("{} joined voice channel! (Time: {})".format(member, voicetime))

    elif before.channel and not after.channel:

        voicetime = int(t.time()) - etc.voiceRead(member)

        xp_gain = int((voicetime * 0.2) * xp_multi)
        money_gain = int(voicetime // 12)

        try:
            q.xpAdd(member, xp_gain)
            q.moneyAdd(member, money_gain)

        except:
            q.newAccount(member)
            q.newStorage(member)
            q.xpAdd(member, xp_gain)
            q.moneyAdd(member, money_gain)

        etc.voiceDelete(member)
        print("{} left voice channel! | {}s | +{}XP | +{}$".format(
            member, voicetime, xp_gain, money_gain))


# 3.4. Message Event
@client.event
async def on_message(message):

    # 3.2.1. XP System
    count = kb.count_break_korean(message.content)
    xp_gain = int((count * 0.3) * xp_multi + 1)
    money_gain = r.randint(5, 15)

    now = datetime.datetime.now() + datetime.timedelta(hours=9)
    now_time = now.strftime('%Y/%m/%d %H:%M:%S')

    global temp_xp, temp_lv

    try:
        temp_xp = q.readXp(message.author)
        temp_lv = etc.level(temp_xp)

    except:
        q.newAccount(message.author)
        q.newStorage(message.author)
        temp_xp = 0
        temp_lv = 1

    q.xpAdd(message.author, xp_gain)
    q.moneyAdd(message.author, money_gain)

    if etc.level_up(temp_lv, temp_xp + xp_gain) and False:

        background_image = Image.open(root_dir + "/config/rankcard/rankup.png").convert(
            'RGBA')
        rank_image_1 = Image.open(
            root_dir + "/config/rankcard/emblem/{}.png".format(temp_lv)).convert('RGBA')
        rank_image_2 = Image.open(
            root_dir + "/config/rankcard/emblem/{}.png".format(temp_lv +
                                                     1)).convert('RGBA')

        rank_image_1 = rank_image_1.resize((60, 60))
        rank_image_2 = rank_image_2.resize((60, 60))

        image = background_image.copy()
        image_width, image_height = image.size

        rank1 = rank_image_1.copy()
        rank2 = rank_image_2.copy()

        rectangle_image = Image.new('RGBA', (image_width, image_height))

        image = Image.alpha_composite(image, rectangle_image)

        draw = ImageDraw.Draw(image)

        avatar_asset = message.author.avatar

        buffer_avatar = io.BytesIO()
        await avatar_asset.save(buffer_avatar)
        buffer_avatar.seek(0)

        avatar_image = Image.open(buffer_avatar)

        avatar_image = avatar_image.resize((96, 96))
        image.paste(avatar_image, (8, 8), mask=avatar_image)
        image.paste(rank1, (112, 44), mask=rank1)
        image.paste(rank2, (188, 44), mask=rank2)

        buffer_output = io.BytesIO()
        image.save(buffer_output, format='PNG')
        buffer_output.seek(0)
        print(temp_lv)
        if temp_lv + 1 == 91:
            await message.channel.send(
                "<@{}> 는 `레벨 {}`에 도달했습니다!\nYou reached `Level {}`!\n레벨 91 달성을 진심으로 축하드립니다! 모든 혜택을 누릴 수 있는 레벨에 도달하기 까지 많을 시간을 함께 해 주셔서 진심으로 감사합니다!\nCongratulations on achieving level 91! Thank you so much for spending a lot of time with me before you reach the level where you can enjoy all the benefits!"
                .format(message.author.id, temp_lv + 1, temp_lv + 1),
                file=discord.File(buffer_output, 'myimage.png'))
        else:
            await message.channel.send(
                "<@{}> 는 `레벨 {}`에 도달했습니다!\nYou reached `Level {}`!".format(
                    message.author.id, temp_lv + 1, temp_lv + 1),
                file=discord.File(buffer_output, 'myimage.png'))

    # 3.4.2. Message Contents Logs
    print(f"{message.author} | {now_time} | +{xp_gain}XP | +${money_gain}")
    #print(message.content)

    #지우지 말 것
    await client.process_commands(message)

    #이것도
    if message.author == client.user:
        return

    #주원이 괴롭히기
    if message.content.startswith("주원"):
        await message.channel.send("<@262899129276039169>", tts=True)

    if message.content.startswith("김주원"):
        await message.channel.send("<@262899129276039169>", tts=True)

    if message.content.startswith("주웡"):
        await message.channel.send("<@262899129276039169>", tts=True)
        choice = 85
        if q.readStorage(message.author, choice) == 0:
            q.storageModify(message.author, choice, 1)

    if message.content.startswith("김주웡"):
        await message.channel.send("<@262899129276039169>", tts=True)
        choice = 85
        if q.readStorage(message.author, choice) == 0:
            q.storageModify(message.author, choice, 1)

    if message.content.startswith("곰국"):
        await message.channel.send(
            "https://cdn.discordapp.com/attachments/526648786605441024/789690716224880640/36e3370a1834456c.png",
            tts=True)

    if message.content.startswith("논문"):
        await message.channel.send(
            "https://cdn.discordapp.com/attachments/526648786605441024/789690716224880640/36e3370a1834456c.png",
            tts=True)

    #이스터에그!!
    if message.content == "stellaforce":

        await message.delete()
        choice = 6

        if q.readStorage(message.author, choice) == 0:
            q.storageModify(message.author, choice, 1)

    if message.content == "당근꼴등":
        choice = 20

        if q.readStorage(message.author, choice) == 0:
            q.storageModify(message.author, choice, 1)

        await message.channel.send("박당근의 골프잇 전적: 29판중 0승 29패 응~ 당근~")
        await message.channel.send("https://youtu.be/X0VGxuq9_sw?t=112")
        await message.channel.send("https://youtu.be/0mdWdL-0fZY?t=1346")
        await message.channel.send(
            "`;skin change 20`을 입력하여 특전을 확인하당근 `( ˃ ⩌˂)`")

    if message.content == "씨애":
        choice = 86

        if q.readStorage(message.author, choice) == 0:
            q.storageModify(message.author, choice, 1)
        randtext = [
            "어? 할래? 어서켜라!!! 으하하하핳", "씨애애애애애!!!!! 발러어어어어!!!! 으하하하하 어서켜라!",
            "씨애? 씨! 오우! 에이취!", "아니 그 좋은것을 왜 혼자 한단 말이야!? 얼른 초대 받아라!",
            "내가 있는한 너도 씨애, 나도 씨애, 내 여동생도 씨애, 짱아도 씨애, 모두가 씨애로 하나 되는것이야!!!",
            "위 갓뎀 빠 빠바 빠 빠 빱 빠 바빱 퐈이어!!", "어? 안돼겠다, 오늘은 1000포인트로 한판 한다.",
            "운명... 씨애... 그리고 발러...", "웰 컴 투 컴퍼니 오브 히어로즈~"
        ]
        """
        uid = str(message.author.id)
        user = await client.get_user(262528817942364160).create_dm()
        print(user)
        await user.send("<@"+uid+"> 가 씨애를 무지 원한다고 합니다!")
        """
        await message.channel.send(
            "https://media.discordapp.net/attachments/1115648878918774794/1157896200377348106/export202310011325364820.png"
        )
        await message.channel.send("<@262528817942364160>: " +
                                   r.choice(randtext))
        await message.channel.send(
            "`;skin change 86`을 입력하여 특전을 확인해보세요~ `( ˃ ⩌˂)`")


# 4. Commands


# 4.1. Sync
@client.hybrid_command(name='sync',
                       description="Sync commands to the current server.")
async def sync(ctx):
    await client.tree.sync()
    await ctx.reply("`⸜(*◉ ᴗ ◉)⸝` Synced commands to the current server!")


async def load_extensions():
    # cogs 폴더의 절대 경로 얻기
    # Pycharm에서 바로 상대 경로를 사용하면 오류가 발생하기 때문에 따로 절대경로를 얻어야한다.
    cogs_path = 'cogs'
    abs_cogs_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                 cogs_path)

    # cogs 폴더에 존재하는 cogs(.py파일) 로드
    for c in tqdm(os.listdir(abs_cogs_path)):
        if c.endswith(".py"):
            await client.load_extension(f"cogs.{c.split('.')[0]}"
                                        )  # .py 부분을 떼고 cog의 이름만 추출


async def main():
    async with client:
        await load_extensions()
        await client.start(token)


keep_alive()
asyncio.run(main())
