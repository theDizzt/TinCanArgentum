"""
;생일추가 @니콜라스 6 7 #생일알림 음력 false
;기념일추가 "파클 슬레이브즈 창단일" 2009 11 16 #기념일 양력 false
;기념일목록
;기념일삭제 3
"""

import sqlite3
from pathlib import Path
from datetime import datetime, date, time
from zoneinfo import ZoneInfo
from typing import Literal
import re

import discord
from discord.ext import commands, tasks

from korean_lunar_calendar import KoreanLunarCalendar


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "anniversary.db"
KST = ZoneInfo("Asia/Seoul")
MIDNIGHT_KST = time(hour=0, minute=0, second=0, tzinfo=KST)


def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS anniversary_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            guild_id INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,

            kind TEXT NOT NULL CHECK (kind IN ('birthday', 'anniversary')),
            calendar_type TEXT NOT NULL CHECK (calendar_type IN ('solar', 'lunar')),

            year INTEGER,
            month INTEGER NOT NULL,
            day INTEGER NOT NULL,
            is_leap_month INTEGER NOT NULL DEFAULT 0,

            user_id INTEGER,
            title TEXT,

            enabled INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

            CHECK (
                (kind = 'birthday' AND user_id IS NOT NULL)
                OR
                (kind = 'anniversary' AND title IS NOT NULL AND year IS NOT NULL)
            )
        );
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS anniversary_sent_logs (
            event_id INTEGER NOT NULL,
            sent_on TEXT NOT NULL,
            PRIMARY KEY (event_id, sent_on)
        );
        """)

        conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_anniversary_today
        ON anniversary_events(calendar_type, month, day, is_leap_month, enabled);
        """)


def calendar_type_to_db(value: str) -> str:
    return "lunar" if value == "음력" else "solar"


def parse_bool_text(value) -> bool:
    if isinstance(value, bool):
        return value

    value = str(value).strip().lower()

    true_values = [
        "true", "1", "yes", "y", "on",
        "예", "네", "ㅇ", "윤달"
    ]

    false_values = [
        "false", "0", "no", "n", "off",
        "아니오", "아니요", "ㄴ", "평달"
    ]

    if value in true_values:
        return True

    if value in false_values:
        return False

    raise ValueError("윤달 여부는 `true` 또는 `false`로 입력해주세요.")


def parse_calendar_type_text(value: str) -> str:
    value = str(value).strip().lower()

    if value in ["양력", "solar", "s"]:
        return "solar"

    if value in ["음력", "lunar", "l"]:
        return "lunar"

    raise ValueError("달력 종류는 `양력` 또는 `음력`으로 입력해주세요.")


async def resolve_text_channel(ctx: commands.Context, channel_text: str):
    channel_text = str(channel_text).strip()

    # <#123456789> 형태에서 숫자만 추출
    match = re.match(r"^<#(\d+)>$", channel_text)

    if match:
        channel_id = int(match.group(1))
    elif channel_text.isdigit():
        channel_id = int(channel_text)
    else:
        raise ValueError("채널은 `<#채널ID>` 멘션 또는 채널 ID 숫자로 입력해주세요.")

    channel = ctx.guild.get_channel(channel_id)

    if channel is None:
        channel = await ctx.bot.fetch_channel(channel_id)

    if not isinstance(channel, discord.TextChannel):
        raise ValueError("알림 채널은 일반 텍스트 채널이어야 합니다.")

    return channel


async def resolve_member_or_user(ctx: commands.Context, user_text: str):
    user_text = str(user_text).strip()

    # <@123>, <@!123> 형태 처리
    match = re.match(r"^<@!?(\d+)>$", user_text)

    if match:
        user_id = int(match.group(1))
    elif user_text.isdigit():
        user_id = int(user_text)
    else:
        raise ValueError("유저는 `@멘션` 또는 유저 ID 숫자로 입력해주세요.")

    member = ctx.guild.get_member(user_id)

    if member is not None:
        return member

    try:
        member = await ctx.guild.fetch_member(user_id)
        return member
    except discord.NotFound:
        user = await ctx.bot.fetch_user(user_id)
        return user


def validate_solar_month_day(month: int, day: int) -> bool:
    try:
        # 2월 29일 생일도 허용하기 위해 윤년인 2000년으로 검사
        date(2000, month, day)
        return True
    except ValueError:
        return False


def validate_anniversary_date(
    calendar_type: str,
    year: int,
    month: int,
    day: int,
    is_leap_month: bool,
) -> bool:
    if calendar_type == "solar":
        try:
            date(year, month, day)
            return True
        except ValueError:
            return False

    calendar = KoreanLunarCalendar()
    return calendar.setLunarDate(year, month, day, is_leap_month)


