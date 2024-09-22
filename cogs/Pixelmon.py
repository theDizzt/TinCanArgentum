import discord
from discord.ext import commands
import fcts.sqlcontrol as q
import fcts.pixelmon as px
import fcts.etcfunctions as etc
import os
import requests
import re
import random
from time import sleep
import numpy
import openpyxl
from config.rootdir import root_dir
from time import sleep


class PaginationDexView(discord.ui.View):
    current_page: int = 1
    sep: int = 18
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
        xp = q.readXp(user)
        lv = etc.level(xp)
        xp1 = xp - etc.need_exp(lv - 1)
        xp2 = etc.need_exp(lv) - etc.need_exp(lv - 1)
        text_xp = f"{xp1:,d} / {xp2:,d} ({100 * xp1 / xp2:.2f}%)"

        embed = discord.Embed(
            title=f"**도감 목록**",
            description="`Level` {} | {}\n{}".format(
                etc.lvicon(lv),text_xp, etc.process_bar(xp1 / xp2)),
            color=0xFFFF72)

        embed.set_thumbnail(url=user.avatar.url)

        for item in data:
            embed.add_field(
                name=f"{px.dexNum(item[1])} {px.dexType(item[2], item[3])}",
                value=f"**{item[0]}**",
                inline=True)

        embed.set_footer(
            text=
            f"Page : {self.current_page} / {int((len(self.data)-1) / self.sep) + 1} · 겸색결과: {len(self.data)}개",
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


class PaginationStatView(discord.ui.View):
    current_page: int = 1
    sep: int = 1
    user = None
    stats = [50, 31, 31, 31, 31, 31, 31, 0, 0, 0, 0, 0, 0, 1.0,1.0,1.0,1.0,1.0,"노력"]
    

    async def send(self, ctx):
        self.message = await ctx.send(
            f":green_circle: **{q.readTag(ctx.author)}**'s request completely loaded!!",
            view=self)
        await self.update_message(self.data[self.current_page-1], self.user)

    def create_embed(self, data, user, stats):

        h = int(10 + ((2*data[13] + stats[1] + (stats[7]/4) + 100) * (stats[0]/100)))
        a = int(((2*data[14] + stats[2] + (stats[8]/4)) * (stats[0]/100) + 5) * stats[13])
        b = int(((2*data[15] + stats[3] + (stats[9]/4)) * (stats[0]/100) + 5) * stats[14])
        c = int(((2*data[16] + stats[4] + (stats[10]/4)) * (stats[0]/100) + 5) * stats[15])
        d = int(((2*data[17] + stats[5] + (stats[11]/4)) * (stats[0]/100) + 5) * stats[16])
        s = int(((2*data[18] + stats[6] + (stats[12]/4)) * (stats[0]/100) + 5) * stats[17])

        embed = discord.Embed(
            title=f"{px.dexNum(data[3])}{px.dexType(data[5], data[6])}{data[1]}",
            description=f"{data[2]} | National No. {data[4]}",
            color=px.dexColor(data[5]))

        embed.add_field(
            name="특성",
            value=f"`{data[7]}` | `{data[8]}` | `{data[9]}`",
            inline=False)
        
        embed.add_field(
            name=f"능력치 `레벨 {stats[0]} | 성격 {stats[18]}`",
            value=f"<:hth:1267015792935960669> **`{str(data[13]).rjust(3,' ')}`** | iv{stats[1]} ev{stats[7]} x1.0 | {h}\n<:atk:1267015794877796406> **`{str(data[14]).rjust(3,' ')}`** | iv{stats[2]} ev{stats[8]} x{stats[13]} | {a}\n<:def:1267015796463370250> **`{str(data[15]).rjust(3,' ')}`** | iv{stats[3]} ev{stats[9]} x{stats[14]} | {b}\n<:spa:1267015798254211092> **`{str(data[16]).rjust(3,' ')}`** | iv{stats[4]} ev{stats[10]} x{stats[15]} | {c}\n<:spd:1267015800116482068> **`{str(data[17]).rjust(3,' ')}`** | iv{stats[5]} ev{stats[11]} x{stats[16]} | {d}\n<:spe:1267015801920290847> **`{str(data[18]).rjust(3,' ')}`** | iv{stats[6]} ev{stats[12]} x{stats[17]} | {s}\n<:sum:1267017153606062224> **`{str(data[13]+data[14]+data[15]+data[16]+data[17]+data[18])}`**",
            inline=False)
        
        embed.add_field(
            name="진화조건",
            value=str(data[11]),
            inline=False)
        
        embed.add_field(
            name="서식지",
            value=str(data[12]),
            inline=False)
        
        embed.add_field(
            name="추가된 기술",
            value=str(data[10]),
            inline=False)

        embed.set_footer(
            text=
            f"Page : {self.current_page} / {len(self.data)} · 겸색결과: {len(self.data)}개",
            icon_url="")
        
        embed.set_thumbnail(url=px.dexImg(data[0]))

        return embed

    async def update_message(self, data, user):
        self.update_buttons()
        await self.message.edit(embed=self.create_embed(data, user, self.stats), view=self)

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

        if self.current_page == len(self.data):
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
        return self.data[self.current_page-1]

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
            self.current_page = len(self.data)
            await self.update_message(self.get_current_page_data(), self.user)


class PaginationTMView(discord.ui.View):
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
        xp = q.readXp(user)
        lv = etc.level(xp)
        xp1 = xp - etc.need_exp(lv - 1)
        xp2 = etc.need_exp(lv) - etc.need_exp(lv - 1)
        text_xp = f"{xp1:,d} / {xp2:,d} ({100 * xp1 / xp2:.2f}%)"

        embed = discord.Embed(
            title=f"**기술머신**",
            description="`Level` {} | {}\n{}".format(
                etc.lvicon(lv),text_xp, etc.process_bar(xp1 / xp2)),
            color=0xFFFF72)

        embed.set_thumbnail(url=user.avatar.url)

        for item in data:
            embed.add_field(
                name=f"{px.dexNum(item[0])} {px.dexType(item[2], item[3])} **{item[1]}**",
                value=f"`위력` {item[4]} | `명중` {item[5]} | `PP` {item[6]}\n{item[7]}",
                inline=False)

        embed.set_footer(
            text=
            f"Page : {self.current_page} / {int((len(self.data)-1) / self.sep) + 1} · 겸색결과: {len(self.data)}개",
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


class Pixelmon(commands.Cog):

    def __init__(self, client: commands.Bot):
        self.client = client

    # 타운맵 [ID: 81]
    @commands.hybrid_command(name='타운맵',
                             description="포켓몬 월드 지도를 불러옵니다.")
    async def townmap(self, ctx):
        await ctx.send("## 타운맵",file=discord.File(root_dir + '/data/pixelmon/map.png'))
        

    # tm 리로드 [ID: 82]
    @commands.hybrid_command(name='tmreload',
                             description="도감 데이터를 다수 불러옵니다.")
    async def tm_reload(self, ctx):
        total = 0
        suc_count = 0
        fail_count = 0
        path = f'{root_dir}/data/pixelmon/tm.xlsx'
        result = []
        bool = True

        px.initSetting()

        try:
            await ctx.send(f"[1/3] tm.xlsx 파일을 찾고있습니다!")
            book = openpyxl.load_workbook(path)
            sheet = book.worksheets[0]

            await ctx.send(f"[2/3] tm.xlsx 파일을 읽고있습니다!")
            for row in sheet.rows:
                line = []
                for data in row:
                    line.append(data.value)

                print(line)
                result.append(line)

        except:
            await ctx.send(f"[오류] tm.xlsx 파일이 없거나 손상된 것 같습니다...")
            bool = False

        if bool:
            total = len(result)
            await ctx.send(
                f"[3/3] {total}개의 데이터를 찾았습니다. 도감에 데이터를 추가합니다."
            )

            for data in result:
                try:
                    px.newTmData(data[1:])
                    suc_count += 1
                except:
                    fail_count += 1

            await ctx.send(
                f'작업이 모두 완료되었습니다! [총 {total}개 / 성공 {suc_count}개 / 실패 {fail_count}개]'
            )

    # 도감 리로드 [ID: 83]
    @commands.hybrid_command(name='pixelreload',
                             description="도감 데이터를 다수 불러옵니다.")
    async def pixel_reload(self, ctx):
        total = 0
        suc_count = 0
        fail_count = 0
        path = f'{root_dir}/data/pixelmon/pixel.xlsx'
        result = []
        bool = True

        px.initSetting()

        try:
            await ctx.send(f"[1/3] pixel.xlsx 파일을 찾고있습니다!")
            book = openpyxl.load_workbook(path)
            sheet = book.worksheets[0]

            await ctx.send(f"[2/3] pixel.xlsx 파일을 읽고있습니다!")
            for row in sheet.rows:
                line = []
                for data in row:
                    line.append(data.value)

                print(line)
                result.append(line)

        except:
            await ctx.send(f"[오류] pixel.xlsx 파일이 없거나 손상된 것 같습니다...")
            bool = False

        if bool:
            total = len(result)
            await ctx.send(
                f"[3/3] {total}개의 데이터를 찾았습니다. 도감에 데이터를 추가합니다."
            )

            for data in result:
                try:
                    px.newDexData(data)
                    suc_count += 1
                except:
                    fail_count += 1

            await ctx.send(
                f'작업이 모두 완료되었습니다! [총 {total}개 / 성공 {suc_count}개 / 실패 {fail_count}개]'
            )

    #Pokedex [ID: 84]
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    @commands.hybrid_command(name='도감', description="포켓몬 목록과 상세정보 검색.")
    async def pokedex(self,
                    ctx,
                    option: str = "목록",
                    category: str = None,
                    search: str = "*",
                    level: int = 50,
                    ivh: int = 31,
                    iva: int = 31,
                    ivb: int = 31,
                    ivc: int = 31,
                    ivd: int = 31,
                    ivs: int = 31,
                    evh: int = 0,
                    eva: int = 0,
                    evb: int = 0,
                    evc: int = 0,
                    evd: int = 0,
                    evs: int = 0,
                    nature: str = "노력",
                    page: int = 1):
        
        if option == "목록":

            if category == "이름":
                pagination_view = PaginationDexView(timeout=None)
                pagination_view.data = px.readDexListName(search)
                pagination_view.user = ctx.author
                pagination_view.current_page = page
                await pagination_view.send(ctx)

            elif category == "지역번호":
                pagination_view = PaginationDexView(timeout=None)
                pagination_view.data = px.readDexListDex(int(search))
                pagination_view.user = ctx.author
                pagination_view.current_page = page
                await pagination_view.send(ctx)

            elif category == "전국번호":
                pagination_view = PaginationDexView(timeout=None)
                pagination_view.data = px.readDexListNat(str(int(search)))
                pagination_view.user = ctx.author
                pagination_view.current_page = page
                await pagination_view.send(ctx)

            elif category == "타입":
                pagination_view = PaginationDexView(timeout=None)
                pagination_view.data = px.readDexListType(search)
                pagination_view.user = ctx.author
                pagination_view.current_page = page
                await pagination_view.send(ctx)

            elif category == "특성":
                pagination_view = PaginationDexView(timeout=None)
                pagination_view.data = px.readDexListAbility(search)
                pagination_view.user = ctx.author
                pagination_view.current_page = page
                await pagination_view.send(ctx)

            else:
                if search == "*":
                    pagination_view = PaginationDexView(timeout=None)
                    pagination_view.data = px.readDexList()
                    pagination_view.user = ctx.author
                    pagination_view.current_page = page
                    await pagination_view.send(ctx)

        elif option == "검색":
            bool = True
            lv = [level]
            iv = [ivh, iva, ivb, ivc, ivd, ivs]
            ev = [evh, eva, evb, evc, evd, evs]
            nv = px.dexNature(nature)

            if min(iv) < 0 or max(iv) > 31:
                bool = False

            if min(ev) < 0 or max(ev) > 252 or sum(ev) > 510:
                bool = False

            if bool:

                if category == "이름":
                    pagination_view = PaginationStatView(timeout=None)
                    pagination_view.data = px.readDexName(search)
                    pagination_view.user = ctx.author
                    pagination_view.stats = lv + iv + ev + nv
                    pagination_view.current_page = page
                    await pagination_view.send(ctx)

                elif category == "지역번호":
                    pagination_view = PaginationStatView(timeout=None)
                    pagination_view.data = px.readDexDex(int(search))
                    pagination_view.user = ctx.author
                    pagination_view.stats = lv + iv + ev + nv
                    pagination_view.current_page = page
                    await pagination_view.send(ctx)

                elif category == "전국번호":
                    pagination_view = PaginationStatView(timeout=None)
                    pagination_view.data = px.readDexNat(str(int(search)))
                    pagination_view.user = ctx.author
                    pagination_view.stats = lv + iv + ev + nv
                    pagination_view.current_page = page
                    await pagination_view.send(ctx)

                elif category == "타입":
                    pagination_view = PaginationStatView(timeout=None)
                    pagination_view.data = px.readDexType(search)
                    pagination_view.user = ctx.author
                    pagination_view.stats = lv + iv + ev + nv
                    pagination_view.current_page = page
                    await pagination_view.send(ctx)

                elif category == "특성":
                    pagination_view = PaginationStatView(timeout=None)
                    pagination_view.data = px.readDexAbility(search)
                    pagination_view.user = ctx.author
                    pagination_view.stats = lv + iv + ev + nv
                    pagination_view.current_page = page
                    await pagination_view.send(ctx)


    @pokedex.error
    async def discrim_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = '`(⩌ʌ ⩌;)` This command is ratelimited, please try again in **{:.2f} seconds**.'.format(
                error.retry_after)
            await ctx.send(msg)

    #TMdex [ID: 85]
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    @commands.hybrid_command(name='기술머신', description="기술머신 목록과 상세정보 검색.")
    async def tmdex(self,
                    ctx,
                    option: str = "목록",
                    keyword: str = "",
                    page: int = 1):

        if option == "목록":
            pagination_view = PaginationTMView(timeout=None)
            pagination_view.data = px.readTmList()
            pagination_view.user = ctx.author
            pagination_view.current_page = page
            await pagination_view.send(ctx)

        elif option == "이름":
            pagination_view = PaginationTMView(timeout=None)
            pagination_view.data = px.readTmName(keyword)
            pagination_view.user = ctx.author
            pagination_view.current_page = page
            await pagination_view.send(ctx)

        elif option == "번호":
            pagination_view = PaginationTMView(timeout=None)
            pagination_view.data = px.readTmIndex(int(keyword))
            pagination_view.user = ctx.author
            pagination_view.current_page = page
            await pagination_view.send(ctx)
        
        elif option == "타입":
            pagination_view = PaginationTMView(timeout=None)
            pagination_view.data = px.readTmType(keyword)
            pagination_view.user = ctx.author
            pagination_view.current_page = page
            await pagination_view.send(ctx)

        elif option == "분류":
            pagination_view = PaginationTMView(timeout=None)
            pagination_view.data = px.readTmCategory(keyword)
            pagination_view.user = ctx.author
            pagination_view.current_page = page
            await pagination_view.send(ctx)


    @tmdex.error
    async def discrim_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = '`(⩌ʌ ⩌;)` This command is ratelimited, please try again in **{:.2f} seconds**.'.format(
                error.retry_after)
            await ctx.send(msg)

async def setup(client):
    await client.add_cog(Pixelmon(client))
