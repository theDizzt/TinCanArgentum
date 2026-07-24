import discord
from discord import app_commands
from discord.ext import commands
import fcts.sqlcontrol as q
import fcts.etcfunctions as etc
import fcts.i18n_runtime as i18n
from PIL import Image, ImageDraw, ImageFont
import io


class PaginationView(discord.ui.View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_page = 1
        self.sep = 5
        self.user = None
        self.data = []
        self.alldata = []
        self.message = None

    async def send(self, ctx):
        self.current_page = max(1, min(self.current_page, self.max_page()))
        self.update_buttons()
        embed = self.create_embed(self.get_current_page_data(), self.user)
        self.message = await ctx.send(
            i18n.t(ctx.author, "reply.complete", name=q.readTag(ctx.author)),
            embed=embed,
            view=self)

    def max_page(self):
        return max(1, (len(self.data) - 1) // self.sep + 1)

    def create_embed(self, data, user):
        userdata = q.storageList(user)
        name = q.readTag(user)
        choice = q.readSkin(user)
        total_skins = len(self.alldata)
        collected = userdata[1:].count(1)
        money = q.readMoney(user)
        lv = etc.level(q.readXp(user))

        embed = discord.Embed(
            title=i18n.t(user, "cmd.19.title", name=name),
            description=i18n.t(user, "cmd.19.summary", icon=etc.lvicon(lv), money=money, skin=self.alldata[choice - 1][0], badge=self.alldata[choice - 1][1], collected=collected, total=total_skins, percent=(collected / total_skins) * 100, bar=etc.process_bar(collected / total_skins)),
            color=0xE2F6CA)

        embed.set_thumbnail(url=user.display_avatar.url)

        for item in data:
            idv = int(item[0])
            embed.add_field(name="`{}` {}".format(
                " " * (3 - len(str(idv))) + str(idv), item[1]),
                            value=f"{etc.checkBox(userdata[idv])} *{item[2]}*",
                            inline=False)

        embed.set_footer(
            text=i18n.t(user, "cmd.19.footer", current=self.current_page, pages=self.max_page(), count=len(self.data)),
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

        if self.current_page == self.max_page():
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
        if self.current_page == self.max_page():
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
            self.current_page = self.max_page()
            await self.update_message(self.get_current_page_data(), self.user)


class SkinStorage(commands.Cog):

    def __init__(self, client: commands.Bot):
        self.client = client

    @staticmethod
    def get_or_create_storage(user):
        return q.ensureStorage(user)

    # Skin Equipment [ID: 17]
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    @commands.hybrid_command(
        name=app_commands.locale_str("equip", key="cmd.17.name"),
        aliases=['장착'],
        description=app_commands.locale_str(
            "Equip one of your profile skins", key="cmd.17.desc"))
    #@discord.app_commands.describe(action="Option", value="Integer only")
    async def equip(self, ctx, skin_id:int = None):

        if skin_id == None:
            await ctx.reply(i18n.t(ctx.author, "cmd.17.invalid_id"))
            
        else:
            userdata = self.get_or_create_storage(ctx.author)

            try:
                skin = q.readSkin(ctx.author)
                if skin_id != skin:
                    if userdata[skin_id] == 0:
                        await ctx.reply(i18n.t(ctx.author, "cmd.17.not_owned"))
                    else:
                        q.skinModify(ctx.author, skin_id)
                        await ctx.reply(i18n.t(ctx.author, "cmd.17.changed"))
                else:
                    await ctx.reply(i18n.t(ctx.author, "cmd.17.already"))
            except:
                await ctx.reply(i18n.t(ctx.author, "cmd.17.unknown_id"))


    @equip.error
    async def equip_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    # Purchase Skin [ID: 18]
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    @commands.hybrid_command(
        name=app_commands.locale_str("purchase", key="cmd.18.name"),
        aliases=['구매'],
        description=app_commands.locale_str(
            "Purchase a new profile skin", key="cmd.18.desc"))
    #@discord.app_commands.describe(action="Option", value="Integer only")
    async def purchase(self, ctx, skin_id:int = None):

        if skin_id == None:
            await ctx.reply(i18n.t(ctx.author, "cmd.17.invalid_id"))
        
        else:
            userdata = self.get_or_create_storage(ctx.author)

            skin_list = etc.storageLineRead("all")

            if skin_id < 1 or skin_id > len(skin_list):
                await ctx.reply(i18n.t(ctx.author, "cmd.17.invalid_id"))
            
            elif userdata[skin_id] == 1:
                await ctx.reply(i18n.t(ctx.author, "cmd.18.already"))
                
            else:
                try:
                    object = skin_list[skin_id - 1]

                    if object[3] == 'level':
                        xp = q.readXp(ctx.author)
                        lv = etc.level(xp)
                        if lv >= int(object[4]):
                            q.storageModify(ctx.author, skin_id, 1)
                            await ctx.reply(i18n.t(ctx.author, "cmd.18.unlocked"))
                        else:
                            await ctx.reply(i18n.t(ctx.author, "cmd.18.level_required", level=object[4]))

                    elif object[3] == 'money':
                        money = q.readMoney(ctx.author)
                        if money >= int(object[4]):
                            q.moneyAdd(ctx.author, (-1) * int(object[4]))
                            q.storageModify(ctx.author, skin_id, 1)
                            await ctx.reply(i18n.t(ctx.author, "cmd.18.purchased"))
                        else:
                            await ctx.reply(i18n.t(ctx.author, "cmd.18.money_required", amount=int(object[4]) - money))

                    elif object[3] == 'daily':
                        daily = q.readDaily(ctx.author)
                        if daily >= int(object[4]):
                            q.storageModify(ctx.author, skin_id, 1)
                            await ctx.reply(i18n.t(ctx.author, "cmd.18.unlocked"))
                        else:
                            await ctx.reply(i18n.t(ctx.author, "cmd.18.daily_required", days=object[4]))

                    else:
                        await ctx.reply(i18n.t(ctx.author, "cmd.18.other_path"))
                        
                except:
                    await ctx.reply(i18n.t(ctx.author, "cmd.17.unknown_id"))

    @purchase.error
    async def purchase_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    # Skin Storage [ID: 19]
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    @commands.hybrid_command(
        name=app_commands.locale_str("skin", key="cmd.19.name"),
        aliases=['스킨'],
        description=app_commands.locale_str(
            "View your profile skin collection", key="cmd.19.desc"))
    #@discord.app_commands.describe(action="Option", value="Integer only")
    async def skin(self, ctx, tag: str = 'all', value: int = 1):

        self.get_or_create_storage(ctx.author)

        pagination_view = PaginationView(timeout=None)
        pagination_view.data = etc.storageLineRead(tag)
        pagination_view.alldata = etc.storageLineRead("all")
        pagination_view.user = ctx.author
        pagination_view.current_page = value
        await pagination_view.send(ctx)

    @skin.error
    async def skin_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            original = getattr(error, "original", error)
            print(f"[SkinStorage ERROR] {type(original).__name__}: {original}")
            await ctx.send(i18n.t(ctx.author, "cmd.19.error"))

async def setup(client):
    await client.add_cog(SkinStorage(client))
