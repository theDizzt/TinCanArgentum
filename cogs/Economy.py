import discord
from discord.ext import commands
import fcts.sqlcontrol as q
import fcts.etcfunctions as etc
import random


class Economy(commands.Cog):

    def __init__(self, client: commands.Bot):
        self.client = client

    #Stats [ID: 21]
    @commands.cooldown(rate=1, per=20, type=commands.BucketType.user)
    @commands.hybrid_command(name='stats', description="Show your stats.")
    async def stats(self, ctx, option: str = 'mystats'):
        if option == 'mystats':
            name = ctx.author.name
            uid = ctx.author.id
            nickname = q.readTag(ctx.author)
            xp = q.readXp(ctx.author)
            money = q.readMoney(ctx.author)
            skin = q.readSkin(ctx.author)
            accountdate = ctx.author.created_at.strftime('%Y-%m-%d')
            startdate = q.readStartDate(ctx.author)

            lv = etc.level(xp)

            if lv >= etc.maxLevel():
                xp1 = 1
                xp2 = 1
            else:
                xp1 = xp - etc.need_exp(lv - 1)
                xp2 = etc.need_exp(lv) - etc.need_exp(lv - 1)

            text_xp = f"{xp1:,d} / {xp2:,d} ({100 * xp1 / xp2:.2f}%)"
            emblem = etc.emblemName(lv)

            storage_list = etc.storageLineRead("all")
            userdata = q.storageList(ctx.author)
            total_skins = len(storage_list)
            collected = userdata[1:].count(1)
            equip = storage_list[skin - 1][0]
            collect = f"{collected}/{total_skins} ({(collected / total_skins) * 100:.2f}%)"

            embed = discord.Embed(title=f":bar_chart: {nickname}'s Statistics",
                                  description=f"UID: {uid}",
                                  color=0xF2BE22)

            embed.set_thumbnail(url=ctx.author.avatar.url)

            embed.add_field(
                name="NAME",
                value=f"`Real Name` {name}\n`Nick Name` {nickname}",
                inline=False)

            embed.add_field(
                name="ACCOUNT",
                value=
                f"`Created` {accountdate}\n`When we were together...` {startdate}",
                inline=False)

            embed.add_field(
                name="LEVELING",
                value=
                f"`Level` **{lv}**/300\n`XP` {text_xp}\n{etc.process_bar(xp1 / xp2)}\n`Total XP` {xp:,d}\n`Emblem` {etc.lvicon(lv)} {emblem}",
                inline=False)

            embed.add_field(name="MONEY",
                            value=f"`Balance` ${money:,d}",
                            inline=False)

            embed.add_field(name="SKIN",
                            value=f"`Equipped` {equip}\n`Progress` {collect}\n{etc.process_bar(collected / total_skins)}",
                            inline=False)

            embed.set_footer(text="Developde by Dizzt")

            await ctx.reply(
                f":green_circle: **{nickname}**'s request completely loaded!!",
                embed=embed)

    @stats.error
    async def stats_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = '`(⩌ʌ ⩌;)` This command is ratelimited, please try again in **{:.2f} seconds**.'.format(
                error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    #Balance [ID: 22]
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    @commands.hybrid_command(name='balance', description="Show your balance.")
    async def balance(self, ctx, option: str = 'mybalance'):
        if option == 'mybalance':
            await ctx.reply(
                f"**`{q.readTag(ctx.author)}`**'s balance is **${q.readMoney(ctx.author):,d}**! `⸜(*◉ ᴗ ◉)⸝`"
            )

    @balance.error
    async def balance_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = '`(⩌ʌ ⩌;)` This command is ratelimited, please try again in **{:.2f} seconds**.'.format(
                error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    #Transfer [ID: 23]
    @commands.cooldown(rate=1, per=100, type=commands.BucketType.user)
    @commands.hybrid_command(
        name='transfer', description="Let's send money to people who need it!")
    async def transfer(self, ctx):
        user = ""
        amount = 0
        balance = q.readMoney(ctx.author)
        boolean = True
        pw = str(random.randint(0, 999999)).zfill(6)

        await ctx.reply(
            "## 계좌이체 | Account Transfer\n`Step: 1/3`\n돈을 받을 사람을 `@mention` 을 통해 지정해 주세요! (`취소` 입력시 거래 취소)\nPlease specify who will receive the money through `@mention`! (Cancel transaction: type 'cancel')"
        )

        while boolean:

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            input_word = await self.client.wait_for("message", check=check)
            check = input_word.content
            if check in ['cancel', '취소']:
                await ctx.reply(
                    "거래가 취소되었습니다.\nThe transaction has been cancelled.")
                boolean = False
                break
            try:
                user = etc.extractUid(check)
                break
            except:
                await ctx.reply("`(⩌Δ ⩌ ;)`\n유효하지 않은 사용자입니다.\nInvalid user.")

        if boolean:
            await ctx.reply(
                f"## 계좌이체 | Account Transfer\n`Step: 2/3`\n**{q.readTagById(user)}** 에게 보낼 금액을 입력해 주세요. 현재 잔액은 **${balance:,d}** 입니다. (`취소` 입력시 거래 취소)\nPlease enter the amount to send to **{q.readTagById(user)}**. Your current balance is **${balance:,d}**. (Cancel transaction: type 'cancel')"
            )

        while boolean:

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            input_word = await self.client.wait_for("message", check=check)
            check = input_word.content
            if check in ['cancel', '취소']:
                await ctx.reply(
                    "거래가 취소되었습니다.\nThe transaction has been cancelled.")
                boolean = False
                break
            try:
                amount = int(check)
                if amount > balance:
                    await ctx.reply(
                        f"`(⩌Δ ⩌ ;)`\n한도 금액(**${balance:,d}**)을 초과하였습니다.\nThe limit amount (**${balance:,d}**) has been exceeded."
                    )
                elif amount < 1:
                    await ctx.reply("`(⩌Δ ⩌ ;)`\n유효하지 않은 금액입니다.\nInvalid user."
                                    )
                else:
                    break

            except:
                await ctx.reply("`(⩌Δ ⩌ ;)`\n유효하지 않은 금액입니다.\nInvalid user.")

        if boolean:
            await ctx.reply(
                f"## 계좌이체 | Account Transfer\n`Step: 3/3`\n**{q.readTagById(user)}** 에게 **${amount:,d}** 를 보내는게 맞다면 `{pw}`를 입력해 주세요. (`취소` 입력시 거래 취소)\nIf it is correct to send **${amount:,d}** to **{q.readTagById(user)}**, enter `{pw}`. (Cancel transaction: type 'cancel')"
            )

        while boolean:

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            input_word = await self.client.wait_for("message", check=check)
            check = input_word.content
            if check in ['cancel', '취소']:
                await ctx.reply(
                    "거래가 취소되었습니다.\nThe transaction has been cancelled.")
                boolean = False
                break

            elif check == pw:
                break

            else:
                await ctx.reply(
                    "`(⩌Δ ⩌ ;)`\n비밀번호가 틀렸습니다.\nYour password is incorrect.")

        if boolean:
            q.moneyAdd(ctx.author, (-1) * amount)
            q.moneyAddById(user, amount)

            embed = discord.Embed(title="명세서 | Specification",
                                  description=f"UID: {ctx.author.id}",
                                  color=0xF2BE22)

            embed.set_thumbnail(url=ctx.author.avatar.url)

            embed.add_field(name="받는사람 | Recipient",
                            value=f"{q.readTagById(user)}\n`{user}`",
                            inline=False)

            embed.add_field(name="이체금액 | Transfer amount",
                            value=f"**${amount:,d}**",
                            inline=False)

            embed.add_field(name="잔액 | Balance",
                            value=f"**${balance - amount:,d}**",
                            inline=False)

            embed.set_footer(text="Developed by Dizzt")

            await ctx.reply(
                "## 계좌이체 | Account Transfer\n거래가 완료되었습니다!\nThe transaction is complete!",
                embed=embed)

    @transfer.error
    async def transfer_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = '`(⩌ʌ ⩌;)` This command is ratelimited, please try again in **{:.2f} seconds**.'.format(
                error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    #Ranking [ID: 24]


async def setup(client):
    await client.add_cog(Economy(client))
