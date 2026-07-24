import discord
from discord.ext import commands
from discord import app_commands
import fcts.i18n_runtime as i18n
import fcts.sqlcontrol as q
import fcts.etcfunctions as etc
from PIL import Image, ImageDraw, ImageFont
import io
import json
from config.rootdir import root_dir

# Black Text Skin
with open(root_dir + '/font/font.json', 'r',encoding='UTF-8') as f:
    font_data = json.load(f)

def fontsize(type, font):
    if type == "name":
        if font in ["chalk", "legend", "square"]:
            return 26
        elif font in ["lcd", "minecraft", "serif", "starcraft", "luxury", "nature", "handwrite", "dragon", "ocean", "math", "wanted"]:
            return 24
        elif font in ["brush", "fluid", "paper", "gothic", "tedne"]:
            return 22
        else:
            return 20
    
    elif type == "xp":
        if font in ["fluid", "lcd", "luxury", "minecraft", "brush", "stencil", "legend", "square", "serif", "math"]:
            return 18
        elif font in ["condense", "handwrite", "stella", "drg"]:
            return 20
        else:
            return 16

def textAltitude(type, font):
    if type == "name":
        if font in ["brush", "legend", "math"]:
            return -6
        elif font in ["chalk", "luxury", "lcd", "handwrite", "nature", "square", "dragon", "modern", "wanted"]:
            return -3
        else:
            return 0
        
    elif type == "xp":
        if font in ["pixel", "minecraft", "stencil", "starcraft", "legend", "gothic", "modern", "legacy"]:
            return 2
        elif font in ["sans"]:
            return 3
        elif font in ["fluid"]:
            return 4
        elif font in ["nature"]:
            return 5
        elif font in ["lcd", "stella", "math"]:
            return -1
        else:
            return 0


# Ranking View
class PaginationView(discord.ui.View):
    current_page: int = 1
    sep: int = 10
    user = None

    def __init__(self, **kwargs):
        super().__init__(timeout=kwargs.get("timeout"))
        self.data = kwargs.get("data", [])
        self.sep = kwargs.get("sep", 10)
        self.user = kwargs.get("user")
        self.current_page = kwargs.get("page", 1)
        self.myrank = kwargs.get("myrank")

    @property
    def total_pages(self) -> int:
        if not self.data:
            return 1
        return (len(self.data) - 1) // self.sep + 1

    async def send(self, ctx):
        self.message = await ctx.send(
            i18n.t(ctx.author, "reply.complete", name=q.readTag(ctx.author)),
            view=self)
        await self.update_message(self.get_current_page_data(), self.user)

    def create_embed(self, data, user):
        myrank = self.myrank if self.myrank is not None else q.xpMyRanking(user)
        total = len(self.data)

        embed = discord.Embed(
            title=i18n.t(user, "cmd.14.t001"),
            description=i18n.t(user, "cmd.14.t002", myrank=myrank, total=total),
            color=0xE2F6CA
        )

        embed.set_thumbnail(url=user.display_avatar.url)

        base_index = (self.current_page - 1) * self.sep
        for offset, item in enumerate(data, start=1):
            rank_num = base_index + offset

            embed.add_field(
                name="#{} {}#{}".format(
                    rank_num,
                    item[2],
                    str(item[1]).zfill(4)
                ),
                value=i18n.t(
                    user,
                    "cmd.14.entry",
                    level=etc.level(item[3]),
                    xp=item[3],
                ),
                inline=False
            )

        embed.set_footer(
            text=i18n.t(user, "cmd.14.t003", current=self.current_page, total=self.total_pages),
            icon_url=""
        )

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

        if self.current_page == self.total_pages:
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
        from_item = (self.current_page - 1) * self.sep
        until_item = min(from_item + self.sep, len(self.data))
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
            self.current_page = self.total_pages
            await self.update_message(self.get_current_page_data(), self.user)