def get_today_lunar(today: date):
    calendar = KoreanLunarCalendar()

    if not calendar.setSolarDate(today.year, today.month, today.day):
        return None

    return {
        "month": calendar.lunarMonth,
        "day": calendar.lunarDay,
        "is_leap_month": int(calendar.isIntercalation),
    }


def fetch_today_events(today: date):
    lunar_today = get_today_lunar(today)

    lunar_month = lunar_today["month"] if lunar_today else -1
    lunar_day = lunar_today["day"] if lunar_today else -1
    lunar_leap = lunar_today["is_leap_month"] if lunar_today else -1

    with get_conn() as conn:
        return conn.execute(
            """
            SELECT *
            FROM anniversary_events
            WHERE enabled = 1
              AND (
                    (calendar_type = 'solar' AND month = ? AND day = ?)
                    OR
                    (calendar_type = 'lunar' AND month = ? AND day = ? AND is_leap_month = ?)
                  )
            ORDER BY kind, id
            """,
            (
                today.month,
                today.day,
                lunar_month,
                lunar_day,
                lunar_leap,
            ),
        ).fetchall()


def was_sent_today(event_id: int, sent_on: str) -> bool:
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT 1
            FROM anniversary_sent_logs
            WHERE event_id = ? AND sent_on = ?
            """,
            (event_id, sent_on),
        ).fetchone()

    return row is not None


def mark_sent(event_id: int, sent_on: str):
    with get_conn() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO anniversary_sent_logs(event_id, sent_on)
            VALUES (?, ?)
            """,
            (event_id, sent_on),
        )


def build_message(row: sqlite3.Row, today: date) -> str:
    is_lunar = row["calendar_type"] == "lunar"
    leap_text = "윤달 " if row["is_leap_month"] else ""

    if row["kind"] == "birthday":
        if is_lunar:
            date_text = (
                f"오늘 **{today.month}월 {today.day}일**, "
                f"음력 **{leap_text}{row['month']}월 {row['day']}일**은"
            )
        else:
            date_text = f"오늘 **{today.month}월 {today.day}일**은"

        return (
            f"{date_text} <@{row['user_id']}> 의 귀빠진 날입니다. "
            f"그의 빠진 귓구멍에 사랑의 메세지를 쑤셔 넣어 줍시다.\n"
            f"`ex) 태어나줘서 고맙다, 이 사랑스러운 녀석, 영혼의 듀오같은 친구, 복 1000포인트 받아도 부족한 녀석...`"
        )

    years = today.year - row["year"]

    if is_lunar:
        anniversary_date_text = (
            f"음력 {row['year']}년 {leap_text}{row['month']}월 {row['day']}일"
        )
        today_text = f"오늘은 양력 **{today.month}월 {today.day}일**,"
    else:
        anniversary_date_text = (
            f"{row['year']}년 {row['month']}월 {row['day']}일"
        )
        today_text = ""

    if is_lunar:
        return (
            f"{today_text} {anniversary_date_text}인 "
            f"**{row['title']}** 입니다! 올해로 {years}주년입니다."
        )

    return (
        f"{anniversary_date_text}은 "
        f"**{row['title']}** 입니다! 올해로 {years}주년입니다."
    )


