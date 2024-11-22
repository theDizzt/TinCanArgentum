# 0. Import modules
import discord
from discord.ext import commands
import sqlite3
import datetime
import random as r
import fcts.leaderboard as l
import fcts.sqlcontrol as q
from fcts.koreanbreak import count_break_korean
from config.rootdir import root_dir

# 1. Connect DB
conn = sqlite3.connect(root_dir + '/data/worddict.db')
c = conn.cursor()


# 2.1. Init Setting
def initSetting():
    conn = sqlite3.connect(root_dir + '/data/worddict.db')
    c = conn.cursor()

    sql = """CREATE TABLE IF NOT EXISTS korean(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT NOT NULL,
    pl TEXT NOT NULL,
    mean TEXT NOT NULL,
    submit INTEGER NOT NULL,
    first TEXT NOT NULL,
    last TEXT NOT NULL,
    score INTEGER DEFAULT 0
    );"""

    c.execute(sql)
    try:
        c.execute("CREATE UNIQUE INDEX wordindex ON korean(word);")
    except:
        pass
    conn.commit()

    conn.close()

    #scoreUpdateAll()


# 3. Actions


# 3.1. Add data
def newWord(user: discord.Member = None,
            word: str = "",
            pl: str = "",
            mean: str = ""):

    conn = sqlite3.connect(root_dir + '/data/worddict.db')
    c = conn.cursor()

    trim_word = word.replace(" ", "")

    INSERT_SQL = '''
    INSERT INTO korean (word, pl, mean, submit, first, last, score) VALUES (?,?,?,?,?,?,?);
    '''
    now = datetime.datetime.now() + datetime.timedelta(hours=9)
    now_time = now.strftime('%Y/%m/%d %H:%M:%S')
    data = ((trim_word, pl, mean, user.id, now_time, now_time, count_break_korean(trim_word)))
    try:
        c.execute(INSERT_SQL, data)
        l.wcUpdateRegist(user)
        q.xpAdd(user, 100)
        q.moneyAdd(user, 30)
        print("단어 등록 완료")
    except:
        print("이미 존재하는 단어입니다.")
    conn.commit()
    conn.close()


def newWordById(user: int = None,
                word: str = "",
                pl: str = "",
                mean: str = ""):

    conn = sqlite3.connect(root_dir + '/data/worddict.db')
    c = conn.cursor()

    trim_word = word.replace(" ", "")

    INSERT_SQL = '''
    INSERT INTO korean (word, pl, mean, submit, first, last, score) VALUES (?,?,?,?,?,?,?);
    '''
    now = datetime.datetime.now() + datetime.timedelta(hours=9)
    now_time = now.strftime('%Y/%m/%d %H:%M:%S')
    data = ((trim_word, pl, mean, user, now_time, now_time, count_break_korean(trim_word)))
    try:
        c.execute(INSERT_SQL, data)
        l.wcUpdateRegistById(user)
        q.xpAddById(user, 100)
        q.moneyAddById(user, 30)
        print("단어 등록 완료")
    except:
        print("이미 존재하는 단어입니다.")
    conn.commit()
    conn.close()


# 3.2.1.1. Xp Value Edit
def wordModify(user: discord.Member = None, value: int = None, nw: str = ""):
    conn = sqlite3.connect(root_dir + '/data/worddict.db')
    c = conn.cursor()
    trim_nw = nw.replace(" ", "")
    now = datetime.datetime.now() + datetime.timedelta(hours=9)
    now_time = now.strftime('%Y/%m/%d %H:%M:%S')
    c.execute("UPDATE korean SET word = ?, submit = ?, last = ?, score = ? WHERE id = ?",
              (trim_nw, user.id, now_time, count_break_korean(trim_nw), value))
    conn.commit()
    c.close()

def plModify(user: discord.Member = None, value: int = None, pl: str = ""):
    conn = sqlite3.connect(root_dir + '/data/worddict.db')
    c = conn.cursor()
    now = datetime.datetime.now() + datetime.timedelta(hours=9)
    now_time = now.strftime('%Y/%m/%d %H:%M:%S')
    c.execute("UPDATE korean SET pl = ?, submit = ?, last = ? WHERE id = ?",
              (pl, user.id, now_time, value))
    conn.commit()
    c.close()

def meanModify(user: discord.Member = None, value: int = None, mean: str = ""):
    conn = sqlite3.connect(root_dir + '/data/worddict.db')
    c = conn.cursor()
    now = datetime.datetime.now() + datetime.timedelta(hours=9)
    now_time = now.strftime('%Y/%m/%d %H:%M:%S')
    c.execute("UPDATE korean SET mean = ?, submit = ?, last = ? WHERE id = ?",
              (mean, user.id, now_time, value))
    conn.commit()
    c.close()

def categoryModify(user: discord.Member = None, opl: str = '*', npl: str = None):
    conn = sqlite3.connect(root_dir + '/data/worddict.db')
    c = conn.cursor()

    if npl is not None:
        if opl == '*':
            now = datetime.datetime.now() + datetime.timedelta(hours=9)
            now_time = now.strftime('%Y/%m/%d %H:%M:%S')
            c.execute("UPDATE korean SET pl = ?, submit = ?, last = ? WHERE pl = ?",
                ('(없음)', user.id, now_time, ''))
            conn.commit()

        else:
            print(0)
            now = datetime.datetime.now() + datetime.timedelta(hours=9)
            now_time = now.strftime('%Y/%m/%d %H:%M:%S')
            c.execute("UPDATE korean SET pl = ?, submit = ?, last = ? WHERE pl = ?",
                (npl, user.id, now_time, opl))
            conn.commit()
            print(1)

    c.close()

