import discord
from discord.ext import commands
import fcts.sqlcontrol as q
import fcts.leaderboard as l
import fcts.lklab as lk
import yaml
import fcts.etcfunctions as etc
from config.rootdir import root_dir
import random as r

admin_login = []
with open(root_dir + '/config/admin.yml',encoding='UTF-8') as f:
    admins = yaml.load(f, Loader=yaml.FullLoader)


class Admins(commands.Cog):  # Cog를 상속하는 클래스를 선언

    def __init__(self, client: commands.Bot):  # 생성자 작성
        self.client = client

    # LKedit [ID: 87]
    @commands.command()
    async def lkedit(self,
                       ctx,
                       user: str = None,
                       option: str = None,
                       value: str = None,
                       svalue: str = None):
        if ctx.author.id in admin_login:

            u = int(etc.extractUid(user))

            if option == 'achievement':
                lk.achieveModifyById(u, int(value), int(svalue))
                await ctx.reply(
                    "`⸜(*◉ ᴗ ◉)⸝` Transformed data with magical powers...")

            elif option == 'startdate':
                lk.dateModifyById(u, str(value)+" "+str(svalue))
                await ctx.reply(
                    "`⸜(*◉ ᴗ ◉)⸝` Transformed data with magical powers...")

            elif option == 'create':
                lk.newAchieveById(u)
                await ctx.reply(
                    "`⸜(*◉ ᴗ ◉)⸝` Transformed data with magical powers...")

            else:
                await ctx.reply("Not allowed!")

        else:
            await ctx.reply("Not allowed!")


    # Admin Login [ID: 89]
    @commands.command()
    async def login(self, ctx, sid: str = None, spw: str = None):

        try:
            await ctx.message.delete()
        except:
            pass

        try:
            user = "UID" + str(ctx.author.id)

            if admins[user]['id'] == sid and admins[user]['pw'] == spw:
                global admin_login
                admin_login.append(ctx.author.id)
                await ctx.send(f"<@{ctx.author.id}> Logined!")
                print(admin_login)
            else:
                await ctx.send(f"<@{ctx.author.id}> Login Failed...")

        except:
            await ctx.send(f"<@{ctx.author.id}> no admin permissions allowed.")

    # Admin Logout [ID: 90]
    @commands.command()
    async def logout(self, ctx):
        if ctx.author.id in admin_login:
            admin_login.remove(ctx.author.id)
            await ctx.reply(f"<@{ctx.author.id}> Logouted!")
            print(admin_login)

    # XP Editing [ID: 91]
    @commands.hybrid_command(name='xp',
                             description="Give XP to selected user.")
    #@discord.app_commands.describe(user="User mention",amount="Write amount of XP to give")
    async def xp(self, ctx, user="all", amount=0):
        if (user == "all" or user == "전체") and ctx.author.id in admin_login:
            q.xpAddAll(int(amount))
            await ctx.reply(
                "**가입자 총원**은 성공적으로 **{}**의 경험치를 받았습니다!".format(amount))

        elif ctx.author.id in admin_login:
            u = int(etc.extractUid(user))
            q.xpAddById(u, int(amount))
            xp = q.readXpById(u)
            lv = etc.level(xp)
            xp1 = xp - etc.need_exp(lv - 1)
            xp2 = etc.need_exp(lv) - etc.need_exp(lv - 1)
            text = "[Level] {}, [XP] {:,d} / {:,d} ({:.2f}%), [Total] {:,d}".format(
                lv, xp1, xp2, 100 * xp1 / xp2, xp)
            await ctx.reply(
                "**{}**(은)는 성공적으로 **{}**의 경험치를 받았습니다!\n현재 경험치: {}".format(
                    q.readTagById(u), amount, text))

    # User List [ID: 92]
    @commands.command(aliases=['유저목록'])
    async def userlist(self, ctx):
        if ctx.author.id in admin_login:
            rank = q.userList()
            await ctx.send("출력을 시작합니다!")
            await ctx.send("총 데이터 수 : `{}`".format(len(rank)))
            for user in rank:
                await ctx.send(
                    "**{}**#{} ({}) | `{} / {}` | `Total : {:,d}`".format(
                        user[2],
                        str(user[1]).zfill(4), user[0], etc.level(user[3]),
                        etc.maxLevel(), user[3]))
            await ctx.send("출력이 끝났습니다!")

    # Rank List [ID: 93]
    @commands.command(aliases=['랭킹목록'])
    async def rankinglist(self, ctx):
        if ctx.author.id in admin_login:
            rank = q.xpRanking()
            rank_value = 1
            await ctx.send(":green_circle: 랭킹 리스트를 출력합니다! (시간이 오래 걸릴수도 있습니다)")

            for user in rank:
                await ctx.send(
                    "{} **{}**#{} | `{} / {}` | `Total : {:,d}`".format(
                        etc.numFont(rank_value), user[2],
                        str(user[1]).zfill(4), etc.level(user[3]),
                        etc.maxLevel(), user[3]))
                rank_value += 1

    @commands.command()
    async def rankingadd(self, ctx):
        if ctx.author.id in admin_login:
            rank = q.xpRanking()
            rank_value = 1
            xp = 100
            print(":green_circle: 랭킹 리스트를 출력합니다! (시간이 오래 걸릴수도 있습니다)")

            for user in rank:
                xp += r.randint(1,50)
                q.xpAddById(user[0], xp)
                print(
                    f"#{rank_value}. **{user[2]}**#{str(user[1]).zfill(4)} | `Total : {q.readXpById(user[0]):,d} (+{xp})`"
                )
                rank_value += 1

    # Leaderboard Edit [ID: 94]
    @commands.command()
    async def lbedit(self, ctx, user: str = None, option: str = None):
        if ctx.author.id in admin_login:
            u = int(etc.extractUid(user))
            if option == "mathgame":
                await ctx.reply("Format: `score/scoredate/count/countdate`")

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                input_word = await self.client.wait_for("message", check=check)
                check = input_word.content
                if check == "cancel":
                    await ctx.reply("`(⩌Δ ⩌ ;)` Cancelled.")
                else:
                    try:
                        result = check.split(",")
                        print(u, result)
                        l.mathDataForcedUpdate(u, int(result[0]),
                                               str(result[1]), int(result[2]),
                                               str(result[3]))
                        await ctx.reply(
                            "`⸜(*◉ ᴗ ◉)⸝` Transformed data with magical powers..."
                        )
                    except:
                        await ctx.reply("`(⩌Δ ⩌ ;)` Invalid format.")

            elif option == "rps":
                await ctx.reply(
                    "Format: `score/s-date/count/c-date/max/m-date/win/w-date/tie/t-date`"
                )

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                input_word = await self.client.wait_for("message", check=check)
                check = input_word.content
                if check == "cancel":
                    await ctx.reply("`(⩌Δ ⩌ ;)` Cancelled.")
                else:
                    try:
                        result = check.split(",")
                        print(u, result)
                        l.rpsDataForcedUpdate(u, int(result[0]),
                                              str(result[1]), int(result[2]),
                                              str(result[3]), int(result[4]),
                                              str(result[5]), int(result[6]),
                                              str(result[7]), int(result[8]),
                                              str(result[9]))
                        await ctx.reply(
                            "`⸜(*◉ ᴗ ◉)⸝` Transformed data with magical powers..."
                        )
                    except:
                        await ctx.reply("`(⩌Δ ⩌ ;)` Invalid format.")

            elif option == "wordchain":
                await ctx.reply(
                    "Format: `reg/i-score/i-count/i-play/i-win/b-score/b-count/m-half/m-full`"
                )

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                input_word = await self.client.wait_for("message", check=check)
                check = input_word.content
                if check == "cancel":
                    await ctx.reply("`(⩌Δ ⩌ ;)` Cancelled.")
                else:
                    try:
                        result = check.split(",")
                        print(u, result)
                        l.wcForcedUpdate(u, int(result[0]), int(result[1]),
                                         int(result[2]), int(result[3]),
                                         int(result[4]), int(result[5]),
                                         int(result[6]), int(result[7]),
                                         int(result[8]))
                        await ctx.reply(
                            "`⸜(*◉ ᴗ ◉)⸝` Transformed data with magical powers..."
                        )
                    except:
                        await ctx.reply("`(⩌Δ ⩌ ;)` Invalid format.")

            elif option == "yahtzee":
                await ctx.reply("Format: `score/score-date/play/wins`")

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                input_word = await self.client.wait_for("message", check=check)
                check = input_word.content
                if check == "cancel":
                    await ctx.reply("`(⩌Δ ⩌ ;)` Cancelled.")
                else:
                    try:
                        result = check.split(",")
                        print(u, result)
                        l.ytForcedUpdate(u, int(result[0]), str(result[1]),
                                         int(result[2]), int(result[3]))
                        await ctx.reply(
                            "`⸜(*◉ ᴗ ◉)⸝` Transformed data with magical powers..."
                        )
                    except:
                        await ctx.reply("`(⩌Δ ⩌ ;)` Invalid format.")

            else:
                await ctx.reply("`(⩌Δ ⩌ ;)` Invalid table name.")

    # Skin Unlock [ID: 95]
    @commands.hybrid_command(name='unlock', description="Unlock user's skin")
    @discord.app_commands.describe(user="User mention",
                                   skin="Integer only",
                                   lock="Binary only")
    async def unlock(self,
                     ctx,
                     user: discord.Member = None,
                     skin: int = None,
                     lock: int = 1):
        if ctx.author.id in admin_login:
            """
            try:
                user = etc.extractUid(obj)
            except:
                await ctx.reply("`(⩌Δ ⩌ ;)` Invalid User id...")
            """
            Rank = etc.storageLineRead('all')
            user_name = q.readTag(user)

            if lock == 1:
                if not q.readStorageById(user.id, skin):
                    q.storageModifyById(user.id, skin, 1)
                    await ctx.reply(
                        f":green_circle: **{user_name}** successfully unlocked `{Rank[skin - 1][0]}`!"
                    )
                else:
                    await ctx.reply(
                        f":exclamation: **{user_name}** already unlocked `{Rank[skin - 1][0]}`!"
                    )
            elif lock == 0:
                if q.readStorageById(user.id, skin):
                    q.storageModifyById(user.id, skin, 0)
                    await ctx.reply(
                        f":green_circle: **{user_name}** successfully locked `{Rank[skin - 1][0]}`!"
                    )
                else:
                    await ctx.reply(
                        f":exclamation: **{user_name}** already locked `{Rank[skin - 1][0]}`!"
                    )
            else:
                await ctx.reply("`(⩌Δ ⩌ ;)` Invalid option.")

    # Ultimate [ID: 96]
    @commands.command()
    async def ultimate(self,
                       ctx,
                       user: str = None,
                       option: str = None,
                       value: str = None):
        if ctx.author.id in admin_login:

            u = int(etc.extractUid(user))

            if option == 'xp':
                q.xpModifyById(u, int(value))
                await ctx.reply(
                    "`⸜(*◉ ᴗ ◉)⸝` Transformed data with magical powers...")

            elif option == 'money':
                q.moneyModifyById(u, int(value))
                await ctx.reply(
                    "`⸜(*◉ ᴗ ◉)⸝` Transformed data with magical powers...")

            elif option == 'skin':
                q.skinModifyById(u, int(value))
                await ctx.reply(
                    "`⸜(*◉ ᴗ ◉)⸝` Transformed data with magical powers...")

            elif option == 'discrim':
                q.discrimModifyById(u, int(value))
                await ctx.reply(
                    "`⸜(*◉ ᴗ ◉)⸝` Transformed data with magical powers...")

            elif option == 'nick':
                q.nickModifyById(u, str(value))
                await ctx.reply(
                    "`⸜(*◉ ᴗ ◉)⸝` Transformed data with magical powers...")

            elif option == 'startdate':
                q.startDateModifyById(u, str(value))
                await ctx.reply(
                    "`⸜(*◉ ᴗ ◉)⸝` Transformed data with magical powers...")

            elif option == 'create':
                q.newAccountById(u, str(value))
                await ctx.reply(
                    "`⸜(*◉ ᴗ ◉)⸝` Transformed data with magical powers...")
                
            elif option == 'storage':
                q.newStorageById(u)
                await ctx.reply(
                    "`⸜(*◉ ᴗ ◉)⸝` Transformed data with magical powers...")
                
            elif option == 'daily':
                q.dailyModifyById(u, str(value))
                await ctx.reply(
                    "`⸜(*◉ ᴗ ◉)⸝` Transformed data with magical powers...")

            else:
                await ctx.reply("Not allowed!")

        else:
            await ctx.reply("Not allowed!")

    # Money Editing [ID: 97]
    @commands.hybrid_command(name='money',
                             description="Give money to selected user.")
    #@discord.app_commands.describe(user="User mention",amount="Write amount of money to give")
    async def money(self, ctx, user: str = "all", amount: int = 0):
        if (user == "all" or user == "전체") and ctx.author.id in admin_login:
            q.moneyAddAll(amount)
            await ctx.reply(f"**가입자 총원**은 성공적으로 **{amount:,d}$**의 돈을 받았습니다!")

        elif ctx.author.id in admin_login:
            u = int(etc.extractUid(user))
            q.moneyAddById(u, amount)
            mn = q.readMoneyById(u)
            await ctx.reply(
                f"**{q.readTagById(u)}**(은)는 성공적으로 **{amount:,d}$**의 돈을 받았습니다!\n현재 소지 금액: **${mn:,d}**"
            )


async def setup(client):  # setup 함수로 cog를 추가한다.
    await client.add_cog(Admins(client))
