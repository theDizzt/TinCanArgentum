import discord
from discord.ext import commands
import fcts.sqlcontrol as q
import fcts.leaderboard as l
import fcts.etcfunctions as etc
import datetime
import random
import math
from time import sleep
import asyncio


def generateProblem(type):
    #[문제유형, 수식, 정답]:
    if type == 1:
        a = random.randint(1, 10) - 1
        b = random.randint(1, 10) - 1
        c = a + b
        return ["Addition", f"{a} + {b} = ?", str(c)]
    elif type == 2:
        a = random.randint(1, 10) - 1
        b = random.randint(1, 10) - 1
        c = a - b
        return ["Subtraction", f"{a} - {b} = ?", str(c)]
    elif type == 3:
        a = random.randint(1, 10) - 1
        b = random.randint(1, 10) - 1
        c = a * b
        return ["Multiplication", f"{a} x {b} = ?", str(c)]
    elif type == 4:
        a = random.randint(1, 9)
        b = random.randint(1, 9)
        c = a * b
        return ["Division", f"{c} ÷ {b} = ?", str(a)]

    elif type == 5:
        a = random.randint(1, 100) - 1
        b = random.randint(1, 100) - 1
        c = a + b
        return ["Addition", f"{a} + {b} = ?", str(c)]
    elif type == 6:  #2자리수 빼기
        a = random.randint(1, 100) - 1
        b = random.randint(1, 100) - 1
        c = a - b
        return ["Subtraction", f"{a} - {b} = ?", str(c)]
    elif type == 7:  #1.2자리수 곱하기
        a = random.randint(1, 100) - 1
        b = random.randint(1, 10) - 1
        c = a * b
        return ["Multiplication", f"{a} x {b} = ?", str(c)]
    elif type == 8:
        a = random.randint(1, 9)
        b = random.randint(1, 99)
        c = a * b
        return ["Division", f"{c} ÷ {b} = ?", str(a)]

    elif type == 9:
        a = random.randint(1, 19) - 10
        b = random.randint(1, 19) - 10
        c = random.randint(1, 19) - 10
        d = a + b + c
        return [
            "Mixed operation",
            f"{minusNum(a)} + {minusNum(b)} + {minusNum(c)} = ?",
            str(d)
        ]
    elif type == 10:
        a = random.randint(1, 19) - 10
        b = random.randint(1, 19) - 10
        c = random.randint(1, 19) - 10
        d = a - b - c
        return [
            "Mixed operation",
            f"{minusNum(a)} - {minusNum(b)} - {minusNum(c)} = ?",
            str(d)
        ]
    elif type == 11:
        a = random.randint(1, 19) - 10
        b = random.randint(1, 19) - 10
        c = a * b
        return [
            "Mixed operation", f"{minusNum(a)} x {minusNum(b)} = ?",
            str(c)
        ]
    elif type == 12:
        a = random.randint(0, 99)
        b = a**2
        return ["Square Root", f"√{b} = ?", str(a)]
    elif type == 13:
        a = random.randint(1, 99)
        b = random.randint(2, 9)
        c = a % b
        return ["Modular", f"{a} (mod {b}) = ?", str(c)]

    elif type == 14:
        a = random.randint(1, 19) - 10
        b = random.randint(1, 19) - 10
        c = random.randint(1, 19) - 10
        d = a * b * c
        return [
            "Mixed operation",
            f"{minusNum(a)} x {minusNum(b)} x {minusNum(c)} = ?",
            str(d)
        ]
    elif type == 15:
        a = random.randint(1, 19) - 10
        b = random.randint(1, 19) - 10
        c = random.randint(1, 19) - 10
        d = a * b - c
        return [
            "Signed Multiplication",
            f"{minusNum(a)} x {minusNum(b)} - {minusNum(c)} = ?",
            str(d)
        ]
    elif type == 16:
        a = random.randint(1, 19) - 10
        b = random.randint(1, 19) - 10
        c = random.randint(1, 19) - 10
        d = a + b * c
        return [
            "Mixed operation",
            f"{minusNum(a)} + {minusNum(b)} x {minusNum(c)} = ?",
            str(d)
        ]
    elif type == 17:
        a = random.randint(0, 9)
        b = random.randint(1, 4)
        c = a**b
        return ["Power Root", f"{c}^(1/{b}) = ?", str(a)]
    elif type == 18:
        a = random.randint(1, 99)
        b = random.randint(1, 19) - 10
        c = a % b
        return ["Modular", f"{a} (mod {b}) = ?", str(c)]

    elif type == 19:
        seq = [["Trigonometry", "sin(0) = ?", "0"],
               ["Trigonometry", "sin(π/2) = ?", "1"],
               ["Trigonometry", "sin(π) = ?", "0"],
               ["Trigonometry", "sin(3π/2) = ?", "-1"],
               ["Trigonometry", "cos(0) = ?", "1"],
               ["Trigonometry", "cos(π/2) = ?", "0"],
               ["Trigonometry", "cos(π) = ?", "-1"],
               ["Trigonometry", "cos(3π/2) = ?", "0"],
               ["Trigonometry", "tan(0) = ?", "0"],
               ["Trigonometry", "tan(π/4) = ?", "1"],
               ["Trigonometry", "tan(3π/4) = ?", "-1"]]
        return random.choice(seq)
    elif type == 20:
        seq = [
            ["Trigonometry", "cosec(π/6) = ?", "2"],
            ["Trigonometry", "cosec(π/2) = ?", "1"],
            ["Trigonometry", "cosec(5π/6) = ?", "2"],
            ["Trigonometry", "cosec(7π/6) = ?", "-2"],
            ["Trigonometry", "cosec(3π/2) = ?", "-1"],
            ["Trigonometry", "cosec(11π/6) = ?", "-2"],
            ["Trigonometry", "sec(0) = ?", "1"],
            ["Trigonometry", "sec(π/3) = ?", "2"],
            ["Trigonometry", "sec(2π/3) = ?", "-2"],
            ["Trigonometry", "sec(π) = ?", "-1"],
            ["Trigonometry", "sec(4π/3) = ?", "-2"],
            ["Trigonometry", "sec(5π/3) = ?", "2"],
            ["Trigonometry", "cot(π/4) = ?", "1"],
            ["Trigonometry", "cot(π/2) = ?", "0"],
            ["Trigonometry", "cot(3π/4) = ?", "-1"],
            ["Trigonometry", "cot(5π/4) = ?", "1"],
            ["Trigonometry", "cot(3π/2) = ?", "0"],
            ["Trigonometry", "cot(7π/4) = ?", "-1"],
        ]
        return random.choice(seq)
    elif type == 21:
        seq = [["Trigonometry", "asin(0) = ?", "0"],
               ["Trigonometry", "acos(1) = ?", "0"],
               ["Trigonometry", "atan(0) = ?", "0"]]
        return random.choice(seq)
    elif type == 22:
        a = random.randint(0, 8) - 1
        b = math.factorial(a)
        return ["Factorial", f"{a}! = ?", str(b)]
    elif type == 23:
        a = random.randint(2, 9)
        if a == 2:
            b = random.randint(1, 17) - 1
        elif a == 3:
            b = random.randint(1, 11) - 1
        elif a == 4:
            b = random.randint(1, 9) - 1
        elif a == 5:
            b = random.randint(1, 8) - 1
        elif a == 6:
            b = random.randint(1, 7) - 1
        else:
            b = random.randint(1, 6) - 1
        c = a**b
        return ["Logarithm", f"log{a}({c}) = ?", str(b)]
    elif type == 24:
        a = random.randint(100, 999)
        b = random.randint(2, 20)
        c = a % b
        return ["Modular", f"{a} (mod {b}) = ?", str(c)]

    elif type == 25:
        a = random.randint(1, 99)
        b = random.randint(1, 99)
        c = a * b
        return ["Multiplication", f"{a} x {b} = ?", str(c)]
    elif type == 26:
        a = random.randint(1, 99)
        b = random.randint(1, 99)
        c = a * b
        return ["Division", f"{c} ÷ {b} = ?", str(a)]
    elif type == 27:
        seq = [["Sub-factorial", "!0", "1"], ["Sub-factorial", "!1", "0"],
               ["Sub-factorial", "!2", "1"], ["Sub-factorial", "!3", "2"],
               ["Sub-factorial", "!4", "9"], ["Sub-factorial", "!5", "44"],
               ["Sub-factorial", "!6", "265"], ["Sub-factorial", "!7", "1854"]]
        return random.choice(seq)
    elif type == 28:
        a = random.randint(1, 255)
        b = bin(a)
        return ["Division", f"{str(b)[2:]}(2) = ?(10)", str(a)]
    elif type == 29:
        a = random.randint(1, 255)
        b = hex(a)
        return ["Division", f"{str(b)[2:]}(16) = ?(10)", str(a)]
    elif type == 30:
        seq = [["RANDOM", "ln(e) = ?", "1"], ["RANDOM", "e^(iπ) = ?", "-1"],
               ["RANDOM", "ζ(2) = ?", "pi^2/6"], ["RANDOM", "∫0dx = ?", "c"]]
        return random.choice(seq)


