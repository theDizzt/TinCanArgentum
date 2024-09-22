# 0. Import modules
import discord
from discord.ext import commands
import sqlite3
import datetime
from config.rootdir import root_dir

# 1. Connect DB
conn = sqlite3.connect(root_dir + '/data/pokedex.db')
c = conn.cursor()


# 2.1. Init Setting
def initSetting():
    conn = sqlite3.connect(root_dir + '/data/pokedex.db')
    c = conn.cursor()

    sql = """CREATE TABLE IF NOT EXISTS dex(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    korean TEXT NOT NULL,
    english TEXT NOT NULL,
    dexnum INTEGER NOT NULL,
    natnum TEXT NOT NULL,
    type1 TEXT NOT NULL,
    type2 TEXT NOT NULL,
    ability1 TEXT NOT NULL,
    ability2 TEXT NOT NULL,
    ability3 TEXT NOT NULL,
    moves TEXT NOT NULL,
    evolution TEXT NOT NULL,
    habitat TEXT NOT NULL,
    hp INTEGER NOT NULL,
    pa INTEGER NOT NULL,
    pd INTEGER NOT NULL,
    sa INTEGER NOT NULL,
    sd INTEGER NOT NULL,
    sp INTEGER NOT NULL
    );"""

    c.execute(sql)
    conn.commit()

    sql = """CREATE TABLE IF NOT EXISTS tm(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    korean TEXT NOT NULL,
    type TEXT NOT NULL,
    category TEXT NOT NULL,
    power TEXT NOT NULL,
    accuracy TEXT NOT NULL,
    pp TEXT NOT NULL,
    desc TEXT NOT NULL
    );"""

    c.execute(sql)
    conn.commit()

    conn.close()


# 3.1. Add data
def newDexData(data):
    conn = sqlite3.connect(root_dir + '/data/pokedex.db')
    c = conn.cursor()

    INSERT_SQL = '''
    INSERT INTO dex (dexnum, natnum, korean, english, type1, type2, ability1, ability2, ability3, moves, evolution, habitat, hp, pa, pd, sa, sd, sp) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);
    '''

    try:
        c.execute(INSERT_SQL, data)
        print("단어 등록 완료")
    except:
        print("이미 존재하는 단어입니다.")

    conn.commit()
    conn.close()

def newTmData(data):
    conn = sqlite3.connect(root_dir + '/data/pokedex.db')
    c = conn.cursor()

    INSERT_SQL = '''
    INSERT INTO tm (korean, type, category, power, accuracy, pp, desc) VALUES (?,?,?,?,?,?,?);
    '''

    try:
        c.execute(INSERT_SQL, data)
        print("단어 등록 완료")
    except:
        print("이미 존재하는 단어입니다.")

    conn.commit()
    conn.close()

# Read Dex Data:
def readDexList():
    conn = sqlite3.connect(root_dir + '/data/pokedex.db')
    c = conn.cursor()
    c.execute("SELECT korean, dexnum, type1, type2 FROM dex;")
    result = c.fetchall()
    return result

def readDexListName(name: str = ""):
    search = "%" + name + "%"
    conn = sqlite3.connect(root_dir + '/data/pokedex.db')
    c = conn.cursor()
    sql = "SELECT korean, dexnum, type1, type2 FROM dex Where korean LIKE ?"
    c.execute(sql, (search,))
    result = c.fetchall()
    return result

def readDexListDex(search: int = ""):
    conn = sqlite3.connect(root_dir + '/data/pokedex.db')
    c = conn.cursor()
    sql = "SELECT korean, dexnum, type1, type2 FROM dex Where dexnum = ?"
    c.execute(sql, (search, ))
    result = c.fetchall()
    return result

def readDexListNat(search: str = ""):
    conn = sqlite3.connect(root_dir + '/data/pokedex.db')
    c = conn.cursor()
    sql = "SELECT korean, dexnum, type1, type2 FROM dex Where natnum = ?"
    c.execute(sql, (search, ))
    result = c.fetchall()
    return result

def readDexListType(search: str = ""):
    if search.find(",") == -1:
        conn = sqlite3.connect(root_dir + '/data/pokedex.db')
        c = conn.cursor()
        sql = "SELECT korean, dexnum, type1, type2 FROM dex Where type1 = ? OR type2 = ?"
        c.execute(sql, (search, search, ))
        result = c.fetchall()
        return result
    else:
        temp = search.split(',')
        conn = sqlite3.connect(root_dir + '/data/pokedex.db')
        c = conn.cursor()
        sql = "SELECT korean, dexnum, type1, type2 FROM dex Where (type1 = ? AND type2 = ?) OR (type1 = ? AND type2 = ?)"
        c.execute(sql, (temp[0], temp[1], temp[1], temp[0], ))
        result = c.fetchall()
        return result
    
def readDexListAbility(search: str = ""):
    conn = sqlite3.connect(root_dir + '/data/pokedex.db')
    c = conn.cursor()
    sql = "SELECT korean, dexnum, type1, type2 FROM dex Where ability1 = ? OR ability2 = ? OR ability3 = ?"
    c.execute(sql, (search, search, search, ))
    result = c.fetchall()
    return result

