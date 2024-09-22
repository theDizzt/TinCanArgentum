# Import modules
import discord
import sqlite3
import datetime
from config.rootdir import root_dir

# Connect DB
conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
c = conn.cursor()


# Init Setting
def initSetting():
    conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
    c = conn.cursor()

    sql = """CREATE TABLE IF NOT EXISTS mathgame(
    id INTEGER PRIMARY KEY,
    score INTEGER NOT NULL,
    scoredate TEXT NOT NULL,
    count INTEGER NOT NULL,
    countdate TEXT NOT NULL
    );"""

    c.execute(sql)
    conn.commit()

    sql = """CREATE TABLE IF NOT EXISTS rps(
    id INTEGER PRIMARY KEY,
    score INTEGER NOT NULL,
    scoredate TEXT NOT NULL,
    count INTEGER NOT NULL,
    countdate TEXT NOT NULL,
    maxchain INTEGER NOT NULL,
    maxchaindate TEXT NOT NULL,
    win INTEGER NOT NULL,
    windate TEXT NOT NULL,
    tie INTEGER NOT NULL,
    tiedate TEXT NOT NULL
    );"""

    c.execute(sql)
    conn.commit()

    sql = """CREATE TABLE IF NOT EXISTS wordchain(
    id INTEGER PRIMARY KEY,
    regist INTEGER NOT NULL,
    indi_score INTEGER NOT NULL,
    indi_count INTEGER NOT NULL,
    indi_play INTEGER NOT NULL,
    indi_win INTEGER NOT NULL,
    bot_score INTEGER NOT NULL,
    bot_count INTEGER NOT NULL,
    mara_half INTEGER NOT NULL,
    mara_full INTEGER NOT NULL
    );"""

    c.execute(sql)
    conn.commit()

    sql = """CREATE TABLE IF NOT EXISTS yahtzee(
    id INTEGER PRIMARY KEY,
    score INTEGER NOT NULL,
    scoredate TEXT NOT NULL,
    play INTEGER NOT NULL,
    win INTEGER NOT NULL
    );"""

    c.execute(sql)
    conn.commit()


#Mathgame
def mathDataUpdate(user: discord.Member = None,
                   score: int = 0,
                   count: int = 0):
    conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
    c = conn.cursor()

    try:
        INSERT_SQL = 'INSERT INTO mathgame (id, score, scoredate, count, countdate) VALUES (?,?,?,?,?);'
        now = datetime.datetime.now() + datetime.timedelta(hours=9)
        now_date = now.strftime('%Y/%m/%d %H:%M:%S')

        data = ((user.id, score, now_date, count, now_date))
        c.execute(INSERT_SQL, data)
        conn.commit()

    except:
        sql = "SELECT * FROM mathgame WHERE id = ?"
        c.execute(sql, (user.id, ))
        result = c.fetchone()

        if score > result[1]:
            now = datetime.datetime.now() + datetime.timedelta(hours=9)
            now_date = now.strftime('%Y/%m/%d %H:%M:%S')
            c.execute(
                "UPDATE mathgame SET score = ?, scoredate = ? WHERE id = ?",
                (score, now_date, user.id))
            conn.commit()

        if count > result[3]:
            now = datetime.datetime.now() + datetime.timedelta(hours=9)
            now_date = now.strftime('%Y/%m/%d %H:%M:%S')
            c.execute(
                "UPDATE mathgame SET count = ?, countdate = ? WHERE id = ?",
                (count, now_date, user.id))
            conn.commit()

        c.close()


def mathDataReadScore(user: discord.Member = None):
    conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
    c = conn.cursor()
    sql = "SELECT id, score, scoredate FROM mathgame WHERE id = ?"
    c.execute(sql, (user.id, ))
    result = c.fetchone()
    return result


def mathDataReadCount(user: discord.Member = None):
    conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
    c = conn.cursor()
    sql = "SELECT id, count, countdate FROM mathgame WHERE id = ?"
    c.execute(sql, (user.id, ))
    result = c.fetchone()
    return result


