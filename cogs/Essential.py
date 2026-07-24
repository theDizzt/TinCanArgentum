import discord
import os
from discord.ext import commands
from discord import app_commands
import fcts.i18n_runtime as i18n
import fcts.sqlcontrol as q
import yaml
import fcts.etcfunctions as etc
from datetime import datetime
from config.rootdir import root_dir
from config.settings import get_required_env

with open(root_dir + '/config/help.yml',encoding='UTF-8') as f:
    helps = yaml.load(f, Loader=yaml.FullLoader)

prefix = get_required_env('BOT_PREFIX')
Version = get_required_env('APP_VERSION')
Update_Date = get_required_env('APP_VERSION_DATE')


class Essential(commands.Cog):  # Cog를 상속하는 클래스를 선언

    def __init__(self, client: commands.Bot):  # 생성자 작성
        self.client = client

    # Help [ID: 00]
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    @commands.hybrid_command(
        name=app_commands.locale_str("help", key="cmd.00.name"),
        description=app_commands.locale_str("Show help", key="cmd.00.desc"),
        aliases=["도움말", "ヘルプ"]
    )
    #@discord.app_commands.describe(command='Command to be explained.')
    async def help(self, ctx, command: str = "main"):
        if command == "main":
            embed = discord.Embed(
                title=i18n.t(ctx.author, "cmd.00.t001"),
                description=
                "Type `;help <command>` for more help. eg> `;help emblem`",
                color=0x78C1F3)

            # Essentials
            embed.add_field(name=i18n.t(ctx.author, "cmd.00.t002"),
                            value=helps[command]['Essentials'],
                            inline=True)

            # User Profile
            embed.add_field(name=i18n.t(ctx.author, "cmd.00.t003"),
                            value=helps[command]['UserProfile'],
                            inline=True)

            embed.add_field(name=i18n.t(ctx.author, "cmd.00.t004"),
                            value=helps[command]['Social'],
                            inline=True)

            embed.add_field(name=i18n.t(ctx.author, "cmd.00.t005"),
                            value=helps[command]['Miscellaneous'],
                            inline=True)

            embed.add_field(name=i18n.t(ctx.author, "cmd.00.t006"),
                            value=helps[command]['Coalition'],
                            inline=True)

            embed.add_field(name=i18n.t(ctx.author, "cmd.00.t007"),
                            value=helps[command]['Minigame'],
                            inline=True)
            
            embed.add_field(name=i18n.t(ctx.author, "cmd.00.t008"),
                            value=helps[command]['Voice'],
                            inline=True)

            embed.add_field(
                name=i18n.t(ctx.author, "cmd.00.t009"),
                value=helps[command]['WagyumonServer'],
                inline=True)

            embed.add_field(name=i18n.t(ctx.author, "cmd.00.t010"),
                            value=helps[command]['AdminFeatures'],
                            inline=True)

            embed.add_field(name=i18n.t(ctx.author, "cmd.00.t011"),
                            value=helps[command]['AdminDebugging'],
                            inline=True)

        else:
            try:
                embed = discord.Embed(
                    title=
                    f":notebook_with_decorative_cover: **{helps[command]['title']}** `ID: {helps[command]['id']}`",
                    description=
                    f"`{prefix}{helps[command]['ctx']}`",
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
            i18n.t(ctx.author, "reply.complete", name=q.readTag(ctx.author)),
            embed=embed)

    @help.error
    async def help_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    # Test Command [ID: 01]
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    @commands.hybrid_command(
        name=app_commands.locale_str("test", key="cmd.01.name"),
        description=app_commands.locale_str("Send test message", key="cmd.01.desc"),
        aliases=["테스트"]
        )
    async def test(self, ctx, *, arg: str = "Hello World!"):
        await ctx.reply(arg)

    @test.error
    async def test_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    # Id Viewer [ID: 02]
    @commands.cooldown(rate=1, per=20, type=commands.BucketType.user)
    @commands.hybrid_command(
        name=app_commands.locale_str("myid", key="cmd.02.name"),
        description=app_commands.locale_str("Show your discord user id and account creation date", key="cmd.02.desc"),
        aliases=["내아이디"])
    async def myid(self, ctx):
        uid = ctx.author.id
        udate = ctx.author.created_at.strftime("%a %#d %B %Y, %I:%M %p")
        await ctx.reply(i18n.t(ctx.author, "cmd.02.t001", uid=uid, udate=udate))

    @myid.error
    async def myid_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    # Credits [ID: 03]
    @commands.cooldown(rate=1, per=20, type=commands.BucketType.user)
    @commands.hybrid_command(
        name=app_commands.locale_str("credits", key="cmd.03.name"),
        description=app_commands.locale_str("Show developers of this bot", key="cmd.03.desc"),
        aliases=["제작자"]
        )
    async def credits(self, ctx):
        embed = discord.Embed(
            title=i18n.t(ctx.author, "cmd.03.t003"),
            description=i18n.t(ctx.author, "cmd.03.t004"),
            color=0xF8FDCF)
        embed.add_field(
            name=i18n.t(ctx.author, "cmd.03.t005"),
            value=i18n.t(ctx.author, "cmd.03.t006"),
            inline=False)
        embed.add_field(
            name=i18n.t(ctx.author, "cmd.03.t007"),
            value=i18n.t(ctx.author, "cmd.03.t008"),
            inline=False)
        embed.add_field(
            name=i18n.t(ctx.author, "cmd.03.t011"),
            value=i18n.t(ctx.author, "cmd.03.t012"),
            inline=False)
        embed.add_field(name="",
                        value="",
                        inline=False)
        await ctx.reply(embed=embed)

    @credits.error
    async def credits_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    # Nickname [ID: 05]
    @commands.cooldown(rate=1, per=100, type=commands.BucketType.user)
    @commands.hybrid_command(
        name=app_commands.locale_str("nickname", key="cmd.05.name"),
        description=app_commands.locale_str("Change your nickname", key="cmd.05.desc"),
        aliases=["nick", "별명"]
    )
    async def nickname(self, ctx, *, name: str = ""):
        user = ctx.author
        if name == "":
            await ctx.reply(
                i18n.t(ctx.author, "cmd.05.error1")
            )
        elif len(name) > 16:
            await ctx.reply(
                i18n.t(ctx.author, "cmd.05.error2")
            )
        else:
            try:
                old = q.readTag(user)
                q.nickModify(user, name)
                new = q.readTag(user)
                await ctx.reply(i18n.t(ctx.author, "cmd.05.accept", old=old, new=new))
            except:
                await ctx.reply("???")

    @nickname.error
    async def nickname_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    # Discrim [ID: 06]
    @commands.cooldown(rate=1, per=100, type=commands.BucketType.user)
    @commands.hybrid_command(
        name=app_commands.locale_str("discrim", key="cmd.06.name"),
        description=app_commands.locale_str("Show your discriminator", key="cmd.06.desc"),
        aliases=["식별번호"]
    )
    async def discrim(self, ctx, option: str = 'mydiscrim'):
        user = ctx.author
        if option == 'mydiscrim':
            await ctx.reply(i18n.t(ctx.author, "cmd.06.accept", discrim=q.readDiscrim(user)))

    @discrim.error
    async def discrim_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    # Bot Info [ID: 07]
    @commands.cooldown(rate=1, per=20, type=commands.BucketType.user)
    @commands.hybrid_command(
        name=app_commands.locale_str("argentumbot", key="cmd.07.name"),
        description=app_commands.locale_str("Bot related infomation", key="cmd.07.desc"),
        aliases=["깡통은비"]
    )
    async def argentumbot(self, ctx):
        name = q.readTag(ctx.author)
        today = datetime.now()
        bday = datetime.strptime("20020801", "%Y%m%d")
        fday = datetime.strptime("20170520", "%Y%m%d")
        age = today.year - bday.year - ((today.month, today.day) <
                                        (bday.month, bday.day))

        embed = discord.Embed(
            title=i18n.t(ctx.author, "cmd.07.t001"),
            description=i18n.t(ctx.author, "cmd.07.t002", ver=Version, date=Update_Date),
            color=0xCEDEBD)

        embed.set_thumbnail(url=self.client.user.avatar.url)

        embed.add_field(name=i18n.t(ctx.author, "cmd.07.t003"),
                        value=i18n.t(ctx.author, "cmd.07.t004"),
                        inline=False)

        embed.add_field(name=i18n.t(ctx.author, "cmd.07.t005"),
                        value=i18n.t(ctx.author, "cmd.07.t006", age=age),
                        inline=False)

        embed.add_field(name=i18n.t(ctx.author, "cmd.07.t007"),
                        value=i18n.t(ctx.author, "cmd.07.t008", days=(today-fday).days+1),
                        inline=False)

        embed.set_footer(text=i18n.t(ctx.author, "cmd.dev.footer"))

        await ctx.reply(
            i18n.t(ctx.author, "reply.complete", name=name),
            embed=embed)

    @argentumbot.error
    async def arg_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    # Ping [ID: 08]
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    @commands.hybrid_command(
        name=app_commands.locale_str("ping", key="cmd.08.name"),
        description=app_commands.locale_str("Check client latency", key="cmd.08.desc"),
        aliases=["핑"]
    )
    async def ping(self, ctx):
        msg = await ctx.reply(embed=discord.Embed(
            title=i18n.t(ctx.author, "cmd.08.t001")))

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

        embed = discord.Embed(title=i18n.t(ctx.author, "cmd.08.t002"),
                              timestamp=datetime.now(),
                              color=0x999999)

        embed.add_field(name=i18n.t(ctx.author, "cmd.08.t003"),
                        value=f"**{statusMark(latency)} {latency:.2f}**ms")

        embed.add_field(name=i18n.t(ctx.author, "cmd.08.t004"),
                        value=f"**{statusMark(ping)} {ping:.2f}**ms")

        embed.set_footer(text=f"{q.readTag(ctx.author)}",
                         icon_url=ctx.author.avatar.url)

        await msg.edit(embed=embed)

    @ping.error
    async def ping_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            raise error
        
    # Daily [ID: 09]
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    @commands.hybrid_command(
        name=app_commands.locale_str("daily", key="cmd.09.name"),
        description=app_commands.locale_str("Get daily rewards", key="cmd.09.desc"),
        aliases=["출석", "출석체크"]
    )
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
            msg = i18n.t(ctx.author, "cmd.09.error", stack=q.readDaily(ctx.author), remain=etc.endOfDate())
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
                money = 20000
            
            q.xpAdd(user, xp)
            q.moneyAdd(user, money)
            q.dailyAdd(user)
            q.dailyDateModify(user, today)

            msg = i18n.t(ctx.author, "cmd.09.accept", xp=xp, money=money, stack=q.readDaily(user), remain=etc.endOfDate())
            await ctx.reply(msg)

    @daily.error
    async def daily_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = '`(⩌ʌ ⩌;)` This command is ratelimited, please try again in **{:.2f} seconds**.'.format(
                error.retry_after)
            await ctx.send(msg)
        else:
            raise error
        
    # 서버별 기능 설정 [ID: 78]
        
    # 언어 설정 [ID: 79]
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    @commands.hybrid_command(
        name=app_commands.locale_str("language", key="cmd.79.name"),
        description=app_commands.locale_str("Change the default language", key="cmd.79.desc"),
        aliases=["언어"]
    )
    async def language(self, ctx, lang:str = None):

        available = ['ko', 'en', 'ja']
        if lang == None:
            current = q.readLanguage(ctx.author)
            if current == "ko":
                await ctx.reply("현재 언어는 한국어입니다.")
            elif current == "en":
                await ctx.reply("Your current language is English.")
            elif current == "ja":
                await ctx.reply("現在の言語は日本語です。")

        elif lang in available:
            q.modifyLanguage(ctx.author, lang)
            current = q.readLanguage(ctx.author)
            if current == "ko":
                await ctx.reply("현재 언어는 한국어입니다.")
            elif current == "en":
                await ctx.reply("Your current language is English.")
            elif current == "ja":
                await ctx.reply("現在の言語は日本語です。")
        
        else:
            pass

    @language.error
    async def language_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            raise error
        
async def setup(client):
    await client.add_cog(Essential(client))