def readDexName(name: str = ""):
    search = "%" + name + "%"
    conn = sqlite3.connect(root_dir + '/data/pokedex.db')
    c = conn.cursor()
    sql = "SELECT * FROM dex Where korean LIKE ?"
    c.execute(sql, (search,))
    result = c.fetchall()
    return result

def readDexDex(search: int = ""):
    conn = sqlite3.connect(root_dir + '/data/pokedex.db')
    c = conn.cursor()
    sql = "SELECT * FROM dex Where dexnum = ?"
    c.execute(sql, (search, ))
    result = c.fetchall()
    return result

def readDexNat(search: str = ""):
    conn = sqlite3.connect(root_dir + '/data/pokedex.db')
    c = conn.cursor()
    sql = "SELECT * FROM dex Where natnum = ?"
    c.execute(sql, (search, ))
    result = c.fetchall()
    return result

def readDexType(search: str = ""):
    if search.find(",") == -1:
        conn = sqlite3.connect(root_dir + '/data/pokedex.db')
        c = conn.cursor()
        sql = "SELECT * FROM dex Where type1 = ? OR type2 = ?"
        c.execute(sql, (search, search, ))
        result = c.fetchall()
        return result
    else:
        temp = search.split(',')
        conn = sqlite3.connect(root_dir + '/data/pokedex.db')
        c = conn.cursor()
        sql = "SELECT * FROM dex Where (type1 = ? AND type2 = ?) OR (type1 = ? AND type2 = ?)"
        c.execute(sql, (temp[0], temp[1], temp[1], temp[0], ))
        result = c.fetchall()
        return result
    
def readDexAbility(search: str = ""):
    conn = sqlite3.connect(root_dir + '/data/pokedex.db')
    c = conn.cursor()
    sql = "SELECT * FROM dex Where ability1 = ? OR ability2 = ? OR ability3 = ?"
    c.execute(sql, (search, search, search, ))
    result = c.fetchall()
    return result

# Read TM Data:
def readTmList():
    conn = sqlite3.connect(root_dir + '/data/pokedex.db')
    c = conn.cursor()
    c.execute("SELECT id, korean, type, category, power, accuracy, pp, desc FROM tm;")
    result = c.fetchall()
    return result

def readTmName(name: str = ""):
    search = "%" + name + "%"
    conn = sqlite3.connect(root_dir + '/data/pokedex.db')
    c = conn.cursor()
    sql = "SELECT id, korean, type, category, power, accuracy, pp, desc FROM tm Where korean LIKE ?"
    c.execute(sql, (search, ))
    result = c.fetchall()
    return result

def readTmIndex(index: int = 0):
    conn = sqlite3.connect(root_dir + '/data/pokedex.db')
    c = conn.cursor()
    sql = "SELECT id, korean, type, category, power, accuracy, pp, desc FROM tm Where id = ?"
    c.execute(sql, (index, ))
    result = c.fetchall()
    return result

def readTmType(search: str = ""):
    conn = sqlite3.connect(root_dir + '/data/pokedex.db')
    c = conn.cursor()
    sql = "SELECT id, korean, type, category, power, accuracy, pp, desc FROM tm Where type = ?"
    c.execute(sql, (search, ))
    result = c.fetchall()
    return result

def readTmCategory(search: str = ""):
    conn = sqlite3.connect(root_dir + '/data/pokedex.db')
    c = conn.cursor()
    sql = "SELECT id, korean, type, category, power, accuracy, pp, desc FROM tm Where category = ?"
    c.execute(sql, (search, ))
    result = c.fetchall()
    return result


# Icons
def dexNum(num:int = 0, digits: int = 3):
    char = [
        "<:n0:1266725696252809216>",
        "<:n1:1266725698249429123>",
        "<:n2:1266725699918499873>",
        "<:n3:1266725701134848033>",
        "<:n4:1266725704154746920>",
        "<:n5:1266725705979269213>",
        "<:n6:1266725707300474965>",
        "<:n7:1266725709511131196>",
        "<:n8:1266725711012565033>",
        "<:n9:1266725712736292945>"
    ]
    temp = ""

    for c in str(num).zfill(digits):
        temp += char[int(c)]

    return temp

def dexType(type1: str = "-", type2: str = "-"):
    icon = {
        "-": ":black_large_square:",
        "노말": "<:normal:1266724471859839086>",
        "불꽃": "<:fire:1266724473571246092>",
        "물": "<:water:1266724475148173342>",
        "풀": "<:grass:1266724476725493874>",
        "전기": "<:electric:1266724478751084596>",
        "얼음": "<:ice:1266724480080674930>",
        "격투": "<:fighting:1266724482370764841>",
        "독": "<:poison:1266724484057141320>",
        "땅": "<:ground:1266724485688459264>",
        "비행": "<:flying:1266724487496470588>",
        "에스퍼": "<:psychic:1266724614508249257>",
        "벌레": "<:bug:1266724491656953898>",
        "바위": "<:rock:1266724494945288224>",
        "고스트": "<:ghost:1266724496652501084>",
        "드래곤": "<:dragon:1266724616077054045>",
        "악": "<:dark:1266724501060587611>",
        "강철": "<:steel:1266724504110104646>",
        "페어리": "<:fairy:1266724507184267325>",
        "물리": "<:physical:1266773802273214566>",
        "특수": "<:special:1266773804617826495> ",
        "변화": "<:status:1266773806240763936>"
    }

    temp = f"{icon[type1]} {icon[type2]}"
    return temp