def mathDataRanking(opt: str = ""):
    conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
    c = conn.cursor()
    if opt == "score":
        sql = "SELECT id, score, scoredate, RANK() OVER (ORDER BY score DESC) AS ranking FROM mathgame;"
        c.execute(sql)
        result = c.fetchall()
    elif opt == "count":
        sql = "SELECT id, count, countdate, RANK() OVER (ORDER BY count DESC) AS ranking FROM mathgame;"
        c.execute(sql)
        result = c.fetchall()
    return result


def mathDataUserRanking(user: discord.Member = None, opt: str = ""):
    conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
    c = conn.cursor()
    if opt == "score":
        sql = "SELECT score, scoredate, ranking FROM (SELECT id, score, scoredate, RANK() OVER (ORDER BY score DESC) AS ranking FROM mathgame) WHERE id = ?;"
        c.execute(sql, (user.id, ))
        result = c.fetchone()
        print(result)
    elif opt == "count":
        sql = "SELECT count, countdate, ranking FROM (SELECT id, count, countdate, RANK() OVER (ORDER BY count DESC) AS ranking FROM mathgame) WHERE id = ?;"
        c.execute(sql, (user.id, ))
        result = c.fetchone()
    return result


def mathDataForcedUpdate(user: int = None,
                         score: int = 0,
                         scoredate: str = "",
                         count: int = 0,
                         countdate: str = ""):
    conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
    c = conn.cursor()
    try:
        INSERT_SQL = 'INSERT INTO mathgame (id, score, scoredate, count, countdate) VALUES (?,?,?,?,?);'
        data = ((user, score, scoredate, count, countdate))
        c.execute(INSERT_SQL, data)

    except:
        c.execute(
            "UPDATE mathgame SET score = ?, scoredate = ?, count = ?, countdate = ? WHERE id = ?",
            (score, scoredate, count, countdate, user))
    conn.commit()
    conn.close()


#RPS
def rpsDataUpdate(user: discord.Member = None,
                  score: int = 0,
                  count: int = 0,
                  maxchain: int = 0,
                  win: int = 0,
                  tie: int = 0):
    conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
    c = conn.cursor()

    try:
        INSERT_SQL = 'INSERT INTO rps (id, score, scoredate, count, countdate, maxchain, maxchaindate, win, windate, tie, tiedate) VALUES (?,?,?,?,?,?,?,?,?,?,?);'
        now = datetime.datetime.now() + datetime.timedelta(hours=9)
        now_date = now.strftime('%Y/%m/%d %H:%M:%S')

        data = ((user.id, score, now_date, count, now_date, maxchain, now_date,
                 win, now_date, tie, now_date))
        c.execute(INSERT_SQL, data)
        conn.commit()

    except:
        sql = "SELECT * FROM rps WHERE id = ?"
        c.execute(sql, (user.id, ))
        result = c.fetchone()
        print(result)

        if score > result[1]:
            now = datetime.datetime.now() + datetime.timedelta(hours=9)
            now_date = now.strftime('%Y/%m/%d %H:%M:%S')
            c.execute("UPDATE rps SET score = ?, scoredate = ? WHERE id = ?",
                      (score, now_date, user.id))
            conn.commit()

        if count > result[3]:
            now = datetime.datetime.now() + datetime.timedelta(hours=9)
            now_date = now.strftime('%Y/%m/%d %H:%M:%S')
            c.execute("UPDATE rps SET count = ?, countdate = ? WHERE id = ?",
                      (count, now_date, user.id))
            conn.commit()

        if maxchain > result[5]:
            now = datetime.datetime.now() + datetime.timedelta(hours=9)
            now_date = now.strftime('%Y/%m/%d %H:%M:%S')
            c.execute(
                "UPDATE rps SET maxchain = ?, maxchaindate = ? WHERE id = ?",
                (maxchain, now_date, user.id))
            conn.commit()

        if win > result[7]:
            now = datetime.datetime.now() + datetime.timedelta(hours=9)
            now_date = now.strftime('%Y/%m/%d %H:%M:%S')
            c.execute("UPDATE rps SET win = ?, windate = ? WHERE id = ?",
                      (win, now_date, user.id))
            conn.commit()

        if tie > result[9]:
            now = datetime.datetime.now() + datetime.timedelta(hours=9)
            now_date = now.strftime('%Y/%m/%d %H:%M:%S')
            c.execute("UPDATE rps SET tie = ?, tiedate = ? WHERE id = ?",
                      (tie, now_date, user.id))
            conn.commit()
        c.close()


