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
apikey = "A56D20B6B9466D154FCDFF50433AFB36"

player_badge = [
    "",
    "<:0_1:1294660411081228328>","<:0_2:1294660419625160734>",
    "<:0_3:1294660428097392712>","<:0_4:1294660438423900262>",
    "<:0_5:1294660447265357854>","<:0_6:1294660457646522410>",
    "<:0_7:1294660471282204733>","<:0_8:1294660480580845590>"
]

color = [0, 0xFFB3BA, 0xFFDFBA, 0xFFFFBA, 0xBAFFC9, 0xBAE1FF, 0xEECBFF, 0xFFD4E5, 0xA39193]

def scoreFont(value, digits, type=0):
    num=[
        [
            "<:255_0:1292433088349212682>",
            "<:255_1:1292433098432057446>",
            "<:255_2:1292433109895086122>",
            "<:255_3:1292433121093881958>",
            "<:255_4:1292433133005836341>",
            "<:255_5:1292433145190154244>",
            "<:255_6:1292433157018226728>",
            "<:255_7:1292433169534025830>",
            "<:255_8:1292433181441654846>",
            "<:255_9:1292433192632062046>",
            "<:255_10:1292433208205377587>",
            "<:255_11:1292498510599426088>"
        ],[
            "<:1_0:1292433220507271188>",
            "<:1_1:1292433231198818377>",
            "<:1_2:1292433239226581022>",
            "<:1_3:1292433247870910546>",
            "<:1_4:1292433256616300555>",
            "<:1_5:1292433265017487452>",
            "<:1_6:1292433274794151969>",
            "<:1_7:1292433283224698901>",
            "<:1_8:1292433292481527898>",
            "<:1_9:1292433302325559370>",
            "<:1_10:1292433311192580126>",
            "<:1_11:1292498523027275820>"
        ],[
            "<:2_0:1292433319837040691>",
            "<:2_1:1292433329521688646>",
            "<:2_2:1292433338539184260>",
            "<:2_3:1292433346013429770>",
            "<:2_4:1292433354838249533>",
            "<:2_5:1292433362841108530>",
            "<:2_6:1292433369875091575>",
            "<:2_7:1292433381635784714>",
            "<:2_8:1292433390347489410>",
            "<:2_9:1292433398924709888>",
            "<:2_10:1292433408034603018>",
            "<:2_11:1292498537564733441>"
        ],[
            "<:3_0:1292433422840631420>",
            "<:3_1:1292433460253687888>",
            "<:3_2:1292433480554381403>",
            "<:3_3:1292433492445237309>",
            "<:3_4:1292433503065214987>",
            "<:3_5:1292433514599419927>",
            "<:3_6:1292433525512867872>",
            "<:3_7:1292433537701642251>",
            "<:3_8:1292433552608071821>",
            "<:3_9:1292433566294085643>",
            "<:3_10:1292433577690136609>",
            "<:3_11:1292498546603327540>"
        ],[
            "<:4_0:1292433594526203935>",
            "<:4_1:1292433610619486321>",
            "<:4_2:1292433622187642960>",
            "<:4_3:1292433637555310592>",
            "<:4_4:1292433648121024565>",
            "<:4_5:1292433658879148136>",
            "<:4_6:1292433671407796335>",
            "<:4_7:1292433683713753128>",
            "<:4_8:1292433695046631494>",
            "<:4_9:1292433708669734952>",
            "<:4_10:1292433720237625374>",
            "<:4_11:1292498560046203031>"
        ],[
            "<:5_0:1292433733953257552>",
            "<:5_1:1292433745252716584>",
            "<:5_2:1292433757109751809>",
            "<:5_3:1292433767578992661>",
            "<:5_4:1292433780102922260>",
            "<:5_5:1292433790802595870>",
            "<:5_6:1292433802567749713>",
            "<:5_7:1292433814483763210>",
            "<:5_8:1292433826600976426>",
            "<:5_9:1292433836977946644>",
            "<:5_10:1292433848952688752>",
            "<:5_11:1292498580556480533>"
        ],[
            "<:6_0:1292433879394680833>",
            "<:6_1:1292433893147807774>",
            "<:6_2:1292433905965862914>",
            "<:6_3:1292433916963197019>",
            "<:6_4:1292433926434066442>",
            "<:6_5:1292433936886272020>",
            "<:6_6:1292433948106035211>",
            "<:6_7:1292433958541328434>",
            "<:6_8:1292433968859189328>",
            "<:6_9:1292433981555347507>",
            "<:6_10:1292433996789321772>",
            "<:6_11:1292498596410687550>"
        ],[
            "<:7_0:1294659397242323045>",
            "<:7_1:1294659414162407475>",
            "<:7_2:1294659425927303251>",
            "<:7_3:1294659437604110368>",
            "<:7_4:1294659452112339035>",
            "<:7_5:1294659462233067581>",
            "<:7_6:1294659479627104348>",
            "<:7_7:1294659492788699249>",
            "<:7_8:1294659503710670898>",
            "<:7_9:1294659515798655067>",
            "<:7_10:1294659531430953031>",
            "<:7_11:1294659550720430236>"
        ],[
            "<:8_0:1294659870854746162>",
            "<:8_1:1294659888852504691>",
            "<:8_2:1294659900080918599>",
            "<:8_3:1294659915511500881>",
            "<:8_4:1294659928216309842>",
            "<:8_5:1294659940681646123>",
            "<:8_6:1294659956657881140>",
            "<:8_7:1294659969106579456>",
            "<:8_8:1294659984067530803>",
            "<:8_9:1294659998650990662>",
            "<:8_10:1294660012236476446>",
            "<:8_11:1294660030498471976>"
        ]
    ]

    if digits < len(str(value)):
        digits = len(str(value))

    if value >= 0:
        temp = str(value)
        result = ""

        for i in range(digits - len(temp)):
            result += num[type][10]

        for char in temp:
            result += num[type][int(char)]

        return result
    
    else:
        temp = str(value)[1:]
        result = num[type][11]

        for i in range(digits - len(temp) - 1):
            result += num[type][10]

        for char in temp:
            result += num[type][int(char)]

        return result

    

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
        "립": "입",
        "0": "영",
        "1": "일",
        "·": "점",
        "0": "영",
        "Ɩ": "일",
        "ς": "이",
        "Ɛ": "삼",
        "μ": "사",
        "ट": "오",
        "მ": "육",
        "٢": "칠",
        "8": "팔",
        "୧": "구",
        "✩": "별"
    }
    if char in SOUND_LIST:
        return SOUND_LIST[char]
    else:
        return None


def isOneKill(word):
    ONEKILL_WORD = [
        '겊', '귬', '깆', '껸', '꼇', '꼍', '꾜', '끠', '냔', '른', '늄', '랒', '읖',
        '릇', '쿄', '룅', '븀', '럴', '텝', '엌', '탉', '텝', '튬', '듐', '눞', '틤', '풂',
        '픔', '핕', '휵', '읗', '틋', '틂', '톹', '훽', '콫', '냘', '뇰', '뉼', '늉'
    ]
    if word in ONEKILL_WORD:
        return True
    else:
        return False
    
