import discord
from discord.ext import commands
import fcts.sqlcontrol as q
import fcts.etcfunctions as etc
import fcts.leaderboard as l
import numpy
import datetime
import asyncio
from time import sleep

player_badge = [
    "<:player1:1150445104692215989>", "<:player2:1150445106646745258>",
    "<:player3:1150445109867970570>", "<:player4:1150445113416364032>",
    "<:player5:1150445115110858752>", "<:player6:1150445118311108678>"
]

class NumberAttack(commands.Cog):

    def __init__(self, client: commands.Bot):
        self.client = client

    # Game [ID: 46]
    @commands.hybrid_command(name='number', description="Play Number Attack game!!")
    async def number_attack(self, ctx, option:str = 'start'):
        
        if option == 'start':
            gamestart = False
            player = []
            player.append({"id": ctx.author.id, "life": 100})
            while True:
                embed = discord.Embed(title='Player List',
                                    description=f'Players: {len(player)}/6',
                                        color=0xBCE29E)
                for i in range(len(player)):
                    lv = etc.level(q.readXpById(player[i]['id']))
                    embed.add_field(
                        name=
                        f"{i+1}. {etc.lvicon(lv)}{q.readTagById(player[i]['id'])}",
                        value=f"Level {lv}",
                        inline=False)
                embed.set_footer(text='Discord Bot by Dizzt')

                await ctx.reply(
                        "## Number Attack - Recruiting\n* You can invite up to 6 people using `@username`!\n* Once invited, type `start`!\n* If you want to cancel the game, type `cancel`!\n* Once the game starts, the order will automatically change!",
                        embed=embed)

                def check(m):
                        return m.author == ctx.author and m.channel == ctx.channel

                input_word = await self.client.wait_for("message", check=check)
                check = input_word.content

                if check == 'start':
                    if len(player) > 1:
                        gamestart = True
                        await ctx.send(":green_circle: Your game has been successfully created!")
                        break
                    else:
                        await ctx.send(
                                '`(⩌ʌ ⩌;)` There are too few people... There must be at least 2 people!')

                elif check == 'cancel':
                    await ctx.send(":x: Game creation was canceled.")
                    break

                else:
                    try:
                        if len(player) >= 6:
                            await ctx.send(
                                        '`(⩌ʌ ⩌;)` Too many people... You can have up to 6 participants!')
                        else:
                            id = int(etc.extractUid(check))
                            name = q.readTagById(id)
                            player.append({"id": id, "life": 100})
                            await ctx.send(
                                    f":green_circle: `{name}` has been added to the list of participants!")
                    except:
                        await ctx.send(
                                '`(⩌ʌ ⩌;)` Invalid participant... Please try again...')

            if gamestart:
                print(player)
                round = 0
                end = False

                await ctx.send(
                    f"**In a few moments, the game will start!**"
                )
                sleep(5)

                start_time = datetime.datetime.now().timestamp()

                while round < 10:
                    numpy.random.shuffle(player)
                    round += 1
                    number = 1
                    index = 0
                    reverse = 1
                    repeat = True
                    a106 = True

                    embed = discord.Embed(title='Sequence',
                                            description=f'Player: {len(player)}/6',
                                            color=0xBCE29E)
                    for i in range(len(player)):
                        lv = etc.level(q.readXpById(player[i]['id']))
                        embed.add_field(
                                name=
                                f"{player_badge[i]}{etc.lvicon(lv)}{q.readTagById(player[i]['id'])} (Lv. {lv})",
                                value=
                                f":heart: **{player[i]['life']}**",
                                inline=False)
                    embed.set_footer(text='Discord Bot by Dizzt')

                    await ctx.send(
                        f"**[ROUND: {round}/10]** The first turn is `{q.readTagById(player[index]['id'])}`'s! Please enter **`1`** when you're ready.", embed=embed)

                    while True:
                        def check(m):
                            return m.author.id == player[index]['id'] and m.channel == ctx.channel

                        input_word = await self.client.wait_for("message",
                                                                    check=check)
                        if input_word.content == str(number):
                            await input_word.add_reaction("✅")
                            break
                        
                    while repeat:

                        if len(player) == 6 and number == 91:
                            for i in range(6):
                                q.storageModify(player[i]['id'], 103, 1)

                        if a106 and number == 55:
                            for i in range(6):
                                q.storageModify(player[i]['id'], 106, 1)
                        
                        a106 = True
                        number += 1
                        index += reverse
                        if index < 0:
                            index += len(player)
                        elif index > len(player)-1:
                            index -= len(player)

                        print(f"R{round} N{number}({str(number)[-1]}) I{index} Re{reverse}")

                        def check(m):
                            return m.channel == ctx.channel
                        try:
                            input_word = await self.client.wait_for("message",
                                                                            timeout = 3,
                                                                            check=check)
                                    
                            if input_word.author.id == player[index]['id']:
                                if input_word.content == str(number) and str(number)[-1] != "0":
                                    await input_word.add_reaction("✅")
                                else:
                                    if str(number)[-1] == "3" or str(number)[-1] == "6" or str(number)[-1] == "9":
                                        if input_word.content == "go" or input_word.content == "g":
                                            await input_word.add_reaction("✅")
                                        elif input_word.content == "back" or input_word.content == "b":
                                            a106 = False
                                            if reverse == 1:
                                                reverse = -1
                                            elif reverse == -1:
                                                reverse = 1
                                            await input_word.add_reaction("✅")
                                        elif input_word.content == "jump" or input_word.content == "j":
                                            index += reverse
                                            await input_word.add_reaction("✅")
                                        else:
                                            player[index]['life'] -= (number-1)
                                            await ctx.send(
                                                        f"`(⩌ʌ ⩌;)` **`{q.readTagById(player[index]['id'])}` -{(number-1)} Life** | Wrong number... (#{number})")
                                            if player[index]['life'] < 0:
                                                player[index]['life'] = 0
                                                
                                            repeat = False
                                            break
                                        

                                    elif str(number)[-1] == "0":
                                        if input_word.content == "zero" or input_word.content == "z":
                                            await input_word.add_reaction("✅")
                                        else:
                                            player[index]['life'] -= (number-1)
                                            await ctx.send(
                                                        f"`(⩌ʌ ⩌;)` **`{q.readTagById(player[index]['id'])}` -{(number-1)} Life** | Wrong number... (#{number})")
                                            if player[index]['life'] < 0:
                                                player[index]['life'] = 0
                                            repeat = False
                                            break
                                            
                                    else:
                                        
                                                
                                        player[index]['life'] -= (number-1)
                                        await ctx.send(
                                                        f"`(⩌ʌ ⩌;)` **`{q.readTagById(input_word.author.id)}` -{(number-1)} Life** | Wrong Number... (#{number})")
                                        if player[index]['life'] < 0:
                                            player[index]['life'] = 0
                                            
                                        repeat = False
                                        break
                                        
                            else:
                                temp = 0
                                for i in range(len(player)):
                                    if input_word.author.id == player[i]['id']:
                                        temp = i
                                        break

                                player[temp]['life'] -= (number-1)
                                await ctx.send(
                                                        f"`(⩌ʌ ⩌;)` **`{q.readTagById(player[temp]['id'])}` -{(number-1)} Life** | It's not your turn... (#{number})")
                                if player[temp]['life'] < 0:
                                    player[temp]['life'] = 0

                                repeat = False
                                break

                        except asyncio.TimeoutError:
                            player[index]['life'] -= (number-1)
                            await ctx.send(
                                                        f"`(⩌ʌ ⩌;)` **`{q.readTagById(player[index]['id'])}` -{(number-1)} Life** | Time's Up!! (#{number})")
                            if player[index]['life'] == 1:
                                q.storageModify(player[index]['id'], 104, 1)
                            
                            if player[index]['life'] < 0:
                                player[index]['life'] = 0

                            repeat = False
                            break

                
                record = datetime.datetime.now().timestamp() - start_time
                recordt = int(record * 100)
                embed = discord.Embed(
                                title='RESULT',
                                description=
                                f'ROUND: {round}\nTIME: {recordt//6000}분 {(recordt%6000)//100:02d}초 {recordt%100:02d}',
                                color=0xBCE29E)

                player.sort(key=lambda x: -x['life'])

                for i in range(len(player)):
                    xp_gain = int(
                                    (player[i]['life'] * 1.8 * round) *(1 - 0.15 * i))
                    money_gain = int((player[i]['life'] * 1.2 * round) *(1 - 0.15 * i))
                    q.xpAddById(player[i]['id'], xp_gain)
                    q.moneyAddById(player[i]['id'], money_gain)
                    lv = etc.level(q.readXpById(player[i]['id']))

                    if player[i]['life'] == 100:
                        q.storageModify(player[i]['id'], 105, 1)

                    embed.add_field(
                                    name=
                                    f"`#{i+1}.` {etc.lvicon(lv)}{q.readTagById(player[i]['id'])} (Lv. {lv})",
                                    value=
                                    f":heart: **{player[i]['life']}** | +{xp_gain}XP, +${money_gain}",
                                    inline=False)
                                
                embed.set_footer(text='Discord Bot by Dizzt')
                await ctx.send("## GAME OVER", embed=embed)

        elif option == "help":
            await ctx.send("""
# NUMBER ATTACK
## How to play
- All players enter one number starting at 1 and incrementing by 1!
- You can't enter a number until it's your turn (3 second time limit).
 - Turns are announced before the game starts, so make sure to memorize them.
 - The unconditional number will increment by 1 after your turn.
- Special commands are used when the last digit is 3, 6, or 9!
 - If you just type in the correct number, it will go exactly the same.
 - If you type `go` or `g`, you pass the next number to the next person.
 - If you type `back` or `b`, the order is reversed, and the next number is passed to the next person.
 - If you type `jump` or `j`, the next person will be skipped, and it will be the next person's turn.
- You must type `zero` or `z` when the last digit is zero!
- The game ends when all 10 rounds have passed, or when one person's life reaches zero.
            """)

        elif option == "도움말":
            await ctx.send("""
# NUMBER ATTACK
## 게임 방법
- 모든 플레이어들은 1부터 시작 해서 1씩 증가하는 숫자를 하나 입력 합니다!
- 자신의 차례가 되어야 숫자 입력 할 수 있습니다. (제한 시간 3초)
 - 차례는 게임 시작 전 알려주니 잘 외워야 합니다.
 - 무조건 숫자는 차례가 지나면 1씩 증가합니다.
- 일의 자리 숫자가 3, 6, 9 일 때 특수한 명령이 사용이 됩니다!
 - 그냥 올바른 숫자를 입력 할 경우, 그대로 똑같이 진행됩니다.
 - `go`나 `g`를 입력 할 경우, 다음 사람에게 다음 숫자를 전달합니다.
 - `back`나 `b`를 입력 할 경우, 순서가 뒤집히며, 다음 사람에게 다음 숫자를 전달합니다.
 - `jump`나 `j`를 입력 할 경우, 다음 사람을 건너뛰고, 그 다음에 오는 사람의 차례가 됩니다.
- 일의 자리 숫자가 0 일 때 `zero`나 `z`를 입력 해야 합니다!
- 게임은 10라운드가 모두 지나거나, 한 사람의 생명이 0이 되면 종료됩니다.
            """)


async def setup(client):
    await client.add_cog(NumberAttack(client))