def rpsDataReadScore(user: discord.Member = None):
    conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
    c = conn.cursor()
    sql = "SELECT id, score, scoredate FROM rps WHERE id = ?"
    c.execute(sql, (user.id, ))
    result = c.fetchone()
    return result


def rpsDataReadCount(user: discord.Member = None):
    conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
    c = conn.cursor()
    sql = "SELECT id, count, countdate FROM rps WHERE id = ?"
    c.execute(sql, (user.id, ))
    result = c.fetchone()
    return result


def rpsDataReadWin(user: discord.Member = None):
    conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
    c = conn.cursor()
    sql = "SELECT id, win, windate FROM rps WHERE id = ?"
    c.execute(sql, (user.id, ))
    result = c.fetchone()
    return result


def rpsDataReadTie(user: discord.Member = None):
    conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
    c = conn.cursor()
    sql = "SELECT id, tie, tiedate FROM rps WHERE id = ?"
    c.execute(sql, (user.id, ))
    result = c.fetchone()
    return result


def rpsDataRanking(opt: str = ""):
    conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
    c = conn.cursor()
    if opt == "score":
        sql = "SELECT id, score, scoredate, RANK() OVER (ORDER BY score DESC) AS ranking FROM rps;"
        c.execute(sql)
        result = c.fetchall()
    elif opt == "count":
        sql = "SELECT id, count, countdate, RANK() OVER (ORDER BY count DESC) AS ranking FROM rps;"
        c.execute(sql)
        result = c.fetchall()
    elif opt == "maxchain":
        sql = "SELECT id, maxchain, maxchaindate, RANK() OVER (ORDER BY maxchain DESC) AS ranking FROM rps;"
        c.execute(sql)
        result = c.fetchall()
    elif opt == "win":
        sql = "SELECT id, win, windate, RANK() OVER (ORDER BY win DESC) AS ranking FROM rps;"
        c.execute(sql)
        result = c.fetchall()
    elif opt == "tie":
        sql = "SELECT id, tie, tiedate, RANK() OVER (ORDER BY tie DESC) AS ranking FROM rps;"
        c.execute(sql)
        result = c.fetchall()
    return result


def rpsDataUserRanking(user: discord.Member = None, opt: str = ""):
    conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
    c = conn.cursor()
    if opt == "score":
        sql = "SELECT score, scoredate, ranking FROM (SELECT id, score, scoredate, RANK() OVER (ORDER BY score DESC) AS ranking FROM rps) WHERE id = ?;"
        c.execute(sql, (user.id, ))
        result = c.fetchone()
    elif opt == "count":
        sql = "SELECT count, countdate, ranking FROM (SELECT id, count, countdate, RANK() OVER (ORDER BY count DESC) AS ranking FROM rps) WHERE id = ?;"
        c.execute(sql, (user.id, ))
        result = c.fetchone()
    elif opt == "maxchain":
        sql = "SELECT maxchain, maxchaindate, ranking FROM (SELECT id, maxchain, maxchaindate, RANK() OVER (ORDER BY maxchain DESC) AS ranking FROM rps) WHERE id = ?;"
        c.execute(sql, (user.id, ))
        result = c.fetchone()
    elif opt == "win":
        sql = "SELECT win, windate, ranking FROM (SELECT id, win, windate, RANK() OVER (ORDER BY win DESC) AS ranking FROM rps) WHERE id = ?;"
        c.execute(sql, (user.id, ))
        result = c.fetchone()
    elif opt == "tie":
        sql = "SELECT tie, tiedate, ranking FROM (SELECT id, tie, tiedate, RANK() OVER (ORDER BY tie DESC) AS ranking FROM rps) WHERE id = ?;"
        c.execute(sql, (user.id, ))
        result = c.fetchone()
    return result


