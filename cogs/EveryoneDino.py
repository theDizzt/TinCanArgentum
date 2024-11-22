import discord
from discord.ext import commands
import fcts.sqlcontrol as q
import fcts.etcfunctions as etc
from config.rootdir import root_dir
import os
import fcts.koreanbreak as kb
import random as r
from datetime import datetime

#SERVER id
server_id = [
    262525769023094785, 716980478992711720, 1114816224522678294,
    453906917719408642
]


class EveryoneDino(commands.Cog):  # Cog를 상속하는 클래스를 선언

    def __init__(self, client: commands.Bot):  # 생성자 작성
        self.client = client

    async def is_server(ctx):
        return ctx.guild.id in server_id

    # 쿠모티콘! [ID: 32]
    @commands.hybrid_command(name='쿠모티콘', description="헬창냥이 김종국의 사진 대방출!")
    #@discord.app_commands.describe(type="옵션을 적어주세요")
    @commands.check(is_server)
    async def coomoji(self, ctx, type="도움"):
        if type == "도움":
            embed = discord.Embed(title="**도움말 입니당!**",
                                  description="",
                                  color=0xFFFF72)
            embed.add_field(
                name="가능한 명령어",
                value="쿠건달, 쿠기만, 쿠긴장, 쿠깡패, 쿠맥심, 쿠무룩, 쿠부릅, 쿠빼꼼, 쿠심심, 쿠일진, 쿠행복",
                inline=False)
            embed.set_thumbnail(
                url=
                "https://cdn.discordapp.com/attachments/526648786605441024/794085625862815754/cookiezleicon.png"
            )
            embed.set_footer(text="Provided by Dizzt", icon_url="")
            await ctx.reply(embed=embed)

        elif type == "쿠건달":
            await ctx.reply(
                "https://media.discordapp.net/attachments/526648786605441024/794077934390083604/1a47a584e7cbc3af.png?width=503&height=670"
            )

        elif type == "쿠긴장":
            await ctx.reply(
                "https://media.discordapp.net/attachments/526648786605441024/794077941667069952/a0f18b3d96227739.png?width=503&height=671"
            )

        elif type == "쿠깡패":
            await ctx.reply(
                "https://media.discordapp.net/attachments/526648786605441024/794077975956029440/b1de0b86664f6e2c.png?width=321&height=428"
            )

        elif type == "쿠맥심":
            await ctx.reply(
                "https://media.discordapp.net/attachments/526648786605441024/794077954456027156/f103ae7abbea7956.png?width=321&height=428"
            )

        elif type == "쿠무룩":
            await ctx.reply(
                "https://media.discordapp.net/attachments/526648786605441024/794077963594760242/c672207f61093215.png?width=321&height=428"
            )

        elif type == "쿠부릅":
            await ctx.reply(
                "https://media.discordapp.net/attachments/526648786605441024/794077943303372800/03d4fcaa7b16e455.png?width=321&height=428"
            )

        elif type == "쿠기만":
            await ctx.reply(
                "https://media.discordapp.net/attachments/526648786605441024/794077941508210708/89550f529dd8aba5.png?width=571&height=428"
            )

        elif type == "쿠빼꼼":
            await ctx.reply(
                "https://media.discordapp.net/attachments/526648786605441024/794077983555584000/1f857131eec553d5.png?width=321&height=428"
            )

        elif type == "쿠심심":
            await ctx.reply(
                "https://media.discordapp.net/attachments/526648786605441024/794077996923093022/29bced3311e422a7.png?width=571&height=428"
            )

        elif type == "쿠일진":
            await ctx.reply(
                "https://media.discordapp.net/attachments/526648786605441024/794078005093335100/00cb58bc92c494e2.png?width=321&height=428"
            )

        elif type == "쿠행복":
            await ctx.reply(
                "https://media.discordapp.net/attachments/526648786605441024/794078015310135326/087b38d4b6ed72e0.png?width=321&height=428"
            )

        elif type == "쿠적발":
            await ctx.reply(
                "https://media.discordapp.net/attachments/689051304953512004/1286697283139797085/b054b0851b0e96f7.png"
            )

        elif type == "쿠최후":
            await ctx.reply(
                "https://media.discordapp.net/attachments/689051304953512004/1286697288160514112/e11b12ebc9a2ab3c.png"
            )

        elif type == "쿠씨애":
            await ctx.reply(
                "https://media.discordapp.net/attachments/689051304953512004/1286697269848047666/a678fc906f93a33d.png"
            )

    @coomoji.error
    async def coomoji_error(error, ctx):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.reply("`전체공룡` 서버 전용 명령어 입니다!")

    # 카카오 데이터 관리 [ID: 98]
    @commands.command(name='카톡', description="...")
    @commands.check(is_server)
    async def kakao(self,
                    ctx,
                    option: str = None,
                    user: str = None,
                    value: int = 0):
        kakao = dict(
            민규=262520957233528832,
            충환=262517377575550977,
            주원=262899129276039169,
            대헌=263595595019583489,
            동건=262528817942364160,
            태형=262524430058520577,
            민성=236100097656487946,
            성훈=264763838673453056,
            영준=370800841055272972,
            승교=394075013541789700,
            선우=263640824170938369,
            승현=262551155815481345,
            민찬=512098892674760705,
            봇=(279909142955687936, 280900407021010944, 310386513236066306,
               310379466578722816, 1115471474250240050, 889173206454386689,
               310404488496283653),
            똥몬창=(544815696463396885, 487619829700886567, 277763741267918848,
                 503185794509438976, 422295213294354432, 429629511227670528,
                 811193433423216650, 265388034415919104))

        if option == "경험치":

            try:
                q.xpAddById(kakao[user], value)
                xp = q.readXpById(kakao[user])
                lv = etc.level(xp)
                xp1 = xp - etc.need_exp(lv - 1)
                xp2 = etc.need_exp(lv) - etc.need_exp(lv - 1)
                text = "[Level] {}, [XP] {:,d} / {:,d} ({:.2f}%), [Total] {:,d}".format(
                    lv, xp1, xp2, 100 * xp1 / xp2, xp)
                await ctx.reply(
                    "`⸜(*◉ ᴗ ◉)⸝` **{}**에게 **{}**의 경험치를 주었습니다!\n`변경 후` {}".
                    format(q.readTagById(kakao[user]), value, text))
            except:
                for u in kakao[user]:
                    q.xpAddById(u, value)
                    xp = q.readXpById(u)
                    lv = etc.level(xp)
                    xp1 = xp - etc.need_exp(lv - 1)
                    xp2 = etc.need_exp(lv) - etc.need_exp(lv - 1)
                    text = "[Level] {}, [XP] {:,d} / {:,d} ({:.2f}%), [Total] {:,d}".format(
                        lv, xp1, xp2, 100 * xp1 / xp2, xp)
                    await ctx.reply(
                        "`⸜(*◉ ᴗ ◉)⸝` **{}**에게 **{}**의 경험치를 주었습니다!\n`변경 후` {}".
                        format(q.readTagById(u), value, text))

        elif option == "돈":
            try:
                q.moneyAddById(kakao[user], value)
                mn = q.readMoneyById((kakao[user]))
                await ctx.reply(
                    f"`⸜(*◉ ᴗ ◉)⸝` **{q.readTagById(kakao[user])}**에게 **${value:,d}**의 돈을 주었습니다!\n현재 소지금액은 **${mn:,d}** 입니다!"
                )
            except:
                for u in kakao[user]:
                    q.moneyAddById(u, value)
                    mn = q.readMoneyById(u)
                    await ctx.reply(
                        f"`⸜(*◉ ᴗ ◉)⸝` **{q.readTagById(u)}**에게 **${value:,d}**의 돈을 주었습니다!\n현재 소지금액은 **${mn:,d}** 입니다!"
                    )

        elif option == "출석":
            data = [
                262520957233528832,
                262517377575550977,
                262899129276039169,
                263595595019583489,
                262528817942364160,
                262524430058520577,
                236100097656487946,
                264763838673453056,
                370800841055272972,
                394075013541789700,
                263640824170938369,
                262551155815481345,
                512098892674760705,
                279909142955687936,
                280900407021010944,
                310386513236066306,
                310379466578722816,
                1115471474250240050,
                889173206454386689,
                310404488496283653,
                544815696463396885,
                487619829700886567,
                277763741267918848,
                503185794509438976,
                422295213294354432,
                429629511227670528,
                811193433423216650,
                265388034415919104,
                341943143098482689,
                307366878551080975,
                387218121250832385
            ]

            result = ""

            now = datetime.now()
            today = now.strftime('%Y-%m-%d')

            for u in data:

                if q.readDailyDateById(u) == today and not(user == "1"):
                    result += f"**`{q.readTagById(u)}`**Already done!**\n"
                
                else:
                    daily = q.readDailyById(u) + 1
                    xp = 0
                    money = 0

                    if daily < 511:
                        xp = 250 * (1 + (daily // 7)) + int(daily ** 1.6) - 1
                        money = 100 * (1 + (daily // 7)) + int(daily ** 1.5) - 1
                    else:
                        xp = 40000
                        money = 40000
                    
                    q.xpAddById(u, xp)
                    q.moneyAddById(u, money)
                    q.dailyAddById(u)
                    q.dailyDateModifyById(u, today)

                    result += f"`{q.readTagById(u)}` | Day {daily} | +{xp}xp +${money}\n"

            await ctx.reply(result)

        elif option == "개인출석":
            u = kakao[user]
            t_xp = 0
            t_money = 0

            if value > 0:
                for i in range(value):

                    daily = q.readDailyById(u) + 1
                    xp = 0
                    money = 0

                    if daily < 511:
                        xp = 250 * (1 + (daily // 7)) + int(daily ** 1.6) - 1
                        money = 100 * (1 + (daily // 7)) + int(daily ** 1.5) - 1
                    else:
                        xp = 40000
                        money = 40000

                    t_xp += xp
                    t_money += money
                        
                    q.xpAddById(u, xp)
                    q.moneyAddById(u, money)
                    q.dailyAddById(u)

                q.dailyDateModifyById(u, today)

            result = f"`{q.readTagById(u)}` | Day {q.readDailyById(u)} | +{t_xp}xp +${t_money}"

            await ctx.reply(result)


        @kakao.error
        async def kakao_error(self, error, ctx):
            if isinstance(error, commands.CheckFailure):
                await ctx.reply("`전체공룡` 서버 전용 명령어 입니다!")

    @commands.command(name='kakaodata', description="...")
    @commands.check(is_server)
    async def kakaodata(self, ctx):

        kakao = dict(
            민규=262520957233528832,
            충환=262517377575550977,
            주원=262899129276039169,
            대헌=263595595019583489,
            동건=262528817942364160,
            태형=262524430058520577,
            민성=236100097656487946,
            성훈=264763838673453056,
            영준=370800841055272972,
            승교=394075013541789700,
            선우=263640824170938369,
            승현=262551155815481345,
            민찬=512098892674760705
            )
        
        path = root_dir + "/data/kakao"
        temp = dict()
        filelist = []

        datalist = os.listdir(path)

        for name in datalist:
            file = open(root_dir + "/data/kakao/" + name, "r", encoding='UTF8')
            filelist += file.readlines()
            os.remove(root_dir + "/data/kakao/" + name)
        
        for data in filelist:
            try:
                trim = data.replace("[", "")
                trim = trim.replace("\n", "")
                line = trim.split("] ")
                count = kb.count_break_korean(line[2])
                xp_gain = int((count * 0.3) * 4.6 + 1)
                money_gain = r.randint(5, 15)
                
                if line[0] in temp:
                    temp[line[0]][0] += xp_gain
                    temp[line[0]][1] += money_gain
                else:
                    temp[line[0]] = [xp_gain, money_gain]
                
            except:
                pass

        result = ""
        for user in temp.keys():
            q.xpAddById(kakao[user], temp[user][0])
            q.moneyAddById(kakao[user], temp[user][1])
            result += f"**`{q.readTagById(kakao[user])}`** | +{temp[user][0]}xp +${temp[user][1]}\n"
        
        await ctx.reply(result)

        
    @kakaodata.error
    async def kakaodata_error(self, error, ctx):
        if isinstance(error, commands.CheckFailure):
            await ctx.reply("`전체공룡` 서버 전용 명령어 입니다!")


async def setup(client):
    await client.add_cog(EveryoneDino(client))
