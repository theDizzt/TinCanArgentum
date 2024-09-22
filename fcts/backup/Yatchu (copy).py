#Module
import discord
from discord.ext import commands
import functions.sqlcontrol as q
import functions.etcfunctions as etc
import random
from time import sleep

player_badge = [
    "<:player1:1150445104692215989>", "<:player2:1150445106646745258>",
    "<:player3:1150445109867970570>", "<:player4:1150445113416364032>",
    "<:player5:1150445115110858752>", "<:player6:1150445118311108678>"
]

def iv(i):
    if i == -1:
        return ":black_large_square:"
    else:
        return ":white_check_mark:"


def iv2(i):
    if i < 63:
        return ":black_large_square:"
    else:
        return ":white_check_mark:"


# 2.4.1. Dice 8
def dt8(i):
    dice = [
        '0', '<:d1:1085510731669180456>', '<:d2:1085510735527944223>',
        '<:d3:1085510738057121839>', '<:d4:1085510742146560130>',
        '<:d5:1085510746143719524>', '<:d6:1085510749759221760>',
        '<:d7:1085510753580240976>', '<:d8:1085510757736775710>'
    ]
    return dice[i]


# 2.4.2. Dice 6
def dt6old(i):
    dice = [
        '0', '<:dice1:897853296767819806>', '<:dice2:897853296507752468>',
        '<:dice3:897853296755236914>', '<:dice4:897853297237569587>',
        '<:dice5:897853296591646740>', '<:dice6:897853297023664168>'
    ]
    return dice[i]


def dt6(i):
    dice = [
        '0', '<:dice1:1150612006777393152>', '<:dice2:1150612009541439508>',
        '<:dice3:1150612013727359027>', '<:dice4:1150612018580160563>',
        '<:dice5:1150612024284426301>', '<:dice6:1150612027505647678>'
    ]
    return dice[i]


#Data
dice = [0, 0, 0, 0, 0]
reroll = []

p1 = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
p2 = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
p3 = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
p4 = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
p5 = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
p6 = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]


#Dice
def rollDice(a=0):
    if a == 0:
        for i in range(5):
            dice[i] = random.randint(1, 6)
    else:
        dice[a - 1] = random.randint(1, 6)
    return dice


#Gameplay


def selectScore(sel, dice, array):
    #Numbers
    #01 Aces
    if sel == 1 and array[0] == -1:
        array[0] = dice.count(1)

    #02 Duces
    elif sel == 2 and array[1] == -1:
        array[1] = 2 * dice.count(2)

    #03
    elif sel == 3 and array[2] == -1:
        array[2] = 3 * dice.count(3)

    #04
    elif sel == 4 and array[3] == -1:
        array[3] = 4 * dice.count(4)

    #05
    elif sel == 5 and array[4] == -1:
        array[4] = 5 * dice.count(5)

    #06
    elif sel == 6 and array[5] == -1:
        array[5] = 6 * dice.count(6)

    #07 3카
    elif sel == 7 and array[6] == -1:
        array[6] = 0
        for item in [1, 2, 3, 4, 5, 6]:
            if dice.count(item) >= 3:
                array[6] = sum(dice)
                break

    #08 4카
    elif sel == 8 and array[7] == -1:
        array[7] = 0
        for item in [1, 2, 3, 4, 5, 6]:
            if dice.count(item) >= 4:
                array[7] = sum(dice)
                break

    #9 풀하우스(25)
    elif sel == 9 and array[8] == -1:
        val1 = dice.count(1)
        val2 = dice.count(2)
        val3 = dice.count(3)
        val4 = dice.count(4)
        val5 = dice.count(5)
        val6 = dice.count(6)
        if (val1 == 3 or val2 == 3 or val3 == 3 or val4 == 3 or val5 == 3
                or val6 == 3) and (val1 == 2 or val2 == 2 or val3 == 2
                                   or val4 == 2 or val5 == 2 or val6 == 2):
            array[8] = 25
        else:
            array[8] = 0

    #10 스스(20)
    elif sel == 10 and array[9] == -1:
        change_dice_result = list(set(dice))
        change_dice_result = sorted(change_dice_result)
        for i in range(1, 4):
            if (i in change_dice_result
                ) and (i + 1 in change_dice_result) and (
                    i + 2 in change_dice_result) and (i + 3
                                                      in change_dice_result):
                array[9] = 20
            elif array[9] != 20:
                array[9] = 0

    #11 라스(30)
    elif sel == 11 and array[10] == -1:
        change_dice_result = list(set(dice))
        change_dice_result = sorted(change_dice_result)
        for i in range(1, 3):
            if (i in change_dice_result) and (
                    i + 1 in change_dice_result
            ) and (i + 2 in change_dice_result) and (
                    i + 3 in change_dice_result) and (i + 4
                                                      in change_dice_result):
                array[10] = 30
            elif array[10] != 30:
                array[10] = 0

    #12 찬스
    elif sel == 12 and array[11] == -1:
        array[11] = sum(dice)

    #13 야추(50)
    elif sel == 13 and array[12] == -1:
        change_dice_result = set(dice)
        if len(change_dice_result) == 1:
            array[12] = 50
        else:
            array[12] = 0

    return None