def rpsDataForcedUpdate(user: int = None,
                        score: int = 0,
                        scoredate: str = "",
                        count: int = 0,
                        countdate: str = "",
                        maxchain: int = 0,
                        maxchaindate: str = "",
                        win: int = 0,
                        windate: str = "",
                        tie: int = 0,
                        tiedate: str = ""):
    conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
    c = conn.cursor()
    try:
        INSERT_SQL = 'INSERT INTO rps (id, score, scoredate, count, countdate, maxchain, maxchaindate, win, windate, tie, tiedate) VALUES (?,?,?,?,?,?,?,?,?,?,?);'
        data = ((user, score, scoredate, count, countdate, maxchain,
                 maxchaindate, win, windate, tie, tiedate))
        c.execute(INSERT_SQL, data)

    except:
        c.execute(
            "UPDATE rps SET score = ?, scoredate = ?, count = ?, countdate = ?, maxchain = ?, maxchaindate = ?, win = ?, windate = ?, tie = ?, tiedate = ? WHERE id = ?",
            (score, scoredate, count, countdate, maxchain, maxchaindate, win,
             windate, tie, tiedate, user))
    conn.commit()
    conn.close()


#Word Chain
def wcUpdateRegist(user: discord.Member = None):
    conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
    c = conn.cursor()

    try:
        INSERT_SQL = 'INSERT INTO wordchain (id, regist, indi_score, indi_count, indi_play, indi_win, bot_score, bot_count, mara_half, mara_full) VALUES (?,?,?,?,?,?,?,?,?,?);'

        data = ((user.id, 1, 0, 0, 0, 0, 0, 0, 0, 0))
        c.execute(INSERT_SQL, data)
        conn.commit()

    except:

        c.execute("UPDATE wordchain SET regist = regist + 1 WHERE id = ?",
                  (user.id, ))
        conn.commit()
    c.close()


def wcUpdateRegistById(user: int = None):
    conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
    c = conn.cursor()

    try:
        INSERT_SQL = 'INSERT INTO wordchain (id, regist, indi_score, indi_count, indi_play, indi_win, bot_score, bot_count, mara_half, mara_full) VALUES (?,?,?,?,?,?,?,?,?,?);'

        data = ((user, 1, 0, 0, 0, 0, 0, 0, 0, 0))
        c.execute(INSERT_SQL, data)
        conn.commit()

    except:

        c.execute("UPDATE wordchain SET regist = regist + 1 WHERE id = ?",
                  (user, ))
        conn.commit()
    c.close()


def wcUpdateIndi(user: int = None,
                 score: int = 0,
                 count: int = 0,
                 winner: bool = False):
    conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
    c = conn.cursor()

    try:
        INSERT_SQL = 'INSERT INTO wordchain (id, regist, indi_score, indi_count, indi_play, indi_win, bot_score, bot_count, mara_half, mara_full) VALUES (?,?,?,?,?,?,?,?,?,?);'
        if winner:
            data = ((user, 0, score, count, 1, 1, 0, 0, 0, 0))
            c.execute(INSERT_SQL, data)
            conn.commit()
        else:
            data = ((user, 0, score, count, 1, 0, 0, 0, 0, 0))
            c.execute(INSERT_SQL, data)
            conn.commit()

    except:
        sql = "SELECT indi_score, indi_count FROM wordchain WHERE id = ?"
        c.execute(sql, (user, ))
        result = c.fetchone()

        if score > result[0]:
            c.execute("UPDATE wordchain SET indi_score = ? WHERE id = ?",
                      (score, user))
            conn.commit()

        if count > result[1]:
            c.execute("UPDATE wordchain SET indi_count = ? WHERE id = ?",
                      (count, user))
            conn.commit()

        if winner:
            c.execute(
                "UPDATE wordchain SET indi_win = indi_win + 1 WHERE id = ?",
                (user, ))
            conn.commit()

        c.execute(
            "UPDATE wordchain SET indi_play = indi_play + 1 WHERE id = ?",
            (user, ))
        conn.commit()
    c.close()


def wcUpdateBot(user: discord.Member = None, score: int = 0, count: int = 0):
    conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
    c = conn.cursor()

    try:
        INSERT_SQL = 'INSERT INTO wordchain (id, regist, indi_score, indi_count, indi_play, indi_win, bot_score, bot_count, mara_half, mara_full) VALUES (?,?,?,?,?,?,?,?,?,?);'
        data = ((user.id, 0, 0, 0, 0, 0, score, count, 0, 0))
        c.execute(INSERT_SQL, data)
        conn.commit()

    except:
        sql = "SELECT bot_score, bot_count FROM wordchain WHERE id = ?"
        c.execute(sql, (user.id, ))
        result = c.fetchone()

        if score > result[0]:
            c.execute("UPDATE wordchain SET bot_score = ? WHERE id = ?",
                      (score, user.id))
            conn.commit()

        if count > result[1]:
            c.execute("UPDATE wordchain SET bot_count = ? WHERE id = ?",
                      (count, user.id))
            conn.commit()

    c.close()


