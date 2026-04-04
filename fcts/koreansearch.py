import fcts.sqlcontrol as q
import fcts.etcfunctions as etc
import fcts.leaderboard as l
import os
import requests
import re
from fcts.koreanbreak import count_break_korean
import fcts.worddict as wd
import random

from config.rootdir import root_dir

apikey = "A56D20B6B9466D154FCDFF50433AFB36"


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