#Score
def dataArray(a):
    if a == 1:
        return p1
    elif a == 2:
        return p2
    elif a == 3:
        return p3
    elif a == 4:
        return p4
    elif a == 5:
        return p5
    elif a == 6:
        return p6


def scoreCalc(array, opt=0):
    bonus = array[0] + array[1] + array[2] + array[3] + array[4] + array[
        5] + array[:6].count((-1))
    total = bonus + array[6] + array[7] + array[8] + array[9] + array[
        10] + array[11] + array[12] + array[6:].count((-1))
    if opt == 0:
        if bonus < 63:
            return total
        else:
            return total + 35
    elif opt == 1:
        return bonus


#Reset
def resetDice():
    global dice
    dice = [0, 0, 0, 0, 0]
    return None


def resetReroll():
    global reroll
    reroll = []
    return None


def resetScore():
    for i in range(13):
        p1[i] = -1
    for i in range(13):
        p2[i] = -1
    for i in range(13):
        p3[i] = -1
    for i in range(13):
        p4[i] = -1
    for i in range(13):
        p5[i] = -1
    for i in range(13):
        p6[i] = -1
    return None


class SelectDice(discord.ui.View):
  

    @discord.ui.button(label="1",
                       style=discord.ButtonStyle.gray,
                       emoji=dt6(dice[0]))
    async def button1(self, interection: discord.Interaction,
                      button: discord.ui.Button):
        if button.style == discord.ButtonStyle.gray:
            button.style = discord.ButtonStyle.green
            reroll.append(1)
        elif button.style == discord.ButtonStyle.green:
            button.style = discord.ButtonStyle.gray
            reroll.remove(1)
        await interection.response.edit_message(view=self)

    @discord.ui.button(label="2",
                       style=discord.ButtonStyle.gray,
                       emoji=dt6(dice[1]))
    async def button2(self, interection: discord.Interaction,
                      button: discord.ui.Button):
        if button.style == discord.ButtonStyle.gray:
            button.style = discord.ButtonStyle.green
            reroll.append(2)
        elif button.style == discord.ButtonStyle.green:
            button.style = discord.ButtonStyle.gray
            reroll.remove(2)
        await interection.response.edit_message(view=self)

    @discord.ui.button(label="3",
                       style=discord.ButtonStyle.gray,
                       emoji=dt6(dice[2]))
    async def button3(self, interection: discord.Interaction,
                      button: discord.ui.Button):
        if button.style == discord.ButtonStyle.gray:
            button.style = discord.ButtonStyle.green
            reroll.append(3)
        elif button.style == discord.ButtonStyle.green:
            button.style = discord.ButtonStyle.gray
            reroll.remove(3)
        await interection.response.edit_message(view=self)

    @discord.ui.button(label="4",
                       style=discord.ButtonStyle.gray,
                       emoji=dt6(dice[3]))
    async def button4(self, interection: discord.Interaction,
                      button: discord.ui.Button):
        if button.style == discord.ButtonStyle.gray:
            button.style = discord.ButtonStyle.green
            reroll.append(4)
        elif button.style == discord.ButtonStyle.green:
            button.style = discord.ButtonStyle.gray
            reroll.remove(4)
        await interection.response.edit_message(view=self)

    @discord.ui.button(label="5",
                       style=discord.ButtonStyle.gray,
                       emoji=dt6(dice[4]))
    async def button5(self, interection: discord.Interaction,
                      button: discord.ui.Button):
        if button.style == discord.ButtonStyle.gray:
            button.style = discord.ButtonStyle.green
            reroll.append(5)
        elif button.style == discord.ButtonStyle.green:
            button.style = discord.ButtonStyle.gray
            reroll.remove(5)
        await interection.response.edit_message(view=self)

    @discord.ui.button(label="ദ്ദി*ˊᗜˋ*) 결정이다!", style=discord.ButtonStyle.red)
    async def okay(self, interection: discord.Interaction,
                   button: discord.ui.Button):

        await interection.response.edit_message(view=self)