def wcUpdateMara(user: discord.Member = None, opt: str = '', record: int = 0):
    conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
    c = conn.cursor()

    try:
        if opt == 'half':
            INSERT_SQL = 'INSERT INTO wordchain (id, regist, indi_score, indi_count, indi_play, indi_win, bot_score, bot_count, mara_half, mara_full) VALUES (?,?,?,?,?,?,?,?,?,?);'
            data = ((user.id, 0, 0, 0, 0, 0, 0, 0, record, 0))
            c.execute(INSERT_SQL, data)
            conn.commit()
        elif opt == 'full':
            INSERT_SQL = 'INSERT INTO wordchain (id, regist, indi_score, indi_count, indi_play, indi_win, bot_score, bot_count, mara_half, mara_full) VALUES (?,?,?,?,?,?,?,?,?,?);'
            data = ((user.id, 0, 0, 0, 0, 0, 0, 0, 0, record))
            c.execute(INSERT_SQL, data)
            conn.commit()

    except:
        sql = "SELECT mara_half, mara_full FROM wordchain WHERE id = ?"
        c.execute(sql, (user.id, ))
        result = c.fetchone()

        if opt == 'half' and record > result[0]:
            c.execute("UPDATE wordchain SET mara_half = ? WHERE id = ?",
                      (record, user.id))
            conn.commit()

        elif opt == 'full' and record > result[1]:
            c.execute("UPDATE wordchain SET mara_full = ? WHERE id = ?",
                      (record, user.id))
            conn.commit()

    c.close()


def wcRanking(opt: str = "", sub: str = ""):
    conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
    c = conn.cursor()
    if opt == "regist":
        sql = "SELECT id, regist, RANK() OVER (ORDER BY regist DESC) AS ranking FROM wordchain;"
        c.execute(sql)
        result = c.fetchall()
    elif opt == "indi":
        if sub == "score":
            sql = "SELECT id, indi_score, RANK() OVER (ORDER BY indi_score DESC) AS ranking FROM wordchain;"
            c.execute(sql)
            result = c.fetchall()
        elif sub == "count":
            sql = "SELECT id, indi_count, RANK() OVER (ORDER BY indi_count DESC) AS ranking FROM wordchain;"
            c.execute(sql)
            result = c.fetchall()
        elif sub == "play":
            sql = "SELECT id, indi_play, RANK() OVER (ORDER BY indi_play DESC) AS ranking FROM wordchain;"
            c.execute(sql)
            result = c.fetchall()
        elif sub == "win":
            sql = "SELECT id, indi_win, indi_play, RANK() OVER (ORDER BY indi_win DESC) AS ranking FROM wordchain;"
            c.execute(sql)
            result = c.fetchall()
    elif opt == "bot":
        if sub == "score":
            sql = "SELECT id, bot_score, RANK() OVER (ORDER BY bot_score DESC) AS ranking FROM wordchain;"
            c.execute(sql)
            result = c.fetchall()
        elif sub == "count":
            sql = "SELECT id, bot_count, RANK() OVER (ORDER BY bot_count DESC) AS ranking FROM wordchain;"
            c.execute(sql)
            result = c.fetchall()
    elif opt == "mara":
        if sub == "half":
            sql = "SELECT id, mara_half, RANK() OVER (ORDER BY mara_half DESC) AS ranking FROM wordchain;"
            c.execute(sql)
            result = c.fetchall()
        elif sub == "full":
            sql = "SELECT id, mara_full, RANK() OVER (ORDER BY mara_full DESC) AS ranking FROM wordchain;"
            c.execute(sql)
            result = c.fetchall()

    return result


