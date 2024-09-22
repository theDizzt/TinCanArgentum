import discord
from discord.ext import commands
import fcts.sqlcontrol as q
import fcts.etcfunctions as etc
from PIL import Image, ImageDraw, ImageFont
import io


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
        userdata = q.storageList(user)
        name = q.readTag(user)
        choice = q.readSkin(user)
        total_skins = len(self.alldata)
        collected = userdata[1:].count(1)
        money = q.readMoney(user)
        lv = etc.level(q.readXp(user))

        embed = discord.Embed(
            title=f"**{name}'s Skin Storage**",
            description="`Level` {} | `Balance` ${:,d}\n`Equip` **{}** {}\n`Collect` {}/{} ({:.2f}%)\n{}".format(
                etc.lvicon(lv), money, self.alldata[choice - 1][0], self.alldata[choice - 1][1], collected, total_skins,
                (collected / total_skins) * 100, etc.process_bar(collected / total_skins)),
            color=0xE2F6CA)

        embed.set_thumbnail(url=user.avatar.url)

        for item in data:
            idv = int(item[0])
            embed.add_field(name="`{}` {}".format(
                " " * (3 - len(str(idv))) + str(idv), item[1]),
                            value=f"{etc.checkBox(userdata[idv])} *{item[2]}*",
                            inline=False)

        embed.set_footer(
            text=
            f"Page : {self.current_page} / {int((len(self.data)-1) / self.sep) + 1} · Number of skins found: {len(self.data)}",
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


class SkinStorage(commands.Cog):

    def __init__(self, client: commands.Bot):
        self.client = client

    # Skin Equipment [ID: 17]
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    @commands.hybrid_command(name='equip',
                             description="Equip the skin you want.")
    #@discord.app_commands.describe(action="Option", value="Integer only")
    async def equip(self, ctx, skin_id:int = None):

        if skin_id == None:
            await ctx.reply(
                "`(⩌Δ ⩌ ;)` Please input a valid skin number.")
            
        else:
            try:
                userdata = q.storageList(ctx.author)
            except:
                q.newStorage(ctx.author)
                userdata = q.storageList(ctx.author)

            try:
                skin = q.readSkin(ctx.author)
                if skin_id != skin:
                    if userdata[skin_id - 1] == 0:
                        await ctx.reply(
                            "`(⩌Δ ⩌ ;)` You don't have that rankcard skin.")
                    else:
                        q.skinModify(ctx.author, skin_id)
                        await ctx.reply(":green_circle: Successfully changed!!")
                else:
                    await ctx.reply(
                        "`(⩌Δ ⩌ ;)` You already equipped that rankcard skin.")
            except:
                await ctx.reply("`(⩌Δ ⩌ ;)` Unknown id value.")


    @equip.error
    async def equip_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = '`(⩌ʌ ⩌;)` This command is ratelimited, please try again in **{:.2f} seconds**.'.format(
                error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    # Purchase Skin [ID: 18]
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    @commands.hybrid_command(name='purchase',
                             description="Purchase skins with money, or unlock them when you complete level up and daily reward stacks.")
    #@discord.app_commands.describe(action="Option", value="Integer only")
    async def purchase(self, ctx, skin_id:int = None):

        if skin_id == None:
            await ctx.reply(
                "`(⩌Δ ⩌ ;)` Please input a valid skin number.")
        
        else:
            try:
                userdata = q.storageList(ctx.author)
            except:
                q.newStorage(ctx.author)
                userdata = q.storageList(ctx.author)

            skin_list = etc.storageLineRead("all")

            if skin_id < 1 and skin_id > len(skin_list):
                await ctx.reply(
                    "`(⩌Δ ⩌ ;)` Please input a valid skin number.")
            
            elif userdata[skin_id] == 1:
                await ctx.reply(
                    "`(⩌Δ ⩌ ;)` You already unlocked that rankcard skin.")
                
            else:
                try:
                    object = skin_list[skin_id - 1]

                    if object[3] == 'level':
                        xp = q.readXp(ctx.author)
                        lv = etc.level(xp)
                        if lv >= int(object[4]):
                            q.storageModify(ctx.author, skin_id, 1)
                            await ctx.reply(
                                ":green_circle: You successfully unlocked skin!")
                        else:
                            await ctx.reply(
                                f"`(⩌Δ ⩌ ;)` You can't unlocked that rankcard skin now.\nYou must be at least **level {object[4]}**."
                            )

                    elif object[3] == 'money':
                        money = q.readMoney(ctx.author)
                        if money >= int(object[4]):
                            q.moneyAdd(ctx.author, (-1) * int(object[4]))
                            q.storageModify(ctx.author, skin_id, 1)
                            await ctx.reply(
                                ":green_circle: You successfully purchased skin!")
                        else:
                            await ctx.reply(
                                f"`(⩌Δ ⩌ ;)` You're out of money.\nYou need **${int(object[4]) - money:,d}** more to make the purchase."
                            )

                    elif object[3] == 'daily':
                        daily = q.readDaily(ctx.author)
                        if daily >= int(object[4]):
                            q.storageModify(ctx.author, skin_id, 1)
                            await ctx.reply(
                                ":green_circle: You successfully unlocked skin!")
                        else:
                            await ctx.reply(
                                f"`(⩌Δ ⩌ ;)` You can't unlocked that rankcard skin now.\nIt must be at least **{object[4]}** days."
                            )

                    else:
                        await ctx.reply(
                            f"`(⩌Δ ⩌ ;)` You can acquire them through different paths.\nOnly skins that can be purchased with **money** or obtained as a **level** or **daily reward** can be obtained with this command."
                        )
                        
                except:
                    await ctx.reply("`(⩌Δ ⩌ ;)` Unknown id value.")

    @purchase.error
    async def purchase_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = '`(⩌ʌ ⩌;)` This command is ratelimited, please try again in **{:.2f} seconds**.'.format(
                error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    # Skin Storage [ID: 19]
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    @commands.hybrid_command(name='skin',
                             description="Shows your skin repository. You can check the status of your skins and the conditions under which they were acquired.")
    #@discord.app_commands.describe(action="Option", value="Integer only")
    async def skin(self, ctx, tag: str = 'all', value: int = 1):

        try:
            userdata = q.storageList(ctx.author)
        except:
            q.newStorage(ctx.author)
            userdata = q.storageList(ctx.author)

        pagination_view = PaginationView(timeout=None)
        pagination_view.data = etc.storageLineRead(tag)
        pagination_view.alldata = etc.storageLineRead("all")
        pagination_view.user = ctx.author
        pagination_view.current_page = value
        await pagination_view.send(ctx)

    @skin.error
    async def skin_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = '`(⩌ʌ ⩌;)` This command is ratelimited, please try again in **{:.2f} seconds**.'.format(
                error.retry_after)
            await ctx.send(msg)
        else:
            raise error
        
    @commands.cooldown(rate=1, per=15, type=commands.BucketType.user)
    @commands.hybrid_command(name='storage',
                             description="Shows your skin repository. You can check the status of your skins and the conditions under which they were acquired.")
    #@discord.app_commands.describe(action="Option", value="Integer only")
    async def storage(self, ctx, tag: str = 'all', value: int = 1):

        try:
            userdata = q.storageList(ctx.author)
        except:
            q.newStorage(ctx.author)
            userdata = q.storageList(ctx.author)

        pagination_view = PaginationView(timeout=None)
        pagination_view.data = etc.storageLineRead(tag)
        pagination_view.alldata = etc.storageLineRead("all")
        pagination_view.user = ctx.author
        pagination_view.current_page = value
        await pagination_view.send(ctx)

    @storage.error
    async def storage_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = '`(⩌ʌ ⩌;)` This command is ratelimited, please try again in **{:.2f} seconds**.'.format(
                error.retry_after)
            await ctx.send(msg)
        else:
            raise error


async def setup(client):
    await client.add_cog(SkinStorage(client))