class UserProfile(commands.Cog):

    def __init__(self, client: commands.Bot):
        self.client = client

    # [id: 11, 20] rankcard generator
    async def rankcard_image(self, *, user: discord.Member, skin_id: int, preview: bool) -> io.BytesIO:
        dname = "@" + str(user)
        if dname.endswith("#0"):
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
            f"{root_dir}/config/rankcard/rankcard_skins/rankcard{skin_id}.png"
        ).convert('RGBA')
        bar_cover_image = Image.open(
            f"{root_dir}/config/rankcard/bar_skins/bar{skin_id}.png"
        ).convert('RGBA')
        emblem_image = Image.open(
            f"{root_dir}/config/rankcard/emblem/{lv}.png"
        ).convert('RGBA')

        emblem_image = emblem_image.resize((72, 72))
        bar_cover_image = bar_cover_image.crop((0, 0, 368 * xp1 / xp2, 8))

        image = background_image.copy()
        rank = emblem_image.copy()
        bar = bar_cover_image.copy()
        draw = ImageDraw.Draw(image)

        text_xp = f"{xp1:,d} / {xp2:,d} | {100 * xp1 / xp2:.2f}% | {xp:,d}"
        emblem = etc.emblemName(lv)

        font_option = font_data['profile'][f'skin{skin_id}']

        font_name = ImageFont.truetype(
            f"{root_dir}/font/{font_option['font']}/name.ttf",
            fontsize("name", font_option['font'])
        )
        font_dname = ImageFont.truetype(f"{root_dir}/font/emblem.ttf", 16)
        font_emblem = ImageFont.truetype(root_dir + "/font/emblem.ttf", 14)
        font_xp = ImageFont.truetype(
            f"{root_dir}/font/{font_option['font']}/xp.ttf",
            fontsize("xp", font_option['font']) - 2
        )

        x1 = 384 - 8 - (draw.textlength(str(name), font=font_name) +
                        draw.textlength(str(discrim), font=font_name))
        y1 = 8 + textAltitude("name", font_option['font'])

        x5 = 384 - 8 - draw.textlength(str(discrim), font=font_name)
        y5 = 8 + textAltitude("name", font_option['font'])

        x2 = 384 - 8 - draw.textlength(dname, font=font_dname)
        y2 = 32

        x3 = 384 - 8 - draw.textlength(emblem, font=font_emblem)
        y3 = 96

        x4 = (384 - draw.textlength(text_xp, font=font_xp)) / 2
        y4 = 124 + textAltitude("xp", font_option['font'])

        x6 = 384 - 8 - draw.textlength(money, font=font_xp)
        y6 = 80

        draw.text(
            (x1, y1), str(name),
            fill=tuple(font_option['name-color']),
            font=font_name,
            stroke_width=font_option['nametext-outline-width'],
            stroke_fill=tuple(font_option['nametext-outline-color'])
        )
        draw.text(
            (x5, y5), str(discrim),
            fill=tuple(font_option['discrim-color']),
            font=font_name,
            stroke_width=font_option['nametext-outline-width'],
            stroke_fill=tuple(font_option['nametext-outline-color'])
        )
        draw.text(
            (x2, y2), dname,
            fill=tuple(font_option['discrim-color']),
            font=font_dname,
            stroke_width=font_option['nametext-outline-width'],
            stroke_fill=tuple(font_option['nametext-outline-color'])
        )
        draw.text(
            (x3, y3), emblem,
            fill=(255, 255, 255, 255),
            font=font_emblem,
            stroke_width=1,
            stroke_fill=(0, 0, 0, 255)
        )
        draw.text(
            (x4, y4), text_xp,
            fill=tuple(font_option['xp-color']),
            font=font_xp,
            stroke_width=font_option['xp-outline-width'],
            stroke_fill=tuple(font_option['xp-outline-color'])
        )
        draw.text(
            (x6, y6), money,
            fill=tuple(font_option['xp-color']),
            font=font_xp,
            stroke_width=font_option['xp-outline-width'],
            stroke_fill=tuple(font_option['xp-outline-color'])
        )

        try:
            avatar_asset = user.display_avatar
            buffer_avatar = io.BytesIO()
            await avatar_asset.save(buffer_avatar)
            buffer_avatar.seek(0)
            avatar_image = Image.open(buffer_avatar).convert('RGBA')
            if skin_id == 140:
                avatar_image = Image.open(
                    root_dir + '/config/rankcard/image140.png'
                )
        except Exception:
            avatar_image = Image.open(
                root_dir + '/config/rankcard/noimage.jpg'
            )

        avatar_image = avatar_image.resize((96, 96))

        image.paste(avatar_image, (8, 8), mask=avatar_image)
        image.paste(rank, (104, 40), mask=rank)
        image.paste(bar, (8, 116), mask=bar)

        if preview:
            wm = Image.open(
                root_dir + "/config/rankcard/watermark.png"
            ).convert('RGBA')
            image.paste(wm, (0, 0), mask=wm)

        buffer_output = io.BytesIO()
        image.save(buffer_output, format='PNG')
        buffer_output.seek(0)
        return buffer_output

    # Profile [ID: 11]
    @commands.cooldown(rate=1, per=15, type=commands.BucketType.user)
    @commands.hybrid_command(
        name=app_commands.locale_str("profile", key="cmd.11.name"),
        description=app_commands.locale_str("Show user's profile", key="cmd.11.desc"),
        aliases=["프로필"]
    )
    #@discord.app_commands.describe(user='User mention')
    async def profile(self, ctx, user:discord.Member = None):
        if user is None:
            user = ctx.author

        try:
            skin_id = q.readSkin(user)
        except Exception:
            skin_id = 1

        buffer_output = await self.rankcard_image(user=user, skin_id=skin_id, preview=False)

        await ctx.reply(
            i18n.t(ctx.author, "cmd.11.t001", username=q.readTag(user)),
            file=discord.File(buffer_output, 'myimage.png')
        )

    @profile.error
    async def profile_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    # Emblem [ID: 12]
    @commands.cooldown(rate=1, per=20, type=commands.BucketType.user)
    @commands.hybrid_command(
        name=app_commands.locale_str("emblem", key="cmd.12.name"),
        description=app_commands.locale_str("Show emblem icons", key="cmd.12.desc"),
        aliases=["계급장"]
    )
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
                await ctx.reply(i18n.t(ctx.author, "cmd.12.t001"))

        if lvl == "1":
            emblem = i18n.t(ctx.author, "cmd.12.t002", ename=etc.emblemName(1))
            emblem_image = Image.open(
                    f"{root_dir}/config/rankcard/emblem/1.png").convert('RGBA')
            emblem_image = emblem_image.resize((128, 128))
            wm = Image.open(root_dir + "/config/rankcard/watermark.png").convert('RGBA')
            wm = wm.resize((96, 54))

            #duplicate image
            image = emblem_image.copy()

            # create object for drawing
            draw = ImageDraw.Draw(image)
            image.paste(wm, (16, 74), mask=wm)

            #sending image
            buffer_output = io.BytesIO()
            image.save(buffer_output, format='PNG')
            buffer_output.seek(0)

            await ctx.reply(emblem, file=discord.File(buffer_output, 'myimage.png'))

        else:

            if int(lv) <= etc.maxLevel() and int(lv) > 0:

                inf0 = etc.need_exp(lv - 1)
                inf1 = etc.need_exp(lv - 1) - etc.need_exp(lv - 2)

                ptxt = "{:,d} / {:,d} ({:.2f}%)".format(
                    xp, inf0, 100 * (xp / inf0))

                if xp >= inf0:
                    ptxt = i18n.t(ctx.author, "cmd.12.t003")

                tlv = int(lv)
                icon = root_dir + "/config/rankcard/emblem/{}.png".format(lv)
                emblem = i18n.t(ctx.author, "cmd.12.t004", ename=etc.emblemName(tlv), info0=inf0, info1=inf1, ptxt=ptxt)
                
                emblem_image = Image.open(
                    f"{root_dir}/config/rankcard/emblem/{lv}.png").convert('RGBA')
                emblem_image = emblem_image.resize((128, 128))
                wm = Image.open(root_dir + "/config/rankcard/watermark.png").convert('RGBA')
                wm = wm.resize((96, 54))

                #duplicate image
                image = emblem_image.copy()

                # create object for drawing
                draw = ImageDraw.Draw(image)
                image.paste(wm, (16, 74), mask=wm)

                #sending image
                buffer_output = io.BytesIO()
                image.save(buffer_output, format='PNG')
                buffer_output.seek(0)

                await ctx.reply(emblem, file=discord.File(buffer_output, 'myimage.png'))

            else:
                await ctx.reply(
                    i18n.t(ctx.author, "cmd.12.t005")
                )

    @emblem.error
    async def emblem_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    # My Ranking [ID: 13]
    @commands.cooldown(rate=1, per=20, type=commands.BucketType.user)
    @commands.hybrid_command(
        name=app_commands.locale_str("myrank", key="cmd.13.name"),
        description=app_commands.locale_str("Show your global ranking", key="cmd.13.desc"),
        aliases=["개인랭킹"]
    )
    async def myrank(self, ctx, server="global"):
        if server in ["global", "전역"]:
            rank = q.xpMyRanking(ctx.author)
            lv = etc.level(q.readXp(ctx.author))
            await ctx.reply(
                i18n.t(ctx.author, "cmd.13.t001", user=q.readTag(ctx.author), rank=etc.numFont(rank), total=len(q.xpRanking()), icon=etc.lvicon(lv), lv=lv,
                        xp=q.readXp(ctx.author))
            )

    @myrank.error
    async def myrank_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    # Ranking [ID: 14]
    @commands.cooldown(rate=1, per=20, type=commands.BucketType.user)
    @commands.hybrid_command(
        name=app_commands.locale_str("ranking", key="cmd.14.name"),
        description=app_commands.locale_str("Show XP leaderboard of this bot", key="cmd.14.desc"),
        aliases=["전체랭킹"]
    )
    #@discord.app_commands.describe(server="Select server (default: global)",page="Page number")
    async def ranking(self, ctx, page: int = 1):
        pagination_view = PaginationView(timeout=None)
        pagination_view.data = q.xpRanking()
        pagination_view.user = ctx.author
        pagination_view.current_page = page
        await pagination_view.send(ctx)

    @ranking.error
    async def ranking_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    # Preview [ID: 20]
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)
    @commands.hybrid_command(
        name=app_commands.locale_str("preview", key="cmd.20.name"),
        description=app_commands.locale_str("Previewing profile skins", key="cmd.20.desc"),
        aliases=["미리보기"]
    )
    async def preview(self, ctx, skin_id: int = 1):

        user = ctx.author

        buffer_output = await self.rankcard_image(user=user, skin_id=skin_id, preview=True)

        await ctx.reply(
            i18n.t(ctx.author, "reply.complete", name=q.readTag(ctx.author)),
            file=discord.File(buffer_output, 'myimage.png')
        )

    @preview.error
    async def preview_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            raise error

async def setup(client):
    await client.add_cog(UserProfile(client))