def minusNum(i: int):
    if i < 0:
        return f"({i})"
    else:
        return str(i)


class GamePrime(commands.Cog):

    def __init__(self, client: commands.Bot):
        self.client = client

    # 가위바위보 [ID: 40]
    @commands.cooldown(rate=1, per=20, type=commands.BucketType.user)
    @commands.hybrid_command(name='rps', description="Rock Paper Scissors")
    async def rps(self, ctx):
        count = 0
        win = 0
        tie = 0
        chain = 0
        max = 0
        score = 0

        def rspEmoji(i):
            if i == 0:
                return ":fist:"
            elif i == 1:
                return ":v:"
            elif i == 2:
                return ":hand_splayed:"

        def rspValue(s):
            if s in ['바위', '0', 'rock', 'r']:
                return 0
            elif s in ['가위', '1', 'scissors', 's']:
                return 1
            elif s in ['보', '2', 'paper', 'p']:
                return 2
            else:
                return -1

        def rspResult(com, user):  #0비김, 1이김, -1짐
            if com == 0:
                if user == 0:
                    return 0
                elif user == 1:
                    return -1
                elif user == 2:
                    return 1
            elif com == 1:
                if user == 0:
                    return 1
                elif user == 1:
                    return 0
                elif user == 2:
                    return -1
            elif com == 2:
                if user == 0:
                    return -1
                elif user == 1:
                    return 1
                elif user == 2:
                    return 0

        await ctx.reply(
            f":green_circle: **{q.readTag(ctx.author)}** The game will start in a moment!\n**Input tips**\n:fist: `바위, 0, rock, r`\n:v: `가위, 1, scissors, s`\n:hand_splayed: `보, 2, paper, p`"
        )
        sleep(3)
        while True:
            count += 1
            computer = random.choice(range(3))
            print(computer)

            await ctx.reply(
                f"**[COUNT: {count} | W/T: {win}/{tie} | SCORE: {score:,d}]**\n`{q.readTag(ctx.author)}` Prepare for the next attack!"
            )

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel and rspValue(
                    m.content) != -1

            input_word = await self.client.wait_for("message", check=check)
            check = input_word.content
            user = rspValue(check)
            result = rspResult(computer, user)

            if result == -1:
                score = int(score * (1 + 0.01 * count))
                xp_gain = int(score * 0.84) + 10 * win + 5 * tie + 2**max
                money_gain = int(score * 0.36) + 10 * win + 3 * tie + 2**max
                l.rpsDataUpdate(ctx.author, score, count - 1, max, win, tie)
                q.moneyAdd(ctx.author, money_gain)
                q.xpAdd(ctx.author, xp_gain)
                await ctx.reply(
                    f"**LOSE**\n## USER:{rspEmoji(user)} VS {rspEmoji(computer)}:BOT\nYOUR SCORE: **{score:,d}** (**{win}**wins / **{tie}**ties / **{max}**max chains)\nPRIZE: +{xp_gain}XP, +${money_gain}"
                )

                #스킨해금 77번
                if score >= 1000 and q.readStorage(ctx.author, 77) == 0:
                    q.storageModify(ctx.author, 77, 1)

                break

            elif result == 0:
                chain = 0
                tie += 1
                await ctx.reply(
                    f"**TIE**\n## USER:{rspEmoji(user)} VS {rspEmoji(computer)}:BOT"
                )

                #스킨해금 75번
                if tie == 9 and q.readStorage(ctx.author, 75) == 0:
                    q.storageModify(ctx.author, 75, 1)

            elif result == 1:
                win += 1
                chain += 1
                if max < chain:
                    max = chain
                score += (2**(chain - 1)) * max
                await ctx.reply(
                    f"**WIN**\n## USER:{rspEmoji(user)} VS {rspEmoji(computer)}:BOT"
                )

                #스킨해금 74, 76번
                if win == 3 and q.readStorage(ctx.author, 74) == 0:
                    q.storageModify(ctx.author, 74, 1)
                if win == 5 and q.readStorage(ctx.author, 76) == 0:
                    q.storageModify(ctx.author, 76, 1)

    @rps.error
    async def rps_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = '`(⩌ʌ ⩌;)` This command is ratelimited, please try again in **{:.2f} seconds**.'.format(
                error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    # Slots [ID: 43]
    @commands.cooldown(rate=1, per=20, type=commands.BucketType.user)
    @commands.hybrid_command(name='slot', description="Slot machine game!")
    async def slot(self, ctx, bet: int = 100):
        check = False
        if bet is not None:
            money = q.readMoney(ctx.author)
            if bet > money:
                await ctx.reply(
                    f"`(⩌Δ ⩌ ;)` Your bet is more than you have!\n(Your balance: ${money:,d})"
                )
            elif bet < 100:
                await ctx.reply(
                    "`(⩌Δ ⩌ ;)` Inappropriate amount entered...\nBet amount must be 100 or more!"
                )
            else:
                check = True
        else:
            await ctx.reply("`(⩌Δ ⩌ ;)` Bet amount must be 100 or more!")

        if check:
            q.moneyAdd(ctx.author, (-1) * bet)

            outcome = ("<:g7:1216696473459097630>", ":dollar:", ":dragon:",
                       ":melon:", ":tangerine:", ":cherries:")
            w = (0.09, 0.12, 0.15, 0.18, 0.21, 0.25)
            s1, s2, s3 = random.choices(outcome, k=3, weights=w)

            #result
            if s1 == s2 == s3:
                multi = 3

                #스킨해금 80번
                if s1 == s2 == s3 == "<:g7:1216696473459097630>" and q.readStorage(
                        ctx.author, 80) == 0:
                    q.storageModify(ctx.author, 80, 1)

            elif s1 == s2 or s2 == s3 or s3 == s1:
                multi = 1.2
            else:
                multi = 0

            #shape
            def shape(s):
                if s == "<:g7:1216696473459097630>":
                    return 1.39
                elif s == ":dollar:":
                    return 1.24
                elif s == ":dragon:":
                    return 1.11
                elif s == ":melon:":
                    return 1.00
                elif s == ":tangerine:":
                    return 0.91
                elif s == ":cherries:":
                    return 0.84

            shape = shape(s1) * shape(s2) * shape(s3)
            prize = int(bet * shape * multi)
            xp = int(10 * shape)
            q.moneyAdd(ctx.author, prize)
            q.xpAdd(ctx.author, xp)

            embed = discord.Embed(title="**:gem: LUCKY MACHINE :gem:**",
                                  description=f"{s1} | {s2} | {s3}",
                                  color=0xE2F6CA)
            embed.add_field(
                name="RESULT",
                value=
                f"${bet} x {multi} x {round(shape,2)} = **${prize:,d}!**\nBalance: **${q.readMoney(ctx.author):,d}** ({prize-bet:+,d})"
            )

            embed.set_footer(text="Developed by Dizzt")

            await ctx.reply(
                f":green_circle: **{q.readTag(ctx.author)}**'s request completely loaded!!",
                embed=embed)

            #스킨해금 78-79번
            if bet >= 10000 and q.readStorage(ctx.author, 79) == 0:
                q.storageModify(ctx.author, 79, 1)
            if prize >= 10000 and q.readStorage(ctx.author, 78) == 0:
                q.storageModify(ctx.author, 78, 1)

    @slot.error
    async def slot_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = '`(⩌ʌ ⩌;)` This command is ratelimited, please try again in **{:.2f} seconds**.'.format(
                error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    # Arithmatic [ID: 44]
    @commands.hybrid_command(name='arithmatic',
                             description="Mental Arithmetic machine game!")
    async def arithmetic(self, ctx):
        score = 0
        count = 0
        end = False
        t = 0
        await ctx.reply(
            f":green_circle: **{q.readTag(ctx.author)}** The game will start in a moment!\nAll questions must be answered correctly within 5 seconds."
        )
        sleep(3)

        while True:
            count += 1

            if count < 11:
                t = random.randint(1, 4)
            elif 11 <= count < 24:
                t = random.randint(1, 8)
            elif 24 <= count < 39:
                t = random.randint(1, 13)
            elif 39 <= count < 56:
                t = random.randint(1, 18)
            elif 56 <= count < 75:
                t = random.randint(1, 24)
            elif 75 <= count < 96:
                t = random.randint(1, 30)
            elif 96 <= count < 119:
                t = random.randint(5, 30)
            else:
                t = random.randint(9, 30)

            quest = generateProblem(t)
            answer = quest[2]
            print(f"Q{count}: {answer}")
            await ctx.reply(
                f"**[COUNT: {count}]** {quest[0]}\n## {quest[1]}\nSCORE: **{score:,d}**"
            )
            stime = datetime.datetime.now().timestamp()

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                input_word = await self.client.wait_for("message",
                                                        timeout=5,
                                                        check=check)

                if input_word.content == answer:
                    gain = datetime.datetime.now().timestamp() - stime
                    if gain > 0:
                        score += int((5 - gain) * 10)

                    #스킨해금 72번
                    if count == 80 and score >= 2500 and q.readStorage(
                            ctx.author, 72) == 0:
                        q.storageModify(ctx.author, 72, 1)
                    #스킨해금 73번
                    if gain >= 4.9 and q.readStorage(ctx.author, 73) == 0:
                        q.storageModify(ctx.author, 73, 1)

                    await ctx.channel.purge(limit=2)
                else:
                    await ctx.channel.purge(limit=2)
                    end = True
                    break

            except asyncio.TimeoutError:
                await ctx.channel.purge(limit=2)
                end = True
                break

        if end:
            xp = int(score * 0.64)
            money = int((count - 1) * 5)

            l.mathDataUpdate(ctx.author, score, count - 1)

            q.moneyAdd(ctx.author, money)
            q.xpAdd(ctx.author, xp)
            await ctx.reply(
                f"## GAME OVER\nThe correct answer is `{answer}`!\n**{q.readTag(ctx.author)}**'s result:\nCorrect: **{count-1}**\nScore: **{score:,d}**\nPrize: +{xp}XP, +${money}"
            )

            #스킨해금 65~71번
            if count > 11 and q.readStorage(ctx.author, 65) == 0:
                q.storageModify(ctx.author, 65, 1)
            if count > 24 and q.readStorage(ctx.author, 66) == 0:
                q.storageModify(ctx.author, 66, 1)
            if count > 39 and q.readStorage(ctx.author, 67) == 0:
                q.storageModify(ctx.author, 67, 1)
            if count > 56 and q.readStorage(ctx.author, 68) == 0:
                q.storageModify(ctx.author, 68, 1)
            if count > 75 and q.readStorage(ctx.author, 69) == 0:
                q.storageModify(ctx.author, 69, 1)
            if count > 96 and q.readStorage(ctx.author, 70) == 0:
                q.storageModify(ctx.author, 70, 1)
            if count > 119 and q.readStorage(ctx.author, 71) == 0:
                q.storageModify(ctx.author, 71, 1)


async def setup(client):
    await client.add_cog(GamePrime(client))