def wcUserRanking(user: discord.Member = None, opt: str = "", sub: str = ""):
    conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
    c = conn.cursor()
    if opt == "regist":
        sql = "SELECT regist, ranking FROM (SELECT id, regist, RANK() OVER (ORDER BY regist DESC) AS ranking FROM wordchain) WHERE id = ?;"
        c.execute(sql, (user.id, ))
        result = c.fetchone()
    elif opt == "indi":
        if sub == "score":
            sql = "SELECT indi_score, ranking FROM (SELECT id, indi_score, RANK() OVER (ORDER BY indi_score DESC) AS ranking FROM wordchain) WHERE id = ?;"
            c.execute(sql, (user.id, ))
            result = c.fetchone()
        elif sub == "count":
            sql = "SELECT indi_count, ranking FROM (SELECT id, indi_count, RANK() OVER (ORDER BY indi_count DESC) AS ranking FROM wordchain) WHERE id = ?;"
            c.execute(sql, (user.id, ))
            result = c.fetchone()
        elif sub == "win":
            sql = "SELECT indi_win, indi_play, ranking FROM (SELECT id, indi_win, indi_play, RANK() OVER (ORDER BY indi_win DESC) AS ranking FROM wordchain) WHERE id = ?;"
            c.execute(sql, (user.id, ))
            result = c.fetchone()
    elif opt == "bot":
        if sub == "score":
            sql = "SELECT bot_score, ranking FROM (SELECT id, bot_score, RANK() OVER (ORDER BY bot_score DESC) AS ranking FROM wordchain) WHERE id = ?;"
            c.execute(sql, (user.id, ))
            result = c.fetchone()
        elif sub == "count":
            sql = "SELECT bot_count, ranking FROM (SELECT id, bot_count, RANK() OVER (ORDER BY bot_count DESC) AS ranking FROM wordchain) WHERE id = ?;"
            c.execute(sql, (user.id, ))
            result = c.fetchone()
    elif opt == "mara":
        if sub == "half":
            sql = "SELECT mara_half, ranking FROM (SELECT id, mara_half, RANK() OVER (ORDER BY mara_half DESC) AS ranking FROM wordchain) WHERE id = ?;"
            c.execute(sql, (user.id, ))
            result = c.fetchone()
        elif sub == "full":
            sql = "SELECT mara_full, ranking FROM (SELECT id, mara_full, RANK() OVER (ORDER BY mara_full DESC) AS ranking FROM wordchain) WHERE id = ?;"
            c.execute(sql, (user.id, ))
            result = c.fetchone()

    return result


def wcForcedUpdate(
    user: int = None,
    reg: int = 0,
    iscore: int = 0,
    icount: int = 0,
    iplay: int = 0,
    iwin: int = 0,
    bscore: int = 0,
    bcount: int = 0,
    mh: int = 0,
    mf: int = 0,
):
    conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
    c = conn.cursor()
    try:
        INSERT_SQL = 'INSERT INTO wordchain (id, regist, indi_score, indi_count, indi_play, indi_win, bot_score, bot_count, mara_half, mara_full) VALUES (?,?,?,?,?,?,?,?,?,?);'
        data = ((user, reg, iscore, icount, iplay, iwin, bscore, bcount, mh,
                 mf))
        c.execute(INSERT_SQL, data)

    except:
        c.execute(
            "UPDATE wordchain SET regist = ?, indi_score = ?, indi_count = ?, indi_play = ?, indi_win = ?, bot_score = ?, bot_count = ?, mara_half = ?, mara_full = ? WHERE id = ?",
            (reg, iscore, icount, iplay, iwin, bscore, bcount, mh, mf, user))
    conn.commit()
    conn.close()


def wcRead(user: discord.Member = None, opt: str = ""):
    conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
    c = conn.cursor()
    if opt == "regist":
        sql = "SELECT regist FROM wordchain WHERE id = ?;"
        c.execute(sql, (user.id, ))
        result = c.fetchone()[0]

    elif opt == "win":
        sql = "SELECT indi_win FROM wordchain WHERE id = ?;"
        c.execute(sql, (user.id, ))
        result = c.fetchone()[0]

    return result


def wcReadById(user: int = None, opt: str = ""):
    conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
    c = conn.cursor()
    if opt == "regist":
        sql = "SELECT regist FROM wordchain WHERE id = ?;"
        c.execute(sql, (user, ))
        result = c.fetchone()[0]

    elif opt == "win":
        sql = "SELECT indi_win FROM wordchain WHERE id = ?;"
        c.execute(sql, (user, ))
        result = c.fetchone()[0]

    return result