class Anniversary(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        init_db()
        self.daily_anniversary_check.start()

    def cog_unload(self):
        self.daily_anniversary_check.cancel()

    async def send_reply(
        self,
        ctx: commands.Context,
        content: str,
        ephemeral: bool = True,
    ):
        if ctx.interaction:
            await ctx.reply(content, ephemeral=ephemeral)
        else:
            await ctx.reply(content)
    
    async def cog_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply("이 명령어를 사용하려면 `서버 관리` 권한이 필요합니다.")
            print(f"[Anniversary ERROR] MissingPermissions | {ctx.author} | {ctx.message.content}")
            return

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(f"필수 인자가 빠졌습니다: `{error.param.name}`")
            print(f"[Anniversary ERROR] MissingRequiredArgument | {error}")
            return

        if isinstance(error, commands.BadArgument):
            await ctx.reply("인자 형식이 잘못되었습니다. 유저/채널 멘션, 날짜 형식을 확인해주세요.")
            print(f"[Anniversary ERROR] BadArgument | {error}")
            return

        await ctx.reply(f"명령어 오류가 발생했습니다: `{type(error).__name__}`")
        print(f"[Anniversary ERROR] {type(error).__name__} | {repr(error)}")

    @tasks.loop(time=MIDNIGHT_KST)
    async def daily_anniversary_check(self):
        today = datetime.now(KST).date()
        sent_on = today.isoformat()

        events = fetch_today_events(today)

        for event in events:
            if was_sent_today(event["id"], sent_on):
                continue

            try:
                channel = self.bot.get_channel(event["channel_id"])

                if channel is None:
                    channel = await self.bot.fetch_channel(event["channel_id"])

                message = build_message(event, today)
                await channel.send(message)

                mark_sent(event["id"], sent_on)

            except discord.Forbidden:
                print(f"[Anniversary] 채널 권한 없음: channel_id={event['channel_id']}")
            except discord.NotFound:
                print(f"[Anniversary] 채널을 찾을 수 없음: channel_id={event['channel_id']}")
            except Exception as e:
                print(f"[Anniversary] 알림 전송 실패: {e}")

    @daily_anniversary_check.before_loop
    async def before_daily_anniversary_check(self):
        await self.bot.wait_until_ready()

    # 생일 등록 [id: 24]
    @commands.hybrid_command(
        name="생일추가",
        aliases=["bday_add", "birthday_add", "생일등록"],
        description="생일 알림을 등록합니다."
    )
    @commands.has_permissions(manage_guild=True)
    async def birthday_add(
        self,
        ctx: commands.Context,
        user_text: str,
        month: int,
        day: int,
        channel_text: str,
        calendar_type: str = "양력",
        is_leap_month: str = "false",
    ):
        if ctx.guild is None:
            await self.send_reply(
                ctx,
                "서버 안에서만 사용할 수 있는 명령어입니다.",
                ephemeral=True,
            )
            return

        try:
            user = await resolve_member_or_user(ctx, user_text)
            channel = await resolve_text_channel(ctx, channel_text)
            db_calendar_type = parse_calendar_type_text(calendar_type)
            leap_bool = parse_bool_text(is_leap_month)

        except ValueError as e:
            await self.send_reply(
                ctx,
                str(e),
                ephemeral=True,
            )
            return

        except discord.NotFound:
            await self.send_reply(
                ctx,
                "유저 또는 채널을 찾을 수 없습니다. 멘션/ID를 확인해주세요.",
                ephemeral=True,
            )
            return

        except discord.Forbidden:
            await self.send_reply(
                ctx,
                "봇이 유저 또는 채널 정보를 가져올 권한이 없습니다.",
                ephemeral=True,
            )
            return

        if db_calendar_type == "solar":
            leap_bool = False

            if not validate_solar_month_day(month, day):
                await self.send_reply(
                    ctx,
                    "날짜가 이상합니다. 예: 7월 2일",
                    ephemeral=True,
                )
                return

        else:
            if not (1 <= month <= 12 and 1 <= day <= 30):
                await self.send_reply(
                    ctx,
                    "음력 날짜가 이상합니다. 음력은 보통 1~12월, 1~30일 범위로 입력해주세요.",
                    ephemeral=True,
                )
                return

        with get_conn() as conn:
            conn.execute(
                """
                INSERT INTO anniversary_events (
                    guild_id, channel_id, kind, calendar_type,
                    month, day, is_leap_month, user_id
                )
                VALUES (?, ?, 'birthday', ?, ?, ?, ?, ?)
                """,
                (
                    ctx.guild.id,
                    channel.id,
                    db_calendar_type,
                    month,
                    day,
                    int(leap_bool),
                    user.id,
                ),
            )

        calendar_type_kor = "음력" if db_calendar_type == "lunar" else "양력"
        leap_text = " 윤달" if leap_bool and db_calendar_type == "lunar" else ""

        await self.send_reply(
            ctx,
            f"{user.mention} 생일을 등록했습니다.\n"
            f"- 날짜: {calendar_type_kor}{leap_text} {month}월 {day}일\n"
            f"- 알림 채널: {channel.mention}",
            ephemeral=True,
        )

    # 기념일 등록 [id: 25]
    @commands.hybrid_command(
        name="기념일추가",
        aliases=["anniv_add", "anniversary_add", "기념일등록"],
        description="기념일 알림을 등록합니다."
    )
    @commands.has_permissions(manage_guild=True)
    async def anniv_add(
        self,
        ctx: commands.Context,
        title: str,
        year: int,
        month: int,
        day: int,
        channel_text: str,
        calendar_type: str = "양력",
        is_leap_month: str = "false",
    ):
        if ctx.guild is None:
            await self.send_reply(
                ctx,
                "서버 안에서만 사용할 수 있는 명령어입니다.",
                ephemeral=True,
            )
            return

        try:
            channel = await resolve_text_channel(ctx, channel_text)
            db_calendar_type = parse_calendar_type_text(calendar_type)
            leap_bool = parse_bool_text(is_leap_month)

        except ValueError as e:
            await self.send_reply(
                ctx,
                str(e),
                ephemeral=True,
            )
            return

        except discord.NotFound:
            await self.send_reply(
                ctx,
                "채널을 찾을 수 없습니다. 채널 ID를 확인해주세요.",
                ephemeral=True,
            )
            return

        except discord.Forbidden:
            await self.send_reply(
                ctx,
                "봇이 해당 채널 정보를 가져올 권한이 없습니다.",
                ephemeral=True,
            )
            return

        if db_calendar_type == "solar":
            leap_bool = False

        if not validate_anniversary_date(
            db_calendar_type,
            year,
            month,
            day,
            leap_bool,
        ):
            await self.send_reply(
                ctx,
                "날짜가 이상하거나 음력 변환 범위를 벗어났습니다.",
                ephemeral=True,
            )
            return

        with get_conn() as conn:
            conn.execute(
                """
                INSERT INTO anniversary_events (
                    guild_id, channel_id, kind, calendar_type,
                    year, month, day, is_leap_month, title
                )
                VALUES (?, ?, 'anniversary', ?, ?, ?, ?, ?, ?)
                """,
                (
                    ctx.guild.id,
                    channel.id,
                    db_calendar_type,
                    year,
                    month,
                    day,
                    int(leap_bool),
                    title,
                ),
            )

        calendar_type_kor = "음력" if db_calendar_type == "lunar" else "양력"
        leap_text = " 윤달" if leap_bool and db_calendar_type == "lunar" else ""

        await self.send_reply(
            ctx,
            f"기념일을 등록했습니다.\n"
            f"- 이름: {title}\n"
            f"- 날짜: {calendar_type_kor}{leap_text} {year}년 {month}월 {day}일\n"
            f"- 알림 채널: {channel.mention}",
            ephemeral=True,
        )

    # 생일 및 기념일 목록 [id: 26]
    @commands.hybrid_command(
        name="기념일목록",
        aliases=["anniv_list", "anniversary_list", "생일목록"],
        description="등록된 생일/기념일 목록을 확인합니다."
    )
    @commands.has_permissions(manage_guild=True)
    async def anniv_list(self, ctx: commands.Context):
        if ctx.guild is None:
            await self.send_reply(
                ctx,
                "서버 안에서만 사용할 수 있는 명령어입니다.",
                ephemeral=True,
            )
            return

        with get_conn() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM anniversary_events
                WHERE guild_id = ?
                  AND enabled = 1
                ORDER BY month, day, kind, id
                """,
                (ctx.guild.id,),
            ).fetchall()

        if not rows:
            await self.send_reply(
                ctx,
                "등록된 생일/기념일이 없습니다.",
                ephemeral=True,
            )
            return

        lines = []

        for row in rows[:30]:
            calendar_name = "음력" if row["calendar_type"] == "lunar" else "양력"
            leap_text = " 윤달" if row["is_leap_month"] else ""
            channel_text = f"<#{row['channel_id']}>"

            if row["kind"] == "birthday":
                lines.append(
                    f"`{row['id']}` 🎂 {calendar_name}{leap_text} "
                    f"{row['month']}월 {row['day']}일 | <@{row['user_id']}> | {channel_text}"
                )
            else:
                lines.append(
                    f"`{row['id']}` 📌 {calendar_name}{leap_text} "
                    f"{row['year']}년 {row['month']}월 {row['day']}일 | "
                    f"{row['title']} | {channel_text}"
                )

        if len(rows) > 30:
            lines.append(f"...외 {len(rows) - 30}개 더 있음")

        await self.send_reply(
            ctx,
            "\n".join(lines),
            ephemeral=True,
        )

    # 생일 및 기념일 삭제 [id: 27]
    @commands.hybrid_command(
        name="기념일삭제",
        aliases=["anniv_del", "anniv_delete", "anniversary_delete", "생일삭제"],
        description="등록된 생일/기념일을 삭제합니다."
    )
    @commands.has_permissions(manage_guild=True)
    async def anniv_delete(
        self,
        ctx: commands.Context,
        event_id: int,
    ):
        if ctx.guild is None:
            await self.send_reply(
                ctx,
                "서버 안에서만 사용할 수 있는 명령어입니다.",
                ephemeral=True,
            )
            return

        with get_conn() as conn:
            cur = conn.execute(
                """
                UPDATE anniversary_events
                SET enabled = 0
                WHERE guild_id = ?
                  AND id = ?
                """,
                (ctx.guild.id, event_id),
            )

        if cur.rowcount == 0:
            await self.send_reply(
                ctx,
                "해당 ID의 생일/기념일을 찾지 못했습니다.",
                ephemeral=True,
            )
            return

        await self.send_reply(
            ctx,
            f"`{event_id}` 항목을 삭제했습니다.",
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Anniversary(bot))
