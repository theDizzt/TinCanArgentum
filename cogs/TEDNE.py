import discord
from discord.ext import commands
import fcts.sqlcontrol as q
import fcts.etcfunctions as etc
import fcts.tedne as ted
import asyncio
import json
from config.rootdir import root_dir

with open(root_dir + '/config/tedne.json', 'r',encoding='UTF-8') as f:
    tedne_data = json.load(f)


class InputCode(discord.ui.Modal, title='TEDNE Achievements Code'):
    code = discord.ui.TextInput(label='Input',
                                style=discord.TextStyle.short,
                                placeholder='Input your 8-digit code...')

    async def on_submit(self, interaction: discord.Interaction):
        codelist = tedne_data['achievements']
        result = codelist.get(str(self.code.value))
        if result == None:
            await interaction.response.send_message(
                f"`(⩌Δ ⩌ ;)` <@{interaction.user.id}> This code does not exist. Please double check that there are no typos!"
            )
        else:
            tempid = result['id']
            temptitle = result['title']
            xp = result['xp']
            money = result['money']
            if ted.readAchieve(interaction.user, tempid) == 1:
                await interaction.response.send_message(
                    f"`(⩌Δ ⩌ ;)` <@{interaction.user.id}> You have already unlocked this achievement!\nInfo: `{temptitle}`"
                )
            else:
                ted.achieveModify(interaction.user, tempid, 1)
                q.xpAdd(interaction.user, xp)
                q.moneyAdd(interaction.user, money)
                await interaction.response.send_message(
                    f":green_circle: <@{interaction.user.id}> Code entered! Your reward has been received.\nInfo: `{temptitle}` | +{xp}XP, +${money}"
                )
            try:
                skin = result['skin']
                if q.readStorage(interaction.user, str(skin)) == 0:
                    q.storageModify(interaction.user, skin, 1)
                    await interaction.response.send_message(
                        f"<@{interaction.user.id}> And you unlocked special skin! Type `;skin change {skin}` to check out!"
                    )
            except:
                None