#Yahtzee
def ytUpdate(user: int = None, score: int = 0, winner: bool = False):
    conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
    c = conn.cursor()

    try:
        INSERT_SQL = 'INSERT INTO yahtzee (id, score, scoredate, play, win) VALUES (?,?,?,?,?);'
        now = datetime.datetime.now() + datetime.timedelta(hours=9)
        now_date = now.strftime('%Y/%m/%d %H:%M:%S')

        if winner:
            data = ((user, score, now_date, 1, 1))
        else:
            data = ((user, score, now_date, 1, 0))

        c.execute(INSERT_SQL, data)
        conn.commit()

    except:
        sql = "SELECT * FROM yahtzee WHERE id = ?"
        c.execute(sql, (user, ))
        result = c.fetchone()

        if score > result[1]:
            now = datetime.datetime.now() + datetime.timedelta(hours=9)
            now_date = now.strftime('%Y/%m/%d %H:%M:%S')
            c.execute(
                "UPDATE yahtzee SET score = ?, scoredate = ? WHERE id = ?",
                (score, now_date, user))
            conn.commit()

        c.execute("UPDATE yahtzee SET play = play + 1 WHERE id = ?", (user, ))
        conn.commit()

        if winner:
            c.execute("UPDATE yahtzee SET win = win + 1 WHERE id = ?",
                      (user, ))
            conn.commit()

        c.close()


def ytReadScore(user: discord.Member = None):
    conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
    c = conn.cursor()
    sql = "SELECT id, score, scoredate FROM yahtzee WHERE id = ?"
    c.execute(sql, (user.id, ))
    result = c.fetchone()
    return result


def ytReadPW(user: discord.Member = None):
    conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
    c = conn.cursor()
    sql = "SELECT id, play, win FROM yahtzee WHERE id = ?"
    c.execute(sql, (user.id, ))
    result = c.fetchone()
    return result


def ytRanking(opt: str = ""):
    conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
    c = conn.cursor()
    if opt == "score":
        sql = "SELECT id, score, scoredate, RANK() OVER (ORDER BY score DESC) AS ranking FROM yahtzee;"
        c.execute(sql)
        result = c.fetchall()
    elif opt == "play":
        sql = "SELECT id, play, RANK() OVER (ORDER BY play DESC) AS ranking FROM yahtzee;"
        c.execute(sql)
        result = c.fetchall()
    elif opt == "win":
        sql = "SELECT id, win, RANK() OVER (ORDER BY win DESC) AS ranking FROM yahtzee;"
        c.execute(sql)
        result = c.fetchall()
    return result


def ytUserRanking(user: discord.Member = None, opt: str = ""):
    conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
    c = conn.cursor()
    if opt == "score":
        sql = "SELECT score, scoredate, ranking FROM (SELECT id, score, scoredate, RANK() OVER (ORDER BY score DESC) AS ranking FROM yahtzee) WHERE id = ?;"
        c.execute(sql, (user.id, ))
        result = c.fetchone()

    elif opt == "play":
        sql = "SELECT play, ranking FROM (SELECT id, play, RANK() OVER (ORDER BY play DESC) AS ranking FROM yahtzee) WHERE id = ?;"
        c.execute(sql, (user.id, ))
        result = c.fetchone()

    elif opt == "win":
        sql = "SELECT win, ranking FROM (SELECT id, win, RANK() OVER (ORDER BY win DESC) AS ranking FROM yahtzee) WHERE id = ?;"
        c.execute(sql, (user.id, ))
        result = c.fetchone()

    return result


def ytForcedUpdate(user: int = None,
                   score: int = 0,
                   scoredate: str = "",
                   play: int = 0,
                   win: int = 0):
    conn = sqlite3.connect(root_dir + '/data/leaderboard.db')
    c = conn.cursor()
    try:
        INSERT_SQL = 'INSERT INTO yahtzee (id, score, scoredate, play, win) VALUES (?,?,?,?,?);'
        data = ((user, score, scoredate, play, win))
        c.execute(INSERT_SQL, data)

    except:
        c.execute(
            "UPDATE yahtzee SET score = ?, scoredate = ?, play = ?, win = ? WHERE id = ?",
            (score, scoredate, play, win, user))
    conn.commit()
    conn.close()