# 3.3.1. Read All
def readAll(word: str = ""):
    trim_word = word.replace(" ", "")
    conn = sqlite3.connect(root_dir + '/data/worddict.db')
    c = conn.cursor()
    c.execute("SELECT * FROM korean WHERE word='{}';".format(trim_word))
    result = c.fetchone()
    return result

def readAllById(value: int = None):
    conn = sqlite3.connect(root_dir + '/data/worddict.db')
    c = conn.cursor()
    c.execute("SELECT * FROM korean WHERE id=?;", (value, ))
    result = c.fetchone()
    return result

def readInGame(word: str = ""):
    trim_word = word.replace(" ", "")
    conn = sqlite3.connect(root_dir + '/data/worddict.db')
    c = conn.cursor()
    c.execute(
        "SELECT word, pl, mean FROM korean WHERE word='{}';".format(trim_word))
    result = c.fetchone()
    return result

def readWordAll():
    conn = sqlite3.connect(root_dir + '/data/worddict.db')
    c = conn.cursor()
    c.execute(
        "SELECT id, word FROM korean;")
    result = c.fetchall()
    return result

def readAllByStart(start: str = "", length: int = 2, fixed: bool = False):
    conn = sqlite3.connect(root_dir + '/data/worddict.db')
    c = conn.cursor()
    if fixed:
        c.execute(
            "SELECT id, word FROM korean WHERE word LIKE '{}';".format(start + (length-1)*'_'))
        result = c.fetchall()
    else:
        c.execute(
            "SELECT id, word FROM korean WHERE word LIKE '{}';".format(start + (length-1)*'_' + '%'))
        result = c.fetchall()

    return result

def readAllByEnd(start: str = ""):
    conn = sqlite3.connect(root_dir + '/data/worddict.db')
    c = conn.cursor()
    c.execute(
        "SELECT id, word FROM korean WHERE word LIKE '%{}';".format(start))
    result = c.fetchall()
    return result

def readAllByPOS(pos: str = ""):
    conn = sqlite3.connect(root_dir + '/data/worddict.db')
    c = conn.cursor()
    c.execute(
        "SELECT id, word FROM korean WHERE pl = '{}';".format(pos))
    result = c.fetchall()
    return result

def readAllRandom():
    conn = sqlite3.connect(root_dir + '/data/worddict.db')
    c = conn.cursor()
    c.execute(
        "SELECT id, word FROM korean;")
    result = c.fetchall()
    return result

def readAllWithPOS():
    conn = sqlite3.connect(root_dir + '/data/worddict.db')
    c = conn.cursor()
    c.execute(
        "SELECT id, word, pl FROM korean;")
    result = c.fetchall()
    return result

def readAllByPOSWithPOS(pos: str = ""):
    conn = sqlite3.connect(root_dir + '/data/worddict.db')
    c = conn.cursor()
    c.execute(
        "SELECT id, word, pl FROM korean WHERE pl = '{}';".format(pos))
    result = c.fetchall()
    return result

def readPOSCount():
    conn = sqlite3.connect(root_dir + '/data/worddict.db')
    c = conn.cursor()
    c.execute(
        "SELECT rowid, pl, COUNT(*) FROM korean GROUP BY pl;")
    result = c.fetchall()
    print(result)
    return result

def readAllPattern(pattern: str = ""):
    conn = sqlite3.connect(root_dir + '/data/worddict.db')
    c = conn.cursor()
    c.execute(
        "SELECT id, word, pl FROM korean WHERE word like '%{}%';".format(pattern))
    result = c.fetchall()
    return result

def readAllScore():
    conn = sqlite3.connect(root_dir + '/data/worddict.db')
    c = conn.cursor()
    c.execute(
        "SELECT id, word, score FROM korean ORDER BY score DESC, word;")
    result = c.fetchall()
    return result

def searchSpecial(start, end, length=0):
    temp = []

    if length == 0:
        conn = sqlite3.connect(root_dir + '/data/worddict.db')
        c = conn.cursor()
        c.execute(
            "SELECT word FROM korean WHERE word like '{}';".format(start+"%"+end))
        result = c.fetchall()

        for t in result:
            temp.append(t[0])

    elif length >= 2:
        conn = sqlite3.connect(root_dir + '/data/worddict.db')
        c = conn.cursor()
        c.execute(
            "SELECT word FROM korean WHERE word like '{}';".format(start + (length-2)*'_' + end))
        result = c.fetchall()

        for t in result:
            temp.append(t[0])

    return temp

def findID(word: str = ""):
    trim_word = word.replace(" ", "")
    conn = sqlite3.connect(root_dir + '/data/worddict.db')
    c = conn.cursor()
    c.execute("SELECT id FROM korean WHERE word='{}';".format(trim_word))
    result = c.fetchone()[0]
    
    return result

def scoreUpdateAll():
    conn = sqlite3.connect(root_dir + '/data/worddict.db')
    c = conn.cursor()
    c.execute("SELECT id, word FROM korean;")
    result = c.fetchall()
    for temp in result:
        c.execute("UPDATE korean SET score = ? WHERE id = ?",
              (count_break_korean(temp[1]), temp[0]))
        conn.commit()
        print(temp[0], '-', count_break_korean(temp[1]))

    return None

def random_korean():
    temp = r.choice(readAllRandom())
    result = r.choice(temp[1])
    return result
