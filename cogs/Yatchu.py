#Module
import discord
from discord.ext import commands
import fcts.sqlcontrol as q
import fcts.etcfunctions as etc
import fcts.leaderboard as l
import random
from time import sleep

player_badge = [
    "<:player1:1150445104692215989>", "<:player2:1150445106646745258>",
    "<:player3:1150445109867970570>", "<:player4:1150445113416364032>",
    "<:player5:1150445115110858752>", "<:player6:1150445118311108678>"
]


class GameScreen(discord.ui.View):

    #Data
    dice = [0, 0, 0, 0, 0]
    reroll = []

    script = [
        "1이 나온 주사위들 눈의 총합", "2가 나온 주사위들 눈의 총합", "3이 나온 주사위들 눈의 총합",
        "4가 나온 주사위들 눈의 총합", "5가 나온 주사위들 눈의 총합", "6이 나온 주사위들 눈의 총합",
        "같은 숫자가 3개 나옴", "같은 숫자가 4개 나옴", "쓰리 카드와 원 페어의 조합", "4개의 연속된 숫자가 나옴",
        "5개의 연속된 숫자가 나옴", "주사위들 눈의 총합", "똑같은 숫자가 5개 나옴"
    ]

    emoji = [
        '0', '<:dice1:1150612006777393152>', '<:dice2:1150612009541439508>',
        '<:dice3:1150612013727359027>', '<:dice4:1150612018580160563>',
        '<:dice5:1150612024284426301>', '<:dice6:1150612027505647678>',
        '<:3k:1163790230621524010>', '<:4k:1163790233872121878>',
        '<:fh:1163790238318067722>', '<:ss:1163790244194291723>',
        '<:ls:1163790240599785502>', '<:choice:1163790235432390656>',
        '<:yt:1163790249445560364>'
    ]

    player_badge = [
        "<:player1:1150445104692215989>", "<:player2:1150445106646745258>",
        "<:player3:1150445109867970570>", "<:player4:1150445113416364032>",
        "<:player5:1150445115110858752>", "<:player6:1150445118311108678>"
    ]

    color = [0xF3B0C3, 0xFFCCB6, 0xFFFF72, 0xADDCC8, 0xABDEE6, 0xCBAACB]

    #Score Board
    round = 1
    seq = 0
    chance = 0
    move = 1
    action = -1
    end = False

    #Menu List
    options = [
        discord.SelectOption(label='1) 에이스/일레기통',
                             description='준비중',
                             emoji=discord.PartialEmoji.from_str(emoji[1])),
        discord.SelectOption(label='2) 듀스',
                             description='준비중',
                             emoji=discord.PartialEmoji.from_str(emoji[2])),
        discord.SelectOption(label='3) 쓰리즈',
                             description='준비중',
                             emoji=discord.PartialEmoji.from_str(emoji[3])),
        discord.SelectOption(label='4) 포즈',
                             description='준비중',
                             emoji=discord.PartialEmoji.from_str(emoji[4])),
        discord.SelectOption(label='5) 파이브즈',
                             description='준비중',
                             emoji=discord.PartialEmoji.from_str(emoji[5])),
        discord.SelectOption(label='6) 식스즈',
                             description='준비중',
                             emoji=discord.PartialEmoji.from_str(emoji[6])),
        discord.SelectOption(label='7) 쓰리카인즈',
                             description='준비중',
                             emoji=discord.PartialEmoji.from_str(emoji[7])),
        discord.SelectOption(label='8) 포카인즈',
                             description='준비중',
                             emoji=discord.PartialEmoji.from_str(emoji[8])),
        discord.SelectOption(label='9) 풀하우스',
                             description='준비중',
                             emoji=discord.PartialEmoji.from_str(emoji[9])),
        discord.SelectOption(label='10) 스몰스트레이트',
                             description='준비중',
                             emoji=discord.PartialEmoji.from_str(emoji[10])),
        discord.SelectOption(label='11) 라지스트레이트',
                             description='준비중',
                             emoji=discord.PartialEmoji.from_str(emoji[11])),
        discord.SelectOption(label='12) 찬스',
                             description='준비중',
                             emoji=discord.PartialEmoji.from_str(emoji[12])),
        discord.SelectOption(label='13) 야추',
                             description='준비중',
                             emoji=discord.PartialEmoji.from_str(emoji[13]))
    ]

    def playerList(self):
        result = []
        for i in range(len(self.player)):

            b = self.player_badge[i]
            uid = self.player[i]['id']
            n = q.readTagById(uid)
            s = self.player[i]['score']

            result.append(
                discord.SelectOption(label=f"{i+1}) {n}",
                                     description=f"{s}점 | 점수판 보기",
                                     emoji=discord.PartialEmoji.from_str(b)))

        return result

    def iv1(self, i):
        if i == -1:
            return ":black_large_square:"
        else:
            return ":white_check_mark:"

    def iv2(self, i):
        if i < 63:
            return ":black_large_square:"
        else:
            return ":white_check_mark:"

    #Roll Dice
    def rollDice(self, a: int = 0):
        if a == 0:
            for i in range(5):
                self.dice[i] = random.randint(1, 6)
        else:
            self.dice[a - 1] = random.randint(1, 6)
        return None

    #score calculate
    def scoreCalc(self, array, opt=0):
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

    def selectScore(self, sel, dice, array):
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
                if (i in change_dice_result) and (
                        i + 1 in change_dice_result) and (
                            i + 2
                            in change_dice_result) and (i + 3
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
                        i + 1 in change_dice_result) and (
                            i + 2 in change_dice_result) and (
                                i + 3 in change_dice_result) and (
                                    i + 4 in change_dice_result):
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

    def showScore(self, sel, dice):
        #01 Aces
        if sel == 1:
            return dice.count(1)

        #02 Duces
        elif sel == 2:
            return 2 * dice.count(2)

        #03
        elif sel == 3:
            return 3 * dice.count(3)

        #04
        elif sel == 4:
            return 4 * dice.count(4)

        #05
        elif sel == 5:
            return 5 * dice.count(5)

        #06
        elif sel == 6:
            return 6 * dice.count(6)

        #07 3카
        elif sel == 7:
            result = 0
            for item in [1, 2, 3, 4, 5, 6]:
                if dice.count(item) >= 3:
                    result = sum(dice)
                    break
            return result

        #08 4카
        elif sel == 8:
            result = 0
            for item in [1, 2, 3, 4, 5, 6]:
                if dice.count(item) >= 4:
                    result = sum(dice)
                    break
            return result

        #9 풀하우스(25)
        elif sel == 9:
            val1 = dice.count(1)
            val2 = dice.count(2)
            val3 = dice.count(3)
            val4 = dice.count(4)
            val5 = dice.count(5)
            val6 = dice.count(6)
            if (val1 == 3 or val2 == 3 or val3 == 3 or val4 == 3 or val5 == 3
                    or val6 == 3) and (val1 == 2 or val2 == 2 or val3 == 2
                                       or val4 == 2 or val5 == 2 or val6 == 2):
                return 25
            else:
                return 0

        #10 스스(20)
        elif sel == 10:
            result = 0
            change_dice_result = list(set(dice))
            change_dice_result = sorted(change_dice_result)
            for i in range(1, 4):
                if (i in change_dice_result) and (
                        i + 1 in change_dice_result) and (
                            i + 2
                            in change_dice_result) and (i + 3
                                                        in change_dice_result):
                    result = 20
                    break

            return result

        #11 라스(30)
        elif sel == 11:
            result = 0
            change_dice_result = list(set(dice))
            change_dice_result = sorted(change_dice_result)
            for i in range(1, 3):
                if (i in change_dice_result) and (
                        i + 1 in change_dice_result) and (
                            i + 2 in change_dice_result) and (
                                i + 3 in change_dice_result) and (
                                    i + 4 in change_dice_result):
                    result = 30
                    break
            return result

        #12 찬스
        elif sel == 12:
            return sum(dice)

        #13 야추(50)
        elif sel == 13:
            change_dice_result = set(dice)
            if len(change_dice_result) == 1:
                return 50
            else:
                return 0

    #game play
    async def send(self, ctx):
        self.message = await ctx.send(view=self)
        await self.update_message()

    async def update_message(self):
        b = self.player_badge[self.seq]
        n = q.readTagById(self.player[self.seq]['id'])

        if self.player[self.seq]['array'][12] == 0 and len(set(
                self.dice)) == 1 and q.readStorageById(
                    self.player[self.seq]['id'], 63) == 0:
            q.storageModifyById(self.player[self.seq]['id'], 63, 1)

        self.action += 1
        self.update_buttons()
        await self.message.edit(
            content=
            f"**[ROUND: {self.round} | MOVES: {self.move}]** {b}`{n}`의 차례입니다! ({self.chance}/2)\n<@{self.player[self.seq]['id']}>",
            embed=self.create_embed(),
            view=self)

    def create_embed(self):
        temp = self.player[self.seq]['array']
        bscore = self.scoreCalc(temp, 1)
        tscore = self.player[self.seq]['score']

        text0 = ""

        for i in range(len(self.player)):
            uid = self.player[i]['id']
            n = q.readTagById(uid)
            l = etc.level(q.readXpById(uid))
            s = self.player[i]['score']
            b = self.player_badge[i]
            if i == 0:
                t = f"{b}{etc.lvicon(l)}{n}: **{s}**"
            else:
                t = f"\n{b}{etc.lvicon(l)}{n}: **{s}**"
            text0 += t

        text1 = f"""
{self.iv1(temp[0])}{self.emoji[1]} 에이스 `{temp[0]}`
{self.iv1(temp[1])}{self.emoji[2]} 듀우스 `{temp[1]}`
{self.iv1(temp[2])}{self.emoji[3]} 쓰리즈 `{temp[2]}`
{self.iv1(temp[3])}{self.emoji[4]} 포오즈  `{temp[3]}`
{self.iv1(temp[4])}{self.emoji[5]} 파이브 `{temp[4]}`
{self.iv1(temp[5])}{self.emoji[6]} 식스즈  `{temp[5]}`
{self.iv2(bscore)}:small_orange_diamond: 보너스 `{bscore}/63`
        """

        text2 = f"""
{self.iv1(temp[6])}{self.emoji[7]} 쓰카 `{temp[6]}`
{self.iv1(temp[7])}{self.emoji[8]} 포카 `{temp[7]}`
{self.iv1(temp[8])}{self.emoji[9]} 풀하 `{temp[8]}`
{self.iv1(temp[9])}{self.emoji[10]} 스스 `{temp[9]}`
{self.iv1(temp[10])}{self.emoji[11]} 라스 `{temp[10]}`
{self.iv1(temp[11])}{self.emoji[12]} 찬스 `{temp[11]}`
{self.iv1(temp[12])}{self.emoji[13]} 야추 `{temp[12]}`
        """

        embed = discord.Embed(title="**Score Table**",
                              description=f"나의 점수: {etc.numFont(tscore)}",
                              color=self.color[self.seq])

        embed.add_field(name="상단부", value=text1, inline=True)

        embed.add_field(name="하단부", value=text2, inline=True)

        embed.add_field(name="점수", value=text0, inline=False)

        embed.set_footer(
            text=
            f"Round: {self.round} | Moves: {self.move} | Actions: {self.action}"
        )

        return embed

    async def update_end_message(self):
        self.action += 1
        cnt = len(self.player)
        self.move = cnt * 13
        result = []
        print(cnt)
        for i in range(cnt):
            uid = self.player[i]['id']
            b = self.player_badge[i]
            n = q.readTagById(uid)
            s = self.player[i]['score']
            result.append([uid, b, n, s])

            if s >= 261 and q.readStorageById(uid, 50) == 0:
                q.storageModifyById(uid, 50, 1)
            elif s == 0 and q.readStorageById(uid, 64) == 0:
                q.storageModifyById(uid, 64, 1)

        result.sort(key=lambda x: -x[3])

        embed = discord.Embed(title="**Result**", color=0x999999)

        for i in range(cnt):
            temp = result[i]
            print(3)
            xp = int(temp[3] * (1 + (0.22 * (cnt - i))))
            money = int(self.betting * 2.91 * ((cnt - i)**2) / (cnt**2))
            q.xpAddById(temp[0], xp)
            q.moneyAddById(temp[0], money)
            print(4)

            if cnt > 1 and i == 0:
                l.ytUpdate(temp[0], temp[3], True)
            else:
                l.ytUpdate(temp[0], temp[3], False)

            print(5)

            tt = f"`{i+1}등` {temp[1]}{etc.lvicon(etc.level(q.readXpById(temp[0])))}{temp[2]}"
            tb = f"**{temp[3]}점** | +{xp:,d}XP, +${money:,d}"
            embed.add_field(name=tt, value=tb, inline=False)

        print(6)

        embed.set_footer(
            text=
            f"Round: {self.round} | Moves: {self.move} | Actions: {self.action}"
        )

        self.end = True
        self.callback.options = self.playerList()
        self.dice1.disabled = True
        self.dice2.disabled = True
        self.dice3.disabled = True
        self.dice4.disabled = True
        self.dice5.disabled = True
        self.okay.disabled = True

        await self.message.edit(
            content=f"**[ROUND: {self.round} | MOVES: {self.move}]** 게임 끝!",
            embed=embed,
            view=self)

    async def update_result_message(self):
        await self.message.edit(embed=self.create_embed(), view=self)

    def update_buttons(self):

        for i in range(13):
            if self.player[self.seq]['array'][i] == -1:
                self.callback.options[
                    i].description = f"{self.showScore(i+1, self.dice)}점 | {self.script[i]}"
            else:
                self.callback.options[i].description = "등록 완료"

        self.okay.label = f"ദ്ദി*ˊᗜˋ*) 결정이다! ({self.chance}/2)"
        self.dice1.emoji = discord.PartialEmoji.from_str(
            self.emoji[self.dice[0]])
        self.dice1.label = str(self.dice[0])
        self.dice2.emoji = discord.PartialEmoji.from_str(
            self.emoji[self.dice[1]])
        self.dice2.label = str(self.dice[1])
        self.dice3.emoji = discord.PartialEmoji.from_str(
            self.emoji[self.dice[2]])
        self.dice3.label = str(self.dice[2])
        self.dice4.emoji = discord.PartialEmoji.from_str(
            self.emoji[self.dice[3]])
        self.dice4.label = str(self.dice[3])
        self.dice5.emoji = discord.PartialEmoji.from_str(
            self.emoji[self.dice[4]])
        self.dice5.label = str(self.dice[4])

        if self.chance == 2:
            self.dice1.disabled = True
            self.dice2.disabled = True
            self.dice3.disabled = True
            self.dice4.disabled = True
            self.dice5.disabled = True
            self.okay.disabled = True

        else:
            self.dice1.disabled = False
            self.dice2.disabled = False
            self.dice3.disabled = False
            self.dice4.disabled = False
            self.dice5.disabled = False
            self.okay.disabled = False

    #Buttons
    @discord.ui.button(label="1", style=discord.ButtonStyle.gray, row=1)
    async def dice1(self, interaction: discord.Interaction,
                    button: discord.ui.Button):
        if interaction.user.id == self.player[self.seq]['id']:
            if button.style == discord.ButtonStyle.gray:
                button.style = discord.ButtonStyle.green
                self.reroll.append(1)
            elif button.style == discord.ButtonStyle.green:
                button.style = discord.ButtonStyle.gray
                self.reroll.remove(1)
            await self.update_message()
            await interaction.response.defer()

    @discord.ui.button(label="2", style=discord.ButtonStyle.gray, row=1)
    async def dice2(self, interaction: discord.Interaction,
                    button: discord.ui.Button):
        if interaction.user.id == self.player[self.seq]['id']:
            if button.style == discord.ButtonStyle.gray:
                button.style = discord.ButtonStyle.green
                self.reroll.append(2)
            elif button.style == discord.ButtonStyle.green:
                button.style = discord.ButtonStyle.gray
                self.reroll.remove(2)
        await self.update_message()
        await interaction.response.defer()

    @discord.ui.button(label="3", style=discord.ButtonStyle.gray, row=1)
    async def dice3(self, interaction: discord.Interaction,
                    button: discord.ui.Button):
        if interaction.user.id == self.player[self.seq]['id']:
            if button.style == discord.ButtonStyle.gray:
                button.style = discord.ButtonStyle.green
                self.reroll.append(3)
            elif button.style == discord.ButtonStyle.green:
                button.style = discord.ButtonStyle.gray
                self.reroll.remove(3)
        await self.update_message()
        await interaction.response.defer()

    @discord.ui.button(label="4", style=discord.ButtonStyle.gray, row=1)
    async def dice4(self, interaction: discord.Interaction,
                    button: discord.ui.Button):
        if interaction.user.id == self.player[self.seq]['id']:
            if button.style == discord.ButtonStyle.gray:
                button.style = discord.ButtonStyle.green
                self.reroll.append(4)
            elif button.style == discord.ButtonStyle.green:
                button.style = discord.ButtonStyle.gray
                self.reroll.remove(4)
        await self.update_message()
        await interaction.response.defer()

    @discord.ui.button(label="5", style=discord.ButtonStyle.gray, row=1)
    async def dice5(self, interaction: discord.Interaction,
                    button: discord.ui.Button):
        if interaction.user.id == self.player[self.seq]['id']:
            if button.style == discord.ButtonStyle.gray:
                button.style = discord.ButtonStyle.green
                self.reroll.append(5)
            elif button.style == discord.ButtonStyle.green:
                button.style = discord.ButtonStyle.gray
                self.reroll.remove(5)
        await self.update_message()
        await interaction.response.defer()

    @discord.ui.button(label="ദ്ദി*ˊᗜˋ*) 결정이다! (0/2)",
                       style=discord.ButtonStyle.red,
                       row=2)
    async def okay(self, interaction: discord.Interaction,
                   button: discord.ui.Button):
        if interaction.user.id == self.player[
                self.seq]['id'] and self.chance < 2:
            self.chance += 1
            for i in self.reroll:
                self.rollDice(i)
            self.reroll = []
            self.dice1.style = discord.ButtonStyle.gray
            self.dice2.style = discord.ButtonStyle.gray
            self.dice3.style = discord.ButtonStyle.gray
            self.dice4.style = discord.ButtonStyle.gray
            self.dice5.style = discord.ButtonStyle.gray
            await self.update_message()
            await interaction.response.defer()

    #Select Menu
    @discord.ui.select(placeholder="점수기록표",
                       min_values=1,
                       max_values=1,
                       options=options)
    async def callback(self, interaction: discord.Interaction, select):
        if self.end:
            r = int(select.values[0].split(")")[0])
            self.seq = r - 1
            await self.update_result_message()
        else:
            if interaction.user.id == self.player[self.seq]['id']:
                r = int(select.values[0].split(")")[0])
                if self.player[self.seq]['array'][r - 1] == -1:
                    self.selectScore(r, self.dice,
                                     self.player[self.seq]['array'])
                    self.player[self.seq]['score'] = self.scoreCalc(
                        self.player[self.seq]['array'])
                    self.rollDice(0)
                    self.chance = 0
                    self.seq += 1
                    self.move += 1
                    if self.seq == len(self.player):
                        if self.round == 13:
                            print('게임끝')
                            await self.update_end_message()
                        else:
                            self.seq = 0
                            self.round += 1
                    await self.update_message()
        await interaction.response.defer()


