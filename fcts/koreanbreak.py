#한글 초중종성 분리기

CHO = [
    'ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ',
    'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'
]
JUNG = [
    'ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ',
    'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ'
]
JONG = [
    '', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ',
    'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'
]


def break_korean(string):
    break_words = []
    for k in string:
        if ord("가") <= ord(k) <= ord("힣"):
            index = ord(k) - ord("가")
            c_cho = int((index / 28) / 21)
            c_jung = int((index / 28) % 21)
            c_jong = int(index % 28)

            break_words.append(CHO[c_cho])
            break_words.append(JUNG[c_jung])
            if c_jong > 0:
                break_words.append(JONG[c_jong])
        else:
            break_words.append(k)
    return break_words


def count_break_korean(string):
    break_words = 0
    for k in string:
        if ord("가") <= ord(k) <= ord("힣"):
            index = ord(k) - ord("가")
            c_jong = int(index % 28)
            break_words += 2
            if c_jong > 0:
                break_words += 1
        else:
            break_words += 1
    return break_words


def random_korean_unused():
    cho = r.choice([0, 1, 2, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 16 ,17 ,18 ,19 ,20])
    jung = r.choice([0, 1, 2, 4, 5, 6, 8, 9, 12, 13, 17 ,18 ,20])
    jong = r.choice([0, 1, 4, 8, 16, 17, 19, 21, 22, 23, 25])
    return chr(ord("가")+ cho*28*21 + jung*28 + jong)