class SelectDiceTest(discord.ui.View):

    def __init__(self):
        super().__init__()

    global dice

    @discord.ui.button(label="1",
                       style=discord.ButtonStyle.gray,
                       emoji=discord.PartialEmoji.from_str(dt6(dice[0])))
    async def button1(self, interection: discord.Interaction,
                      button: discord.ui.Button):
        if button.style == discord.ButtonStyle.gray:
            button.style = discord.ButtonStyle.green
            reroll.append(1)
        elif button.style == discord.ButtonStyle.green:
            button.style = discord.ButtonStyle.gray
            reroll.remove(1)
        await interection.response.edit_message(view=self)


class Yatchu(commands.Cog):

    def __init__(self, client: commands.Bot):  # 생성자 작성
        self.client = client

    #Button Test
    @commands.hybrid_command(name='button', description="Button Test")
    async def buttontest(self, ctx):
        await ctx.send(
            "누르면 색깔이 바뀌는 버튼 입니다!\nIt's a button that changes color when you press it!",
            view=View())

    @commands.hybrid_command(name='button2', description="Button Test")
    async def buttontest2(self, ctx):
        rollDice(0)
        await ctx.send("테스트1", view=SelectDiceTest())

    #야추 다이스 [ID: 41]
    @commands.hybrid_command(name='야추다이스', description="야추한판 갈까요?")
    async def yatchu(self, ctx):
        gamestart = False
        betting = 0
        player = []
        player.append({"id": ctx.author.id, "score": 0})
        while True:
            embed = discord.Embed(title='참가자 목록',
                                  description=f'인원: {len(player)}/6',
                                  color=0xBCE29E)
            for i in range(len(player)):
                embed.add_field(
                    name=f"{player_badge[i]} {q.readTagById(player[i]['id'])}",
                    value=
                    f"Level {etc.level(q.readXpById(player[i]['id']))} | ${q.readMoneyById(player[i]['id']):,d}",
                    inline=False)
            embed.set_footer(text='Discord Bot by Dizzt')
            await ctx.reply(
                "## 야추다이스ㄱㄱ - 인원 모집\n* `@username`을 이용하여 최대 6명 까지 초대가 가능합니다!\n* 초대가 완료되면 `시작`를 입력해 주세요!\n* 게임 생성을 취소하고 싶다면 `취소`를 입력해 주세요!",
                embed=embed)

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            input_word = await self.client.wait_for("message", check=check)
            check = input_word.content

            if check == '시작':
                gamestart = True
                await ctx.send(":green_circle: 게임이 성공적으로 생성 되었습니다!")
                break

            elif check == '취소':
                await ctx.send(":x: 게임 생성이 취소되었습니다.")
                break

            else:
                try:
                    if len(player) >= 6:
                        await ctx.send(
                            '`(⩌ʌ ⩌;)` 인원이 너무 많습니다... 최대 6명 까지 참가가 가능합니다!')
                    else:
                        id = int(etc.extractUid(check))
                        name = q.readTagById(id)
                        player.append({"id": id, "score": 0})
                        await ctx.send(
                            f":green_circle: `{name}`가 참가자 목록에 추가되었습니다! ")
                except:
                    await ctx.send('`(⩌ʌ ⩌;)` 유효하지 않은 참가자 입니다... 다시 시도해 보세요...'
                                   )

        if gamestart:
            if len(player) == 1:
                await ctx.send('인원 수가 너무 적어 배팅 금액 없이 게임이 진행됩니다!')
            else:
                while True:
                    moneylist = []
                    for i in range(len(player)):
                        moneylist.append(q.readMoneyById(player[i]['id']))

                    await ctx.reply(
                        f"## 야추다이스ㄱㄱ - 배팅 금액\n* 단위 제외 숫자만 입력하여 배팅 금액을 지정해 주세요!\n금액은 최소 $0, 최대 ${min(moneylist)} 를 입력할 수 있습니다!",
                        embed=embed)

                    def check(m):
                        return m.author == ctx.author and m.channel == ctx.channel

                    input_word = await self.client.wait_for("message",
                                                            check=check)
                    try:
                        check = int(input_word.content)
                        if check >= 0 and check <= min(moneylist):
                            betting = check
                            await ctx.reply(
                                f":green_circle: 배팅 금액은 ${betting}으로 지정 되었습니다!"
                            )
                            break
                        else:
                            await ctx.send("`(⩌ʌ ⩌;)` 잘못된 금액을 입력 하였습니다...")
                    except:
                        await ctx.send("`(⩌ʌ ⩌;)` 잘못된 금액을 입력 하였습니다...")

                for i in range(len(player)):
                    q.moneyAddById(player[i]['id'], (-1) * betting)
            await ctx.send(f"인당 **${betting:,d}**가 베팅되었습니다. 잠시후 게임이 시작됩니다!")
            sleep(3)

            #Game
            for rn in range(13):  #인당 13번씩 게임 진행
                embed = discord.Embed(title="**총점**",
                                      description=f"`라운드: {rn +1} / 13`",
                                      color=0x22A699)

                for i in range(len(player)):
                    embed.add_field(
                        name=
                        f"{player_badge[i]} **{q.readTagById(player[i]['id'])}** (Lv. {etc.level(q.readXpById(player[i]['id']))})",
                        value=etc.numFont(scoreCalc(dataArray(i + 1), 0)),
                        inline=False)

                await ctx.send(embed=embed)

                for p in range(len(player)):
                    sleep(3)

                    temp2 = dataArray(p + 1)
                    totals = scoreCalc(temp2, 0)
                    bonuss = scoreCalc(temp2, 1)

                    embed = discord.Embed(
                        title=f"**{q.readTagById(player[p]['id'])}의 점수**",
                        description=f"`라운드: {rn + 1} / 13`",
                        color=0xF2BE22)
                    embed.add_field(
                        name="Upper Section",
                        value=
                        "`1` Ones {} {}\n`2` Twos {} {}\n`3` Threes {} {}\n`4` Fours {} {}\n`5` Fives {} {}\n`6` Sixes {} {}\n`Sp` Above 63 (+35p) `{}/63` {}"
                        .format(iv(temp2[0]), temp2[0], iv(temp2[1]), temp2[1],
                                iv(temp2[2]), temp2[2], iv(temp2[3]), temp2[3],
                                iv(temp2[4]), temp2[4], iv(temp2[5]), temp2[5],
                                bonuss, iv2(bonuss)),
                        inline=False)
                    embed.add_field(
                        name="Lower Section",
                        value=
                        "`7` 3 Kinds {} {}\n`8` 4 Kinds {} {}\n`9` Full House (+25p) {} {}\n`10` S-Straight (+20p) {} {}\n`11` L-Straight (+30p) {} {}\n`12` Chance {} {}\n`13` Yatch (+50p) {} {}"
                        .format(iv(temp2[6]), temp2[6], iv(temp2[7]), temp2[7],
                                iv(temp2[8]), temp2[8], iv(temp2[9]), temp2[9],
                                iv(temp2[10]), temp2[10], iv(temp2[11]),
                                temp2[11], iv(temp2[12]), temp2[12]),
                        inline=False)
                    embed.add_field(name="현재 점수:",
                                    value=etc.numFont(totals),
                                    inline=False)
                    await ctx.send(
                        f":green_circle: **{q.readTagById(player[p]['id'])}**의 차례입니다!\n첫 주사위는 자동으로 굴러갑니다!",
                        embed=embed)

                    sleep(1)

                    templ = rollDice()
                    await ctx.send(
                        f"**[1/2]** `{q.readTagById(player[p]['id'])}` 다시 던질 주사위를 선택해 주세요!\n{dt6(templ[0])} {dt6(templ[1])} {dt6(templ[2])} {dt6(templ[3])} {dt6(templ[4])}",
                        view=SelectDice())


async def setup(client):
    await client.add_cog(Yatchu(client))
