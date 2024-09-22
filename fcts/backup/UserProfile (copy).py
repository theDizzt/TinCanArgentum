import discord
from discord.ext import commands
import functions.sqlcontrol as q
import functions.etcfunctions as etc
from PIL import Image, ImageDraw, ImageFont
import io

# Black Text Skin
bktext = [40, 52, 55]


class PaginationView(discord.ui.View):
    current_page: int = 1
    sep: int = 10

    async def send(self, ctx):
        self.message = await ctx.send(view=self)
        await self.update_message(self.data[:self.sep])

    def create_embed(self, option, data):
        embed = discord.Embed(
            title="text",
            description=f"Page: {self.current_page} / {int(len(self.data) / self.sep) + 1}",
            color=color)
        for item in data:
            embed.add_field(name=item['label'], value=item[''], inline=False)
        return embed

    async def update_message(self, option, data):
        self.update_buttons()
        await self.message.edit(embed=self.create_embed(option, data),
                                view=self)

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

        if self.current_page == int(len(self.data) / self.sep) + 1:
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
        if not self.current_page == 1:
            from_item = 0
            until_item = self.sep
        if self.current_page == int(len(self.data) / self.sep) + 1:
            from_item = self.current_page * self.sep - self.sep
            until_item = len(self.data)
        return self.data[from_item:until_item]

    #맨 앞 페이지로 이동
    @discord.ui.button(label="|<", style=discord.ButtonStyle.green)
    async def first_page_button(self, interaction: discord.Interaction,
                                button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page = 1

        await self.update_message(self.get_current_page_data())

    #앞 뒷 페이지로 이동
    @discord.ui.button(label="<", style=discord.ButtonStyle.primary)
    async def prev_button(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page -= 1
        await self.update_message(self.get_current_page_data())

    #뒷 페이지로 이동
    @discord.ui.button(label=">", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page += 1
        await self.update_message(self.get_current_page_data())

    #맨 뒷 페이지로 이동
    @discord.ui.button(label=">|", style=discord.ButtonStyle.green)
    async def last_page_button(self, interaction: discord.Interaction,
                               button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page = int(len(self.data) / self.sep) + 1
        await self.update_message(self.get_current_page_data())


class UserProfile(commands.Cog):

    def __init__(self, client: commands.Bot):
        self.client = client

    # Profile [ID: 11]
    @commands.hybrid_command(name='profile',
                             description="Show user's profile.")
    #@discord.app_commands.describe(user='User mention')
    async def profile(self, ctx, user: discord.Member = None):

        if user == None:
            user = ctx.author

        dname = "@" + str(user)

        if dname[-2:] == "#0":
            dname = dname[:-2]

        name = q.readNick(user)
        discrim = '#' + q.readDiscrim(user)
        money = '${:,d}'.format(q.readMoney(user))

        xp = q.readXp(user)
        lv = etc.level(xp)

        if lv >= etc.maxLevel():
            xp1 = 1
            xp2 = 1
        else:
            xp1 = xp - etc.need_exp(lv - 1)
            xp2 = etc.need_exp(lv) - etc.need_exp(lv - 1)

        try:
            skin_id = q.readSkin(user)
        except:
            skin_id = 1

        background_image = Image.open(
            f"./config/rankcard/rankcard_skins/rankcard{skin_id}.png").convert(
                'RGBA')
        bar_cover_image = Image.open(
            f"./config/rankcard/bar_skins/bar{skin_id}.png").convert('RGBA')
        emblem_image = Image.open(
            f"./config/rankcard/emblem/{lv}.png").convert('RGBA')

        emblem_image = emblem_image.resize((72, 72))
        bar_cover_image = bar_cover_image.crop((0, 0, 368 * xp1 / xp2, 8))

        #duplicate image
        image = background_image.copy()
        image_width, image_height = image.size
        rank = emblem_image.copy()
        rank_width, rank_height = rank.size
        bar = bar_cover_image.copy()

        # create object for drawing
        draw = ImageDraw.Draw(image)

        # draw text in center
        text_xp = f"[XP] {xp1:,d} / {xp2:,d} ({100 * xp1 / xp2:.2f}%), [Total] {xp:,d}"
        emblem = etc.emblemName(lv)

        font_name = ImageFont.truetype("./font/name.ttf", 20)
        font_discrim = ImageFont.truetype("./font/name.ttf", 20)
        font_dname = ImageFont.truetype("./font/xp.ttf", 16)
        font_emblem = ImageFont.truetype("./font/emblem.ttf", 14)
        font_xp = ImageFont.truetype("./font/xp.ttf", 14)
        font_dname = ImageFont.truetype("./font/xp.ttf", 16)

        tw_name, th_name = draw.textbbox((0, 0), str(name), font=font_name)[:2]
        tw_discrim, th_discrim = draw.textbbox((0, 0),
                                               str(discrim),
                                               font=font_discrim)[:2]
        tw_dname, th_dname = draw.textbbox((0, 0), dname, font=font_dname)[:2]
        tw_emblem, th_emblem = draw.textbbox((0, 0), emblem,
                                             font=font_emblem)[:2]
        tw_xp, th_xp = draw.textbbox((0, 0), text_xp, font=font_xp)[:2]
        tw_m, th_m = draw.textbbox((0, 0), money, font=font_xp)[:2]

        x1 = 384 - 8 - (draw.textlength(str(name), font=font_name) +
                        draw.textlength(str(discrim), font=font_name))
        y1 = 8

        x5 = 384 - 8 - draw.textlength(str(discrim), font=font_name)
        y5 = 8

        x2 = 384 - 8 - draw.textlength(str(dname), font=font_dname)
        y2 = 32

        x3 = 384 - 8 - draw.textlength(str(emblem), font=font_emblem)
        y3 = 96

        x4 = (384 - draw.textlength(text_xp, font=font_xp)) / 2
        y4 = 124

        x6 = 384 - 8 - draw.textlength(money, font=font_xp)
        y6 = 80

        draw.text((x1, y1),
                  str(name),
                  fill=(255, 255, 255, 255),
                  font=font_name)
        draw.text((x5, y5),
                  str(discrim),
                  fill=(204, 204, 204, 255),
                  font=font_discrim)
        draw.text((x2, y2), dname, fill=(204, 204, 204, 255), font=font_dname)
        draw.text((x3, y3),
                  emblem,
                  fill=(255, 255, 255, 255),
                  font=font_emblem)
        if skin_id in bktext:
            draw.text((x4, y4), text_xp, fill=(0, 0, 0, 255), font=font_xp)
        else:
            draw.text((x4, y4),
                      text_xp,
                      fill=(255, 255, 255, 255),
                      font=font_xp)
        draw.text((x6, y6), money, fill=(255, 255, 255, 255), font=font_xp)

        try:
            #avatar
            avatar_asset = user.avatar

            # read JPG from server to buffer (file-like object)
            buffer_avatar = io.BytesIO()
            await avatar_asset.save(buffer_avatar)
            buffer_avatar.seek(0)

            # read JPG from buffer to Image
            avatar_image = Image.open(buffer_avatar).convert('RGBA')

        except:
            avatar_image = Image.open('./config/rankcard/noimage.jpg')

        # resize it
        avatar_image = avatar_image.resize((96, 96))
        image.paste(avatar_image, (8, 8), mask=avatar_image)
        image.paste(rank, (104, 40), mask=rank)
        image.paste(bar, (8, 116), mask=bar)

        #sending image
        buffer_output = io.BytesIO()
        image.save(buffer_output, format='PNG')
        buffer_output.seek(0)

        await ctx.reply(
            f":green_circle: **{q.readTag(user)}**'s profile card completely loaded!!",
            file=discord.File(buffer_output, 'myimage.png'))

    # Emblem [ID: 12]
    @commands.hybrid_command(name='emblem', description="Show emblem icons.")
    #@discord.app_commands.describe(lvl='Choose emblem level to show (default: your level)')
    async def emblem(self, ctx, lvl=None):
        xp = q.readXp(ctx.author)
        user_lv = etc.level(xp)

        if lvl == None:
            lv = user_lv

        else:
            try:
                lv = int(lvl)
            except:
                await ctx.reply("`(⩌Δ ⩌ ;)` 타입오류!\nType Error!\n")

        if lvl == "1":
            icon = "./config/rankcard/emblem/1.png"
            emblem = "**{}**\nRequired XP: 0 | 0\nProgression: You already reached this level!".format(
                etc.emblemName(1))

            await ctx.reply(emblem, file=discord.File(icon))

        else:

            if int(lv) <= etc.maxLevel() and int(lv) > 0:

                inf0 = etc.need_exp(lv - 1)
                inf1 = etc.need_exp(lv - 1) - etc.need_exp(lv - 2)

                ptxt = "{:,d} / {:,d} ({:.2f}%)".format(
                    xp, inf0, 100 * (xp / inf0))

                if xp >= inf0:
                    ptxt = "You already reached this level!"

                tlv = int(lv)
                icon = "./config/rankcard/emblem/{}.png".format(lv)
                emblem = "**{}**\nRequired XP: {:,d} | {:,d}\nProgression: {}".format(
                    etc.emblemName(tlv), inf0, inf1, ptxt)

                await ctx.reply(emblem, file=discord.File(icon))

            else:
                await ctx.reply(
                    "`(⩌Δ ⩌ ;)` 범위에서 벗어난 정수를 입력하였습니다. 1-240 의 자연수를 입력받을 수 있습니다.\nYou entered an integer out of range. You can enter a natural number from 1 to 240.\n`CTX : icon <int: 1~240>`"
                )

    # My Ranking [ID: 13]
    @commands.hybrid_command(name='myrank',
                             description="Show your global ranking.")
    async def myrank(self, ctx, server="global"):
        if server == "global" or server == "전역":
            users = q.xpRanking()
            rank = 0
            for i in range(len(users)):
                if users[i][0] == ctx.author.id:
                    rank = i + 1
                    break
            await ctx.reply(
                ">>> :green_circle: **{}**'s Global Ranking\n`Ranking` **{}**/{}\n`Level` **{}**\n`Total XP` **{:,d}**"
                .format(q.readTag(ctx.author), etc.numFont(rank),
                        len(q.xpRanking()), etc.level(q.readXp(ctx.author)),
                        q.readXp(ctx.author)))

    # Ranking [ID: 14]
    @commands.hybrid_command(name='ranking',
                             description="Show leaderboard of this bot!")
    #@discord.app_commands.describe(server="Select server (default: global)",page="Page number")
    async def ranking(self, ctx, server="global", page=1):
        rank = q.xpRanking()
        if server == "global" or server == "전역":
            rank_value = 1
            cons = 10 * (page - 1)

            if len(rank) % 10 == 0:
                max_page = len(rank) // 10
            else:
                max_page = len(rank) // 10 + 1

            embed = discord.Embed(title="**Global Ranking**",
                                  description="`Page: {} / {}`".format(
                                      page, max_page),
                                  color=0x9BE8D8)
            for user in rank[cons:]:
                try:
                    embed.add_field(
                        name="{} **{}**#{}".format(
                            etc.numFont(rank_value + cons), user[2],
                            str(user[1]).zfill(4)),
                        value="`Level` **{}**/{} - `Total XP` **{:,d}**".
                        format(etc.level(user[3]), etc.maxLevel(), user[3]),
                        inline=False)

                    if rank_value == 10:
                        break
                    else:
                        rank_value += 1
                except:
                    if rank_value == 10:
                        break
                    else:
                        rank_value += 1

        await ctx.reply(embed=embed)

    # Storage [ID: 19]
    @commands.hybrid_command(name='skin',
                             description="Manage your rankcard skin!")
    #@discord.app_commands.describe(action="Option", value="Integer only")
    async def storage(self, ctx, action: str = 'mylist', value: int = 1):

        userdata = q.storageList(ctx.author)
        name = data = q.readTag(ctx.author)

        if action == 'list':

            storage_list = etc.storageLineRead()
            choice = q.readSkin(ctx.author)
            page = value

            Rank_int = 1
            max_page = 1
            cons = 8 * (page - 1)
            total_skins = len(storage_list)
            collected = userdata[1:].count(1)

            if len(storage_list) % 8 == 0:
                max_page = total_skins // 8
            else:
                max_page = total_skins // 8 + 1

            if page > max_page:
                await ctx.send("`(⩌Δ ⩌ *)` Out of indexes...")
            else:
                embed = discord.Embed(
                    title="**{}'s Skin Storage**".format(name),
                    description="Equipped: {}\nCollected: {}/{} ({:.2f}%)".
                    format(storage_list[choice - 1][0], collected, total_skins,
                           (collected / total_skins) * 100),
                    color=0xE2F6CA)

                for data in storage_list[cons:]:
                    embed.add_field(name="{} {}".format(
                        data[0], etc.checkBox(userdata[cons + Rank_int])),
                                    value="`" + data[1] + "`",
                                    inline=False)
                    if Rank_int == 8:
                        break
                    else:
                        Rank_int += 1

                embed.set_footer(text="Page : {} / {}".format(page, max_page),
                                 icon_url="")

                await ctx.reply(
                    ":green_circle: **{}**'s request completely loaded!!".
                    format(name),
                    embed=embed)

        elif action == 'change':
            try:
                skin = q.readSkin(ctx.author)
                choice = int(value)

                if choice != skin:
                    if userdata[choice] == 0:
                        await ctx.reply(
                            "`(⩌Δ ⩌ ;)` You don't have that rankcard skin.")
                    else:
                        q.skinModify(ctx.author, choice)
                        await ctx.reply(":green_circle: Successfully changed!!"
                                        )
                else:
                    await ctx.reply(
                        "`(⩌Δ ⩌ ;)` You already equipped that rankcard skin.")
            except:
                await ctx.reply("`(⩌Δ ⩌ ;)` Unknown id value.")

        elif action == 'unlock':
            choice = int(value)

            if userdata[choice] == 1:
                await ctx.reply(
                    "`(⩌Δ ⩌ ;)` You already unlocked that rankcard skin.")
            else:
                try:
                    tarr = etc.storageLineRead()[int(value) - 1]
                    if tarr[2] == 'level':
                        xp = q.readXp(ctx.author)
                        lv = etc.level(xp)
                        if lv >= int(tarr[3]):
                            q.storageModify(ctx.author, choice, 1)
                            await ctx.reply(
                                ":green_circle: Successfully unlocked!!")
                        else:
                            await ctx.reply(
                                "`(⩌Δ ⩌ ;)` You can't unlocked that rankcard skin now."
                            )

                    elif tarr[2] == 'money':
                        money = q.readMoney(ctx.author)
                        if money >= int(tarr[3]):
                            q.moneyAdd(ctx.author, (-1) * int(tarr[3]))
                            q.storageModify(ctx.author, choice, 1)
                            await ctx.reply(
                                ":green_circle: Successfully unlocked!!")
                        else:
                            await ctx.reply(
                                "`(⩌Δ ⩌ ;)` You can't unlocked that rankcard skin now."
                            )
                except:
                    await ctx.reply("`(⩌Δ ⩌ ;)` Unknown id value.")

    # Preview [ID: 20]
    @commands.hybrid_command(name='preview',
                             description="Show user's profile.")
    #@discord.app_commands.describe(user='User mention')
    async def preview(self, ctx, skin_id: int = None):

        user = ctx.author
        dname = "@" + str(user)

        if dname[-2:] == "#0":
            dname = dname[:-2]

        name = q.readNick(user)
        discrim = '#' + q.readDiscrim(user)
        money = '${:,d}'.format(q.readMoney(user))

        xp = q.readXp(user)
        lv = etc.level(xp)

        if lv >= etc.maxLevel():
            xp1 = 1
            xp2 = 1
        else:
            xp1 = xp - etc.need_exp(lv - 1)
            xp2 = etc.need_exp(lv) - etc.need_exp(lv - 1)

        background_image = Image.open(
            f"./config/rankcard/rankcard_skins/rankcard{skin_id}.png").convert(
                'RGBA')
        bar_cover_image = Image.open(
            f"./config/rankcard/bar_skins/bar{skin_id}.png").convert('RGBA')
        emblem_image = Image.open(
            f"./config/rankcard/emblem/{lv}.png").convert('RGBA')
        wm = Image.open("./config/rankcard/watermark.png").convert('RGBA')

        emblem_image = emblem_image.resize((72, 72))
        bar_cover_image = bar_cover_image.crop((0, 0, 368 * xp1 / xp2, 8))

        #duplicate image
        image = background_image.copy()
        image_width, image_height = image.size
        rank = emblem_image.copy()
        rank_width, rank_height = rank.size
        bar = bar_cover_image.copy()

        # create object for drawing
        draw = ImageDraw.Draw(image)

        # draw text in center
        text_xp = f"[XP] {xp1:,d} / {xp2:,d} ({100 * xp1 / xp2:.2f}%), [Total] {xp:,d}"
        emblem = etc.emblemName(lv)

        font_name = ImageFont.truetype("./font/name.ttf", 20)
        font_discrim = ImageFont.truetype("./font/name.ttf", 20)
        font_dname = ImageFont.truetype("./font/xp.ttf", 16)
        font_emblem = ImageFont.truetype("./font/emblem.ttf", 14)
        font_xp = ImageFont.truetype("./font/xp.ttf", 14)
        font_dname = ImageFont.truetype("./font/xp.ttf", 16)

        tw_name, th_name = draw.textbbox((0, 0), str(name), font=font_name)[:2]
        tw_discrim, th_discrim = draw.textbbox((0, 0),
                                               str(discrim),
                                               font=font_discrim)[:2]
        tw_dname, th_dname = draw.textbbox((0, 0), dname, font=font_dname)[:2]
        tw_emblem, th_emblem = draw.textbbox((0, 0), emblem,
                                             font=font_emblem)[:2]
        tw_xp, th_xp = draw.textbbox((0, 0), text_xp, font=font_xp)[:2]
        tw_m, th_m = draw.textbbox((0, 0), money, font=font_xp)[:2]

        x1 = 384 - 8 - (draw.textlength(str(name), font=font_name) +
                        draw.textlength(str(discrim), font=font_name))
        y1 = 8

        x5 = 384 - 8 - draw.textlength(str(discrim), font=font_name)
        y5 = 8

        x2 = 384 - 8 - draw.textlength(str(dname), font=font_dname)
        y2 = 32

        x3 = 384 - 8 - draw.textlength(str(emblem), font=font_emblem)
        y3 = 96

        x4 = (384 - draw.textlength(text_xp, font=font_xp)) / 2
        y4 = 124

        x6 = 384 - 8 - draw.textlength(money, font=font_xp)
        y6 = 80

        draw.text((x1, y1),
                  str(name),
                  fill=(255, 255, 255, 255),
                  font=font_name)
        draw.text((x5, y5),
                  str(discrim),
                  fill=(204, 204, 204, 255),
                  font=font_discrim)
        draw.text((x2, y2), dname, fill=(204, 204, 204, 255), font=font_dname)
        draw.text((x3, y3),
                  emblem,
                  fill=(255, 255, 255, 255),
                  font=font_emblem)
        if skin_id in bktext:
            draw.text((x4, y4), text_xp, fill=(0, 0, 0, 255), font=font_xp)
        else:
            draw.text((x4, y4),
                      text_xp,
                      fill=(255, 255, 255, 255),
                      font=font_xp)
        draw.text((x6, y6), money, fill=(255, 255, 255, 255), font=font_xp)

        try:
            #avatar
            avatar_asset = user.avatar

            # read JPG from server to buffer (file-like object)
            buffer_avatar = io.BytesIO()
            await avatar_asset.save(buffer_avatar)
            buffer_avatar.seek(0)

            # read JPG from buffer to Image
            avatar_image = Image.open(buffer_avatar).convert('RGBA')

        except:
            avatar_image = Image.open('./config/rankcard/noimage.jpg')

        # resize it
        avatar_image = avatar_image.resize((96, 96))
        image.paste(avatar_image, (8, 8), mask=avatar_image)
        image.paste(rank, (104, 40), mask=rank)
        image.paste(bar, (8, 116), mask=bar)
        image.paste(wm, (0, 0), mask=wm)

        #sending image
        buffer_output = io.BytesIO()
        image.save(buffer_output, format='PNG')
        buffer_output.seek(0)

        await ctx.reply(
            f":green_circle: **{q.readTag(user)}**'s preview completely loaded!!",
            file=discord.File(buffer_output, 'myimage.png'))


async def setup(client):
    await client.add_cog(UserProfile(client))