def searchKiller(start, length=0):
    HARD_WORD = [
        '겊', '귬', '깆', '껸', '꼇', '꼍', '꾜', '끠', '냔', '른', '녘', '늄', '랒', '읖',
        '릇', '쿄', '룅', '륨', '븀', '럴', '텝', '엌', '탉', '텝', '튬', '듐', '눞', '틤', '풂',
        '픔', '핕', '휵', '읗', '빱', '믄', '쁨', '궈', '뤄', '삸', '갊', '랏', '긔', '뮴', '틋',
        '틂', '톹', '훽', '콫', '냘', '뇰', '뉼', '늉', '덟', '돎', '듈', '랖', '랸', '럿', '렁',
        '렝', '롸', '룔', '륀', '릅', '릇', '릊', '릎', '먕', '믐', '밗', '볜', '븐', '븜', '앝',
        '엌', '왑', '웤', '읓', '읔', '읕', '읖', '읗', '잌', '쭘', '쭹', '웡', '찱', '캇', '쾃',
        '쿄', '탉', '텝', '곹', '궃', '궆', '궘', '긑', '깞', '꺠', '껱', '껼', '꽅', '꽌', '꾈',
        '꿑', '뀨', '낕', '넠', '녝', '녬', '놩', '뇸', '눤', '닼', '돍', '돜', '땽', '뚭', '뜹',
        '띱', '랓', '렃', '렄', '렆', '롕', '롶', '롹', '뢔', '뤌', '밲', '뤗', '릋', '릏', '먄',
        '멐', '볌', '봠', '븣', '붤', '븡', '풰', '빝', '뼌', '샄', '샆', '샡', '섳', '솣', '솦',
        '쇔', '숡', '솤', '싥', '싴', '썀', '쎂', '쎕', '얨', '얶', '옄', '왙', '욈', '웆', '웉',
        '윶', '읅', '읨', '쟤', '쟹', '젘', '짗', '캍', '컽', '쾜', '큭', '큿', '탘', '톔', '툿',
        '퓜', '훕', '픠', '윰', '쭝'
    ]
    result = []
    for char in HARD_WORD:
        result += wd.searchSpecial(start, char, length)

    return result

def detectZwong(index, player):
    max_i = len(player) - 1
    detect = None
    if index == max_i:
        detect = 0
    else:
        detect = index + 1

    if player[index]['id'] == 262899129276039169:
        print("Zwong Detected")
        return True
    else:
        print("사격중지 아군이다!")
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
        "별을노래하는마음으로",
        "한송이의국화꽃을피우기위해",
        "가나다라마바사아자차카타파하",
        "내입술의말과",
        "희푸른모니터너머의빛을통해",
        "반짝이는재가당신의불꽃을따라",
        "생명가득한하늘을보여주자",
        "내희망의내용은질투뿐",
        "리갤말고리게로",
        "쌀독에서인심난다",
        "은비의비밀일기장",
        "영일이삼사오육칠팔구",
        "그저나답게빛나는거예요",
        "천포인트한판간다",
        "한비가비비빅을사오면서",
        "●▅▇█▇▆▅▄▇",
        "환자의용태에관한문제·0ƖςƐμटმ٢8୧진단0·1",
        "스텔라✩아르투아",
        "꽃들은천재지변이있더라도아랑곳하지않는다",
        "정원을갖게된후로시간이다르게흐른다",
        "내가더럽혀지더라도오직너에게흰것만을줄게",
        "너무뜨거워서다른사람이부담스러워하지도않고너무차가워서다른사람이상처받지도않는온도는따뜻함",
        "여름과함께떠나보낸너의그뒷모습은행복한꿈이었다말할테니"
    ]
    result = random.choice(sample)
    return result

def shufflePlayer(player, i):
    result = []
    result.append(player[i])
    print(result)
    player.pop(i)
    numpy.random.shuffle(player)
    result = result + player
    print(result)
    return result


# 웹 크롤링으로 단어 검색
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


# 봇 끝말잇기 단어 제시 기능
def startWord(query, history, page=1, length=2, fixed_length=0):
    ans = []
    alter = replace_sound_char(query)
    url = f'https://opendict.korean.go.kr/api/search?key={apikey}&target_type=search&req_type=xml&q={query}&num=100&start={page}'
    r = requests.get(url, verify=False)
    max_page = int(midReturn(r.text, '<total>', '</total>')) // 100

    #단어 목록을 불러오기
    words = midReturn_all(r.text, '<item>', '</item>')
    for w in words:
        word = midReturn(w, '<word>', '</word>')
        word = re.sub('[^A-Za-z0-9가-힣]', '', word)
        if word[0] == query and len(word) >= length and not (word in history):
            if fixed_length == 0:
                ans.append(word)
            elif len(word) == fixed_length:
                ans.append(word)
    
    if fixed_length == 0:
        custom = wd.readAllByStart(query, length)
        for word in custom:
            if len(word) > 1 and not (word in history):
                ans.append(word[1])

    else:
        custom = wd.readAllByStart(query, fixed_length, True)
        for word in custom:
            if len(word) > 1 and not (word in history):
                ans.append(word[1])

    if alter is not None:
        url = f'https://opendict.korean.go.kr/api/search?key={apikey}&target_type=search&req_type=xml&q={alter}&num=100&start={page}'
        r = requests.get(url, verify=False)
        max_page = int(midReturn(r.text, '<total>', '</total>')) // 100

        #단어 목록을 불러오기
        words = midReturn_all(r.text, '<item>', '</item>')
        for w in words:
            word = midReturn(w, '<word>', '</word>')
            word = re.sub('[^A-Za-z0-9가-힣]', '', word)
            if word[0] == query and len(word) >= length and not (word in history):
                ans.append(word)

        if fixed_length == 0:
            custom = wd.readAllByStart(alter, length)
            for word in custom:
                if len(word) > 1 and not (word in history):
                    ans.append(word[1])

        else:
            custom = wd.readAllByStart(alter, fixed_length, True)
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