def dexNature(nature: str = ""):
    temp = [1.0, 1.0, 1.0, 1.0, 1.0, nature]

    if nature in ["외로움", "고집", "개구쟁이", "용감"]:
        temp[0] = 1.1
    elif nature in ["대담", "장난꾸러기", "촐랑", "무사태평"]:
        temp[1] = 1.1
    elif nature in ["조심", "의젓", "덜렁", "냉정"]:
        temp[2] = 1.1
    elif nature in ["차분", "얌전", "신중", "건방"]:
        temp[3] = 1.1
    elif nature in ["겁쟁이", "성급", "명랑", "천진난만"]:
        temp[4] = 1.1

    if nature in ["대담", "조심", "차분", "겁쟁이"]:
        temp[0] = 0.9
    elif nature in ["외로움", "의젓", "얌전", "성급"]:
        temp[1] = 0.9
    elif nature in ["고집", "장난꾸러기", "신중", "명랑"]:
        temp[2] = 0.9
    elif nature in ["개구쟁이", "촐랑", "덜렁", "천진난만"]:
        temp[3] = 0.9
    elif nature in ["용감", "무사태평", "냉정", "건방"]:
        temp[4] = 0.9

    return temp

def dexColor(first: str = ""):
    temp = {
        "노말": 0xa8a878,
        "불꽃": 0xf08030,
        "물": 0x6890f0,
        "풀": 0x78c850,
        "전기": 0xf8d030,
        "얼음": 0x98d8d8,
        "격투": 0xc03028,
        "독": 0xa03ca0,
        "땅": 0xe0c068,
        "비행": 0xa890f0,
        "에스퍼": 0xf85888,
        "벌레": 0xa8b820,
        "바위": 0xb8a038,
        "고스트": 0x705898,
        "드래곤": 0x7038f8,
        "악": 0x705848,
        "강철": 0xb8b8d0,
        "페어리": 0xee99ac
    }
    return temp[first]