class Yatchu(commands.Cog):

    def __init__(self, client: commands.Bot):  # 생성자 작성
        self.client = client

    #야추 다이스 [ID: 41]
    @commands.hybrid_command(name='야추다이스', description="야추한판 갈까요?")
    async def yatchu(self, ctx):
        gamestart = False
        betting = 100
        player = []
        money = []
        player.append({
            "id":
            ctx.author.id,
            "array": [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
            "score":
            0
        })
        money.append(q.readMoney(ctx.author))
        while True:
            embed = discord.Embed(title='참가자 목록',
                                  description=f'인원: {len(player)}/6',
                                  color=0xBCE29E)
            for i in range(len(player)):
                lv = etc.level(q.readXpById(player[i]['id']))
                embed.add_field(
                    name=
                    f"{player_badge[i]}{etc.lvicon(lv)}{q.readTagById(player[i]['id'])}",
                    value=
                    f"Level {lv} | ${q.readMoneyById(player[i]['id']):,d}",
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
                        player.append({
                            "id":
                            id,
                            "array": [
                                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                                -1
                            ],
                            "score":
                            0
                        })
                        money.append(q.readMoneyById(id))
                        await ctx.send(
                            f":green_circle: `{name}`가 참가자 목록에 추가되었습니다! ")
                except:
                    await ctx.send('`(⩌ʌ ⩌;)` 유효하지 않은 참가자 입니다... 다시 시도해 보세요...'
                                   )

        while gamestart and len(player) > 1:
            await ctx.reply(
                f"## 야추다이스ㄱㄱ - 베팅 금액 설정\n* 배팅 금액을 입력해 주세요! 최소 `$0` 에서 `${min(money):,d}`까지 금액을 입력 할 수 있습니다!\n* 숫자만 입력해 주세요. 단위($)와 쉼표(천 단위 구분자)를 제외하고 숫자만 입력합니다!\n* 게임 생성을 취소하고 싶다면 `취소`를 입력해 주세요!"
            )

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            input_value = await self.client.wait_for("message", check=check)
            check = input_value.content

            if check == '취소':
                gamestart = False
                await ctx.send(":x: 게임 생성이 취소되었습니다.")
                break

            else:
                try:
                    betting = int(check)
                    if 0 <= betting and betting <= min(money):
                        for user in player:
                            q.moneyAddById(user['id'], (-1) * betting)
                        await ctx.send(":green_circle: 게임이 성공적으로 생성 되었습니다!")
                        break
                    else:
                        await ctx.send(
                            f"`(⩌ʌ ⩌;)` 범위에 맞지 않은 금액입니다... 최소 `$0`, 최대 `${min(money):,d}` 입니다."
                        )
                except:
                    await ctx.send('`(⩌ʌ ⩌;)` 숫자만 입력해 주세요...')

        if gamestart:
            game_view = GameScreen(timeout=None)
            game_view.player = player
            game_view.betting = betting
            game_view.rollDice(0)
            await game_view.send(ctx)


async def setup(client):
    await client.add_cog(Yatchu(client))