class PaginationView(discord.ui.View):
    current_page: int = 1
    sep: int = 5
    user = None

    async def send(self, ctx):
        self.message = await ctx.send(
            f":green_circle: **{q.readTag(ctx.author)}**'s request completely loaded!!",
            view=self)
        if self.current_page == 1:
            await self.update_message(self.data[:self.sep], self.user)
        elif self.current_page == int((len(self.data) - 1) / self.sep) + 1:
            await self.update_message(
                self.data[self.current_page * self.sep -
                          self.sep:len(self.data)], self.user)
        else:
            await self.update_message(
                self.data[(self.current_page - 1) *
                          self.sep:self.current_page * self.sep], self.user)

    def create_embed(self, data, user):
        userdata = ted.achieveList(user)
        name = q.readTag(user)
        total = len(self.data)
        unlocked = userdata[1:].count(1)

        xp = q.readXp(user)
        lv = etc.level(xp)
        xp1 = xp - etc.need_exp(lv - 1)
        xp2 = etc.need_exp(lv) - etc.need_exp(lv - 1)
        text_xp = f"{xp1:,d} / {xp2:,d} ({100 * xp1 / xp2:.2f}%)"

        embed = discord.Embed(
            title=f"**{name}'s TEDNE Achievements**",
            description="`Progress` **{}/{}** ({:.2f}%)\n{}\n`Level` {} | {}\n{}".format(
                unlocked, total, (unlocked / total) * 100, etc.process_bar(unlocked / total), etc.lvicon(lv),
                text_xp, etc.process_bar(xp1 / xp2)),
            color=0xA1FFFF)

        embed.set_thumbnail(url=user.avatar.url)

        for item in data:
            if item['hidden']:
                desc = "Hidden Achievements"
            else:
                desc = item['description']
            prize = f"+{item['xp']:,d}XP | +${item['money']:,d}"
            embed.add_field(
                name="{} {}".format(item['title'],
                                    etc.checkBox(userdata[item['id']])),
                value=
                f"{desc}\n`Award` {prize}\n`Complete` {ted.readAchieveTime(user, item['id'])}",
                inline=False)

        embed.set_footer(
            text=
            f"Page : {self.current_page} / {int((len(self.data)-1) / self.sep) + 1}",
            icon_url="")

        return embed

    async def update_message(self, data, user):
        self.update_buttons()
        await self.message.edit(embed=self.create_embed(data, user), view=self)

    def update_buttons(self):
        if self.current_page == 1:
            self.first_page_button.disabled = True
            self.prev_button.disabled = True
            self.first_page_button.style = discord.ButtonStyle.gray
            self.prev_button.style = discord.ButtonStyle.gray
        else:
            self.first_page_button.disabled = False
            self.prev_button.disabled = False
            self.first_page_button.style = discord.ButtonStyle.green
            self.prev_button.style = discord.ButtonStyle.primary

        if self.current_page == int((len(self.data) - 1) / self.sep) + 1:
            self.next_button.disabled = True
            self.last_page_button.disabled = True
            self.last_page_button.style = discord.ButtonStyle.gray
            self.next_button.style = discord.ButtonStyle.gray
        else:
            self.next_button.disabled = False
            self.last_page_button.disabled = False
            self.last_page_button.style = discord.ButtonStyle.green
            self.next_button.style = discord.ButtonStyle.primary

    def get_current_page_data(self):
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        if self.current_page == 1:
            from_item = 0
            until_item = self.sep
        if self.current_page == int((len(self.data) - 1) / self.sep) + 1:
            from_item = self.current_page * self.sep - self.sep
            until_item = len(self.data)
        return self.data[from_item:until_item]

    #맨 앞 페이지로 이동
    @discord.ui.button(label="|<", style=discord.ButtonStyle.green)
    async def first_page_button(self, interaction: discord.Interaction,
                                button: discord.ui.Button):
        if interaction.user == self.user:
            await interaction.response.defer()
            self.current_page = 1

            await self.update_message(self.get_current_page_data(), self.user)

    #앞 뒷 페이지로 이동
    @discord.ui.button(label="<", style=discord.ButtonStyle.primary)
    async def prev_button(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
        if interaction.user == self.user:
            await interaction.response.defer()
            self.current_page -= 1
            await self.update_message(self.get_current_page_data(), self.user)

    #앞 뒷 페이지로 이동
    @discord.ui.button(label="CODE", style=discord.ButtonStyle.danger)
    async def code_button(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
        if interaction.user == self.user:
            await interaction.response.send_modal(InputCode())

    #뒷 페이지로 이동
    @discord.ui.button(label=">", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
        if interaction.user == self.user:
            await interaction.response.defer()
            self.current_page += 1
            await self.update_message(self.get_current_page_data(), self.user)

    #맨 뒷 페이지로 이동
    @discord.ui.button(label=">|", style=discord.ButtonStyle.green)
    async def last_page_button(self, interaction: discord.Interaction,
                               button: discord.ui.Button):
        if interaction.user == self.user:
            await interaction.response.defer()
            self.current_page = int((len(self.data) - 1) / self.sep) + 1
            await self.update_message(self.get_current_page_data(), self.user)


class TEDNE(commands.Cog):  # Cog를 상속하는 클래스를 선언

    def __init__(self, client: commands.Bot):  # 생성자 작성
        self.client = client

    async def is_server(ctx):
        return ctx.channel.id in [1115648878918774794, 1158619424278982736]

    # TEDNE [ID: 38]
    @commands.check(is_server)
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    @commands.hybrid_command(name='tedne', description="TEDNE related command")
    async def tedne(self,
                    ctx,
                    option: str = "help",
                    value: int = 1,
                    sub: int = 0):

        if option == "help" or option == "hp":
            name = q.readTag(ctx.author)

            embed = discord.Embed(title="TEDNE Support Functions",
                                  description="Beta: 2023-10-14",
                                  color=0xA1FFFF)

            embed.add_field(
                name="COMMANDS",
                value=
                "`;tedne help` Show this page.\n`;tedne achievements` Show and unlock your achievements list.\n`;tedne hint` Get some hints.\n`;tedne user` Show your profile.",
                inline=False)

            embed.set_footer(text=name, icon_url=ctx.author.avatar.url)

            await ctx.reply(
                f":green_circle: **{name}**'s request completely loaded!!",
                embed=embed)

        elif option == "achievements" or option == "achieve" or option == "a":

            try:
                ted.newAchieve(ctx.author)
            except:
                None
            pagination_view = PaginationView(timeout=None)
            pagination_view.data = list(tedne_data['achievements'].values())
            pagination_view.user = ctx.author
            pagination_view.current_page = value
            await pagination_view.send(ctx)

        elif option == "user" or option == "u":
            name = q.readTag(ctx.author)
            xp = q.readXp(ctx.author)
            lv = etc.level(xp)
            xp1 = xp - etc.need_exp(lv - 1)
            xp2 = etc.need_exp(lv) - etc.need_exp(lv - 1)
            text_xp = f"{xp1:,d} / {xp2:,d} ({100 * xp1 / xp2:.2f}%)"
            joindate = ted.readJoinTime(ctx.author)
            userdata = ted.achieveList(ctx.author)
            total = len(list(tedne_data['achievements'].values()))
            unlocked = userdata[1:].count(1)

            embed = discord.Embed(title=f"**{name}'s TEDNE Profile**",
                                  description=f"{etc.lvicon(lv)} | {text_xp}\n{etc.process_bar(xp1 / xp2)}",
                                  color=0xA1FFFF)

            embed.set_thumbnail(url=ctx.author.avatar.url)

            embed.add_field(name="Join Date", value=joindate, inline=False)

            embed.add_field(
                name="Achievements",
                value=f"{unlocked}/{total} ({unlocked / total * 100:.2f}%)\n{etc.process_bar(unlocked / total)}",
                inline=False)

            await ctx.reply(
                f":green_circle: **{name}**'s request completely loaded!!",
                embed=embed)

        elif option == "hint" or option == "ht":
            name = q.readTag(ctx.author)
            hints = tedne_data['hint']

            if sub == 0:
                label = 'level' + str(value)
                temp = hints[label]

                embed = discord.Embed(
                    title=f"TEDNE Level {value} Hints",
                    description=f"Your balance: ${q.readMoney(ctx.author):,d}",
                    color=0xA1FFFF)

                embed.add_field(
                    name=
                    f"Type `;tedne hint {value} <hint_number>` to get hints.",
                    value=
                    f"Cost: **${value*120:,d}** per each.\nThere are **{len(temp)-1} hints** to provide.",
                    inline=False)

                temp_list = ""

                for i in range(1, len(temp)):
                    hl = 'hint' + str(i)

                    if i == 1:
                        temp_list += f"`{i}` {temp[hl]['hinttitle']}"
                    else:
                        temp_list += f"\n`{i}` {temp[hl]['hinttitle']}"

                embed.add_field(name="Hint list",
                                value=temp_list,
                                inline=False)

                embed.set_footer(text=name, icon_url=ctx.author.avatar.url)

                await ctx.reply(
                    f":green_circle: **{name}**'s request completely loaded!!",
                    embed=embed)

            else:
                if q.readMoney(ctx.author) >= value * 120:
                    q.moneyAdd(ctx.author, value * 120 * (-1))

                    label = 'level' + str(value)
                    temp = hints[label]

                    hl = 'hint' + str(sub)

                    embed = discord.Embed(title=f"TEDNE Level {value} Hints",
                                          description=temp['title'],
                                          color=0xA1FFFF)

                    embed.add_field(
                        name=f"`Hint {sub}` {temp[hl]['hinttitle']}",
                        value=temp[hl]['hint'],
                        inline=False)

                    embed.set_footer(text=name, icon_url=ctx.author.avatar.url)

                    user = await ctx.author.create_dm()
                    await user.send(
                        f":green_circle: **{name}**'s request completely loaded!!",
                        embed=embed)

                    await ctx.reply(
                        f":green_circle: Check out your DM channel!!")

    @tedne.error
    async def discrim_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = '`(⩌ʌ ⩌;)` This command is ratelimited, please try again in **{:.2f} seconds**.'.format(
                error.retry_after)
            await ctx.send(msg)

        elif isinstance(error, commands.errors.CheckFailure):
            await ctx.reply(
                "## `(⩌ʌ ⩌;)` NOT ALLOWED\nTo use this command, you need to go to the **#tedne-bot** channel on the **TEDNE Discord server**!"
            )

        else:
            raise error

    @commands.command(name='tedaccount', description="")
    async def tedaccount(self, ctx, user: discord.Member = None):
        ted.newAchieve(user)
        await ctx.reply("Done")


async def setup(client):
    await client.add_cog(TEDNE(client))