def dexImg(index: int = 0):
    temp = [
        "https://i.ibb.co/N2sVRwn/image.png",
        "https://i.ibb.co/X5s9SPV/1.png",
        "https://i.ibb.co/Xjng2pc/2.png",
        "https://i.ibb.co/0YCS4dS/3.png",
        "https://i.ibb.co/pnMrGX1/4.png",
        "https://i.ibb.co/rwPH7DR/5.png",
        "https://i.ibb.co/H73RQrX/6.png",
        "https://i.ibb.co/SsHw2tp/7.png",
        "https://i.ibb.co/yqZ3xX8/8.png",
        "https://i.ibb.co/zSHXjQW/9.png",
        "https://i.ibb.co/KyNRc9k/10.png",
        "https://i.ibb.co/x7Mp2wY/11.png",
        "https://i.ibb.co/nRKKz0F/12.png",
        "https://i.ibb.co/b6WGJJ9/13.png",
        "https://i.ibb.co/GP7G1xj/14.png",
        "https://i.ibb.co/n8QmMFT/15.png",
        "https://i.ibb.co/rZgtG3W/16.png",
        "https://i.ibb.co/4SMFDxJ/17.png",
        "https://i.ibb.co/MRcZY6j/18.png",
        "https://i.ibb.co/jbpx7Bf/19.png",
        "https://i.ibb.co/9nXgKvm/20.png",
        "https://i.ibb.co/LZ6Zcvt/21.png",
        "https://i.ibb.co/z5ygJ7K/22.png",
        "https://i.ibb.co/92Fsk6S/23.png",
        "https://i.ibb.co/0Y41MSW/24.png",
        "https://i.ibb.co/HdRhzMx/25.png",
        "https://i.ibb.co/0pNJfs2/26.png",
        "https://i.ibb.co/c8QWBSD/27.png",
        "https://i.ibb.co/vHTFgcd/28.png",
        "https://i.ibb.co/6XdqpDh/29.png",
        "https://i.ibb.co/Mg8F46n/30.png",
        "https://i.ibb.co/wNmQwym/31.png",
        "https://i.ibb.co/mBf4MH6/32.png",
        "https://i.ibb.co/L6GHQLW/33.png",
        "https://i.ibb.co/7R6Cv0G/34.png",
        "https://i.ibb.co/YZD7vpB/35.png",
        "https://i.ibb.co/PgmdMW8/36.png",
        "https://i.ibb.co/6w6cKjs/37.png",
        "https://i.ibb.co/MBCSDtW/38.png",
        "https://i.ibb.co/ZNfRRCh/39.png",
        "https://i.ibb.co/6Xq2yBP/40.png",
        "https://i.ibb.co/XChyCYB/41.png",
        "https://i.ibb.co/0twdGNv/42.png",
        "https://i.ibb.co/W5MDQ04/43.png",
        "https://i.ibb.co/2Z3RJLZ/44.png",
        "https://i.ibb.co/9sJt3CK/45.png",
        "https://i.ibb.co/cxqSBkv/46.png",
        "https://i.ibb.co/dMTrJn8/47.png",
        "https://i.ibb.co/s9DVvNc/48.png",
        "https://i.ibb.co/4743hg2/49.png",
        "https://i.ibb.co/fYDz6pS/50.png",
        "https://i.ibb.co/z2bSNXB/51.png",
        "https://i.ibb.co/hMD4jbT/52.png",
        "https://i.ibb.co/bL2MKnY/53.png",
        "https://i.ibb.co/4SFPvPW/54.png",
        "https://i.ibb.co/X5g1sGT/55.png",
        "https://i.ibb.co/LYkNBqL/56.png",
        "https://i.ibb.co/54F4hqL/57.png",
        "https://i.ibb.co/h795NSL/58.png",
        "https://i.ibb.co/hZq4d3m/59.png",
        "https://i.ibb.co/pfV2thg/60.png",
        "https://i.ibb.co/pX6ZhBz/61.png",
        "https://i.ibb.co/pLsR1Dr/62.png",
        "https://i.ibb.co/m4TD0Kh/63.png",
        "https://i.ibb.co/CmyPvhN/64.png",
        "https://i.ibb.co/23BXhXR/65.png",
        "https://i.ibb.co/KmCDPcX/66.png",
        "https://i.ibb.co/pvdRsgX/67.png",
        "https://i.ibb.co/5KS8jXV/68.png",
        "https://i.ibb.co/WgChfLF/69.png",
        "https://i.ibb.co/RCGPXLm/70.png",
        "https://i.ibb.co/L0pLDcn/71.png",
        "https://i.ibb.co/72PT5PB/72.png",
        "https://i.ibb.co/g7KV8ds/73.png",
        "https://i.ibb.co/pw12n4W/74.png",
        "https://i.ibb.co/XXMHc4m/75.png",
        "https://i.ibb.co/mtVxRsC/76.png",
        "https://i.ibb.co/7XPV4hV/77.png",
        "https://i.ibb.co/Z2zqXzR/78.png",
        "https://i.ibb.co/J35tJ0H/79.png",
        "https://i.ibb.co/7tfGGvM/80.png",
        "https://i.ibb.co/4MfNbRm/81.png",
        "https://i.ibb.co/L1g41pZ/82.png",
        "https://i.ibb.co/642GgXm/83.png",
        "https://i.ibb.co/bRcwX6N/84.png",
        "https://i.ibb.co/6ZNqk6S/85.png",
        "https://i.ibb.co/zHFsLzK/86.png",
        "https://i.ibb.co/TB1m74M/87.png",
        "https://i.ibb.co/HNSpWVK/88.png",
        "https://i.ibb.co/mNGd8sj/89.png",
        "https://i.ibb.co/gFKHFHJ/90.png",
        "https://i.ibb.co/ZHJp8v1/91.png",
        "https://i.ibb.co/FDfJGVQ/92.png",
        "https://i.ibb.co/hKm40Wt/93.png",
        "https://i.ibb.co/MGZNdMV/94.png",
        "https://i.ibb.co/tz3k0PN/95.png",
        "https://i.ibb.co/J2Bc2C1/96.png",
        "https://i.ibb.co/nLGxMvd/97.png",
        "https://i.ibb.co/WDZQ4QG/98.png",
        "https://i.ibb.co/F7vy4qk/99.png",
        "https://i.ibb.co/Mpq7W7T/100.png",
        "https://i.ibb.co/X2Zbjz7/101.png",
        "https://i.ibb.co/3mhkK3y/102.png",
        "https://i.ibb.co/g7RL5jM/103.png",
        "https://i.ibb.co/t4jqW5R/104.png",
        "https://i.ibb.co/zSRSs7v/105.png",
        "https://i.ibb.co/j3zS0qn/106.png",
        "https://i.ibb.co/SsS3sx9/107.png",
        "https://i.ibb.co/zFFHHsg/108.png",
        "https://i.ibb.co/9vD9QVn/109.png",
        "https://i.ibb.co/BBp2n06/110.png",
        "https://i.ibb.co/7RWGX7v/111.png",
        "https://i.ibb.co/1GwZxMg/112.png",
        "https://i.ibb.co/pd6tk5R/113.png",
        "https://i.ibb.co/GWPSRdV/114.png",
        "https://i.ibb.co/T204PY3/115.png",
        "https://i.ibb.co/TvL6w49/116.png",
        "https://i.ibb.co/YfSLDjL/117.png",
        "https://i.ibb.co/mNkV6kn/118.png",
        "https://i.ibb.co/4JfcKzd/119.png",
        "https://i.ibb.co/J7cQd0g/120.png",
        "https://i.ibb.co/BCztPq4/121.png",
        "https://i.ibb.co/t4qgRx6/122.png",
        "https://i.ibb.co/LYxXgWw/123.png",
        "https://i.ibb.co/zXtPTz0/124.png",
        "https://i.ibb.co/1frSbPL/125.png",
        "https://i.ibb.co/DKWZWcm/126.png",
        "https://i.ibb.co/W3yX6qJ/127.png",
        "https://i.ibb.co/G2dS8v3/128.png",
        "https://i.ibb.co/MDBbhY3/129.png",
        "https://i.ibb.co/W58WwYM/130.png",
        "https://i.ibb.co/5nYrwRX/131.png",
        "https://i.ibb.co/XW64jfx/132.png",
        "https://i.ibb.co/1RCnDGZ/133.png",
        "https://i.ibb.co/HdqPbHK/134.png",
        "https://i.ibb.co/S7ssxTz/135.png",
        "https://i.ibb.co/Rc2YPqZ/136.png",
        "https://i.ibb.co/StZgWfN/137.png",
        "https://i.ibb.co/SvMBNMp/138.png",
        "https://i.ibb.co/LZYJPxn/139.png",
        "https://i.ibb.co/xHPcCQK/140.png",
        "https://i.ibb.co/HVmhwbV/141.png",
        "https://i.ibb.co/89PLzZ1/142.png",
        "https://i.ibb.co/2FNP8pp/143.png",
        "https://i.ibb.co/TKfj30J/144.png",
        "https://i.ibb.co/sVMcDXY/145.png",
        "https://i.ibb.co/9NS0ZDf/146.png",
        "https://i.ibb.co/kXt51Sv/147.png",
        "https://i.ibb.co/tKSKTNH/148.png",
        "https://i.ibb.co/tCG1bNc/149.png",
        "https://i.ibb.co/cY43zyK/150.png",
        "https://i.ibb.co/WcMfwSk/151.png",
        "https://i.ibb.co/KqLJyHT/152.png",
        "https://i.ibb.co/MDCKv6C/153.png",
        "https://i.ibb.co/6yX3Jnv/154.png",
        "https://i.ibb.co/LPrBhfH/155.png",
        "https://i.ibb.co/G3Mc6Yp/156.png",
        "https://i.ibb.co/P5VnWXK/157.png",
        "https://i.ibb.co/B6q5VrR/158.png",
        "https://i.ibb.co/GHdDDcn/159.png",
        "https://i.ibb.co/YZ6QxZ6/160.png",
        "https://i.ibb.co/jLv8BJk/161.png",
        "https://i.ibb.co/3ymtt9q/162.png",
        "https://i.ibb.co/yfk1NnC/163.png",
        "https://i.ibb.co/cDDjztw/164.png",
        "https://i.ibb.co/L9V9QPt/165.png",
        "https://i.ibb.co/CPyLYHQ/166.png",
        "https://i.ibb.co/d2MPCRB/167.png",
        "https://i.ibb.co/XWg1H9k/168.png",
        "https://i.ibb.co/frm3LVj/169.png",
        "https://i.ibb.co/hHNzwwB/170.png",
        "https://i.ibb.co/bBdT5rL/171.png",
        "https://i.ibb.co/99tCysm/172.png",
        "https://i.ibb.co/TPxMTPg/173.png",
        "https://i.ibb.co/XxrVyG6/174.png",
        "https://i.ibb.co/s9gTpPS/175.png",
        "https://i.ibb.co/Dbd5MBJ/176.png",
        "https://i.ibb.co/bJDH5Tn/177.png",
        "https://i.ibb.co/z8FpBqw/178.png",
        "https://i.ibb.co/yNk0cMq/179.png",
        "https://i.ibb.co/WgxxMjF/180.png",
        "https://i.ibb.co/zF4jT2G/181.png",
        "https://i.ibb.co/x38ddxD/182.png",
        "https://i.ibb.co/VtsjGrk/183.png",
        "https://i.ibb.co/RpjKFjy/184.png",
        "https://i.ibb.co/QJv0jTJ/185.png",
        "https://i.ibb.co/SQ97zhB/186.png",
        "https://i.ibb.co/zn1pXcz/187.png",
        "https://i.ibb.co/5FXmpgb/188.png",
        "https://i.ibb.co/xsHwZXB/189.png",
        "https://i.ibb.co/tsD4GLh/190.png",
        "https://i.ibb.co/qsSM2Kc/191.png",
        "https://i.ibb.co/df9RsTX/192.png",
        "https://i.ibb.co/1m7KNBV/193.png",
        "https://i.ibb.co/H2GXqcd/194.png",
        "https://i.ibb.co/fx5MT8K/195.png",
        "https://i.ibb.co/WtrKRCV/196.png",
        "https://i.ibb.co/Pg1t7WJ/197.png",
        "https://i.ibb.co/T1cLSMy/198.png",
        "https://i.ibb.co/JqyvVXm/199.png",
        "https://i.ibb.co/b7b7QKG/200.png",
        "https://i.ibb.co/wCT3J3q/201.png",
        "https://i.ibb.co/RhS14sD/202.png",
        "https://i.ibb.co/z8Cf3wt/203.png",
        "https://i.ibb.co/sykvT2H/204.png",
        "https://i.ibb.co/hmTg8SC/205.png",
        "https://i.ibb.co/DL9jmvD/206.png",
        "https://i.ibb.co/9GQBJwn/207.png",
        "https://i.ibb.co/nk4QkYm/208.png",
        "https://i.ibb.co/dGX6D7q/209.png",
        "https://i.ibb.co/BBzBYky/210.png",
        "https://i.ibb.co/ynkNL7b/211.png",
        "https://i.ibb.co/YyF9Dkz/212.png",
        "https://i.ibb.co/Tc9jmF0/213.png",
        "https://i.ibb.co/0KsbRqK/214.png",
        "https://i.ibb.co/RDrNDzk/215.png",
        "https://i.ibb.co/qsmQbV1/216.png",
        "https://i.ibb.co/vQdwQ0L/217.png",
        "https://i.ibb.co/Svhr6mx/218.png",
        "https://i.ibb.co/Xxc0JKv/219.png",
        "https://i.ibb.co/BN3680X/220.png",
        "https://i.ibb.co/6HXCPsm/221.png",
        "https://i.ibb.co/1Zt0Ty7/222.png",
        "https://i.ibb.co/qBrYJ5P/223.png",
        "https://i.ibb.co/g4HnMNr/224.png",
        "https://i.ibb.co/GR4wZxH/225.png",
        "https://i.ibb.co/QFr0rst/226.png",
        "https://i.ibb.co/qRtRM0b/227.png",
        "https://i.ibb.co/K6P65QR/228.png",
        "https://i.ibb.co/kSmKFkb/229.png",
        "https://i.ibb.co/tzWPTrt/230.png",
        "https://i.ibb.co/6H86NCt/231.png",
        "https://i.ibb.co/5YvJnX3/232.png",
        "https://i.ibb.co/h2TLJsB/233.png",
        "https://i.ibb.co/rtcdN1N/234.png",
        "https://i.ibb.co/PQfSPnv/235.png",
        "https://i.ibb.co/3k2bHxr/236.png",
        "https://i.ibb.co/z8mPPJY/237.png",
        "https://i.ibb.co/j8tLJck/238.png",
        "https://i.ibb.co/1nbY4V2/239.png",
        "https://i.ibb.co/PG28bTt/240.png",
        "https://i.ibb.co/PNqvYM8/241.png",
        "https://i.ibb.co/SybqBfN/242.png",
        "https://i.ibb.co/PwfMKb9/243.png",
        "https://i.ibb.co/W5sQMzh/244.png",
        "https://i.ibb.co/tqRbRcc/245.png",
        "https://i.ibb.co/w05v6vR/246.png",
        "https://i.ibb.co/ZMp8s6Q/247.png",
        "https://i.ibb.co/pZh0Mk2/248.png",
        "https://i.ibb.co/T1XfyC5/249.png",
        "https://i.ibb.co/LZ1Bx8j/250.png",
        "https://i.ibb.co/RDGw6WS/251.png",
        "https://i.ibb.co/ckrY6g1/252.png",
        "https://i.ibb.co/Bz5rXJr/253.png",
        "https://i.ibb.co/BKVvqxM/254.png",
        "https://i.ibb.co/R9Z7p37/255.png",
        "https://i.ibb.co/BZRBxLG/256.png",
        "https://i.ibb.co/VQ0VRZ5/257.png",
        "https://i.ibb.co/fvD945j/258.png",
        "https://i.ibb.co/2W36qX0/259.png",
        "https://i.ibb.co/BzdhyRJ/260.png",
        "https://i.ibb.co/tpzQDRd/261.png",
        "https://i.ibb.co/L5G0rD7/262.png",
        "https://i.ibb.co/rfYbXCt/263.png",
        "https://i.ibb.co/mDqP7ZV/264.png",
        "https://i.ibb.co/z2rW1SL/265.png",
        "https://i.ibb.co/8BTzYjp/266.png",
        "https://i.ibb.co/GFrCbDZ/267.png",
        "https://i.ibb.co/4smtzgX/268.png",
        "https://i.ibb.co/vd38cB7/269.png",
        "https://i.ibb.co/234TGGF/270.png",
        "https://i.ibb.co/m8ghS18/271.png",
        "https://i.ibb.co/549xmhQ/272.png",
        "https://i.ibb.co/QYMxSyG/273.png",
        "https://i.ibb.co/wCWjVQM/274.png",
        "https://i.ibb.co/ZK4g71h/275.png",
        "https://i.ibb.co/Z8PGL1y/276.png",
        "https://i.ibb.co/KN7JY1Q/277.png",
        "https://i.ibb.co/SxbRL79/278.png",
        "https://i.ibb.co/hySHqzX/279.png",
        "https://i.ibb.co/ym9NS4H/280.png",
        "https://i.ibb.co/3TY10wj/281.png",
        "https://i.ibb.co/zFhjSrk/282.png",
        "https://i.ibb.co/xS565sT/283.png",
        "https://i.ibb.co/93RCTTT/284.png",
        "https://i.ibb.co/GH037tt/285.png",
        "https://i.ibb.co/5Ft0BZf/286.png",
        "https://i.ibb.co/qW17F2z/287.png",
        "https://i.ibb.co/Br0HkZ2/288.png",
        "https://i.ibb.co/tPHKMFL/289.png",
        "https://i.ibb.co/H4hCtqt/290.png",
        "https://i.ibb.co/hZHvymY/291.png",
        "https://i.ibb.co/4ddgZ3P/292.png",
        "https://i.ibb.co/0mRtBxp/293.png",
        "https://i.ibb.co/0BqWN4h/294.png",
        "https://i.ibb.co/ngVY6dy/295.png",
        "https://i.ibb.co/7yB0mHn/296.png",
        "https://i.ibb.co/CW6mM2P/297.png",
        "https://i.ibb.co/rvSw0L3/298.png",
        "https://i.ibb.co/Tbn61JB/299.png",
        "https://i.ibb.co/GJbx92L/300.png",
        "https://i.ibb.co/1ssj3YP/301.png",
        "https://i.ibb.co/KyM3B6x/302.png",
        "https://i.ibb.co/5GxyL7L/303.png",
        "https://i.ibb.co/y0c8tST/304.png",
        "https://i.ibb.co/PTdbncZ/305.png",
        "https://i.ibb.co/3rXpTSd/306.png",
        "https://i.ibb.co/nBfFY2z/307.png",
        "https://i.ibb.co/Xk8RBn5/308.png",
        "https://i.ibb.co/9T21XK3/309.png",
        "https://i.ibb.co/WPPzFrN/310.png",
        "https://i.ibb.co/ZSfcTrS/311.png",
        "https://i.ibb.co/KXYxwKH/312.png",
        "https://i.ibb.co/mbHMpKT/313.png",
        "https://i.ibb.co/ZhchVxX/314.png",
        "https://i.ibb.co/MDbC9f8/315.png",
        "https://i.ibb.co/4fW60ZQ/316.png",
        "https://i.ibb.co/5rSqzXg/317.png",
        "https://i.ibb.co/hCWqzLY/318.png",
        "https://i.ibb.co/7WmDbQv/319.png",
        "https://i.ibb.co/p2DPDhv/320.png",
        "https://i.ibb.co/0K9vPT5/321.png",
        "https://i.ibb.co/n7qL29D/322.png",
        "https://i.ibb.co/tQVRC8R/323.png",
        "https://i.ibb.co/gP30dVv/324.png",
        "https://i.ibb.co/NZHS23x/325.png",
        "https://i.ibb.co/PQJZXQQ/326.png",
        "https://i.ibb.co/C2jxvJF/327.png",
        "https://i.ibb.co/cJdtnjp/328.png",
        "https://i.ibb.co/SQkJBXX/329.png",
        "https://i.ibb.co/0swcLG6/330.png",
        "https://i.ibb.co/XjKktMz/331.png",
        "https://i.ibb.co/8bjLfVb/332.png",
        "https://i.ibb.co/8xGgjbw/333.png",
        "https://i.ibb.co/NsK61px/334.png",
        "https://i.ibb.co/ZhFZMTw/335.png",
        "https://i.ibb.co/8KLS4GM/336.png",
        "https://i.ibb.co/DM4v4ph/337.png",
        "https://i.ibb.co/VB65JyN/338.png",
        "https://i.ibb.co/7QHjQgZ/339.png",
        "https://i.ibb.co/9tjNRqF/340.png",
        "https://i.ibb.co/7W2rvMD/341.png",
        "https://i.ibb.co/Y35kdYM/342.png",
        "https://i.ibb.co/q995YWq/343.png",
        "https://i.ibb.co/fHmRhXF/344.png",
        "https://i.ibb.co/LgnM2DV/345.png",
        "https://i.ibb.co/yp6XZdX/346.png",
        "https://i.ibb.co/DprhST9/347.png",
        "https://i.ibb.co/y8FnVHV/348.png",
        "https://i.ibb.co/dPh0Jmp/349.png",
        "https://i.ibb.co/2gjdv9m/350.png",
        "https://i.ibb.co/FV3pRvp/351.png",
        "https://i.ibb.co/qj4sy0v/352.png",
        "https://i.ibb.co/yYBs9CH/353.png",
        "https://i.ibb.co/t8YdNNp/354.png",
        "https://i.ibb.co/3RVM5qh/355.png",
        "https://i.ibb.co/CwpXwr4/356.png",
        "https://i.ibb.co/VLkHcqL/357.png",
        "https://i.ibb.co/VwybLLJ/358.png",
        "https://i.ibb.co/sq99VvG/359.png",
        "https://i.ibb.co/Q6XfKs6/360.png",
        "https://i.ibb.co/mFx9mKK/361.png",
        "https://i.ibb.co/f85QsvX/362.png",
        "https://i.ibb.co/qCp9YRM/363.png",
        "https://i.ibb.co/Wnn64fq/364.png",
        "https://i.ibb.co/8MdbZgk/365.png",
        "https://i.ibb.co/t8FsJPq/366.png",
        "https://i.ibb.co/nLfVy0X/367.png",
        "https://i.ibb.co/djnLG6r/368.png",
        "https://i.ibb.co/bH01Lk7/369.png",
        "https://i.ibb.co/QXYPp31/370.png",
        "https://i.ibb.co/svz6vfx/371.png",
        "https://i.ibb.co/2Ss2ncM/372.png",
        "https://i.ibb.co/s2MBbd3/373.png",
        "https://i.ibb.co/pJjQpsF/374.png",
        "https://i.ibb.co/tLztZrD/375.png",
        "https://i.ibb.co/mb1C8fh/376.png",
        "https://i.ibb.co/DWq2wbs/377.png",
        "https://i.ibb.co/WK8xNRY/378.png",
        "https://i.ibb.co/RHnsKSK/379.png",
        "https://i.ibb.co/6tgMYwG/380.png",
        "https://i.ibb.co/QCMQn49/381.png",
        "https://i.ibb.co/vV451TV/382.png",
        "https://i.ibb.co/wWJWyTX/383.png",
        "https://i.ibb.co/bvntswS/384.png",
        "https://i.ibb.co/j4FVpKL/385.png",
        "https://i.ibb.co/162Zn9S/386.png",
        "https://i.ibb.co/HXH5q1d/387.png",
        "https://i.ibb.co/qYcVfMx/388.png",
        "https://i.ibb.co/F8jb9wV/389.png",
        "https://i.ibb.co/NSw3kBp/390.png",
        "https://i.ibb.co/6FFsWpf/391.png",
        "https://i.ibb.co/XXQgc2h/392.png",
        "https://i.ibb.co/VMhD3WZ/393.png",
        "https://i.ibb.co/wcHv5Ty/394.png",
        "https://i.ibb.co/G3hJ5Jj/395.png",
        "https://i.ibb.co/pwqRHfG/396.png",
        "https://i.ibb.co/44qbqkj/397.png",
        "https://i.ibb.co/CtgGz2r/398.png",
        "https://i.ibb.co/VQwJ3ZK/399.png",
        "https://i.ibb.co/Qvh2p7g/400.png",
        "https://i.ibb.co/kVZBB4q/401.png",
        "https://i.ibb.co/DMFtcKx/402.png",
        "https://i.ibb.co/k166Kd3/403.png",
        "https://i.ibb.co/M5QpcTg/404.png",
        "https://i.ibb.co/jG38QDk/405.png",
        "https://i.ibb.co/2MMsMxK/406.png",
        "https://i.ibb.co/8xTYrjF/407.png",
        "https://i.ibb.co/SfF7XQx/408.png",
        "https://i.ibb.co/XZrFjMt/409.png",
        "https://i.ibb.co/LgKCC72/410.png",
        "https://i.ibb.co/6rWK3xL/411.png",
        "https://i.ibb.co/QYPTJvh/412.png",
        "https://i.ibb.co/72NmBHb/413.png",
        "https://i.ibb.co/W63nbvh/414.png",
        "https://i.ibb.co/V3Ds697/415.png",
        "https://i.ibb.co/9Ysphc8/416.png",
        "https://i.ibb.co/c1X4wSK/417.png",
        "https://i.ibb.co/2qCD1Yw/418.png",
        "https://i.ibb.co/r7f4Rrp/419.png",
        "https://i.ibb.co/r5n0gBv/420.png",
        "https://i.ibb.co/syr6tDk/421.png",
        "https://i.ibb.co/6mzxtXJ/422.png",
        "https://i.ibb.co/nbCMbCF/423.png",
        "https://i.ibb.co/bFQSpDj/424.png",
        "https://i.ibb.co/fv9Jvmb/425.png",
        "https://i.ibb.co/hRvZ6Ks/426.png",
        "https://i.ibb.co/vz37Qcz/427.png",
        "https://i.ibb.co/qddLCvX/428.png",
        "https://i.ibb.co/prgF7cL/429.png",
        "https://i.ibb.co/27T0Xft/430.png",
        "https://i.ibb.co/1GfF1T1/431.png",
        "https://i.ibb.co/qpBcrkT/432.png",
        "https://i.ibb.co/4TpRPRz/433.png",
        "https://i.ibb.co/bzQVdQ8/434.png",
        "https://i.ibb.co/kQvb8sT/435.png",
        "https://i.ibb.co/rMs9vkm/436.png",
        "https://i.ibb.co/vJhBvVV/437.png",
        "https://i.ibb.co/XJrJDf5/438.png",
        "https://i.ibb.co/txKn0Ss/439.png",
        "https://i.ibb.co/Pt1jgkF/440.png",
        "https://i.ibb.co/TgF8T7B/441.png",
        "https://i.ibb.co/wW8vTJm/442.png",
        "https://i.ibb.co/CBV8kt8/443.png",
        "https://i.ibb.co/Qk2F8XH/444.png",
        "https://i.ibb.co/HBbmfyR/445.png",
        "https://i.ibb.co/rfLbvkN/446.png",
        "https://i.ibb.co/B4L501m/447.png",
        "https://i.ibb.co/ynj2yN0/448.png",
        "https://i.ibb.co/091HhWq/449.png",
        "https://i.ibb.co/jzLFmk3/450.png",
        "https://i.ibb.co/N7VDrpc/451.png",
        "https://i.ibb.co/cFGPTTd/452.png",
        "https://i.ibb.co/DwZhkD5/453.png",
        "https://i.ibb.co/KbnQYNg/454.png",
        "https://i.ibb.co/M19cBR1/455.png",
        "https://i.ibb.co/wYd3FqG/456.png",
        "https://i.ibb.co/rkQTcwj/457.png",
        "https://i.ibb.co/BwHBj01/458.png",
        "https://i.ibb.co/XpdcFyx/459.png",
        "https://i.ibb.co/hsnNhvr/460.png",
        "https://i.ibb.co/3hRNQmx/461.png",
        "https://i.ibb.co/Ln3DdfF/462.png",
        "https://i.ibb.co/747BMsY/463.png",
        "https://i.ibb.co/0yp9G1m/464.png",
        "https://i.ibb.co/44L0RxG/465.png",
        "https://i.ibb.co/K7qfGY8/466.png",
        "https://i.ibb.co/tQY4LgF/467.png",
        "https://i.ibb.co/30n1QZZ/468.png",
    ]

    return temp[index]