# 단어목록 뷰어 UI

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
            word = item[1]
            if len(word) > 12:
                word = item[1][:9] + "..."

            result += f"`{item[0]}` • **{word}** • {item[2]}\n"

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
    @commands.hybrid_command(name='사전', description="우리말샘(국립국어원)에 실린 단어 뜻을 검색합니다!")
    async def word_search(self, ctx, *, word: str = ''):
        if word != '':
            result = searchWord(word)
            if result is not None:
                wd.newWord(ctx.author, str(result[0]), str(result[1]),
                           str(result[2]))

                temp = wd.readAll(word)
                embed = discord.Embed(title=temp[1],
                                        description=f'[{temp[2]}] {temp[3]}',
                                        color=0xBCE29E)
                embed.set_footer(
                    text=
                    f'색인번호: {temp[0]}\n등록일: {temp[5]}\n마지막 수정: {q.readTagById(temp[4])} ({temp[6]})'
                )
                await ctx.reply(':green_circle: 우리말샘(국립국어원) 검색 결과입니다.',
                                embed=embed)

            else:
                await ctx.reply('`(⩌Δ ⩌ ;)` 등록되지 않은 단어입니다...')

    @commands.hybrid_command(name='dict', description="단어 뜻을 검색합니다!")
    async def en_search(self, ctx, word: str = ''):
        if word != '':
            result = searchEn(word)
            if result is not None:
                await ctx.reply(f'## {result[0]}\n[{result[1]}] {result[2]}')
            else:
                await ctx.reply('`(⩌ʌ ⩌;)` 등록되지 않은 단어입니다...')

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
                value="단어를 검색합니다. 키워드 서식에 따라 조건 검색도 가능합니다.\n`<키워드>` 키워드가 일치하는 단어의 정보를 불러옵니다.\n`<글자>-` 해당 글자로 시작하는 단어들을 랜덤으로 골라 목록으로 보여줍니다.\n`-<글자>` 해당 글자로 끝나는 단어들을 랜덤으로 골라 목록으로 보여줍니다.\n`~<품사>` 해당 품사에 해당하는 단어들을 랜덤으로 골라 목록으로 보여줍니다.\n`id:<색인번호>` 해당 색인번호를 가진 단어의 정보를 불러옵니다.\%`<패턴>` 패턴을 만족하는 단어의 정보를 불러옵니다.\n`*` 랜덤으로 10개의 단어를 골라 목록으로 보여줍니다.",
                inline=False)
            
            embed.add_field(
                name=f"**등록**",
                value="사용자 지정 단어를 등록합니다.\n기본 형식은 `;은비사전 등록 <단어>/<품사/주제>/<뜻>`입니다.\n`;은비사전 등록`을 통해 등록 요령을 볼 수 있습니다.",
                inline=False)
            
            embed.add_field(
                name=f"**수정**",
                value="사용자 지정 단어의 데이터를 수정합니다.\n기본 형식은 `;은비사전 수정 <색인번호>/<단어>/<품사/주제>/<뜻>`입니다.\n`;은비사전 수정`을 통해 정보 수정 요령을 볼 수 있습니다.",
                inline=False)
            
            embed.add_field(
                name=f"**품사변경**",
                value="품사 데이터를 일괄적으로 변경합니다.\n기본 형식은 `;은비사전 품사변경 <변경전>/<변경후>`입니다.\n`;은비사전 품사변경`을 통해 정보 수정 요령을 볼 수 있습니다.",
                inline=False)
            
            embed.add_field(
                name=f"**목록**",
                value="검색 조건에 해당하는 전체 단어의 목록을 불러옵니다.\n기본 형식은 `;은비사전 목록 <검색조건>`입니다.\n`검색조건`은 `<페이지>`, `<품사>/<페이지>`, `점수/<페이지>`, `품사/<페이지>, `%<패턴>/<페이지>` 가 있습니다.",
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

            elif word[-1] == "!" and len(word) == 2:
                result = searchKiller(word[0], 0)
                print(result)
                if len(result) > 10:
                    temp = random.sample(result, 10)
                else:
                    temp = result

                embed = discord.Embed(
                    title=f'{word[0]}(으)로 시작하는 공격단어',
                    description=
                    f'총 {len(result)}개 중 {len(temp)}개를 무작위로 들고왔습니다!',
                    color=0x8ECDDD)

                for word in temp:
                    info = wd.readAll(word)
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
            
            elif word[0] == "%":
                result = wd.readAllPattern(word[1:])
                if len(result) > 10:
                    temp = random.sample(result, 10)
                else:
                    temp = result

                embed = discord.Embed(
                    title=f'패턴 "{word[1:]}"을 만족하는 단어',
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
                        f'색인번호: {result[0]}\n등록일: {result[5]}\n마지막 수정: {q.readTagById(result[4])} ({result[6]})'
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
                        f'색인번호: {result[0]}\n등록일: {result[5]}\n마지막 수정: {q.readTagById(result[4])} ({result[6]})'
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
                        f'색인번호: {temp[0]}\n등록일: {temp[5]}\n마지막 수정: {q.readTagById(temp[4])} ({temp[6]})'
                    )
                    await ctx.reply(':green_circle: 단어 등록이 완료되었습니다!',
                                    embed=embed)
                except:
                    await ctx.reply(
                        '## `(⩌Δ ⩌ ;)` 단어 등록에 실패 하였습니다...\n* `은비사전 검색 <단어>`로 이미 등록된 단어인지 확인해 주세요.\n* `은비사전 등록 <단어>/<품사>/<뜻>` 구문이 정확한지 확인해 주세요.'
                    )

        elif option == "동의어":
            if word == "도움말":
                await ctx.reply('`은비사전 동의어 <색인번호>/<단어>/` 구문으로 단어 등록이 가능합니다!')
            elif word != "":
                try:
                    result = word.split("/")
                    text = re.sub('[^A-Za-z0-9가-힣ㄱ-ㆎ]', '', result[1])
                    desc = wd.readAllById(int(result[0]))
                    wd.newWord(ctx.author, text, desc[2], desc[3])

                    temp = wd.readAll(text)
                    embed = discord.Embed(title=temp[1],
                                          description=f'[{temp[2]}] {temp[3]}',
                                          color=0xBCE29E)
                    embed.set_footer(
                        text=
                        f'색인번호: {temp[0]}\n등록일: {temp[5]}\n마지막 수정: {q.readTagById(temp[4])} ({temp[6]})'
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
                    '`은비사전 수정 <색인번호>/<단어>/<품사>/<뜻>` 구문으로 단어 수정이 가능합니다.\n`수정 후` 인자들은 비워두면 수정이 되지않고 전 데이터를 유지하게 됩니다.\n`뜻` 항목 맨앞에 `+`를 입력하여 뒤에 이어쓰기를 할 수 있습니다.'
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
                        f'색인번호: {temp[0]}\n등록일: ({temp[5]})\n수정: {q.readTagById(temp[4])} ({temp[6]})'
                    )
                    await ctx.reply(':green_circle: 단어 수정이 완료되었습니다!',
                                    embed=embed)
                    q.xpAdd(ctx.author, 100)
                    q.moneyAdd(ctx.author, 30)
                except:
                    await ctx.reply(
                        '## `(⩌Δ ⩌ ;)` 단어 수정에 실패 하였습니다...\n* `은비사전 검색 <단어>`로 등록되지 않은 단어인지 확인해 주세요.\n* `<전단어>/<후단어>/<품사>/<뜻>` 구문이 정확한지 확인해 주세요.'
                    )

        elif option == "품사변경":

            if word == "도움말":
                await ctx.reply(
                    '`은비사전 품사변경 <변경전>/<변경후>` 구문으로 품사 변경이 가능합니다.\n`변경전` 인자들은 비워두면 품사가 지정되지 않은 단어들이 선택됩니다.'
                )
            elif word != "":
                temp = word.split('/')
                print(temp)
                if len(temp) == 2:
                    wd.categoryModify(ctx.author, temp[0], temp[1])
                    await ctx.reply(f':green_circle: 품사 수정({temp[0]} → {temp[1]})이 완료되었습니다!')
                else:
                    await ctx.reply(
                            '## `(⩌Δ ⩌ ;)` 단어 수정에 실패 하였습니다...\n* `은비사전 품사변경 <변경전>/<변경후>` 구문이 정확한지 확인해 주세요.'
                        )

        elif option == "목록":

            temp = word.split('/')

            if len(temp) == 2:
                try:
                    page = int(temp[1])
                except:
                    None
                if temp[0][0] == "%":
                    pagination_view = PaginationList(timeout=None)
                    pagination_view.data = wd.readAllPattern(temp[0][1:])
                    pagination_view.user = ctx.author
                    pagination_view.current_page = page
                    await pagination_view.send(ctx)
                elif temp[0] == "점수":
                    pagination_view = PaginationList(timeout=None)
                    pagination_view.data = wd.readAllScore()
                    pagination_view.user = ctx.author
                    pagination_view.current_page = page
                    await pagination_view.send(ctx)
                elif temp[0] == "품사":
                    pagination_view = PaginationList(timeout=None)
                    pagination_view.data = wd.readPOSCount()
                    pagination_view.user = ctx.author
                    pagination_view.current_page = page
                    await pagination_view.send(ctx)
                else:
                    pagination_view = PaginationList(timeout=None)
                    pagination_view.data = wd.readAllByPOSWithPOS(temp[0])
                    pagination_view.user = ctx.author
                    pagination_view.current_page = page
                    await pagination_view.send(ctx)

            else:
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
    @commands.hybrid_command(name='일괄수정',
                             description="엑셀에 저장된 파일을 일괄적으로 업데이트 합니다!")
    async def word_edit_db(self, ctx, uid: int = None, file: str = ""):
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
                f"[3/3] {total}개의 파일을 찾았습니다. 사전에 데이터를 추가합니다! 데이터가 많으면 시간이 좀 오래 걸립니다!"
            )

            for data in result:
                try:
                    index = wd.readAll(data[0])[0]
                    if data[2] == "우리말샘":
                        try:
                            mean = searchWord(data[0])[2]
                            wd.plModify(ctx.author, int(index), data[1])
                            wd.meanModify(ctx.author, int(index), mean)
                        except: #mean이 none 일 경우
                            mean = f"{data[1]} 관련 단어."
                            wd.plModify(ctx.author, int(index), data[1])
                            wd.meanModify(ctx.author, int(index), mean)
                    else:
                        wd.plModify(ctx.author, int(index), data[1])
                        wd.meanModify(ctx.author, int(index), data[2])

                    temp = wd.readAll(data[0])
                    embed = discord.Embed(title=temp[1],
                                          description=f'[{temp[2]}] {temp[3]}',
                                          color=0xBCE29E)
                    embed.set_footer(
                        text=
                        f'색인번호: {temp[0]}\n등록일: {temp[5]}\n마지막 수정: {q.readTagById(temp[4])} ({temp[6]})'
                    )
                    suc_count += 1
                    await ctx.send(
                        f'[{suc_count+fail_count}/{total}] 단어 수정이 완료되었습니다.',
                        embed=embed)
                except:
                    fail_count += 1
                    await ctx.send(
                        f'[{suc_count+fail_count}/{total}] 서식에 오류가 있는 단어 입니다.'
                    )

            await ctx.send(
                f'작업이 모두 완료되었습니다! [총 {total}개 / 성공 {suc_count}개 / 실패 {fail_count}개]'
            )

    # Functions [ID: 87]
    @commands.hybrid_command(name='일괄등록',
                             description="엑셀에 저장된 파일을 일괄적으로 업데이트 합니다!")
    async def word_enlist_db(self, ctx, uid: int = None, file: str = "", option:int = 0):
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
                f"[3/3] {total}개의 파일을 찾았습니다. 사전에 데이터를 추가합니다! 데이터가 많으면 시간이 좀 오래 걸립니다!"
            )

            for data in result:
                try:
                    if data[2] == "우리말샘":
                        try:
                            mean = searchWord(data[0])[2]
                            wd.newWordById(uid, data[0], data[1], mean)
                        except: #mean이 none 일 경우
                            mean = f"{data[1]} 관련 단어."
                            wd.newWordById(uid, data[0], data[1], mean)
                    else:
                        wd.newWordById(uid, data[0], data[1], data[2])

                    temp = wd.readAll(data[0])
                    suc_count += 1

                    if option == 0 or data[1] != temp[2]:
                        embed = discord.Embed(title=temp[1],
                                            description=f'[{temp[2]}] {temp[3]}',
                                            color=0xBCE29E)
                        embed.set_footer(
                            text=
                            f'색인번호: {temp[0]}\n등록일: {temp[5]}\n마지막 수정: {q.readTagById(temp[4])} ({temp[6]})'
                        )
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

    @commands.hybrid_command(name='조건등록',
                             description="엑셀에 저장된 파일을 일괄적으로 업데이트 합니다!")
    async def word_c_enlist_db(self, ctx, uid: int = None, file: str = ""):
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
                f"[3/3] {total}개의 파일을 찾았습니다. 사전에 데이터를 추가합니다! 데이터가 많으면 시간이 좀 오래 걸립니다!"
            )

            for data in result:
                try:
                    if data[2] == "우리말샘":
                        try:
                            mean = searchWord(data[0])[2]
                            pos = searchWord(data[0])[1]
                            wd.newWordById(uid, data[0], pos, mean)
                        except: #mean이 none 일 경우
                            mean = f"{data[1]} 관련 단어."
                            wd.newWordById(uid, data[0], data[1], mean)
                    else:
                        wd.newWordById(uid, data[0], data[1], data[2])

                    temp = wd.readAll(data[0])
                    embed = discord.Embed(title=temp[1],
                                          description=f'[{temp[2]}] {temp[3]}',
                                          color=0xBCE29E)
                    embed.set_footer(
                        text=
                        f'색인번호: {temp[0]}\n등록일: {temp[5]}\n마지막 수정: {q.readTagById(temp[4])} ({temp[6]})'
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

    @commands.hybrid_command(name='빠른등록',
                             description="엑셀에 저장된 파일을 일괄적으로 업데이트 합니다!")
    async def word_q_enlist_db(self, ctx, uid: int = None, file: str = ""):
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
                f"[3/3] {total}개의 파일을 찾았습니다. 사전에 데이터를 추가합니다! 데이터가 많으면 시간이 좀 오래 걸립니다!"
            )

            for data in result:
                try:
                    if data[2] == "우리말샘":
                        try:
                            mean = searchWord(data[0])[2]
                            wd.newWordById(uid, data[0], data[1], mean)
                        except: #mean이 none 일 경우
                            mean = f"{data[1]} 관련 단어."
                            wd.newWordById(uid, data[0], data[1], mean)
                    else:
                        wd.newWordById(uid, data[0], data[1], data[2])

                    suc_count += 1
                except:
                    fail_count += 1
                print(f"[{suc_count+fail_count}/{total} | {(suc_count+fail_count)/total:.2%}] 작업 완료")

            await ctx.send(
                f'작업이 모두 완료되었습니다! [총 {total}개 / 성공 {suc_count}개 / 실패 {fail_count}개]'
            )

    @commands.hybrid_command(name='빠른조건등록',
                             description="엑셀에 저장된 파일을 일괄적으로 업데이트 합니다!")
    async def word_qc_enlist_db(self, ctx, uid: int = None, file: str = ""):
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
                f"[3/3] {total}개의 파일을 찾았습니다. 사전에 데이터를 추가합니다! 데이터가 많으면 시간이 좀 오래 걸립니다!"
            )

            for data in result:
                try:
                    if data[2] == "우리말샘":
                        try:
                            mean = searchWord(data[0])[2]
                            pos = searchWord(data[0])[1]
                            wd.newWordById(uid, data[0], pos, mean)
                        except: #mean이 none 일 경우
                            mean = f"{data[1]} 관련 단어."
                            wd.newWordById(uid, data[0], data[1], mean)
                    else:
                        wd.newWordById(uid, data[0], data[1], data[2])

                    suc_count += 1
                except:
                    fail_count += 1
                print(f"[{suc_count+fail_count}/{total} | {(suc_count+fail_count)/total:.2%}] 작업 완료")

            await ctx.send(
                f'작업이 모두 완료되었습니다! [총 {total}개 / 성공 {suc_count}개 / 실패 {fail_count}개]'
            )


    # Functions [ID: 42]
    @commands.hybrid_command(name='끝말잇기', description="일반 끝말잇기를 시작합니다!")
    async def word_chain(self, ctx, option: str = '일반', team: str = '개인'):
        if team == '개인':
            if option in ['일반', '쿵쿵따']:
                gamestart = False
                not_include = []
                player = []
                player.append({"id": ctx.author.id, "score": 0, "life": 3, "color": 0})
                not_include.append(ctx.author.id)
                while True:
                    embed = discord.Embed(title='참가자 목록',
                                            description=f'인원: {len(player)}/8',
                                            color=0xBCE29E)
                    for i in range(len(player)):
                        lv = etc.level(q.readXpById(player[i]['id']))
                        sts = l.wcReadById(player[i]['id'], 'stats')
                        print(sts)
                        embed.add_field(
                            name=
                            f"{i+1}. {etc.lvicon(lv)}{q.readTagById(player[i]['id'])}",
                            value=f"`전적` {sts[2]}전 {sts[3]}승 | {sts[0]}점 | {sts[1]}체인",
                            inline=False)
                    embed.set_footer(text='Discord Bot by Dizzt')
                    await ctx.reply(
                        f"## 끝말잇기 ({option}) - 인원 모집\n* `@username`을 이용하여 최대 8명 까지 초대가 가능합니다!\n* 초대가 완료되면 `시작`를 입력해 주세요!\n* 게임 생성을 취소하고 싶다면 `취소`를 입력해 주세요!\n* 게임이 시작되면 자동으로 순서가 바뀝니다!",
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
                            if len(player) >= 8:
                                await ctx.send(
                                    '`(⩌ʌ ⩌;)` 인원이 너무 많습니다... 최대 8명 까지 참가가 가능합니다!')                            
                            else:
                                if q.tagToUid(check) is not None:
                                    id = q.tagToUid(check)
                                    if id in not_include:
                                        await ctx.send(
                                        '`(⩌ʌ ⩌;)` 이미 참가한 사람입니다...')
                                    else:
                                        name = q.readTagById(id)
                                        player.append({"id": id, "score": 0, "life": 3, "color": 0})
                                        not_include.append(id)
                                        await ctx.send(
                                            f":green_circle: `{name}`가 참가자 목록에 추가되었습니다! ")
                                else:
                                    id = int(etc.extractUid(check))
                                    if id in not_include:
                                        await ctx.send(
                                        '`(⩌ʌ ⩌;)` 이미 참가한 사람입니다...')
                                    else:
                                        name = q.readTagById(id)
                                        player.append({"id": id, "score": 0, "life": 3, "color": 0})
                                        not_include.append(id)
                                        await ctx.send(
                                            f":green_circle: `{name}`가 참가자 목록에 추가되었습니다! ")
                        except:
                            await ctx.send(
                                '`(⩌ʌ ⩌;)` 유효하지 않은 참가자 입니다... 다시 시도해 보세요...')

                if gamestart and option == '일반':
                    numpy.random.shuffle(player)
                    chain = 1
                    history = []
                    sample = sampleText()
                    start = random.choice(sample)
                    start_alter = ""
                    bonus = wd.random_korean()
                    end = False
                    shCheck = False

                    color_arr = [1, 2, 3, 4, 5 ,6, 7, 8]
                    numpy.random.shuffle(color_arr)

                    for i in range(len(player)):
                        player[i]['color'] = color_arr[i]

                    embed = discord.Embed(title='참가자 목록',
                                            description=f'인원: {len(player)}/6',
                                            color=0xBCE29E)
                    for i in range(len(player)):
                        lv = etc.level(q.readXpById(player[i]['id']))
                        embed.add_field(
                            name=
                            f"{player_badge[player[i]['color']]}{etc.lvicon(lv)}{q.readTagById(player[i]['id'])} (Lv. {lv})",
                            value=
                            f"**{scoreFont(player[i]['score'], 4, player[i]['color'])}점** | {lifeUI(player[i]['life'],3)}",
                            inline=False)
                    embed.set_footer(text='Discord Bot by Dizzt')
                    await ctx.send(
                        f"**잠시후 게임이 시작됩니다!**\n종목: 끝말잇기 (**`{sample}`** 중 한 글자가 랜덤으로 배치 됩니다.)"
                    )
                    sleep(5)
                    start_time = datetime.datetime.now().timestamp()

                    while True:
                        for i in range(len(player)):

                            uid = player[i]['id']
                            ulv = etc.level(q.readXpById(uid))

                            if player[i]['life'] > 0 and isOneKill(start):
                                s = int(player[i]['score'] * 0.42)
                                player[i]['score'] -= s
                                player[i]['life'] -= 1
                                start = random.choice(sample)
                                await ctx.send(
                                    f'`(⩌ʌ ⩌;)` <@{uid}> **-1 목숨 | -{s}점** 한방 단어 공격을 받았습니다...'
                                )
                                player = shufflePlayer(player, i)
                                bonus = wd.random_korean()
                                break

                            while player[i]['life'] > 0:

                                if replace_sound_char(start) is not None:
                                    start_alter = replace_sound_char(start)
                                    await ctx.send(
                                        f":chains:{scoreFont(chain, 3, 0)} | {player_badge[player[i]['color']]}{etc.lvicon(ulv)}{q.readTagById(uid)} | {scoreFont(player[i]['score'], 4, player[i]['color'])} | {lifeUI(player[i]['life'],3)} <@{uid}>\n## {start}({start_alter})\n`보너스 글자` {bonus}\n(으)로 시작하는 단어를 입력하세요! ('q' 입력시 포기)"
                                    )
                                else:
                                    start_alter = ""
                                    await ctx.send(
                                        f":chains:{scoreFont(chain, 3, 0)} | {player_badge[player[i]['color']]}{etc.lvicon(ulv)}{q.readTagById(uid)} | {scoreFont(player[i]['score'], 4, player[i]['color'])} | {lifeUI(player[i]['life'],3)} <@{uid}>\n## {start}\n`보너스 글자` {bonus}\n(으)로 시작하는 단어를 입력하세요! ('q' 입력시 포기)"
                                    )

                                if player[i]['id'] == 691455977270149171:
                                    if sample == '●▅▇█▇▆▅▄▇':
                                        alterlist = "가나다라마사바아자파카타파하"
                                        pick = random.randint(1, len(alterlist))
                                        start = alterlist[pick]

                                    dice = 0
                                    if detectZwong(i, player):
                                        dice = random.randint(1, 2)
                                    else:
                                        dice = random.randint(1, 7)
                                    start_alter = replace_sound_char(start)
                                    if dice == 1:
                                        result = searchKiller(start, 0)
                                        if start_alter is not None:
                                            result += searchKiller(start_alter, 0)
                                        if len(result) != 0:
                                            input_word = await ctx.send(random.choice(result))
                                        else:
                                            result = startWord(start, history)
                                            if result is not None:
                                                input_word = await ctx.send(result[0])
                                            else:
                                                input_word = await ctx.send("q")
                                    else:
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
                                    s = int(player[i]['score'] * 0.33)
                                    player[i]['score'] -= s
                                    player[i]['life'] -= 1
                                    start = random.choice(sample)
                                    await ctx.send(
                                        f'`(⩌ʌ ⩌;)` <@{uid}> **-1 목숨 | -{s}점** 방어에 실패하였습니다...'
                                    )
                                    shCheck = True
                                    break

                                else:
                                    if (
                                        check[0] == start
                                        or check[0] == start_alter
                                        or sample == '●▅▇█▇▆▅▄▇'
                                    ) and len(check) > 1 and check not in history:

                                        result = wd.readInGame(check)

                                        if result is None:
                                            result = searchWord(check)

                                        if result is not None:
                                            start = check[-1]
                                            history.append(check)
                                            gain = count_break_korean(check)

                                            if bonus in check:
                                                gain += 2**check.count(bonus)
                                                bonus = wd.random_korean()

                                            player[i]['score'] += scoreBoost(
                                                gain,
                                                player[i]['life'])
                                            wd.newWordById(player[i]['id'],
                                                            str(result[0]),
                                                            str(result[1]),
                                                            str(result[2]))
                                            index = wd.findID(check)
                                            name = q.readTagById(player[i]['id'])
                                            embed = discord.Embed(
                                                title=f'{result[0]} `id: {index}`',
                                                description=
                                                f'[{result[1]}] {result[2]}',
                                                color=color[player[i]['color']])
                                            
                                            if len(player) < 5:
                                                text = ""
                                                for i in range(len(player)):
                                                    lv = etc.level(
                                                        q.readXpById(player[i]['id']))
                                                    if i == 0:
                                                        text += f"{player_badge[player[i]['color']]} {scoreFont(player[i]['score'], 4, player[i]['color'])} {lifeUI(player[i]['life'],3)} {etc.lvicon(lv)}{q.readTagById(player[i]['id'])}"
                                                    else:
                                                        text += f"\n{player_badge[player[i]['color']]} {scoreFont(player[i]['score'], 4, player[i]['color'])} {lifeUI(player[i]['life'],3)} {etc.lvicon(lv)}{q.readTagById(player[i]['id'])}"
                                                embed.add_field(name="**점수**",
                                                                value=text,
                                                                inline=False)
                                            else:
                                                upper = ""
                                                lower = ""
                                                for i in range(4):
                                                    lv = etc.level(
                                                        q.readXpById(player[i]['id']))
                                                    if i == 0:
                                                        upper += f"{player_badge[player[i]['color']]} {scoreFont(player[i]['score'], 4, player[i]['color'])} {lifeUI(player[i]['life'],3)} {etc.lvicon(lv)}{q.readTagById(player[i]['id'])}"
                                                    else:
                                                        upper += f"\n{player_badge[player[i]['color']]} {scoreFont(player[i]['score'], 4, player[i]['color'])} {lifeUI(player[i]['life'],3)} {etc.lvicon(lv)}{q.readTagById(player[i]['id'])}"
                                                for i in range(4, len(player)):
                                                    lv = etc.level(
                                                        q.readXpById(player[i]['id']))
                                                    if i == 4:
                                                        lower += f"{player_badge[player[i]['color']]} {scoreFont(player[i]['score'], 4, player[i]['color'])} {lifeUI(player[i]['life'],3)} {etc.lvicon(lv)}{q.readTagById(player[i]['id'])}"
                                                    else:
                                                        lower += f"\n{player_badge[player[i]['color']]} {scoreFont(player[i]['score'], 4, player[i]['color'])} {lifeUI(player[i]['life'],3)} {etc.lvicon(lv)}{q.readTagById(player[i]['id'])}"
                                                embed.add_field(name="**점수**",
                                                            value=upper,
                                                            inline=False)
                                                embed.add_field(name="",
                                                            value=lower,
                                                            inline=False)

                                            embed.set_footer(
                                                text=f"{name} | CHAIN: {chain}")
                                            await ctx.send(embed=embed)
                                            chain += 1
                                            break

                                        else:
                                            player[i]['life'] -= 1
                                            player[i]['score'] -= 30
                                            await ctx.send(
                                                f'`(⩌ʌ ⩌;)` <@{uid}> **-1 목숨 | -30점** 없는 단어입니다...'
                                            )
                                            shCheck = True
                                            break

                                    elif check[0] != start:
                                        player[i]['life'] -= 1
                                        player[i]['score'] -= 30
                                        await ctx.send(
                                            f'`(⩌ʌ ⩌;)` <@{uid}> **-1 목숨 | -30점** **`{start}`**(으)로 시작하는 단어를 입력해 주세요...'
                                        )

                                    elif check in history:
                                        player[i]['life'] -= 1
                                        player[i]['score'] -= 50
                                        await ctx.send(
                                            f'`(⩌ʌ ⩌;)` <@{uid}> **-1 목숨 | -50점** 이미 사용한 단어 입니다...'
                                        )
                                        shCheck = True
                                        break

                                    elif len(check) < 2:
                                        player[i]['life'] -= 1
                                        player[i]['score'] -= 30
                                        await ctx.send(
                                            f'`(⩌ʌ ⩌;)` <@{uid}> **-1 목숨 | -30점** 적어도 2글자 이상 되어야 합니다...'
                                        )
                                        shCheck = True
                                        break

                            if player[i]['life'] == 0:
                                await ctx.send(
                                    f'`(⩌ʌ ⩌;)` **{q.readTagById(uid)}** 님이 탈락하였습니다...'
                                )
                                end = True
                                break

                            elif player[i]['life'] > 0 and shCheck:
                                shCheck = False
                                player = shufflePlayer(player, i)
                                bonus = wd.random_korean()
                                print(player)
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
                            
                            for i in range(len(player)):
                                if player[i]['life'] == 3:
                                    player[i]['score'] = int(player[i]['score']*2.4)

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
                                    f"{scoreFont(i+1, 1, 0)} {etc.lvicon(lv)}{q.readTagById(player[i]['id'])}",
                                    value=
                                    f"{scoreFont(player[i]['score'], 4, player[i]['color'])} | {lifeUI(player[i]['life'],3)} | +{xp_gain}XP, +${money_gain}",
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

                                if player[i]['score'] >= 1000 and q.readStorageById(
                                            player[i]['id'], 150) == 0:
                                    q.storageModifyById(player[i]['id'], 150, 1)

                                if i == 0:
                                    if player[i]['life'] == 3 and q.readStorageById(player[i]['id'], 148) == 0:
                                        q.storageModifyById(player[i]['id'], 148, 1)

                                    elif player[i]['life'] == 0 and q.readStorageById(player[i]['id'], 149) == 0:
                                        q.storageModifyById(player[i]['id'], 149, 1)


                            embed.set_footer(text='Discord Bot by Dizzt')
                            await ctx.send("## 게임 끝", embed=embed)
                            break

                elif gamestart and option == '쿵쿵따':
                    numpy.random.shuffle(player)
                    chain = 1
                    history = []
                    sample = sampleText()
                    start = random.choice(sample)
                    start_alter = ""
                    length = random.randint(2,5)
                    end = False
                    shCheck = False

                    color_arr = [1, 2, 3, 4, 5 ,6, 7, 8]
                    numpy.random.shuffle(color_arr)

                    for i in range(len(player)):
                        player[i]['color'] = color_arr[i]

                    embed = discord.Embed(title='참가자 목록',
                                            description=f'인원: {len(player)}/6',
                                            color=0xBCE29E)
                    for i in range(len(player)):
                        lv = etc.level(q.readXpById(player[i]['id']))
                        embed.add_field(
                            name=
                            f"{player_badge[player[i]['color']]}{etc.lvicon(lv)}{q.readTagById(player[i]['id'])} (Lv. {lv})",
                            value=
                            f"**{scoreFont(player[i]['score'], 4, player[i]['color'])}점** | {lifeUI(player[i]['life'],3)}",
                            inline=False)
                    embed.set_footer(text='Discord Bot by Dizzt')
                    await ctx.send(
                        f"**잠시후 게임이 시작됩니다!**\n종목: 끝말잇기 (**`{sample}`** 중 한 글자가 랜덤으로 배치 됩니다.)"
                    )
                    sleep(5)
                    start_time = datetime.datetime.now().timestamp()

                    while True:
                        for i in range(len(player)):

                            uid = player[i]['id']
                            ulv = etc.level(q.readXpById(uid))

                            if player[i]['life'] > 0 and isOneKill(start):
                                s = int(player[i]['score'] * 0.42)
                                player[i]['score'] -= s
                                player[i]['life'] -= 1
                                start = random.choice(sample)
                                await ctx.send(
                                    f'`(⩌ʌ ⩌;)` <@{uid}> **-1 목숨 | -{s}점** 한방 단어 공격을 받았습니다...'
                                )
                                player = shufflePlayer(player, i)
                                length = random.randint(2,5)
                                break

                            while player[i]['life'] > 0:

                                if replace_sound_char(start) is not None:
                                    start_alter = replace_sound_char(start)
                                    await ctx.send(
                                        f":chains:{scoreFont(chain, 3, 0)} | {player_badge[player[i]['color']]}{etc.lvicon(ulv)}{q.readTagById(uid)} | {scoreFont(player[i]['score'], 4, player[i]['color'])} | {lifeUI(player[i]['life'],3)} <@{uid}>\n## {start}({start_alter})\n`제한 길이` {length}글자\n(으)로 시작하는 단어를 입력하세요! ('q' 입력시 포기)"
                                    )
                                else:
                                    start_alter = ""
                                    await ctx.send(
                                        f":chains:{scoreFont(chain, 3, 0)} | {player_badge[player[i]['color']]}{etc.lvicon(ulv)}{q.readTagById(uid)} | {scoreFont(player[i]['score'], 4, player[i]['color'])} | {lifeUI(player[i]['life'],3)} <@{uid}>\n## {start}\n`제한 길이` {length}글자\n(으)로 시작하는 단어를 입력하세요! ('q' 입력시 포기)"
                                    )

                                if player[i]['id'] == 691455977270149171:
                                    if sample == '●▅▇█▇▆▅▄▇':
                                        alterlist = "가나다라마사바아자파카타파하"
                                        pick = random.randint(1, len(alterlist))
                                        start = alterlist[pick]

                                    dice = 0
                                    if detectZwong(i, player):
                                        dice = random.randint(1, 2)
                                    else:
                                        dice = random.randint(1, 7)
                                    start_alter = replace_sound_char(start)
                                    if dice == 1:
                                        result = searchKiller(start, length)
                                        if start_alter is not None:
                                            result += searchKiller(start_alter, length)
                                        if len(result) != 0:
                                            input_word = await ctx.send(random.choice(result))
                                        else:
                                            result = startWord(start, history, fixed_length=length)
                                            if result is not None:
                                                input_word = await ctx.send(result[0])
                                            else:
                                                input_word = await ctx.send("q")
                                    else:
                                        result = startWord(start, history, fixed_length=length)
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
                                    s = int(player[i]['score'] * 0.33)
                                    player[i]['score'] -= s
                                    player[i]['life'] -= 1
                                    start = random.choice(sample)
                                    await ctx.send(
                                        f'`(⩌ʌ ⩌;)` <@{uid}> **-1 목숨 | -{s}점** 방어에 실패하였습니다...'
                                    )
                                    shCheck = True
                                    break

                                else:
                                    if (
                                        check[0] == start
                                        or check[0] == start_alter
                                        or sample == '●▅▇█▇▆▅▄▇'
                                    ) and len(check) == length and check not in history:

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
                                            index = wd.findID(check)
                                            name = q.readTagById(player[i]['id'])
                                            embed = discord.Embed(
                                                title=f'{result[0]} `id: {index}`',
                                                description=
                                                f'[{result[1]}] {result[2]}',
                                                color=color[player[i]['color']])
                                            
                                            if len(player) < 5:
                                                text = ""
                                                for i in range(len(player)):
                                                    lv = etc.level(
                                                        q.readXpById(player[i]['id']))
                                                    if i == 0:
                                                        text += f"{player_badge[player[i]['color']]} {scoreFont(player[i]['score'], 4, player[i]['color'])} {lifeUI(player[i]['life'],3)} {etc.lvicon(lv)}{q.readTagById(player[i]['id'])}"
                                                    else:
                                                        text += f"\n{player_badge[player[i]['color']]} {scoreFont(player[i]['score'], 4, player[i]['color'])} {lifeUI(player[i]['life'],3)} {etc.lvicon(lv)}{q.readTagById(player[i]['id'])}"
                                                embed.add_field(name="**점수**",
                                                                value=text,
                                                                inline=False)
                                            else:
                                                upper = ""
                                                lower = ""
                                                for i in range(4):
                                                    lv = etc.level(
                                                        q.readXpById(player[i]['id']))
                                                    if i == 0:
                                                        upper += f"{player_badge[player[i]['color']]} {scoreFont(player[i]['score'], 4, player[i]['color'])} {lifeUI(player[i]['life'],3)} {etc.lvicon(lv)}{q.readTagById(player[i]['id'])}"
                                                    else:
                                                        upper += f"\n{player_badge[player[i]['color']]} {scoreFont(player[i]['score'], 4, player[i]['color'])} {lifeUI(player[i]['life'],3)} {etc.lvicon(lv)}{q.readTagById(player[i]['id'])}"
                                                for i in range(4, len(player)):
                                                    lv = etc.level(
                                                        q.readXpById(player[i]['id']))
                                                    if i == 4:
                                                        lower += f"{player_badge[player[i]['color']]} {scoreFont(player[i]['score'], 4, player[i]['color'])} {lifeUI(player[i]['life'],3)} {etc.lvicon(lv)}{q.readTagById(player[i]['id'])}"
                                                    else:
                                                        lower += f"\n{player_badge[player[i]['color']]} {scoreFont(player[i]['score'], 4, player[i]['color'])} {lifeUI(player[i]['life'],3)} {etc.lvicon(lv)}{q.readTagById(player[i]['id'])}"
                                                embed.add_field(name="**점수**",
                                                            value=upper,
                                                            inline=False)
                                                embed.add_field(name="",
                                                            value=lower,
                                                            inline=False)

                                            embed.set_footer(
                                                text=f"{name} | CHAIN: {chain}")
                                            await ctx.send(embed=embed)
                                            chain += 1
                                            break

                                        else:
                                            player[i]['life'] -= 1
                                            player[i]['score'] -= 30
                                            await ctx.send(
                                                f'`(⩌ʌ ⩌;)` <@{uid}> **-1 목숨 | -30점** 없는 단어입니다...'
                                            )
                                            shCheck = True
                                            break

                                    elif check[0] != start:
                                        player[i]['life'] -= 1
                                        player[i]['score'] -= 30
                                        await ctx.send(
                                            f'`(⩌ʌ ⩌;)` <@{uid}> **-1 목숨 | -30점** **`{start}`**(으)로 시작하는 단어를 입력해 주세요...'
                                        )

                                    elif check in history:
                                        player[i]['life'] -= 1
                                        player[i]['score'] -= 50
                                        await ctx.send(
                                            f'`(⩌ʌ ⩌;)` <@{uid}> **-1 목숨 | -50점** 이미 사용한 단어 입니다...'
                                        )
                                        shCheck = True
                                        break

                                    elif len(check) != length:
                                        player[i]['life'] -= 1
                                        player[i]['score'] -= 30
                                        await ctx.send(
                                            f'`(⩌ʌ ⩌;)` <@{uid}> **-1 목숨 | -30점** {length}글자 단어만 가능합니다...'
                                        )
                                        shCheck = True
                                        break

                            if player[i]['life'] == 0:
                                await ctx.send(
                                    f'`(⩌ʌ ⩌;)` **{q.readTagById(uid)}** 님이 탈락하였습니다...'
                                )
                                end = True
                                break

                            elif player[i]['life'] > 0 and shCheck:
                                shCheck = False
                                length = random.randint(2,5)
                                player = shufflePlayer(player, i)
                                print(player)
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
                            
                            for i in range(len(player)):
                                if player[i]['life'] == 3:
                                    player[i]['score'] = int(player[i]['score']*2.4)

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
                                    f"{scoreFont(i+1, 1, 0)} {etc.lvicon(lv)}{q.readTagById(player[i]['id'])}",
                                    value=
                                    f"{scoreFont(player[i]['score'], 4, player[i]['color'])} | {lifeUI(player[i]['life'],3)} | +{xp_gain}XP, +${money_gain}",
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

                                if player[i]['score'] >= 1000 and q.readStorageById(
                                            player[i]['id'], 150) == 0:
                                    q.storageModifyById(player[i]['id'], 150, 1)

                                if i == 0:
                                    if player[i]['life'] == 3 and q.readStorageById(player[i]['id'], 148) == 0:
                                        q.storageModifyById(player[i]['id'], 148, 1)
                                        
                                    elif player[i]['life'] == 0 and q.readStorageById(player[i]['id'], 149) == 0:
                                        q.storageModifyById(player[i]['id'], 149, 1)

                            embed.set_footer(text='Discord Bot by Dizzt')
                            await ctx.send("## 게임 끝", embed=embed)
                            break
        
        if team == '팀전':
            if option in ['일반', '쿵쿵따']:
                gamestart = False

                not_include = []
                player = []
                team1 = []
                team2 = []

                player.append({"id": ctx.author.id, "score": 0, "life": 3, "color": 0, "team": 0})
                not_include.append(ctx.author.id)

                while True:
                    embed = discord.Embed(title='참가자 목록',
                                            description=f'인원: {len(player)}/8',
                                            color=0xBCE29E)
                    for i in range(len(player)):
                        lv = etc.level(q.readXpById(player[i]['id']))
                        sts = l.wcReadById(player[i]['id'], 'stats')
                        print(sts)
                        embed.add_field(
                            name=
                            f"`Team {player[i]['team']}` {etc.lvicon(lv)}{q.readTagById(player[i]['id'])}",
                            value=f"`전적` {sts[2]}전 {sts[3]}승 | {sts[0]}점 | {sts[1]}체인",
                            inline=False)
                    embed.set_footer(text='Discord Bot by Dizzt')
                    await ctx.reply(
                        f"## 끝말잇기 ({option}) - 인원 모집\n* `@username`을 이용하여 최대 8명 까지 초대가 가능합니다!\n* 초대가 완료되면 `시작`를 입력해 주세요!\n* 게임 생성을 취소하고 싶다면 `취소`를 입력해 주세요!\n* 게임이 시작되면 자동으로 순서가 바뀝니다!",
                        embed=embed)

                    def check(m):
                        return m.author == ctx.author and m.channel == ctx.channel

                    input_word = await self.client.wait_for("message", check=check)
                    check = input_word.content

                    if check == '시작':
                        if len(player) > 2:
                            if len(player) % 2 == 0:
                                if 2*len(team1) <= len(player) and 2*len(team2) <= len(player):
                                    gamestart = True
                                    await ctx.send(":green_circle: 게임이 성공적으로 생성 되었습니다!")
                                    break
                                else:
                                    await ctx.send(
                                    '`(⩌ʌ ⩌;)` 팀 구성원 수가 다릅니다... 각 팀에는 같은 수의 플레이어가 있어야 합니다.')
                            else:
                                await ctx.send(
                                '`(⩌ʌ ⩌;)` 팀 구성원 수가 다릅니다... 각 팀에는 같은 수의 플레이어가 있어야 합니다.')
                        else:
                            await ctx.send(
                                '`(⩌ʌ ⩌;)` 인원이 너무 적습니다... 적어도 2명 이상 있어야 합니다!')

                    elif check == '취소':
                        await ctx.send(":x: 게임 생성이 취소되었습니다.")
                        break

                    else:
                        try:
                            if len(player) >= 8:
                                await ctx.send(
                                    '`(⩌ʌ ⩌;)` 인원이 너무 많습니다... 최대 8명 까지 참가가 가능합니다!')                            
                            else:
                                if q.tagToUid(check) is not None:
                                    id = q.tagToUid(check)
                                    if id in not_include:
                                        await ctx.send(
                                        '`(⩌ʌ ⩌;)` 이미 참가한 사람입니다...')
                                    else:
                                        name = q.readTagById(id)
                                        player.append({"id": id, "score": 0, "life": 3, "color": 0})
                                        not_include.append(id)
                                        await ctx.send(
                                            f":green_circle: `{name}`가 참가자 목록에 추가되었습니다! ")
                                else:
                                    id = int(etc.extractUid(check))
                                    if id in not_include:
                                        await ctx.send(
                                        '`(⩌ʌ ⩌;)` 이미 참가한 사람입니다...')
                                    else:
                                        name = q.readTagById(id)
                                        player.append({"id": id, "score": 0, "life": 3, "color": 0})
                                        not_include.append(id)
                                        await ctx.send(
                                            f":green_circle: `{name}`가 참가자 목록에 추가되었습니다! ")
                        except:
                            await ctx.send(
                                '`(⩌ʌ ⩌;)` 유효하지 않은 참가자 입니다... 다시 시도해 보세요...')

    # Wordchain Test [ID: 79]
    @commands.hybrid_command(name='테스트용',
                             description="테스트")
    async def wordchain_test(self, ctx):
        wd.readPOSCount()
        await ctx.send('테스트')


async def setup(client):
    await client.add_cog(TestCommands(client))
