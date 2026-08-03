# 0. Import modules
import discord
from discord.ext import commands
import sqlite3
import random as r
import datetime
from contextlib import closing
from project_paths import DATA_DIR


DB_PATH = DATA_DIR / "user.db"


def _execute(sql, parameters=()):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, parameters)
        conn.commit()
        cursor.close()


def _fetchone(sql, parameters=()):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, parameters)
        result = cursor.fetchone()
        cursor.close()
        return result


def _fetchall(sql, parameters=()):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, parameters)
        result = cursor.fetchall()
        cursor.close()
        return result


# 2. Sub Functions

# 2.1. Init Setting
def initSetting():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    sql = """CREATE TABLE IF NOT EXISTS main(
    id INTEGER PRIMARY KEY,
    discrim INTEGER NOT NULL,
    nick TEXT NOT NULL,
    xp INTEGER NOT NULL,
    money INTEGER NOT NULL,
    skin INTEGER NOT NULL,
    startdate TEXT NOT NULL,
    daily INTEGER NOT NULL,
    dailydate TEXT NOT NULL,
    language TEXT NOT NULL
    );"""

    c.execute(sql)
    conn.commit()

    sql = """CREATE TABLE IF NOT EXISTS storage(id INTEGER PRIMARY KEY);"""

    c.execute(sql)
    conn.commit()

    for i in range(1, 1025):
        try:
            sql = "ALTER TABLE storage ADD COLUMN {} [TINYINT] DEFAULT 0;".format(
                "id" + str(i))
            c.execute(sql)
            conn.commit()
        except:
            pass

    conn.close()


# 2.2. Backup Data
def initSetting2():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    sql = """CREATE TABLE IF NOT EXISTS main(
    id INTEGER PRIMARY KEY,
    discrim INTEGER NOT NULL,
    nick TEXT NOT NULL,
    xp INTEGER NOT NULL,
    money INTEGER NOT NULL,
    skin INTEGER NOT NULL,
    startdate TEXT NOT NULL,
    daily INTEGER NOT NULL,
    dailydate TEXT NOT NULL,
    language TEXT NOT NULL);"""

    c.execute(sql)
    conn.commit()

    sql = """CREATE TABLE IF NOT EXISTS storage(
    id INTEGER PRIMARY KEY);"""

    c.execute(sql)
    conn.commit()

    for i in range(1, 1024):
        try:
            sql = "ALTER TABLE storage ADD COLUMN {} [TINYINT] DEFAULT 0;".format(
                "id" + str(i))
            c.execute(sql)
            conn.commit()
        except:
            pass

    conn.close()


# 3. Actions


