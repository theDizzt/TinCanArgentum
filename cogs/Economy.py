import discord
from discord.ext import commands
from discord import app_commands
import fcts.i18n_runtime as i18n
import fcts.sqlcontrol as q
import fcts.etcfunctions as etc
import random


class Economy(commands.Cog):

    def __init__(self, client: commands.Bot):
        self.client = client

    #Stats [ID: 21]
    @commands.cooldown(rate=1, per=20, type=commands.BucketType.user)
    @commands.hybrid_command(
        name=app_commands.locale_str("stats", key="cmd.21.name"),
        description=app_commands.locale_str("Show your stats", key="cmd.21.desc"),
        aliases=["통계"]
    )
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
                name=i18n.t(ctx.author, "cmd.21.t001"),
                value=i18n.t(ctx.author, "cmd.21.t002", name=name, nickname=nickname),
                inline=False)

            embed.add_field(
                name=i18n.t(ctx.author, "cmd.21.t003"),
                value=i18n.t(ctx.author, "cmd.21.t004", adate=accountdate, sdate=startdate),
                inline=False)

            embed.add_field(
                name=i18n.t(ctx.author, "cmd.21.t005"),
                value=i18n.t(ctx.author, "cmd.21.t006", lv=lv, txp=text_xp, bar=etc.process_bar(xp1 / xp2), xp=xp, icon=etc.lvicon(lv), emblem=emblem),
                inline=False)

            embed.add_field(name=i18n.t(ctx.author, "cmd.21.t007"),
                            value=i18n.t(ctx.author, "cmd.21.t008", money=money),
                            inline=False)

            embed.add_field(name=i18n.t(ctx.author, "cmd.21.t009"),
                            value=i18n.t(ctx.author, "cmd.21.t010", equip=equip, collect=collect, bar=etc.process_bar(collected / total_skins)),
                            inline=False)

            embed.set_footer(text=i18n.t(ctx.author, "cmd.dev.footer"))

            await ctx.reply(i18n.t(ctx.author, "reply.complete", name=q.readTag(ctx.author)), embed=embed)

    @stats.error
    async def stats_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    #Balance [ID: 22]
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    @commands.hybrid_command(
        name=app_commands.locale_str("balance", key="cmd.22.name"),
        description=app_commands.locale_str("Show your balance", key="cmd.22.desc"),
        aliases=["잔액"]
    )
    async def balance(self, ctx, option: str = 'mybalance'):
        if option == 'mybalance':
            await ctx.reply(i18n.t(ctx.author, "cmd.22.t001", user=q.readTag(ctx.author), money=q.readMoney(ctx.author)))

    @balance.error
    async def balance_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    #Transfer [ID: 23]
    @commands.cooldown(rate=1, per=100, type=commands.BucketType.user)
    @commands.hybrid_command(
        name=app_commands.locale_str("transfer", key="cmd.23.name"),
        description=app_commands.locale_str("Let's send money to people who need it", key="cmd.23.desc"),
        aliases=["송금"]
    )
    async def transfer(self, ctx):
        user = ""
        amount = 0
        balance = q.readMoney(ctx.author)
        boolean = True
        pw = str(random.randint(0, 999999)).zfill(6)

        await ctx.reply(
            i18n.t(ctx.author, "cmd.23.t001")
        )

        while boolean:

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            input_word = await self.client.wait_for("message", check=check)
            check = input_word.content
            if check in ['cancel', '취소']:
                await ctx.reply(
                    i18n.t(ctx.author, "cmd.23.t002"))
                boolean = False
                break
            try:
                user = etc.extractUid(check)
                break
            except:
                await ctx.reply(i18n.t(ctx.author, "cmd.23.t003"))

        if boolean:
            await ctx.reply(
                i18n.t(ctx.author, "cmd.23.t004", obj=q.readTagById(user), balance=balance)
            )

        while boolean:

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            input_word = await self.client.wait_for("message", check=check)
            check = input_word.content
            if check in ['cancel', '취소']:
                await ctx.reply(
                    i18n.t(ctx.author, "cmd.23.t002"))
                boolean = False
                break
            try:
                amount = int(check)
                if amount > balance:
                    await ctx.reply(
                        i18n.t(ctx.author, "cmd.23.t007", balance=balance)
                    )
                elif amount < 1:
                    await ctx.reply(i18n.t(ctx.author, "cmd.23.t005"))
                else:
                    break

            except:
                await ctx.reply(i18n.t(ctx.author, "cmd.23.t005"))

        if boolean:
            await ctx.reply(
                i18n.t(ctx.author, "cmd.23.t006", obj=q.readTagById(user), amount=amount, pw=pw)
            )

        while boolean:

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            input_word = await self.client.wait_for("message", check=check)
            check = input_word.content
            if check in ['cancel', '취소']:
                await ctx.reply(
                    i18n.t(ctx.author, "cmd.23.t002"))
                boolean = False
                break

            elif check == pw:
                break

            else:
                await ctx.reply(i18n.t(ctx.author, "cmd.23.t008"))

        if boolean:
            q.moneyAdd(ctx.author, (-1) * amount)
            q.moneyAddById(user, amount)

            embed = discord.Embed(title=i18n.t(ctx.author, "cmd.23.t009"),
                                  description=f"UID: {ctx.author.id}",
                                  color=0xF2BE22)

            embed.set_thumbnail(url=ctx.author.avatar.url)

            embed.add_field(name=i18n.t(ctx.author, "cmd.23.t010"),
                            value=f"{q.readTagById(user)}\n`{user}`",
                            inline=False)

            embed.add_field(name=i18n.t(ctx.author, "cmd.23.t011"),
                            value=f"**${amount:,d}**",
                            inline=False)

            embed.add_field(name=i18n.t(ctx.author, "cmd.23.t012"),
                            value=f"**${balance - amount:,d}**",
                            inline=False)

            embed.set_footer(text=i18n.t(ctx.author, "cmd.dev.footer"))

            await ctx.reply(
                i18n.t(ctx.author, "cmd.23.t013"),
                embed=embed)

    @transfer.error
    async def transfer_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    #Ranking [ID: 24]


async def setup(client):
    await client.add_cog(Economy(client))
