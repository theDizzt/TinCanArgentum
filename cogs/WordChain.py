import discord
from discord.ext import commands
import fcts.sqlcontrol as q
import fcts.etcfunctions as etc
import fcts.leaderboard as l
import os
import requests
import re
from fcts.koreanbreak import count_break_korean
import fcts.worddict as wd
import datetime
import random
from time import sleep
import numpy
import openpyxl
from config.rootdir import root_dir

apikey = ""

player_badge = [
    "<:player1:1150445104692215989>", "<:player2:1150445106646745258>",
    "<:player3:1150445109867970570>", "<:player4:1150445113416364032>",
    "<:player5:1150445115110858752>", "<:player6:1150445118311108678>"
]

color = [0xF3B0C3, 0xFFCCB6, 0xFFFF72, 0xADDCC8, 0xABDEE6, 0xCBAACB]


def midReturn(val, s, e):
    if s in val:
        val = val[val.find(s) + len(s):]
        if e in val:
            val = val[:val.find(e)]
    return val


#지정한 두 개의 문자열 사이의 문자열 여러개를 리턴하는 함수
#string에서 XML 등의 요소를 분석할때 사용됩니다
def midReturn_all(val, s, e):
    if s in val:
        tmp = val.split(s)
        val = []
        for i in range(0, len(tmp)):
            if e in tmp[i]:
                val.append(tmp[i][:tmp[i].find(e)])
    else:
        val = []
    return val


def replace_sound_char(char):
    SOUND_LIST = {
        "라": "나",
        "락": "낙",
        "란": "난",
        "랄": "날",
        "람": "남",
        "랍": "납",
        "랑": "낭",
        "래": "내",
        "랭": "냉",
        "냑": "약",
        "략": "약",
        "냥": "양",
        "량": "양",
        "녀": "여",
        "려": "여",
        "녁": "역",
        "력": "역",
        "년": "연",
        "련": "연",
        "녈": "열",
        "렬": "열",
        "념": "염",
        "렴": "염",
        "렵": "엽",
        "녕": "영",
        "령": "영",
        "녜": "예",
        "례": "예",
        "로": "노",
        "록": "녹",
        "론": "논",
        "롱": "농",
        "뢰": "뇌",
        "뇨": "요",
        "료": "요",
        "룡": "용",
        "루": "누",
        "뉴": "유",
        "류": "유",
        "뉵": "육",
        "륙": "육",
        "륜": "윤",
        "률": "율",
        "륭": "융",
        "륵": "늑",
        "름": "늠",
        "릉": "능",
        "니": "이",
        "리": "이",
        "린": "인",
        "림": "임",
        "립": "입"
    }
    if char in SOUND_LIST:
        return SOUND_LIST[char]
    else:
        return None


def isOneKill(word):
    ONEKILL_WORD = [
        '겊', '귬', '깆', '껸', '꼇', '꼍', '꾜', '끠', '냔', '른', '녘', '늄', '랒', '읖',
        '릇', '쿄', '룅', '륨', '븀', '럴', '텝', '엌', '탉', '튬', '듐', '눞', '틤', '풂',
        '픔', '핕', '휵', '읗'
    ]
    if word in ONEKILL_WORD:
        return True
    else:
        return False


#UI
def lifeUI(life, max):
    icon = [':black_heart:', ':heart:']
    return icon[1] * life + icon[0] * (max - life)


def scoreBoost(score, life):
    if life == 3:
        return score
    elif life == 2:
        return int(score * 1.16)
    elif life == 1:
        return int(score * 1.39)


def sampleText():
    sample = [
        "별을노래하는마음으로", "한송이의국화꽃을피우기위해", "가나다라마바사아자차카타파하", "내입술의말과", "희푸른모니터너머의빛을통해",
        "반짝이는재가당신의불꽃을따라", "생명가득한하늘을보여주자", "내희망의내용은질투뿐", "리갤말고리게로", "쌀독에서인심난다",
        "은비의비밀일기장", "영일이삼사오육칠팔구", "그저나답게빛나는거예요", "천포인트한판간다", "한비가비비빅을사오면서"
    ]
    result = random.choice(sample)
    return result


# Functions [ID: 82]
def searchWord(query):
    url = f'https://opendict.korean.go.kr/api/search?key={apikey}&target_type=search&req_type=xml&q={query}&advanced=y'
    r = requests.get(url, verify=False)
    result = int(midReturn(r.text, '<total>', '</total>'))

    if result != 0:
        word = midReturn(r.text, '<word>', '</word>')
        word = re.sub('[^A-Za-z0-9가-힣]', '', word)
        pos = midReturn(r.text, '<pos>', '</pos>')
        if pos == "":
            pos = "명사"
        mean = midReturn(r.text, '<definition>', '</definition >')
        return [word, pos, mean]
    else:
        return None


def searchEn(query):
    url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{query}'
    r = requests.get(url, verify=False)
    j = r.json()
    print(j[0])

    try:
        word = j[0]['word']
        word = re.sub('[^A-Za-z0-9]', '', word)
        print(word)
        pos = j[0]["meanings"][0]["partOfSpeech"]
        print(pos)
        mean = j[0]["meanings"][0]["definitions"][0]["definition"]
        return [word, pos, mean]
    except:
        return None


def startWord(query, history, page=1):
    url = f'https://opendict.korean.go.kr/api/search?key={apikey}&target_type=search&req_type=xml&q={query}&num=100&start={page}'
    r = requests.get(url, verify=False)
    ans = []
    max_page = int(midReturn(r.text, '<total>', '</total>')) // 100

    #단어 목록을 불러오기
    words = midReturn_all(r.text, '<item>', '</item>')
    for w in words:
        word = midReturn(w, '<word>', '</word>')
        word = re.sub('[^A-Za-z0-9가-힣]', '', word)
        if word[0] == query and len(word) > 1 and not (word in history):
            ans.append(word)

    custom = wd.readAllByStart(query)
    for word in custom:
        if len(word) > 1 and not (word in history):
            ans.append(word[1])

    #중복제거
    ans = list(set(ans))

    if len(ans) > 0:
        result = random.choice(ans)
        temp = wd.readInGame(result)

        if temp is None:
            return searchWord(result)

        else:
            return temp

    else:
        if page < max_page:
            return startWord(query, history, page + 1)
        else:
            return None