# 3.1. Add data
def newAccount(user: discord.Member = None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    INSERT_SQL = 'INSERT INTO main (id, discrim, nick, xp, money, skin, startdate, daily, dailydate, language) VALUES (?,?,?,?,?,?,?,?,?,?);'

    nickname = user.name
    discrim = r.randint(1, 10000)
    now = datetime.datetime.now()
    now_date = now.strftime('%Y-%m-%d')
    
    retry = 0

    while True:
        if tagIsOkay(nickname, discrim):
            break

        else:
            retry += 1
            discrim = r.randint(1, 10000)

            if retry == 10:
                retry = 0
                nickname += "!"


    data = ((user.id, discrim, nickname, 0, 5000, 1, now_date, 0, '-', 'ko'))
    print(data)
    c.execute(INSERT_SQL, data)
    conn.commit()
    print("added!")

    conn.close()


def newAccountById(user: int = None, name: str = None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    INSERT_SQL = 'INSERT INTO main (id, discrim, nick, xp, money, skin, startdate, daily, dailydate, language) VALUES (?,?,?,?,?,?,?,?,?,?);'

    nickname = name
    discrim = r.randint(1, 10000)
    now = datetime.datetime.now()
    now_date = now.strftime('%Y-%m-%d')

    retry = 0

    while True:
        print(nickname, '#', discrim)
        if tagIsOkay(nickname, discrim):
            break

        else:
            retry += 1
            discrim = r.randint(1, 10000)

            if retry == 10:
                retry = 0
                nickname += "!"

    data = ((user, discrim, nickname, 0, 5000, 1, now_date, 0, '-', 'ko'))
    print(data)
    c.execute(INSERT_SQL, data)
    conn.commit()
    print("added!")

    conn.close()


# 3.2. Write data

# 3.2.1. Xp Modifier


# 3.2.1.1. Xp Value Edit
def xpModify(user: discord.Member = None, amount: int = None):
    _execute("UPDATE main SET xp = ? WHERE id = ?", (amount, user.id))


def xpModifyById(user: int = None, amount: int = None):
    _execute("UPDATE main SET xp = ? WHERE id = ?", (amount, user))


# 3.2.1.2. Xp Add
def xpAdd(user: discord.Member = None, amount: int = None):
    _execute("UPDATE main SET xp = xp + ? WHERE id = ?", (amount, user.id))


def xpAddById(user: int = None, amount: int = None):
    _execute("UPDATE main SET xp = xp + ? WHERE id = ?", (amount, user))


# 3.2.1.3. Xp Add All
def xpAddAll(amount: int = None):
    _execute("UPDATE main SET xp = xp + ?", (amount,))


# 3.2.2. Money Modifier


# 3.2.2.1. Money Value Edit
def moneyModify(user: discord.Member = None, amount: int = None):
    _execute("UPDATE main SET money = ? WHERE id = ?", (amount, user.id))


def moneyModifyById(user: int = None, amount: int = None):
    _execute("UPDATE main SET money = ? WHERE id = ?", (amount, user))


# 3.2.2.2. Money Add
def moneyAdd(user: discord.Member = None, amount: int = None):
    _execute(
        "UPDATE main SET money = money + ? WHERE id = ?",
        (amount, user.id),
    )


def moneyAddById(user: int = None, amount: int = None):
    _execute("UPDATE main SET money = money + ? WHERE id = ?", (amount, user))


def rewardsAddBulk(
    rewards: dict[int, tuple[int, int]],
    import_keys=(),
) -> None:
    """Atomically add rewards and record keys that prevent duplicate imports."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS reward_imports (
                    import_key TEXT PRIMARY KEY,
                    imported_at TEXT NOT NULL DEFAULT
                        (datetime('now', '+9 hours'))
                )
                """
            )
            normalized_keys = tuple(str(key) for key in import_keys)
            for import_key in normalized_keys:
                if cursor.execute(
                    "SELECT 1 FROM reward_imports WHERE import_key = ?",
                    (import_key,),
                ).fetchone() is not None:
                    raise ValueError("This data file has already been processed.")

            for user_id, (xp_amount, money_amount) in rewards.items():
                cursor.execute(
                    """
                    UPDATE main
                    SET xp = xp + ?, money = money + ?
                    WHERE id = ?
                    """,
                    (int(xp_amount), int(money_amount), int(user_id)),
                )
                if cursor.rowcount != 1:
                    raise ValueError(
                        f"User {int(user_id)} does not have a bot account."
                    )
            cursor.executemany(
                "INSERT INTO reward_imports (import_key) VALUES (?)",
                ((key,) for key in normalized_keys),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()


# 3.2.1.3. Xp Add All
def moneyAddAll(amount: int = None):
    _execute("UPDATE main SET money = money + ?", (amount,))


# 3.2.3. Tag Modifier


# 3.2.3.1. Nickname Edit
def nickModify(user: discord.Member = None, name: str = None):
    if tagIsOkay(name, int(readDiscrim(user))):
        _execute("UPDATE main SET nick = ? WHERE id = ?", (name, user.id))


def nickModifyById(user: int = None, name: str = None):
    if tagIsOkay(name, int(readDiscrimById(user))):
        _execute("UPDATE main SET nick = ? WHERE id = ?", (name, user))


# 3.2.3.2. Discrim Edit
def discrimModify(user: discord.Member = None, value: int = None):
    if tagIsOkay(readNick(user), value):
        _execute("UPDATE main SET discrim = ? WHERE id = ?", (value, user.id))


def discrimModifyById(user: int = None, value: int = None):
    if tagIsOkay(readNickById(user), value):
        _execute("UPDATE main SET discrim = ? WHERE id = ?", (value, user))


# 3.2.4. Skin Value Edit
def skinModify(user: discord.Member = None, value: int = None):
    _execute("UPDATE main SET skin = ? WHERE id = ?", (value, user.id))


def skinModifyById(user: int = None, value: int = None):
    _execute("UPDATE main SET skin = ? WHERE id = ?", (value, user))


# 3.2.5. Start Date Value Edit
def startDateModify(user: discord.Member = None, value: str = None):
    _execute("UPDATE main SET startdate = ? WHERE id = ?", (value, user.id))


def startDateModifyById(user: int = None, value: str = None):
    _execute("UPDATE main SET startdate = ? WHERE id = ?", (value, user))

# 3.2.6. Daily Edit
    
def dailyAdd(user: discord.Member = None):
    _execute("UPDATE main SET daily = daily + 1 WHERE id = ?", (user.id,))

def dailyAddById(user: int = None):
    _execute("UPDATE main SET daily = daily + 1 WHERE id = ?", (user,))
    
def dailyModify(user: discord.Member = None, value: int = None):
    _execute("UPDATE main SET daily = ? WHERE id = ?", (value, user.id))

def dailyModifyById(user: int = None, value: int = None):
    _execute("UPDATE main SET daily = ? WHERE id = ?", (value, user))

def dailyDateModify(user: discord.Member = None, value: str = None):
    _execute("UPDATE main SET dailydate = ? WHERE id = ?", (value, user.id))

def dailyDateModifyById(user: int = None, value: str = None):
    _execute("UPDATE main SET dailydate = ? WHERE id = ?", (value, user))

# 3.3. Read data

# 3.3.1. Read All
def readAll(user: discord.Member):
    return _fetchall("SELECT * FROM main WHERE id = ?;", (user.id,))


def accountExistsById(user: int) -> bool:
    """Return whether the user has a main profile row."""
    return _fetchone("SELECT 1 FROM main WHERE id = ?", (user,)) is not None


def storageExistsById(user: int) -> bool:
    """Return whether the user has a skin-storage row."""
    return _fetchone("SELECT 1 FROM storage WHERE id = ?", (user,)) is not None


# 3.3.2. Read Name

# 3.3.2.1. Name only
def readNick(user: discord.Member = None):
    return str(_fetchone("SELECT nick FROM main WHERE id = ?", (user.id,))[0])


def readNickById(user: int = None):
    return str(_fetchone("SELECT nick FROM main WHERE id = ?", (user,))[0])


# 3.3.2.2. Discrim only
def readDiscrim(user: discord.Member = None):
    result = _fetchone("SELECT discrim FROM main WHERE id = ?", (user.id,))[0]
    return str(result).zfill(4)


def readDiscrimById(user: int = None):
    result = _fetchone("SELECT discrim FROM main WHERE id = ?", (user,))[0]
    return str(result).zfill(4)


# 3.3.2.3. Full Tag
def readTag(user: discord.Member = None):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute("SELECT nick, discrim FROM main WHERE id = ?", (user.id, ))
        temp = c.fetchone()
        c.close()
        return str(temp[0]) + "#" + str(temp[1]).zfill(4)


def readTagById(user: int = None):
    result = _fetchone(
        "SELECT nick, discrim FROM main WHERE id = ?",
        (user,),
    )
    return str(result[0]) + "#" + str(result[1]).zfill(4)


# 3.3.3. Read Xp
def readXp(user: discord.Member = None):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute("SELECT xp FROM main WHERE id = ?", (user.id, ))
        result = c.fetchone()[0]
        c.close()
        return result


def readXpById(user: int = None):
    return _fetchone("SELECT xp FROM main WHERE id = ?", (user,))[0]


# 3.3.4. Read Money
def readMoney(user: discord.Member = None):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute("SELECT money FROM main WHERE id = ?", (user.id, ))
        result = c.fetchone()[0]
        c.close()
        return result


def readMoneyById(user: int = None):
    return _fetchone("SELECT money FROM main WHERE id = ?", (user,))[0]


# 3.3.5. Read Skin
def readSkin(user: discord.Member = None):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute("SELECT skin FROM main WHERE id = ?", (user.id, ))
        result = c.fetchone()[0]
        c.close()
        return result


def readSkinById(user: int = None):
    return _fetchone("SELECT skin FROM main WHERE id = ?", (user,))[0]


# 3.3.6. Read StartDate
def readStartDate(user: discord.Member = None):
    return _fetchone("SELECT startdate FROM main WHERE id = ?", (user.id,))[0]


def readStartDateById(user: int = None):
    return _fetchone("SELECT startdate FROM main WHERE id = ?", (user,))[0]

# 3.3.7. Read Daily
def readDaily(user: discord.Member = None):
    return _fetchone("SELECT daily FROM main WHERE id = ?", (user.id,))[0]


def readDailyById(user: int = None):
    return _fetchone("SELECT daily FROM main WHERE id = ?", (user,))[0]

def readDailyDate(user: discord.Member = None):
    return _fetchone("SELECT dailydate FROM main WHERE id = ?", (user.id,))[0]

def readDailyDateById(user: int = None):
    return _fetchone("SELECT dailydate FROM main WHERE id = ?", (user,))[0]


# 3.4. List & Ranking


# 3.4.1. User List
def userList():
    return _fetchall("SELECT * FROM main")


# 3.4.2. User id List
def idList():
    return _fetchall("SELECT id FROM main")


def userCount():
    return _fetchone("SELECT COUNT(*) FROM main;")[0]


# 3.4.3. XP Ranking
def xpRanking():
    return _fetchall(
        "SELECT *, RANK() OVER (ORDER BY xp DESC) ranking FROM main;"
    )


def xpMyRanking(user: discord.Member = None):
    return _fetchone(
        "SELECT id, xp, ranking FROM "
        "(SELECT id, xp, RANK() OVER (ORDER BY xp DESC) AS ranking FROM main) "
        "WHERE id = ?;",
        (user.id,),
    )[2]


# 3.4.4. Money Ranking
def moneyRanking():
    return _fetchall(
        "SELECT *, RANK() OVER (ORDER BY money DESC) ranking FROM main;"
    )


# 3.5. Skin Data

# 3.5.0. Drop table
def dropStorage():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    INSERT_SQL = 'DROP TABLE IF EXISTS storage;'
    c.execute(INSERT_SQL)
    conn.commit()

    conn.close()


# 3.5.1 Add data
def newStorage(user: discord.Member = None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    INSERT_SQL = 'INSERT OR IGNORE INTO storage (id) VALUES (?);'

    data = (user.id, )
    c.execute(INSERT_SQL, data)
    conn.commit()

    c.execute("UPDATE storage SET id1 = ? WHERE id = ?", (1, user.id))

    for i in range(2, 1025):
        c.execute(
            "UPDATE storage SET {} = ? WHERE id = ?".format("id" + str(i)),
            (0, user.id))

    conn.commit()

    conn.close()


def newStorageById(user: int = None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    INSERT_SQL = 'INSERT OR IGNORE INTO storage (id) VALUES (?);'

    c.execute(INSERT_SQL, (user, ))
    conn.commit()

    c.execute("UPDATE storage SET id1 = ? WHERE id = ?", (1, user))

    for i in range(2, 1025):
        c.execute(
            "UPDATE storage SET {} = ? WHERE id = ?".format("id" + str(i)),
            (0, user))

    conn.commit()

    conn.close()


# 3.5.2. Xp Data Write
def storageModify(user: discord.Member = None,
                  id: int = None,
                  value: int = None):
    _execute(
        "UPDATE storage SET {} = ? WHERE id = ?".format("id" + str(id)),
        (value, user.id),
    )


def storageModifyById(user: int = None, id: int = None, value: int = None):
    _execute(
        "UPDATE storage SET {} = ? WHERE id = ?".format("id" + str(id)),
        (value, user),
    )


# 3.5.3. Read Storage
def readStorage(user: discord.Member = None, id: str = None):
    sql = "SELECT {} FROM storage WHERE id = ?;".format("id" + str(id))
    return _fetchone(sql, (user.id,))[0]


def readStorageById(user: int = None, id: str = None):
    sql = "SELECT {} FROM storage WHERE id = ?;".format("id" + str(id))
    return _fetchone(sql, (user,))[0]


# 3.5.4. User Storage List
def storageList(user: discord.Member = None):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM storage WHERE id = ?;", (user.id, ))
        result = c.fetchone()
        c.close()
        return result


def ensureStorage(user: discord.Member = None):
    result = storageList(user)
    if result is None:
        newStorage(user)
        result = storageList(user)
    if result is None:
        raise RuntimeError(f"Failed to initialize storage for user {user.id}")
    return result


def ensureStorageById(user: int):
    result = _fetchone("SELECT * FROM storage WHERE id = ?;", (user,))
    if result is None:
        _execute(
            "INSERT INTO storage (id, id1) VALUES (?, ?);",
            (user, 1),
        )
        result = _fetchone("SELECT * FROM storage WHERE id = ?;", (user,))
    if result is None:
        raise RuntimeError(f"Failed to initialize storage for user {user}")
    return result


# 3.6. Etc

# 3.6.1. Full Tag to UID
def tagToUid(tag: str = None):
    try:
        from fcts.user_resolver import resolve_user_id
        return resolve_user_id(tag)
    except ValueError:
        return None

# 3.6.2. Duplicate Check
def tagIsOkay(name: str = "", discrim: int = 0):
    print(name,'#',discrim)
    result = _fetchall(
        "SELECT id FROM main WHERE nick = ? AND discrim = ?",
        (name, discrim),
    )

    print(result)

    if len(result) == 0 and name != "" and discrim != 0:
        return True

    else:
        return False

# 3.7. 언어 설정
# 3.7.0. 언어 초깃값 추가
def add_language_column():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        c.execute("ALTER TABLE main ADD COLUMN language TEXT NOT NULL DEFAULT 'ko'")
        conn.commit()
        print("language column added.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("language column already exists.")
        else:
            raise
    finally:
        c.close()
        conn.close()

# 3.7.1. 언어 설정 불러오기
def readLanguage(user: discord.Member = None):
    result = _fetchone("SELECT language FROM main WHERE id = ?", (user.id,))
    if result is None or result[0] is None:
        return "ko"
    return result[0]

def readLanguageById(user: int):
    result = _fetchone("SELECT language FROM main WHERE id = ?", (user,))
    if result is None or result[0] is None:
        return "ko"
    return result[0]

# 3.7.2. 언어 설정 수정
def modifyLanguage(user: discord.Member = None, language: str = None):
    _execute("UPDATE main SET language = ? WHERE id = ?", (language, user.id))

def modifyLanguageById(user: int, language: str = None):
    _execute("UPDATE main SET language = ? WHERE id = ?", (language, user))
