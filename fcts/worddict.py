# 0. Import modules
import discord
from discord.ext import commands
import sqlite3
import datetime
import fcts.leaderboard as l
import fcts.sqlcontrol as q
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
    last TEXT NOT NULL
    );"""

    c.execute(sql)
    try:
        c.execute("CREATE UNIQUE INDEX wordindex ON korean(word);")
    except:
        pass
    conn.commit()

    conn.close()


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
    INSERT INTO korean (word, pl, mean, submit, first, last) VALUES (?,?,?,?,?,?);
    '''
    now = datetime.datetime.now() + datetime.timedelta(hours=9)
    now_time = now.strftime('%Y/%m/%d %H:%M:%S')
    data = ((trim_word, pl, mean, user.id, now_time, now_time))
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
    INSERT INTO korean (word, pl, mean, submit, first, last) VALUES (?,?,?,?,?,?);
    '''
    now = datetime.datetime.now() + datetime.timedelta(hours=9)
    now_time = now.strftime('%Y/%m/%d %H:%M:%S')
    data = ((trim_word, pl, mean, user, now_time, now_time))
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
    c.execute("UPDATE korean SET word = ?, submit = ?, last = ? WHERE id = ?",
              (trim_nw, user.id, now_time, value))
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


def readAllByStart(start: str = ""):
    conn = sqlite3.connect(root_dir + '/data/worddict.db')
    c = conn.cursor()
    c.execute(
        "SELECT id, word FROM korean WHERE word LIKE '{}%';".format(start))
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
