import discord
import os
from discord.ext import commands
import fcts.sqlcontrol as q
import yaml
import fcts.etcfunctions as etc
from datetime import datetime
from config.rootdir import root_dir

with open(root_dir + '/config/help.yml',encoding='UTF-8') as f:
    helps = yaml.load(f, Loader=yaml.FullLoader)

with open(root_dir + '/config/config.yml',encoding='UTF-8') as f:
    keys = yaml.load(f, Loader=yaml.FullLoader)

Version = keys['Version']['ver']
Update_Date = keys['Version']['date']


class Essential(commands.Cog):  # Cog를 상속하는 클래스를 선언

    def __init__(self, client: commands.Bot):  # 생성자 작성
        self.client = client

    # Help [ID: 00]
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    @commands.hybrid_command(name='help',
                             description="Provides help for commands.")
    #@discord.app_commands.describe(command='Command to be explained.')
    async def help(self, ctx, command: str = "main"):
        if command == "main":
            embed = discord.Embed(
                title=":notebook_with_decorative_cover: **Help Section**",
                description=
                "Type `;help <command>` for more help. eg> `;help emblem`",
                color=0x78C1F3)

            embed.add_field(name=":stars: **Essentials**",
                            value=helps[command]['Essentials'],
                            inline=True)

            embed.add_field(name=":busts_in_silhouette: **User Profile**",
                            value=helps[command]['UserProfile'],
                            inline=True)

            embed.add_field(name=":dollar: **Economy**",
                            value=helps[command]['Economy'],
                            inline=True)

            embed.add_field(name=":magic_wand: **Miscellaneous**",
                            value=helps[command]['Miscellaneous'],
                            inline=True)

            embed.add_field(name=":globe_with_meridians: **Coalition**",
                            value=helps[command]['Coalition'],
                            inline=True)

            embed.add_field(name=":8ball: **Mini Games**",
                            value=helps[command]['Minigame'],
                            inline=True)
            
            embed.add_field(name=":sound: **Voice**",
                            value=helps[command]['Voice'],
                            inline=True)

            embed.add_field(
                name="<:pokeball:1145214279134482503> **Wagyumon Server**",
                value=helps[command]['WagyumonServer'],
                inline=True)

            embed.add_field(name=":crown: **Admin Features**",
                            value=helps[command]['AdminFeatures'],
                            inline=True)

            embed.add_field(name=":tools: **Admin Debugging**",
                            value=helps[command]['AdminDebugging'],
                            inline=True)

        else:
            try:
                embed = discord.Embed(
                    title=
                    f":notebook_with_decorative_cover: **{helps[command]['title']}** `ID: {helps[command]['id']}`",
                    description=
                    f"`{keys['Bot']['prefix']}{helps[command]['ctx']}`",
                    color=0xF2D7D9)

                embed.add_field(name="**Feature Description**",
                                value=helps[command]['discript'],
                                inline=False)
                embed.add_field(name="**Arguments**",
                                value=helps[command]['args'],
                                inline=False)
                if command == 'translate':
                    embed.add_field(
                        name="**Language Code**",
                        value=
                        "`ko` Korean, `ja` Japanese, `zh-CN` Simplified Chinese, `zh-TW` Traditional Chinese, `hi` Hindi, `en` English, `es` Spanish, `fr` French, `de` German, `pt` Portuguese, `vi` Vietnamese, `id` Indonesian,  `fa` Persian, `ar` Arabic, `mm` Burmese, `th` Thai, `ru` Russian, `it` Italian",
                        inline=False)
            except:
                pass

        #Common Part
        embed.set_footer(text="Developed by Dizzt", icon_url="")
        await ctx.reply(
            ":green_circle: **{}**'s request completely loaded!!".format(
                q.readTag(ctx.author)),
            embed=embed)

    @help.error
    async def help_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = '`(⩌ʌ ⩌;)` This command is ratelimited, please try again in **{:.2f} seconds**.'.format(
                error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    # Test Command [ID: 01]
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    @commands.hybrid_command(name='test', description="Send test message.")
    #@discord.app_commands.describe(arg='Text Message')
    async def test(self, ctx, *, arg: str = "Hello World!"):
        await ctx.reply(arg)

    @test.error
    async def test_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = '`(⩌ʌ ⩌;)` This command is ratelimited, please try again in **{:.2f} seconds**.'.format(
                error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    # Id Viewer [ID: 02]
    @commands.cooldown(rate=1, per=20, type=commands.BucketType.user)
    @commands.hybrid_command(
        name='myid',
        description="Show your discord user id and account creation date.")
    async def myid(self, ctx):
        uid = ctx.author.id
        udate = ctx.author.created_at.strftime("%a %#d %B %Y, %I:%M %p")
        await ctx.reply("ID: {}\nCreation date: {}".format(uid, udate))

    @myid.error
    async def myid_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = '`(⩌ʌ ⩌;)` This command is ratelimited, please try again in **{:.2f} seconds**.'.format(
                error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    # Credits [ID: 03]
    @commands.cooldown(rate=1, per=20, type=commands.BucketType.user)
    @commands.hybrid_command(name='credits',
                             description="Show developers of this bot.")
    async def credits(self, ctx):
        embed = discord.Embed(
            title=":small_orange_diamond:**Credits**",
            description=
            "`People who helped with code writing, graphic design, beta testing, and error correction!!`",
            color=0xF8FDCF)
        embed.add_field(
            name="Director",
            value="**`Dizzt`** Overall code writing and graphic design",
            inline=False)
        embed.add_field(
            name="Programming",
            value="**`OperaSeria`**\n**`me the newb`**`\n**`최은비`**\n**`Mono`**",
            inline=False)
        embed.add_field(
            name="Testers",
            value=
            "**`와규`**\n**`SOF`**`\n**`히로프`**\n**`Doheeeee`**\n**`Coral_Whale`**",
            inline=False)
        embed.add_field(name="Special Thanks",
                        value="**`NTG`**\n**`HighStrike!!`**\n**`Logi`**",
                        inline=False)
        await ctx.reply(embed=embed)

    @credits.error
    async def credits_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = '`(⩌ʌ ⩌;)` This command is ratelimited, please try again in **{:.2f} seconds**.'.format(
                error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    # Nickname [ID: 05]
    @commands.cooldown(rate=1, per=100, type=commands.BucketType.user)
    @commands.hybrid_command(name='nickname',
                             description="Change your nickname.")
    #@discord.app_commands.describe(name="Nickname to change")
    async def nickname(self, ctx, *, name: str = ""):
        user = ctx.author
        if name == "":
            await ctx.reply(
                "`(⩌Δ ⩌ ;)` Without a name, existence is worthless... A name is important to all dear ones..."
            )
        elif len(name) > 16:
            await ctx.reply(
                "`(⩌Δ ⩌ ;)` Nicknames are up to 16 characters long. Please choose something else..."
            )
        else:
            try:
                old = q.readTag(user)
                q.nickModify(user, name)
                new = q.readTag(user)
                await ctx.reply(
                    "`⸜(*◉ ᴗ ◉)⸝` By magic powers... your name has changed from `{}` to `{}`!"
                    .format(old, new))
            except:
                await ctx.reply("???")

    @nickname.error
    async def nickname_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = '`(⩌ʌ ⩌;)` This command is ratelimited, please try again in **{:.2f} seconds**.'.format(
                error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    # Discrim [ID: 06]
    @commands.cooldown(rate=1, per=100, type=commands.BucketType.user)
    @commands.hybrid_command(name='discrim',
                             description="Show your discriminator.")
    async def discrim(self, ctx, option: str = 'mydiscrim'):
        user = ctx.author
        if option == 'mydiscrim':
            await ctx.reply(
                "Discriminator is an identification number randomly assigned to each user!\nYour number is **#{}**! `⸜(*◉ ᴗ ◉)⸝`"
                .format(q.readDiscrim(user)))

    @discrim.error
    async def discrim_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = '`(⩌ʌ ⩌;)` This command is ratelimited, please try again in **{:.2f} seconds**.'.format(
                error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    # Bot Info [ID: 07]
    @commands.cooldown(rate=1, per=20, type=commands.BucketType.user)
    @commands.hybrid_command(name='argentumbot',
                             description="Bot related infomation")
    async def argentumbot(self, ctx):
        name = q.readTag(ctx.author)
        today = datetime.now()
        bday = datetime.strptime("20020801", "%Y%m%d")
        fday = datetime.strptime("20170520", "%Y%m%d")
        age = today.year - bday.year - ((today.month, today.day) <
                                        (bday.month, bday.day))

        embed = discord.Embed(
            title="Hello, I'm ArgentumBot",
            description=f"Current version: {Version} ({Update_Date})",
            color=0xCEDEBD)

        embed.set_thumbnail(url=self.client.user.avatar.url)

        embed.add_field(name="NAME",
                        value="Cyborg Eunbi (aka ArgentumBot)",
                        inline=False)

        embed.add_field(name="BIRTHDAY",
                        value=f"August 1 ({age}-year-old)",
                        inline=False)

        embed.add_field(name="Start date of Operation",
                        value=f"May 20, 2017 ({(today-fday).days+1:,d} days)",
                        inline=False)

        embed.set_footer(text="Developed by Dizzt")

        await ctx.reply(
            f":green_circle: **{name}**'s request completely loaded!!",
            embed=embed)

    @argentumbot.error
    async def arg_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = '`(⩌ʌ ⩌;)` This command is ratelimited, please try again in **{:.2f} seconds**.'.format(
                error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    # Ping [ID: 08]
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    @commands.hybrid_command(name='ping', description="Check client latency.")
    async def ping(self, ctx):
        msg = await ctx.reply(embed=discord.Embed(
            title="<a:load:1165572655202697216> LOADING..."))

        ping = self.client.latency * 1000
        latency = (msg.created_at.timestamp() -
                   ctx.message.created_at.timestamp()) * 1000

        def statusMark(ping):
            if ping >= 0 and ping < 500:
                return ":green_circle:"
            elif ping >= 500 and ping <= 1000:
                return ":yellow_circle:"
            elif ping >= 100 and ping <= 2000:
                return ":orange_circle:"
            elif ping >= 2000:
                return ":red_circle:"

        embed = discord.Embed(title="Pong!",
                              timestamp=datetime.now(),
                              color=0x999999)

        embed.add_field(name="Latency",
                        value=f"**{statusMark(latency)} {latency:.2f}**ms")

        embed.add_field(name="API Latency",
                        value=f"**{statusMark(ping)} {ping:.2f}**ms")

        embed.set_footer(text=f"{q.readTag(ctx.author)}",
                         icon_url=ctx.author.avatar.url)

        await msg.edit(embed=embed)

    @ping.error
    async def ping_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = '`(⩌ʌ ⩌;)` This command is ratelimited, please try again in **{:.2f} seconds**.'.format(
                error.retry_after)
            await ctx.send(msg)
        else:
            raise error
        
    # Daily [ID: 09]
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    @commands.hybrid_command(name='daily', description="Get daily rewards.")
    async def daily(self, ctx ,user:discord.Member = None):

        if user == None:
            user = ctx.author
        elif ctx.author != user:
            if ctx.author.id == 262517377575550977:
                pass
            else:
                user = ctx.author

        now = datetime.now()
        today = now.strftime('%Y-%m-%d')

        if q.readDailyDate(user) == today:
            msg = f"## :x: You have already received your reward today.\n**Come back tomorrow for your reward.**\n`Stack` {q.readDaily(ctx.author)} days\n`Next Rewards` **{etc.endOfDate()}** later"
            await ctx.reply(msg)
        
        else:
            daily = q.readDaily(user) + 1
            xp = 0
            money = 0

            if daily < 511:
                xp = 250 * (1 + (daily // 7)) + int(daily ** 1.6) - 1
                money = 100 * (1 + (daily // 7)) + int(daily ** 1.5) - 1
            else:
                xp = 40000
                money = 40000
            
            q.xpAdd(user, xp)
            q.moneyAdd(user, money)
            q.dailyAdd(user)
            q.dailyDateModify(user, today)

            msg = f"## :green_circle: You have received your daily reward!\n**+{xp:,d}XP | +${money:,d}**\n`Stack` {q.readDaily(user)} days\n`Next Rewards` **{etc.endOfDate()}** later"
            await ctx.reply(msg)

    @daily.error
    async def daily_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = '`(⩌ʌ ⩌;)` This command is ratelimited, please try again in **{:.2f} seconds**.'.format(
                error.retry_after)
            await ctx.send(msg)
        else:
            raise error
        
async def setup(client):
    await client.add_cog(Essential(client))
