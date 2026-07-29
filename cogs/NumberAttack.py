import discord
from discord.ext import commands
import fcts.sqlcontrol as q
import fcts.etcfunctions as etc
import fcts.leaderboard as l
import fcts.i18n_runtime as i18n
import random
import datetime
import asyncio

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
                embed = discord.Embed(title=i18n.t(ctx.author, "cmd.46.players.title"),
                                    description=i18n.t(ctx.author, "cmd.46.players.count", count=len(player)),
                                        color=0xBCE29E)
                for i in range(len(player)):
                    lv = etc.level(q.readXpById(player[i]['id']))
                    embed.add_field(
                        name=
                        f"{i+1}. {etc.lvicon(lv)}{q.readTagById(player[i]['id'])}",
                        value=i18n.t(ctx.author, "cmd.46.level", level=lv),
                        inline=False)
                embed.set_footer(text='Discord Bot by Dizzt')

                await ctx.reply(i18n.t(ctx.author, "cmd.46.recruit"), embed=embed)

                def check(m):
                        return m.author == ctx.author and m.channel == ctx.channel

                try:
                    input_word = await self.client.wait_for(
                        "message",
                        check=check,
                        timeout=300,
                    )
                except asyncio.TimeoutError:
                    await ctx.send(i18n.t(ctx.author, "cmd.46.cancelled"))
                    return
                check = input_word.content

                if check.lower() in ('start', '시작', '開始', '开始'):
                    if len(player) > 1:
                        gamestart = True
                        await ctx.send(i18n.t(ctx.author, "cmd.46.created"))
                        break
                    else:
                        await ctx.send(i18n.t(ctx.author, "cmd.46.too_few"))

                elif check.lower() in ('cancel', '취소', 'キャンセル', '取消'):
                    await ctx.send(i18n.t(ctx.author, "cmd.46.cancelled"))
                    break

                else:
                    try:
                        if len(player) >= 6:
                            await ctx.send(i18n.t(ctx.author, "cmd.46.too_many"))
                        else:
                            id = int(etc.extractUid(check))
                            name = q.readTagById(id)
                            player.append({"id": id, "life": 100})
                            await ctx.send(i18n.t(ctx.author, "cmd.46.added", name=name))
                    except:
                        await ctx.send(i18n.t(ctx.author, "cmd.46.invalid_player"))

            if gamestart:
                print(player)
                round = 0
                end = False

                await ctx.send(i18n.t(ctx.author, "cmd.46.starting"))
                await asyncio.sleep(5)

                start_time = datetime.datetime.now().timestamp()

                while round < 10:
                    random.shuffle(player)
                    round += 1
                    number = 1
                    index = 0
                    reverse = 1
                    repeat = True
                    a106 = True

                    embed = discord.Embed(title=i18n.t(ctx.author, "cmd.46.sequence"),
                                            description=i18n.t(ctx.author, "cmd.46.players.count", count=len(player)),
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

                    await ctx.send(i18n.t(
                        ctx.author,
                        "cmd.46.round_start",
                        round=round,
                        name=q.readTagById(player[index]['id']),
                    ), embed=embed)

                    while True:
                        def check(m):
                            return m.author.id == player[index]['id'] and m.channel == ctx.channel

                        try:
                            input_word = await self.client.wait_for(
                                "message",
                                check=check,
                                timeout=60,
                            )
                        except asyncio.TimeoutError:
                            await ctx.send(i18n.t(ctx.author, "cmd.46.cancelled"))
                            return
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
                                            await ctx.send(i18n.t(ctx.author, "cmd.46.wrong", name=q.readTagById(player[index]['id']), damage=number-1, number=number))
                                            if player[index]['life'] < 0:
                                                player[index]['life'] = 0
                                                
                                            repeat = False
                                            break
                                        

                                    elif str(number)[-1] == "0":
                                        if input_word.content == "zero" or input_word.content == "z":
                                            await input_word.add_reaction("✅")
                                        else:
                                            player[index]['life'] -= (number-1)
                                            await ctx.send(i18n.t(ctx.author, "cmd.46.wrong", name=q.readTagById(player[index]['id']), damage=number-1, number=number))
                                            if player[index]['life'] < 0:
                                                player[index]['life'] = 0
                                            repeat = False
                                            break
                                            
                                    else:
                                        
                                                
                                        player[index]['life'] -= (number-1)
                                        await ctx.send(i18n.t(ctx.author, "cmd.46.wrong", name=q.readTagById(input_word.author.id), damage=number-1, number=number))
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
                                await ctx.send(i18n.t(ctx.author, "cmd.46.not_turn", name=q.readTagById(player[temp]['id']), damage=number-1, number=number))
                                if player[temp]['life'] < 0:
                                    player[temp]['life'] = 0

                                repeat = False
                                break

                        except asyncio.TimeoutError:
                            player[index]['life'] -= (number-1)
                            await ctx.send(i18n.t(ctx.author, "cmd.46.timeout", name=q.readTagById(player[index]['id']), damage=number-1, number=number))
                            if player[index]['life'] == 1:
                                q.storageModify(player[index]['id'], 104, 1)
                            
                            if player[index]['life'] < 0:
                                player[index]['life'] = 0

                            repeat = False
                            break

                
                record = datetime.datetime.now().timestamp() - start_time
                recordt = int(record * 100)
                embed = discord.Embed(
                                title=i18n.t(ctx.author, "cmd.46.result"),
                                description=i18n.t(ctx.author, "cmd.46.result.desc", round=round, minute=recordt//6000, second=(recordt%6000)//100, centisecond=recordt%100),
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
                await ctx.send(i18n.t(ctx.author, "cmd.46.game_over"), embed=embed)

        elif option.lower() in ("help", "도움말"):
            await ctx.send(i18n.t(ctx.author, "cmd.46.help"))


async def setup(client):
    await client.add_cog(NumberAttack(client))
