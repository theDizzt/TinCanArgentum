# 0. Import modules
import discord
from discord.ext import commands
import sqlite3
import datetime
from config.rootdir import root_dir

# 1. Connect DB
conn = sqlite3.connect(root_dir + '/data/levelkiller.db')
c = conn.cursor()

# 2. Sub Functions


# 2.1. Init Setting
def initSetting():
    conn = sqlite3.connect(root_dir + '/data/levelkiller.db')
    c = conn.cursor()

    sql = """CREATE TABLE IF NOT EXISTS achievements(
    id INTEGER PRIMARY KEY);"""

    c.execute(sql)
    conn.commit()

    #max 256 achievements
    for i in range(1, 257):
        try:
            sql = "ALTER TABLE achievements ADD COLUMN {} [TINYINT] DEFAULT 0;".format(
                "id" + str(i))
            c.execute(sql)
            conn.commit()
        except:
            pass

    sql = """CREATE TABLE IF NOT EXISTS achievetime(
    id INTEGER PRIMARY KEY);"""

    c.execute(sql)
    conn.commit()

    #max 256 achievements
    for i in range(1, 257):
        try:
            sql = "ALTER TABLE achievetime ADD COLUMN {} [TEXT] DEFAULT '-';".format(
                "id" + str(i))
            c.execute(sql)
            conn.commit()
        except:
            pass

    sql = """CREATE TABLE IF NOT EXISTS userdata(
    id INTEGER PRIMARY KEY,
    createdate TEXT);"""

    c.execute(sql)
    conn.commit()

    conn.close()


# 3. Actions


# 3.5.1 Add data
def newAchieve(user: discord.Member = None):
    conn = sqlite3.connect(root_dir + '/data/levelkiller.db')
    c = conn.cursor()
    now = datetime.datetime.now() + datetime.timedelta(hours=9)
    now_time = now.strftime('%Y/%m/%d %H:%M:%S')
    c.execute('INSERT INTO achievements (id) VALUES (?);', (user.id, ))
    conn.commit()
    c.execute('INSERT INTO achievetime (id) VALUES (?);', (user.id, ))
    conn.commit()
    c.execute('INSERT INTO userdata (id, createdate) VALUES (?, ?);',
              (user.id, now_time))
    conn.commit()
    print(f"{user.id} created at {now_time}")

    conn.close()


def newAchieveById(user: int = None):
    conn = sqlite3.connect(root_dir + '/data/levelkiller.db')
    c = conn.cursor()
    now = datetime.datetime.now() + datetime.timedelta(hours=9)
    now_time = now.strftime('%Y/%m/%d %H:%M:%S')
    c.execute('INSERT INTO achievements (id) VALUES (?);', (user, ))
    conn.commit()
    c.execute('INSERT INTO achievetime (id) VALUES (?);', (user, ))
    conn.commit()
    c.execute('INSERT INTO userdata (id, createdate) VALUES (?, ?);',
              (user, now_time))
    conn.commit()
    print(f"{user} created at {now_time}")

    conn.close()

def dateModifyById(user: int = None, date:str = "2020/12/19 21:24:39"):
    conn = sqlite3.connect(root_dir + '/data/levelkiller.db')
    c = conn.cursor()
    c.execute("UPDATE userdata SET createdate = ? WHERE id = ?",(date, user))
    conn.commit()

    conn.close()


# 3.5.2. Data Write
def achieveModify(user: discord.Member = None,
                  id: int = None,
                  value: int = None):
    conn = sqlite3.connect(root_dir + '/data/levelkiller.db')
    c = conn.cursor()

    if value == 0:
        c.execute(
            "UPDATE achievements SET {} = ? WHERE id = ?".format("id" +
                                                                 str(id)),
            (value, user.id))
        conn.commit()

        c.execute(
            "UPDATE achievetime SET {} = ? WHERE id = ?".format("id" +
                                                                str(id)),
            ('-', user.id))
        conn.commit()

    elif value == 1:
        now = datetime.datetime.now() + datetime.timedelta(hours=9)
        now_time = now.strftime('%Y/%m/%d %H:%M:%S')

        c.execute(
            "UPDATE achievements SET {} = ? WHERE id = ?".format("id" +
                                                                 str(id)),
            (value, user.id))
        conn.commit()

        c.execute(
            "UPDATE achievetime SET {} = ? WHERE id = ?".format("id" +
                                                                str(id)),
            (now_time, user.id))
        conn.commit()

    c.close()


def achieveModifyById(user: int = None, id: int = None, value: int = None):
    conn = sqlite3.connect(root_dir + '/data/levelkiller.db')
    c = conn.cursor()
    if value == 0:
        c.execute(
            "UPDATE achievements SET {} = ? WHERE id = ?".format("id" +
                                                                 str(id)),
            (value, user))
        conn.commit()

        c.execute(
            "UPDATE achievetime SET {} = ? WHERE id = ?".format("id" +
                                                                str(id)),
            ('-', user))
        conn.commit()

    elif value == 1:
        now = datetime.datetime.now() + datetime.timedelta(hours=9)
        now_time = now.strftime('%Y/%m/%d %H:%M:%S')

        c.execute(
            "UPDATE achievements SET {} = ? WHERE id = ?".format("id" +
                                                                 str(id)),
            (value, user))
        conn.commit()

        c.execute(
            "UPDATE achievetime SET {} = ? WHERE id = ?".format("id" +
                                                                str(id)),
            (now_time, user))
        conn.commit()

    c.close()


# 3.5.3. Read Storage
def readAchieve(user: discord.Member = None, id: str = None):
    conn = sqlite3.connect(root_dir + '/data/levelkiller.db')
    c = conn.cursor()
    sql = "SELECT {} FROM achievements WHERE id = ?;".format("id" + str(id))
    c.execute(sql, (user.id, ))
    result = c.fetchone()[0]
    return result


def readAchieveById(user: int = None, id: str = None):
    conn = sqlite3.connect(root_dir + '/data/levelkiller.db')
    c = conn.cursor()
    sql = "SELECT {} FROM achievements WHERE id = ?;".format("id" + str(id))
    c.execute(sql, (user, ))
    result = c.fetchone()[0]
    return result


def readAchieveTime(user: discord.Member = None, id: str = None):
    conn = sqlite3.connect(root_dir + '/data/levelkiller.db')
    c = conn.cursor()
    sql = "SELECT {} FROM achievetime WHERE id = ?;".format("id" + str(id))
    c.execute(sql, (user.id, ))
    result = c.fetchone()[0]
    return result


def readJoinTime(user: discord.Member = None):
    conn = sqlite3.connect(root_dir + '/data/levelkiller.db')
    c = conn.cursor()
    sql = "SELECT createdate FROM userdata WHERE id = ?;"
    c.execute(sql, (user.id, ))
    result = c.fetchone()[0]
    return result


# 3.5.4. User Storage List
def achieveList(user: discord.Member = None):
    conn = sqlite3.connect(root_dir + '/data/levelkiller.db')
    c = conn.cursor()
    sql = "SELECT * FROM achievements WHERE id = ?;"
    c.execute(sql, (user.id, ))
    result = c.fetchone()
    return result