def startWord3(query, history, page=1):
    url = f'https://opendict.korean.go.kr/api/search?key={apikey}&target_type=search&req_type=xml&q={query}&num=100&start={page}'
    r = requests.get(url, verify=False)
    ans = []
    max_page = int(midReturn(r.text, '<total>', '</total>')) // 100

    #단어 목록을 불러오기
    words = midReturn_all(r.text, '<item>', '</item>')
    for w in words:
        word = midReturn(w, '<word>', '</word>')
        word = re.sub('[^A-Za-z0-9가-힣]', '', word)
        if word[0] == query and len(word) == 3 and not (word in history):
            ans.append(word)

    custom = wd.readAllByStart(query)
    for word in custom:
        if len(word) == 3 and not (word in history):
            ans.append(word[1])

    #중복제거
    ans = list(set(ans))

    if len(ans) > 0:
        result = random.choice(ans)
        temp = wd.readInGame(result)

        if temp is None:
            return searchWord(result)

        else:
            return temp

    else:
        if page < max_page:
            return startWord(query, history, page + 1)
        else:
            return None


class PaginationList(discord.ui.View):
    current_page: int = 1
    sep: int = 20
    user = None

    async def send(self, ctx):
        self.message = await ctx.send(
            ":green_circle: ** 단어 검색이 완료되었습니다!",
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
        embed = discord.Embed(
            title=f"**은비사전에 등록된 단어 목록**",
            description=f"총 {len(self.data)}개의 단어가 등록되었습니다.",
            color=0xFFFF72)
        
        result = ""

        for item in data:
            result += f"`{item[0]}` • **{item[1]}** • {item[2]}\n"

        embed.add_field(
            name="",
            value=result[:-1],
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


class TestCommands(commands.Cog):

    def __init__(self, client: commands.Bot):
        self.client = client

    # Functions [ID: 33]
    @commands.hybrid_command(name='사전', description="단어 뜻을 검색합니다!")
    async def word_search(self, ctx, *, word: str = ''):
        if word != '':
            result = searchWord(word)
            if result is not None:
                wd.newWord(ctx.author, str(result[0]), str(result[1]),
                           str(result[2]))
                await ctx.reply(f'## {result[0]}\n[{result[1]}] {result[2]}')
            else:
                await ctx.reply('등록되지 않은 단어입니다...')

    @commands.hybrid_command(name='dict', description="단어 뜻을 검색합니다!")
    async def en_search(self, ctx, word: str = ''):
        if word != '':
            result = searchEn(word)
            if result is not None:
                await ctx.reply(f'## {result[0]}\n[{result[1]}] {result[2]}')
            else:
                await ctx.reply('등록되지 않은 단어입니다...')

    # Functions [ID: 34]
    @commands.hybrid_command(name='은비사전', description="학습 된 단어 뜻을 검색합니다!")
    async def word_search_db(self,
                             ctx,
                             option: str = "검색",
                             *,
                             word: str = "*"):
        
        if option == "도움말":
            embed = discord.Embed(
                    title=f'은비사전 이용 가이드',
                    description=
                    '기본 형태는 `;은비사전 <옵션> <키워드/페이지>` 이고\n기본값은 `;은비사전 검색 *` 입니다.',
                    color=0x8ECDDD)

            embed.add_field(
                name=f"**도움말**",
                value="도움말을 열람합니다.\n따로 사용 가능한 키워드는 없습니다.",
                inline=False)
            
            embed.add_field(
                name=f"**검색**",
                value="단어를 검색합니다. 키워드 서식에 따라 조건 검색도 가능합니다.\n`<키워드>` 키워드가 일치하는 단어의 정보를 불러옵니다.\n`<글자>-` 해당 글자로 시작하는 단어들을 랜덤으로 골라 목록으로 보여줍니다.\n`-<글자>` 해당 글자로 끝나는 단어들을 랜덤으로 골라 목록으로 보여줍니다.\n`~<품사>` 해당 품사에 해당하는 단어들을 랜덤으로 골라 목록으로 보여줍니다.\n`id:<색인번호>` 해당 색인번호를 가진 단어의 정보를 불러옵니다.\n`*` 랜덤으로 10개의 단어를 골라 목록으로 보여줍니다.",
                inline=False)
            
            embed.add_field(
                name=f"**등록**",
                value="사용자 지정 단어를 등록합니다.\n기본 형식은 `;은비사전 등록 <단어>/<품사/주제>/<뜻>`입니다.\n`;은비사전 등록`을 통해 등록 요령을 볼 수 있습니다.",
                inline=False)
            
            embed.add_field(
                name=f"**수정**",
                value="사용자 지정 단어의 데이터를 수정합니다.\n기본 형식은 `;은비사전 수정 <색인번호>/<단어>/<품사/주제>/<뜻>`입니다.\n`;은비사전 수정`을 통해 정보 수정 요령을 볼 수 있습니다.",
                inline=False)

            embed.set_footer(text='Discord Bot by Dizzt')

            await ctx.reply(':green_circle: 단어 검색이 완료되었습니다!', embed=embed)


        elif option == "검색":
            if word[-1] == "-" and len(word) == 2:
                result = wd.readAllByStart(word[0])
                if len(result) > 10:
                    temp = random.sample(result, 10)
                else:
                    temp = result

                embed = discord.Embed(
                    title=f'{word[0]}(으)로 시작하는 단어',
                    description=
                    f'총 {len(result)}개 중 {len(temp)}개를 무작위로 들고왔습니다!',
                    color=0x8ECDDD)

                for info in temp:
                    embed.add_field(
                        name=f"**{info[1]}**",
                        value=
                        f"ID: {info[0]} | 점수: {count_break_korean(info[1])}",
                        inline=False)

                embed.set_footer(text='Discord Bot by Dizzt')
                await ctx.reply(':green_circle: 단어 검색이 완료되었습니다!', embed=embed)

            elif word[0] == "-" and len(word) == 2:
                result = wd.readAllByEnd(word[-1])
                if len(result) > 10:
                    temp = random.sample(result, 10)
                else:
                    temp = result

                embed = discord.Embed(
                    title=f'{word[-1]}(으)로 끝나는 단어',
                    description=
                    f'총 {len(result)}개 중 {len(temp)}개를 무작위로 들고왔습니다!',
                    color=0x8ECDDD)

                for info in temp:
                    embed.add_field(
                        name=f"**{info[1]}**",
                        value=
                        f"ID: {info[0]} | 점수: {count_break_korean(info[1])}",
                        inline=False)

                embed.set_footer(text='Discord Bot by Dizzt')
                await ctx.reply(':green_circle: 단어 검색이 완료되었습니다!', embed=embed)

            elif word[0] == "~":
                result = wd.readAllByPOS(word[1:])
                if len(result) > 10:
                    temp = random.sample(result, 10)
                else:
                    temp = result

                embed = discord.Embed(
                    title=f'품사가 {word[1:]}인 단어',
                    description=
                    f'총 {len(result)}개 중 {len(temp)}개를 무작위로 들고왔습니다!',
                    color=0x8ECDDD)

                for info in temp:
                    embed.add_field(
                        name=f"**{info[1]}**",
                        value=
                        f"ID: {info[0]} | 점수: {count_break_korean(info[1])}",
                        inline=False)

                embed.set_footer(text='Discord Bot by Dizzt')
                await ctx.reply(':green_circle: 단어 검색이 완료되었습니다!', embed=embed)

            elif word[0:3] == "id:":
                val = int(word[3:])
                result = wd.readAllById(val)
                if result is not None:
                    point = count_break_korean(result[1])
                    embed = discord.Embed(
                        title=result[1],
                        description=f'[{result[2]}] {result[3]}\n\n획득가능 점수: 3목숨 (+0%) **{point}점** | 2목숨 (+16%) **{int(1.16*point)}점** | 1목숨 (+39%) **{int(1.39*point)}점**',
                        color=0x8ECDDD)
                    embed.set_footer(
                        text=
                        f'등록번호: {result[0]}\n등록일: {result[5]}\n마지막 수정: {q.readTagById(result[4])} ({result[6]})'
                    )
                    await ctx.reply(':green_circle: 단어 검색이 완료되었습니다!',
                                    embed=embed)
                else:
                    await ctx.reply(
                        '## `(⩌Δ ⩌ ;)` 없는 단어 입니다...\n 혹시 단어를 새로 등록해 보는 것은 어떨까요?'
                    )

            elif word == "*":
                result = wd.readAllRandom()
                temp = random.sample(result, 10)
                print(temp)
                embed = discord.Embed(
                    title='랜덤 단어 생성',
                    description=
                    f'총 {len(result)}개 중 {len(temp)}개를 무작위로 들고왔습니다!',
                    color=0x8ECDDD)

                for info in temp:
                    embed.add_field(
                        name=f"**{info[1]}**",
                        value=
                        f"ID: {info[0]} | 점수: {count_break_korean(info[1])}",
                        inline=False)

                embed.set_footer(text='Discord Bot by Dizzt')
                await ctx.reply(':green_circle: 단어 검색이 완료되었습니다!', embed=embed)

            elif word != "":
                result = wd.readAll(word)
                if result is not None:
                    point = count_break_korean(result[1])
                    embed = discord.Embed(
                        title=result[1],
                        description=f'[{result[2]}] {result[3]}\n\n획득가능 점수: 3목숨 (+0%) **{point}점** | 2목숨 (+16%) **{int(1.16*point)}점** | 1목숨 (+39%) **{int(1.39*point)}점**',
                        color=0x8ECDDD)
                    embed.set_footer(
                        text=
                        f'등록번호: {result[0]}\n등록일: {result[5]}\n마지막 수정: {q.readTagById(result[4])} ({result[6]})'
                    )
                    await ctx.reply(':green_circle: 단어 검색이 완료되었습니다!',
                                    embed=embed)
                else:
                    await ctx.reply(
                        '## `(⩌Δ ⩌ ;)` 없는 단어 입니다...\n 혹시 단어를 새로 등록해 보는 것은 어떨까요?'
                    )

        elif option == "등록":
            if word == "도움말":
                await ctx.reply('`은비사전 등록 <단어>/<품사>/<뜻>` 구문으로 단어 등록이 가능합니다!')
            elif word != "":
                try:
                    result = word.split("/")
                    text = re.sub('[^A-Za-z0-9가-힣ㄱ-ㆎ]', '', result[0])
                    wd.newWord(ctx.author, text, result[1], result[2])

                    temp = wd.readAll(result[0])
                    embed = discord.Embed(title=temp[1],
                                          description=f'[{temp[2]}] {temp[3]}',
                                          color=0xBCE29E)
                    embed.set_footer(
                        text=
                        f'등록번호: {temp[0]}\n등록일: {temp[5]}\n마지막 수정: {q.readTagById(temp[4])} ({temp[6]})'
                    )
                    await ctx.reply(':green_circle: 단어 등록이 완료되었습니다!',
                                    embed=embed)
                except:
                    await ctx.reply(
                        '## `(⩌Δ ⩌ ;)` 단어 등록에 실패 하였습니다...\n* `은비사전 검색 <단어>`로 이미 등록된 단어인지 확인해 주세요.\n* `은비사전 등록 <단어>/<품사>/<뜻>` 구문이 정확한지 확인해 주세요.'
                    )

        elif option == "수정":
            if word == "도움말":
                await ctx.reply(
                    '`은비사전 수정 <등록번호>/<단어>/<품사>/<뜻>` 구문으로 단어 수정이 가능합니다.\n`수정 후` 인자들은 비워두면 수정이 되지않고 전 데이터를 유지하게 됩니다.\n`뜻` 항목 맨앞에 `+`를 입력하여 뒤에 이어쓰기를 할 수 있습니다.'
                )
            elif word != "":
                try:
                    result = word.split("/")

                    if result[1] != "":
                        text = re.sub('[^A-Za-z0-9가-힣ㄱ-ㆎ]', '', result[1])
                        wd.wordModify(ctx.author, int(result[0]), text)

                    if result[2] != "":
                        wd.plModify(ctx.author, int(result[0]), result[2])

                    if result[3] != "":
                        wd.meanModify(ctx.author, int(result[0]), result[3])

                    temp = wd.readAllById(int(result[0]))
                    embed = discord.Embed(title=temp[1],
                                          description=f'[{temp[2]}] {temp[3]}',
                                          color=0xFFCC70)
                    embed.set_footer(
                        text=
                        f'등록번호: {temp[0]}\n등록일: ({temp[5]})\n수정: {q.readTagById(temp[4])} ({temp[6]})'
                    )
                    await ctx.reply(':green_circle: 단어 수정이 완료되었습니다!',
                                    embed=embed)
                    q.xpAdd(ctx.author, 100)
                    q.moneyAdd(ctx.author, 30)
                except:
                    await ctx.reply(
                        '## `(⩌Δ ⩌ ;)` 단어 수정에 실패 하였습니다...\n* `은비사전 검색 <단어>`로 등록되지 않은 단어인지 확인해 주세요.\n* `<전단어>/<후단어>/<품사>/<뜻>` 구문이 정확한지 확인해 주세요.'
                    )

        elif option == "목록":
            page = 1
            try:
                page = int(word)
            except:
                None
            pagination_view = PaginationList(timeout=None)
            pagination_view.data = wd.readAllWithPOS()
            pagination_view.user = ctx.author
            pagination_view.current_page = page
            await pagination_view.send(ctx)


    # Functions [ID: 87]
    @commands.hybrid_command(name='일괄등록',
                             description="엑셀에 저장된 파일을 일괄적으로 업데이트 합니다!")
    async def word_enlist_db(self, ctx, uid: int = None, file: str = ""):
        total = 0
        suc_count = 0
        fail_count = 0
        path = f'{root_dir}/data/word_enlist/{file}.xlsx'
        result = []
        bool = True

        try:
            await ctx.send(f"[1/3] {file}.xlsx 파일을 찾고있습니다!")
            book = openpyxl.load_workbook(path)
            sheet = book.worksheets[0]

            await ctx.send(f"[2/3] {file}.xlsx 파일을 읽고있습니다!")
            for row in sheet.rows:
                result.append([row[0].value, row[1].value, row[2].value])
        except:
            await ctx.send(f"[오류] {file}.xlsx 파일이 없거나 손상된 것 같습니다...")
            bool = False

        if bool:
            total = len(result)
            await ctx.send(
                f"[3/3] {total}개의 파일을 찾았습니다. 사전에 데이터를 추가합니다! 데이터가 많으면 시잔이 좀 오래 걸립니다!"
            )

            for data in result:
                try:
                    if data[2] == "우리말샘":
                        try:
                            mean = searchWord(data[0])[2]
                            wd.newWordById(uid, data[0], data[1], mean)
                        except: #mean이 none 일 경우
                            mean = f"{data[2]} 관련 단어."
                            wd.newWordById(uid, data[0], data[1], mean)
                    else:
                        wd.newWordById(uid, data[0], data[1], data[2])

                    temp = wd.readAll(data[0])
                    embed = discord.Embed(title=temp[1],
                                          description=f'[{temp[2]}] {temp[3]}',
                                          color=0xBCE29E)
                    embed.set_footer(
                        text=
                        f'등록번호: {temp[0]}\n등록일: {temp[5]}\n마지막 수정: {q.readTagById(temp[4])} ({temp[6]})'
                    )
                    suc_count += 1
                    await ctx.send(
                        f'[{suc_count+fail_count}/{total}] 단어 등록이 완료되었습니다.',
                        embed=embed)
                except:
                    fail_count += 1
                    await ctx.send(
                        f'[{suc_count+fail_count}/{total}] 이미 등록된 단어이거나 서식에 오류가 있는 단어 입니다.'
                    )

            await ctx.send(
                f'작업이 모두 완료되었습니다! [총 {total}개 / 성공 {suc_count}개 / 실패 {fail_count}개]'
            )

    # Functions [ID: 42]
    @commands.hybrid_command(name='끝말잇기', description="학습 된 단어 뜻을 검색합니다!")
    async def word_chain(self, ctx, option: str = '일반'):
        if option == '마라톤':
            round = 50
            history = []
            sample = sampleText()
            start = random.choice(sample)
            start_alter = ""
            record = 0
            time_text = "0분 00초 00"
            await ctx.send(
                f"**잠시후 게임이 시작됩니다!**\n도전자: `{q.readTag(ctx.author)}`\n종목: 단어 이어 말하기 ('{sample}' 중 한 글자가 랜덤으로 배치 됩니다.)"
            )
            sleep(5)
            while True:

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                if replace_sound_char(start) is not None:
                    start_alter = replace_sound_char(start)
                    await ctx.reply(
                        f"**[ROUND: {len(history)+1}/{round}]** `{q.readTag(ctx.author)}`\n## {start}({start_alter})\n으로 시작하는 단어를 입력하세요!\n현재 기록: **`{time_text}`**"
                    )
                else:
                    start_alter = replace_sound_char(start)
                    await ctx.reply(
                        f"**[ROUND: {len(history)+1}/{round}]** `{q.readTag(ctx.author)}`\n## {start}\n으로 시작하는 단어를 입력하세요!\n현재 기록: **`{time_text}`**"
                    )
                start_time = datetime.datetime.now().timestamp()
                input_word = await self.client.wait_for("message", check=check)
                check = input_word.content
                record += datetime.datetime.now().timestamp() - start_time
                recordt = int(record * 100)
                time_text = f"{recordt//6000}분 {(recordt%6000)//100:02d}초 {recordt%100:02d}"

                if check == 'q':
                    await ctx.send("포기 하셨습니다")
                    break
                else:
                    if (check[0] == start or check[0]
                            == start_alter) and check not in history:
                        result = searchWord(check)
                        if result is not None:
                            start = check[-1]
                            history.append(check)
                            wd.newWord(ctx.author, str(result[0]),
                                       str(result[1]), str(result[2]))
                            embed = discord.Embed(
                                title=result[0],
                                description=f'[{result[1]}] {result[2]}',
                                color=0xFFCC70)
                            await ctx.send(embed=embed)
                            if len(history) == round:
                                gain = round * 5 + 3 * int(300 - record) * (
                                    (300 - record) > 0)
                                q.xpAdd(ctx.author, gain)
                                q.moneyAdd(ctx.author, gain)
                                await ctx.reply(
                                    f"## 게임 끝!\n도전자: `{q.readTag(ctx.author)}`\n기록: **`{time_text}`**\n보상: +{gain}XP, +${gain})"
                                )

                                #도전과제
                                if recordt <= 11500 and q.readStorage(
                                        ctx.author, 82) == 0:
                                    q.storageModify(ctx.author, 82, 1)

                                if l.wcRead(
                                        ctx.author,
                                        'regist') >= 1446 and q.readStorage(
                                            ctx.author, 84) == 0:
                                    q.storageModify(ctx.author, 84, 1)

                                break
                        else:
                            record += 5
                            recordt = int(record * 100)
                            time_text = f"{recordt//6000}분 {(recordt%6000)//100:02d}초 {recordt%100:02d}"
                            await ctx.send('`(⩌ʌ ⩌;)`**패널티 +5초!** 없는 단어 입니다...'
                                           )

                    elif check[0] != start:
                        record += 5
                        recordt = int(record * 100)
                        time_text = f"{recordt//6000}분 {(recordt%6000)//100:02d}초 {recordt%100:02d}"
                        await ctx.send(
                            f'`(⩌ʌ ⩌;)` **패널티 +5초!** **`{start}`**로 시작하는 단어를 입력해 주세요...'
                        )

                    elif check in history:
                        record += 3
                        recordt = int(record * 100)
                        time_text = f"{recordt//6000}분 {(recordt%6000)//100:02d}초 {recordt%100:02d}"
                        await ctx.send('`(⩌ʌ ⩌;)`**패널티 +3초!** 이미 사용한 단어 입니다...'
                                       )

        elif option == '일반':
            gamestart = False
            player = []
            player.append({"id": ctx.author.id, "score": 0, "life": 3})
            while True:
                embed = discord.Embed(title='참가자 목록',
                                      description=f'인원: {len(player)}/6',
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
                    "## 끝말잇기 - 인원 모집\n* `@username`을 이용하여 최대 6명 까지 초대가 가능합니다!\n* 초대가 완료되면 `시작`를 입력해 주세요!\n* 게임 생성을 취소하고 싶다면 `취소`를 입력해 주세요!\n* 게임이 시작되면 자동으로 순서가 바뀝니다!",
                    embed=embed)

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                input_word = await self.client.wait_for("message", check=check)
                check = input_word.content

                if check == '시작':
                    if len(player) > 1:
                        gamestart = True
                        await ctx.send(":green_circle: 게임이 성공적으로 생성 되었습니다!")
                        break
                    else:
                        await ctx.send(
                            '`(⩌ʌ ⩌;)` 인원이 너무 적습니다... 적어도 2명 이상 있어야 합니다!')

                elif check == '취소':
                    await ctx.send(":x: 게임 생성이 취소되었습니다.")
                    break

                else:
                    try:
                        if len(player) >= 6:
                            await ctx.send(
                                '`(⩌ʌ ⩌;)` 인원이 너무 많습니다... 최대 6명 까지 참가가 가능합니다!')
                        else:
                            id = int(etc.extractUid(check))
                            name = q.readTagById(id)
                            player.append({"id": id, "score": 0, "life": 3})
                            await ctx.send(
                                f":green_circle: `{name}`가 참가자 목록에 추가되었습니다! ")
                    except:
                        await ctx.send(
                            '`(⩌ʌ ⩌;)` 유효하지 않은 참가자 입니다... 다시 시도해 보세요...')

            if gamestart:
                print(player)
                numpy.random.shuffle(player)
                print(player)
                chain = 1
                history = []
                sample = sampleText()
                start = random.choice(sample)
                start_alter = ""
                end = False

                embed = discord.Embed(title='참가자 목록',
                                      description=f'인원: {len(player)}/6',
                                      color=0xBCE29E)
                for i in range(len(player)):
                    lv = etc.level(q.readXpById(player[i]['id']))
                    embed.add_field(
                        name=
                        f"{player_badge[i]}{etc.lvicon(lv)}{q.readTagById(player[i]['id'])} (Lv. {lv})",
                        value=
                        f"**{player[i]['score']}점** | {lifeUI(player[i]['life'],3)}",
                        inline=False)
                embed.set_footer(text='Discord Bot by Dizzt')
                await ctx.send(
                    f"**잠시후 게임이 시작됩니다!**\n종목: 끝말잇기 ('{sample}' 중 한 글자가 랜덤으로 배치 됩니다.)"
                )
                sleep(5)
                start_time = datetime.datetime.now().timestamp()

                while True:
                    for i in range(len(player)):
                        uid = player[i]['id']
                        ulv = etc.level(q.readXpById(uid))

                        if isOneKill(start):
                            s = int(player[i]['score'] * 0.36)
                            player[i]['score'] -= s
                            player[i]['life'] -= 1
                            start = random.choice(sample)
                            await ctx.send(
                                f'`(⩌ʌ ⩌;)` <@{uid}> **-1 목숨 | -{s}점** 한방 단어 공격을 받았습니다...'
                            )

                        while player[i]['life'] > 0:
                            if replace_sound_char(start) is not None:
                                start_alter = replace_sound_char(start)
                                await ctx.send(
                                    f"**[CHAIN: {chain} | LIFE: {lifeUI(player[i]['life'],3)}]** <@{uid}>\n{player_badge[i]}{etc.lvicon(ulv)} `{q.readTagById(uid)} (Lv. {ulv})`의 차례입니다!\n## {start}({start_alter})\n으로 시작하는 단어를 입력하세요! ('q' 입력시 포기)\n현재 점수는 **{player[i]['score']}점** 입니다."
                                )
                            else:
                                start_alter = ""
                                await ctx.send(
                                    f"**[CHAIN: {chain} | LIFE: {lifeUI(player[i]['life'],3)}]** <@{uid}>\n{player_badge[i]}{etc.lvicon(ulv)} `{q.readTagById(uid)} (Lv. {ulv})`의 차례입니다!\n## {start}\n으로 시작하는 단어를 입력하세요! ('q' 입력시 포기)\n현재 점수는 **{player[i]['score']}점** 입니다."
                                )

                            if player[i]['id'] == 691455977270149171:
                                result = startWord(start, history)
                                if result is not None:
                                    input_word = await ctx.send(result[0])
                                else:
                                    input_word = await ctx.send("q")

                            else:

                                def check(m):
                                    return m.author.id == uid and m.channel == ctx.channel

                                input_word = await self.client.wait_for(
                                    "message", check=check)

                            check = input_word.content

                            if check == 'q':
                                s = int(player[i]['score'] * 0.3)
                                player[i]['score'] -= s
                                player[i]['life'] -= 1
                                start = random.choice(sample)
                                await ctx.send(
                                    f'`(⩌ʌ ⩌;)` <@{uid}> **-1 목숨 | -{s}점** 방어에 실패하였습니다...'
                                )

                            else:
                                if (
                                        check[0] == start
                                        or check[0] == start_alter
                                ) and len(check) > 1 and check not in history:

                                    result = wd.readInGame(check)

                                    if result is None:
                                        result = searchWord(check)

                                    if result is not None:
                                        start = check[-1]
                                        history.append(check)
                                        player[i]['score'] += scoreBoost(
                                            count_break_korean(check),
                                            player[i]['life'])
                                        wd.newWordById(player[i]['id'],
                                                       str(result[0]),
                                                       str(result[1]),
                                                       str(result[2]))
                                        name = q.readTagById(player[i]['id'])
                                        embed = discord.Embed(
                                            title=result[0],
                                            description=
                                            f'[{result[1]}] {result[2]}',
                                            color=color[i])
                                        text = ""
                                        for i in range(len(player)):
                                            lv = etc.level(
                                                q.readXpById(player[i]['id']))
                                            if i == 0:
                                                text += f"{player_badge[i]}{etc.lvicon(lv)}{q.readTagById(player[i]['id'])} | **{player[i]['score']}점** | {lifeUI(player[i]['life'],3)}"
                                            else:
                                                text += f"\n{player_badge[i]}{etc.lvicon(lv)}{q.readTagById(player[i]['id'])} | **{player[i]['score']}점** | {lifeUI(player[i]['life'],3)}"
                                        embed.add_field(name="**점수**",
                                                        value=text,
                                                        inline=False)
                                        embed.set_footer(
                                            text=f"{name} | CHAIN: {chain}")
                                        await ctx.send(embed=embed)
                                        chain += 1
                                        break

                                    else:
                                        player[i]['life'] -= 1
                                        player[i]['score'] -= 20
                                        await ctx.send(
                                            f'`(⩌ʌ ⩌;)` <@{uid}> **-1 목숨 | -20점** 없는 단어입니다...'
                                        )
                                elif check[0] != start:
                                    player[i]['life'] -= 1
                                    player[i]['score'] -= 20
                                    await ctx.send(
                                        f'`(⩌ʌ ⩌;)` <@{uid}> **-1 목숨 | -20점** **`{start}`**로 시작하는 단어를 입력해 주세요...'
                                    )
                                elif check in history:
                                    player[i]['life'] -= 1
                                    player[i]['score'] -= 20
                                    await ctx.send(
                                        f'`(⩌ʌ ⩌;)` <@{uid}> **-1 목숨 | -20점** 이미 사용한 단어 입니다...'
                                    )
                                elif len(check) < 2:
                                    player[i]['life'] -= 1
                                    player[i]['score'] -= 20
                                    await ctx.send(
                                        f'`(⩌ʌ ⩌;)` <@{uid}> **-1 목숨 | -20점** 적어도 2글자 이상 되어야 합니다...'
                                    )

                        if player[i]['life'] == 0:
                            await ctx.send(
                                f'`(⩌ʌ ⩌;)` **{q.readTagById(uid)}** 님이 탈락하였습니다...'
                            )
                            end = True
                            break

                    if end:
                        record = datetime.datetime.now().timestamp(
                        ) - start_time
                        recordt = int(record * 100)
                        embed = discord.Embed(
                            title='결과',
                            description=
                            f'CHAIN: {chain-1}\nTIME: {recordt//6000}분 {(recordt%6000)//100:02d}초 {recordt%100:02d}',
                            color=0xBCE29E)

                        player.sort(key=lambda x: -x['score'])

                        for i in range(len(player)):
                            if player[i]['score'] < 0:
                                player[i]['score'] = 0
                            xp_gain = int(
                                (player[i]['score'] * 1.8 + chain * 5) *
                                (1 - 0.15 * i))
                            money_gain = int(
                                (player[i]['score'] * 1.2 + chain * 3) *
                                (1 - 0.15 * i))
                            q.xpAddById(player[i]['id'], xp_gain)
                            q.moneyAddById(player[i]['id'], money_gain)
                            lv = etc.level(q.readXpById(player[i]['id']))
                            if i == 0:
                                l.wcUpdateIndi(player[i]['id'],
                                               player[i]['score'], chain - 1,
                                               True)
                            else:
                                l.wcUpdateIndi(player[i]['id'],
                                               player[i]['score'], chain - 1,
                                               False)
                            embed.add_field(
                                name=
                                f"`{i+1}등` {etc.lvicon(lv)}{q.readTagById(player[i]['id'])} (Lv. {lv})",
                                value=
                                f"**{player[i]['score']}점** | {lifeUI(player[i]['life'],3)} | +{xp_gain}XP, +${money_gain}",
                                inline=False)

                            #도전과제
                            if l.wcReadById(player[i]['id'],
                                            'win') >= 84 and q.readStorageById(
                                                player[i]['id'], 81) == 0:
                                q.storageModifyById(player[i]['id'], 81, 1)

                            if chain > 421 and q.readStorageById(
                                    player[i]['id'], 83) == 0:
                                q.storageModifyById(player[i]['id'], 83, 1)

                            if l.wcReadById(
                                    player[i]['id'],
                                    'regist') >= 1446 and q.readStorageById(
                                        player[i]['id'], 84) == 0:
                                q.storageModifyById(player[i]['id'], 84, 1)

                        embed.set_footer(text='Discord Bot by Dizzt')
                        await ctx.send("## 게임 끝", embed=embed)
                        break

        elif option == '쿵쿵따':
            gamestart = False
            player = []
            player.append({"id": ctx.author.id, "score": 0, "life": 3})
            while True:
                embed = discord.Embed(title='참가자 목록',
                                      description=f'인원: {len(player)}/6',
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
                    "## 세글자 쿵쿵따 - 인원 모집\n* `@username`을 이용하여 최대 6명 까지 초대가 가능합니다!\n* 초대가 완료되면 `시작`를 입력해 주세요!\n* 게임 생성을 취소하고 싶다면 `취소`를 입력해 주세요!\n* 게임이 시작되면 자동으로 순서가 바뀝니다!",
                    embed=embed)

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                input_word = await self.client.wait_for("message", check=check)
                check = input_word.content

                if check == '시작':
                    if len(player) > 1:
                        gamestart = True
                        await ctx.send(":green_circle: 게임이 성공적으로 생성 되었습니다!")
                        break
                    else:
                        await ctx.send(
                            '`(⩌ʌ ⩌;)` 인원이 너무 적습니다... 적어도 2명 이상 있어야 합니다!')

                elif check == '취소':
                    await ctx.send(":x: 게임 생성이 취소되었습니다.")
                    break

                else:
                    try:
                        if len(player) >= 6:
                            await ctx.send(
                                '`(⩌ʌ ⩌;)` 인원이 너무 많습니다... 최대 6명 까지 참가가 가능합니다!')
                        else:
                            id = int(etc.extractUid(check))
                            name = q.readTagById(id)
                            player.append({"id": id, "score": 0, "life": 3})
                            await ctx.send(
                                f":green_circle: `{name}`가 참가자 목록에 추가되었습니다! ")
                    except:
                        await ctx.send(
                            '`(⩌ʌ ⩌;)` 유효하지 않은 참가자 입니다... 다시 시도해 보세요...')

            if gamestart:
                print(player)
                numpy.random.shuffle(player)
                print(player)
                chain = 1
                history = []
                sample = sampleText()
                start = random.choice(sample)
                start_alter = ""
                end = False

                embed = discord.Embed(title='참가자 목록',
                                      description=f'인원: {len(player)}/6',
                                      color=0xBCE29E)
                for i in range(len(player)):
                    lv = etc.level(q.readXpById(player[i]['id']))
                    embed.add_field(
                        name=
                        f"{player_badge[i]}{etc.lvicon(lv)}{q.readTagById(player[i]['id'])} (Lv. {lv})",
                        value=
                        f"**{player[i]['score']}점** | {lifeUI(player[i]['life'],3)}",
                        inline=False)
                embed.set_footer(text='Discord Bot by Dizzt')
                await ctx.send(
                    f"**잠시후 게임이 시작됩니다!**\n종목: 세글자 쿵쿵따 ('{sample}' 중 한 글자가 랜덤으로 배치 됩니다.)"
                )
                sleep(5)
                start_time = datetime.datetime.now().timestamp()

                while True:
                    for i in range(len(player)):
                        uid = player[i]['id']
                        ulv = etc.level(q.readXpById(uid))

                        if isOneKill(start):
                            s = int(player[i]['score'] * 0.36)
                            player[i]['score'] -= s
                            player[i]['life'] -= 1
                            start = random.choice(sample)
                            await ctx.send(
                                f'`(⩌ʌ ⩌;)` <@{uid}> **-1 목숨 | -{s}점** 한방 단어 공격을 받았습니다...'
                            )

                        while player[i]['life'] > 0:
                            if replace_sound_char(start) is not None:
                                start_alter = replace_sound_char(start)
                                await ctx.send(
                                    f"**[CHAIN: {chain} | LIFE: {lifeUI(player[i]['life'],3)}]** <@{uid}>\n{player_badge[i]}{etc.lvicon(ulv)} `{q.readTagById(uid)} (Lv. {ulv})`의 차례입니다!\n## {start}({start_alter})\n으로 시작하는 단어를 입력하세요! ('q' 입력시 포기)\n현재 점수는 **{player[i]['score']}점** 입니다."
                                )
                            else:
                                start_alter = ""
                                await ctx.send(
                                    f"**[CHAIN: {chain} | LIFE: {lifeUI(player[i]['life'],3)}]** <@{uid}>\n{player_badge[i]}{etc.lvicon(ulv)} `{q.readTagById(uid)} (Lv. {ulv})`의 차례입니다!\n## {start}\n으로 시작하는 단어를 입력하세요! ('q' 입력시 포기)\n현재 점수는 **{player[i]['score']}점** 입니다."
                                )

                            if player[i]['id'] == 691455977270149171:
                                result = startWord3(start, history)
                                if result is not None:
                                    input_word = await ctx.send(result[0])
                                else:
                                    input_word = await ctx.send("q")

                            else:

                                def check(m):
                                    return m.author.id == uid and m.channel == ctx.channel

                                input_word = await self.client.wait_for(
                                    "message", check=check)

                            check = input_word.content

                            if check == 'q':
                                s = int(player[i]['score'] * 0.3)
                                player[i]['score'] -= s
                                player[i]['life'] -= 1
                                start = random.choice(sample)
                                await ctx.send(
                                    f'`(⩌ʌ ⩌;)` <@{uid}> **-1 목숨 | -{s}점** 방어에 실패하였습니다...'
                                )

                            else:
                                if (
                                        check[0] == start
                                        or check[0] == start_alter
                                ) and len(check) == 3 and check not in history:

                                    result = wd.readInGame(check)

                                    if result is None:
                                        result = searchWord(check)

                                    if result is not None:
                                        start = check[-1]
                                        history.append(check)
                                        player[i]['score'] += scoreBoost(
                                            count_break_korean(check),
                                            player[i]['life'])
                                        wd.newWordById(player[i]['id'],
                                                       str(result[0]),
                                                       str(result[1]),
                                                       str(result[2]))
                                        name = q.readTagById(player[i]['id'])
                                        embed = discord.Embed(
                                            title=result[0],
                                            description=
                                            f'[{result[1]}] {result[2]}',
                                            color=color[i])
                                        text = ""
                                        for i in range(len(player)):
                                            lv = etc.level(
                                                q.readXpById(player[i]['id']))
                                            if i == 0:
                                                text += f"{player_badge[i]}{etc.lvicon(lv)}{q.readTagById(player[i]['id'])} | **{player[i]['score']}점** | {lifeUI(player[i]['life'],3)}"
                                            else:
                                                text += f"\n{player_badge[i]}{etc.lvicon(lv)}{q.readTagById(player[i]['id'])} | **{player[i]['score']}점** | {lifeUI(player[i]['life'],3)}"
                                        embed.add_field(name="**점수**",
                                                        value=text,
                                                        inline=False)
                                        embed.set_footer(
                                            text=f"{name} | CHAIN: {chain}")
                                        await ctx.send(embed=embed)
                                        chain += 1

                                        break

                                    else:
                                        player[i]['life'] -= 1
                                        player[i]['score'] -= 20
                                        await ctx.send(
                                            f'`(⩌ʌ ⩌;)` <@{uid}> **-1 목숨 | -20점** 없는 단어입니다...'
                                        )
                                elif check[0] != start:
                                    player[i]['life'] -= 1
                                    player[i]['score'] -= 20
                                    await ctx.send(
                                        f'`(⩌ʌ ⩌;)` <@{uid}> **-1 목숨 | -20점** **`{start}`**로 시작하는 단어를 입력해 주세요...'
                                    )
                                elif check in history:
                                    player[i]['life'] -= 1
                                    player[i]['score'] -= 20
                                    await ctx.send(
                                        f'`(⩌ʌ ⩌;)` <@{uid}> **-1 목숨 | -20점** 이미 사용한 단어 입니다...'
                                    )
                                elif len(check) != 3:
                                    player[i]['life'] -= 1
                                    player[i]['score'] -= 20
                                    await ctx.send(
                                        f'`(⩌ʌ ⩌;)` <@{uid}> **-1 목숨 | -20점** 3글자 단어를 입력해야 합니다...'
                                    )

                        if player[i]['life'] == 0:
                            await ctx.send(
                                f'`(⩌ʌ ⩌;)` **{q.readTagById(uid)}** 님이 탈락하였습니다...'
                            )
                            end = True
                            break

                    if end:
                        record = datetime.datetime.now().timestamp(
                        ) - start_time
                        recordt = int(record * 100)
                        embed = discord.Embed(
                            title='결과',
                            description=
                            f'CHAIN: {chain-1}\nTIME: {recordt//6000}분 {(recordt%6000)//100:02d}초 {recordt%100:02d}',
                            color=0xBCE29E)

                        player.sort(key=lambda x: -x['score'])

                        for i in range(len(player)):
                            if player[i]['score'] < 0:
                                player[i]['score'] = 0
                            xp_gain = int(
                                (player[i]['score'] * 1.8 + chain * 5) *
                                (1 - 0.15 * i))
                            money_gain = int(
                                (player[i]['score'] * 1.2 + chain * 3) *
                                (1 - 0.15 * i))
                            q.xpAddById(player[i]['id'], xp_gain)
                            q.moneyAddById(player[i]['id'], money_gain)
                            lv = etc.level(q.readXpById(player[i]['id']))
                            if i == 0:
                                l.wcUpdateIndi(player[i]['id'],
                                               player[i]['score'], chain - 1,
                                               True)
                            else:
                                l.wcUpdateIndi(player[i]['id'],
                                               player[i]['score'], chain - 1,
                                               False)
                            embed.add_field(
                                name=
                                f"`{i+1}등` {etc.lvicon(lv)}{q.readTagById(player[i]['id'])} (Lv. {lv})",
                                value=
                                f"**{player[i]['score']}점** | {lifeUI(player[i]['life'],3)} | +{xp_gain}XP, +${money_gain}",
                                inline=False)

                            #도전과제
                            if l.wcReadById(player[i]['id'],
                                            'win') >= 84 and q.readStorageById(
                                                player[i]['id'], 81) == 0:
                                q.storageModifyById(player[i]['id'], 81, 1)

                            if chain > 421 and q.readStorageById(
                                    player[i]['id'], 83) == 0:
                                q.storageModifyById(player[i]['id'], 83, 1)

                            if l.wcReadById(
                                    player[i]['id'],
                                    'regist') >= 1446 and q.readStorageById(
                                        player[i]['id'], 84) == 0:
                                q.storageModifyById(player[i]['id'], 84, 1)

                        embed.set_footer(text='Discord Bot by Dizzt')
                        await ctx.send("## 게임 끝", embed=embed)
                        break

        elif option == '은비':
            chain = 1
            score = 0
            life = 3
            history = []
            sample = sampleText()
            start = random.choice(sample)
            start_alter = ""
            await ctx.send(
                f"**잠시후 게임이 시작됩니다!**\n도전자: `{q.readTag(ctx.author)}`\n종목: 끝말잇기 vs 은비 ('{sample}' 중 한 글자가 랜덤으로 배치 됩니다.)"
            )
            sleep(5)
            start_time = datetime.datetime.now().timestamp()

            while True:

                if life == 0:
                    break

                lv = etc.level(q.readXp(ctx.author))
                blv = etc.level(q.readXp(self.client.user))

                if replace_sound_char(start) is not None:
                    start_alter = replace_sound_char(start)
                    await ctx.reply(
                        f"**[CHAIN: {chain} | LIFE: {lifeUI(life,3)}]** `{q.readTag(ctx.author)}`의 차례입니다!\n## {start}({start_alter})\n으로 시작하는 단어를 입력하세요! (q 입력시 포기)\n{player_badge[0]}{etc.lvicon(lv)}{q.readTag(ctx.author)} (Lv. {lv}) | {score}점 | {lifeUI(life,3)}\n{player_badge[1]}{etc.lvicon(blv)}은비#0142 (Lv. {blv}) | 봇은 점수가 기록되지 않습니다..."
                    )
                else:
                    start_alter = ""
                    await ctx.reply(
                        f"**[CHAIN: {chain} | LIFE: {lifeUI(life,3)}]** `{q.readTag(ctx.author)}`의 차례입니다!\n## {start}\n으로 시작하는 단어를 입력하세요! (q 입력시 포기)\n{player_badge[0]}{etc.lvicon(lv)}{q.readTag(ctx.author)} (Lv. {lv}) | {score}점 | {lifeUI(life,3)}\n{player_badge[1]}{etc.lvicon(blv)}은비#0142 (Lv. {blv}) | 봇은 점수가 기록되지 않습니다..."
                    )

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                input_word = await self.client.wait_for("message", check=check)
                check = input_word.content

                if check == 'q':
                    await ctx.send("포기 하셨습니다")
                    break
                else:
                    if (check[0] == start or check[0]
                            == start_alter) and check not in history:

                        result = wd.readInGame(check)

                        if result is None:
                            result = searchWord(check)

                        if result is not None:
                            start = check[-1]
                            history.append(check)
                            score += count_break_korean(check)
                            chain += 1
                            wd.newWord(ctx.author, str(result[0]),
                                       str(result[1]), str(result[2]))
                            await ctx.send(
                                f'## {result[0]}\n[{result[1]}] {result[2]}')

                            lv = etc.level(q.readXp(ctx.author))
                            blv = etc.level(q.readXp(self.client.user))

                            if replace_sound_char(start) is not None:
                                start_alter = replace_sound_char(start)
                                await ctx.send(
                                    f"**[CHAIN: {chain}]** `은비#0142`의 차례입니다!\n## {start}({start_alter})\n으로 시작하는 단어를 입력하세요!\n{player_badge[0]}{etc.lvicon(lv)}{q.readTag(ctx.author)} (Lv. {lv}) | {score}점 | {lifeUI(life,3)}\n{player_badge[1]}{etc.lvicon(blv)}은비#0142 (Lv. {blv}) | 봇은 점수가 기록되지 않습니다..."
                                )
                                result = startWord(
                                    random.choice([start, start_alter]),
                                    history)
                            else:
                                start_alter = ""
                                await ctx.send(
                                    f"**[CHAIN: {chain}]** `은비#0142`의 차례입니다!\n## {start}\n으로 시작하는 단어를 입력하세요!\n{player_badge[0]}{etc.lvicon(lv)}{q.readTag(ctx.author)} (Lv. {lv}) | {score}점 | {lifeUI(life,3)}\n{player_badge[1]}{etc.lvicon(blv)}은비#0142 (Lv. {blv}) | 봇은 점수가 기록되지 않습니다..."
                                )
                                result = startWord(start, history)
                            if result is not None and (result[0][0] == start
                                                       or result[0][0]
                                                       == start_alter):
                                check = result[0]
                                start = check[-1]
                                history.append(check)
                                chain += 1
                                wd.newWord(self.client.user, str(result[0]),
                                           str(result[1]), str(result[2]))
                                await ctx.send(
                                    f'## {result[0]}\n[{result[1]}] {result[2]}'
                                )

                            else:
                                await ctx.reply('`ヽ(￣д￣;)ノ` 항복 할게요 ㅠㅠ')
                                break
                        else:
                            life -= 1
                            score -= 20
                            await ctx.reply('`(⩌ʌ ⩌;)` **-1 목숨** 없는 단어입니다...')
                    elif check[0] != start:
                        life -= 1
                        score -= 20
                        await ctx.reply(
                            f'`(⩌ʌ ⩌;)` **-1 목숨** **`{start}`**로 시작하는 단어를 입력해 주세요...'
                        )
                    elif check in history:
                        life -= 1
                        score -= 20
                        await ctx.reply('`(⩌ʌ ⩌;)` **-1 목숨** 이미 사용한 단어 입니다...')

            record = datetime.datetime.now().timestamp() - start_time
            recordt = int(record * 100)
            if score < 0:
                score = 0
            else:
                score += int(score * 0.1 * life)
            gain_xp = chain * 5 + score * life
            gain_money = chain * 5 + score
            q.xpAdd(ctx.author, gain_xp)
            q.moneyAdd(ctx.author, gain_money)
            l.wcUpdateBot(ctx.author, score, chain - 1)
            lv = etc.level(q.readXp(ctx.author))
            blv = etc.level(q.readXp(self.client.user))
            await ctx.send(
                f"## 게임 끝!\nCHAIN: **{chain-1}**\n{player_badge[0]}{etc.lvicon(lv)}{q.readTag(ctx.author)} (Lv. {lv}) | **{score}점** | +{gain_xp}XP | +${gain_money}\n{player_badge[1]}{etc.lvicon(blv)}은비#0142 (Lv. {blv}) | 봇은 점수가 기록되지 않습니다...\n총 게임 시간: **`{recordt//6000}분 {(recordt%6000)//100:02d}초 {recordt%100:02d}`**"
            )

            #도전과제
            if chain > 421 and q.readStorage(ctx.author, 83) == 0:
                q.storageModify(ctx.author, 83, 1)

            if l.wcRead(ctx.author, 'regist') >= 1446 and q.readStorage(
                    ctx.author, 84) == 0:
                q.storageModify(ctx.author, 84, 1)


async def setup(client):
    await client.add_cog(TestCommands(client))
