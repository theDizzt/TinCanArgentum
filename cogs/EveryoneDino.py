import discord
from discord.ext import commands
from discord import app_commands
import fcts.sqlcontrol as q
import fcts.etcfunctions as etc
import fcts.i18n_runtime as i18n
from fcts.user_resolver import UserResolutionError, resolve_discord_user
import fcts.drawing as dr
from project_paths import DATA_DIR, FONT_DIR, RANKCARD_DIR
import fcts.koreanbreak as kb
from fcts.line_chat import read_line_export
import random as r
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import io
import asyncio
import hashlib

#SERVER id
server_id = [
    262525769023094785, 716980478992711720, 1114816224522678294,
    453906917719408642, 348750582200270848
]

GOAT_TITLE_MAX_LENGTH = 120

LINE_USERS = {
    "민규": 262520957233528832,
    "충환": 262517377575550977,
    "주원": 262899129276039169,
    "대헌": 263595595019583489,
    "동건": 262528817942364160,
    "태형": 262524430058520577,
    "민성": 236100097656487946,
    "태균": 263273764312186881,
    "성훈": 264763838673453056,
    "영준": 370800841055272972,
    "승교": 394075013541789700,
    "선우": 263640824170938369,
    "승현": 262551155815481345,
    "민찬": 512098892674760705,
}


def fit_font(draw, text, font_path, max_size, min_size, max_width):
    """Return the largest font that keeps a single line inside max_width."""
    for size in range(max_size, min_size - 1, -1):
        font = ImageFont.truetype(font_path, size)
        if draw.textlength(str(text), font=font) <= max_width:
            return font
    return ImageFont.truetype(font_path, min_size)


class EveryoneDino(commands.Cog):  # Cog를 상속하는 클래스를 선언

    def __init__(self, client: commands.Bot):  # 생성자 작성
        self.client = client
        self.image_semaphore = asyncio.Semaphore(2)

    # [id: 30] 오늘의 인물 카드 제작
    async def goat_image(self, *, user: discord.Member, title: str) -> io.BytesIO:
        # 이름
        dname = "@" + str(user)
        if dname.endswith("#0"):
            dname = dname[:-2]

        try:
            name = q.readTag(user)
        except (IndexError, TypeError):
            # DB 가입 전인 멤버도 카드에 표시할 수 있게 Discord 표시명을 사용한다.
            name = user.display_name
        
        # 배경 이미지 불러오기
        background_image = Image.open(
            RANKCARD_DIR / "goat.png"
        ).convert('RGBA')

        mask_image = Image.open(
            RANKCARD_DIR / "goat_mask.png"
        ).convert('RGBA')

        image = background_image.copy()
        draw = ImageDraw.Draw(image)

        # 현재시간
        now = datetime.now() + timedelta(hours=9)
        now_time = now.strftime('%Y년 %m월 %d일 %H시 %M분 %S초')

        font_name_path = FONT_DIR / "emblem.ttf"
        font_title_path = FONT_DIR / "slay" / "name.ttf"
        font_name = fit_font(draw, name, font_name_path, 22, 8, 236)
        font_date = ImageFont.truetype(FONT_DIR / "slay" / "name.ttf", 14)
        font_display = fit_font(draw, dname, font_title_path, 14, 8, 236)
        font_title = ImageFont.truetype(font_title_path, 20)

        x1 = (256 - draw.textlength(name, font=font_name)) / 2
        y1 = 208

        x2 = (256 - draw.textlength(dname, font=font_display)) / 2
        y2 = 240

        x3 = (256 - draw.textlength(now_time, font=font_date)) / 2
        y3 = 260

        y4 = 284

        draw.text(
            (x1, y1), str(name),
            fill=(255, 255, 255, 255),
            font=font_name,
            stroke_width=2,
            stroke_fill=(46, 139, 255, 255)
        )

        draw.text(
            (x2, y2), str(dname),
            fill=(204, 204, 204, 255),
            font=font_display,
            stroke_width=2,
            stroke_fill=(46, 139, 255, 255)
        )

        draw.text(
            (x3, y3), str(now_time),
            fill=(255, 255, 255, 255),
            font=font_date,
            stroke_width=2,
            stroke_fill=(46, 139, 255, 255)
        )

        # 제목 영역(하단 84px)에 들어갈 때까지 글꼴 크기를 자동으로 줄인다.
        for size in range(20, 7, -1):
            candidate_font = ImageFont.truetype(font_title_path, size)
            font_title = candidate_font
            title_lines = dr.wrap_text(draw, str(title), candidate_font, 236)
            if len(title_lines) * (size + 4) <= 84:
                break

        dr.draw_multiline_text_center(
            draw=draw,
            text=str(title),
            font=font_title,
            start_y=y4,
            max_width=236,
            canvas_width=256
        )

        try:
            avatar_asset = user.display_avatar
            buffer_avatar = io.BytesIO()
            await avatar_asset.save(buffer_avatar)
            buffer_avatar.seek(0)
            avatar_image = Image.open(buffer_avatar).convert('RGBA')

        except Exception:
            avatar_image = Image.open(
                RANKCARD_DIR / "noimage.jpg"
            ).convert('RGBA')

        # 디스코드 프로필 사진 붙이기
        avatar_image = avatar_image.resize((96, 96), Image.Resampling.LANCZOS)
        image.paste(avatar_image, (80, 100), mask=mask_image)

        buffer_output = io.BytesIO()
        image.save(buffer_output, format='PNG')
        buffer_output.seek(0)
        return buffer_output

    async def is_server(ctx):
        return ctx.guild is not None and ctx.guild.id in server_id
    
    # GOAT [ID: 30]
    @commands.hybrid_command(
        name=app_commands.locale_str("goat", key="cmd.30.name"),
        description=app_commands.locale_str(
            "Celebrate the friend who made the biggest impact today",
            key="cmd.30.desc"
        ),
        aliases=["똥딸", "똥딸놈", "스카웃", "똥딸년", "똥잠바", "더러운똥딸년"]
    )
    @commands.check(is_server)
    async def goat(self, ctx, user: str = None, *, title: str = "똥딸"):
        try:
            user = await resolve_discord_user(ctx, user)
        except UserResolutionError:
            await ctx.reply(i18n.t(ctx.author, "common.invalid_user"))
            return

        title = title.strip() or "똥딸"
        if len(title) > GOAT_TITLE_MAX_LENGTH:
            await ctx.reply(i18n.t(
                ctx.author,
                "cmd.30.title_too_long",
                max_length=GOAT_TITLE_MAX_LENGTH
            ))
            return

        async with self.image_semaphore:
            buffer_output = await self.goat_image(user=user, title=title)
        try:
            await ctx.reply(
                i18n.t(ctx.author, "cmd.30.result", user_id=user.id),
                file=discord.File(buffer_output, 'myimage.png')
            )
        finally:
            buffer_output.close()

        try:
            q.ensureStorage(user)
            if q.readStorage(user, 161) == 0:
                q.storageModify(user, 161, 1)
        except Exception as storage_error:
            # 업적 기록 실패가 이미 생성된 명령 결과까지 실패시키지 않게 한다.
            print(f"[EveryoneDino.goat] storage update failed: {storage_error}")
    
    @goat.error
    async def goat_error(self, ctx, error):
        original = getattr(error, "original", error)

        if isinstance(error, commands.CheckFailure) or isinstance(
            original, commands.CheckFailure
        ):
            await ctx.reply(i18n.t(ctx.author, "common.server_only", server="전체공룡"))
        elif isinstance(error, commands.BadArgument) or isinstance(
            original, commands.BadArgument
        ):
            await ctx.reply(i18n.t(ctx.author, "common.invalid_user"))
        else:
            print(f"[EveryoneDino.goat] {type(original).__name__}: {original}")
            await ctx.reply(i18n.t(ctx.author, "cmd.30.error"))

    # 쿠모티콘! [ID: 32]
    @commands.hybrid_command(name='쿠모티콘', description="헬창냥이 김종국의 사진 대방출!")
    #@discord.app_commands.describe(type="옵션을 적어주세요")
    @commands.check(is_server)
    async def coomoji(self, ctx, type="도움"):
        if type == "도움":
            embed = discord.Embed(title="**도움말 입니당!**",
                                  description="",
                                  color=0xFFFF72)
            embed.add_field(
                name="가능한 명령어",
                value="쿠건달, 쿠기만, 쿠긴장, 쿠깡패, 쿠맥심, 쿠무룩, 쿠부릅, 쿠빼꼼, 쿠심심, 쿠일진, 쿠행복",
                inline=False)
            embed.set_thumbnail(
                url=
                "https://cdn.discordapp.com/attachments/526648786605441024/794085625862815754/cookiezleicon.png"
            )
            embed.set_footer(text="Provided by Dizzt", icon_url="")
            await ctx.reply(embed=embed)

        elif type == "쿠건달":
            await ctx.reply(
                "https://media.discordapp.net/attachments/526648786605441024/794077934390083604/1a47a584e7cbc3af.png?width=503&height=670"
            )

        elif type == "쿠긴장":
            await ctx.reply(
                "https://media.discordapp.net/attachments/526648786605441024/794077941667069952/a0f18b3d96227739.png?width=503&height=671"
            )

        elif type == "쿠깡패":
            await ctx.reply(
                "https://media.discordapp.net/attachments/526648786605441024/794077975956029440/b1de0b86664f6e2c.png?width=321&height=428"
            )

        elif type == "쿠맥심":
            await ctx.reply(
                "https://media.discordapp.net/attachments/526648786605441024/794077954456027156/f103ae7abbea7956.png?width=321&height=428"
            )

        elif type == "쿠무룩":
            await ctx.reply(
                "https://media.discordapp.net/attachments/526648786605441024/794077963594760242/c672207f61093215.png?width=321&height=428"
            )

        elif type == "쿠부릅":
            await ctx.reply(
                "https://media.discordapp.net/attachments/526648786605441024/794077943303372800/03d4fcaa7b16e455.png?width=321&height=428"
            )

        elif type == "쿠기만":
            await ctx.reply(
                "https://media.discordapp.net/attachments/526648786605441024/794077941508210708/89550f529dd8aba5.png?width=571&height=428"
            )

        elif type == "쿠빼꼼":
            await ctx.reply(
                "https://media.discordapp.net/attachments/526648786605441024/794077983555584000/1f857131eec553d5.png?width=321&height=428"
            )

        elif type == "쿠심심":
            await ctx.reply(
                "https://media.discordapp.net/attachments/526648786605441024/794077996923093022/29bced3311e422a7.png?width=571&height=428"
            )

        elif type == "쿠일진":
            await ctx.reply(
                "https://media.discordapp.net/attachments/526648786605441024/794078005093335100/00cb58bc92c494e2.png?width=321&height=428"
            )

        elif type == "쿠행복":
            await ctx.reply(
                "https://media.discordapp.net/attachments/526648786605441024/794078015310135326/087b38d4b6ed72e0.png?width=321&height=428"
            )

        elif type == "쿠적발":
            await ctx.reply(
                "https://media.discordapp.net/attachments/689051304953512004/1286697283139797085/b054b0851b0e96f7.png"
            )

        elif type == "쿠최후":
            await ctx.reply(
                "https://media.discordapp.net/attachments/689051304953512004/1286697288160514112/e11b12ebc9a2ab3c.png"
            )

        elif type == "쿠씨애":
            await ctx.reply(
                "https://media.discordapp.net/attachments/689051304953512004/1286697269848047666/a678fc906f93a33d.png"
            )

    @coomoji.error
    async def coomoji_error(self, ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.reply(i18n.t(ctx.author, "common.server_only", server="전체공룡"))

    # 카카오 데이터 관리 [ID: 98]
    @commands.command(name='카톡', aliases=['라인', 'line'], description="...")
    @commands.check(is_server)
    async def kakao(self,
                    ctx,
                    option: str = None,
                    user: str = None,
                    value: int = 0):
        kakao = dict(
            봇=691455977270149171,
            민규=262520957233528832,
            충환=262517377575550977,
            주원=262899129276039169,
            대헌=263595595019583489,
            동건=262528817942364160,
            태형=262524430058520577,
            민성=236100097656487946,
            태균=263273764312186881,
            성훈=264763838673453056,
            영준=370800841055272972,
            승교=394075013541789700,
            선우=263640824170938369,
            승현=262551155815481345,
            민찬=512098892674760705,
            우현=584613297643323392,
            동현=178695589788123136,
            창훈=316933512852930562,
            현수=333236160853704714,
            ㅅㅁ=320827061952315392,
            은비=279909142955687936,
            한비=280900407021010944,
            쿠키=791364491325210625,
            짱아=404498587461091328,
            예빈=332793142745104384,
            도희=310386513236066306,
            화랑=310379466578722816,
            상아=1115471474250240050,
            부계=889173206454386689,
            수향=310404488496283653,
            똥몬창=(544815696463396885, 487619829700886567, 277763741267918848,
                 503185794509438976, 422295213294354432, 429629511227670528,
                 811193433423216650, 265388034415919104))

        if option in {"경험치", "돈"}:
            try:
                target = kakao.get(user)
                if target is None:
                    target = etc.extractUid(user)
            except ValueError:
                await ctx.reply(i18n.t(ctx.author, "common.invalid_user"))
                return

            targets = target if isinstance(target, tuple) else (target,)
            for u in targets:
                if option == "경험치":
                    q.xpAddById(u, value)
                    xp = q.readXpById(u)
                    lv = etc.level(xp)
                    xp1 = xp - etc.need_exp(lv - 1)
                    xp2 = etc.need_exp(lv) - etc.need_exp(lv - 1)
                    text = "[Level] {}, [XP] {:,d} / {:,d} ({:.2f}%), [Total] {:,d}".format(
                        lv, xp1, xp2, 100 * xp1 / xp2, xp)
                    await ctx.reply(
                        "`⸜(*◉ ᴗ ◉)⸝` **{}**에게 **{}**의 경험치를 주었습니다!\n`변경 후` {}".
                        format(q.readTagById(u), value, text))
                else:
                    q.moneyAddById(u, value)
                    mn = q.readMoneyById(u)
                    await ctx.reply(
                        f"`⸜(*◉ ᴗ ◉)⸝` **{q.readTagById(u)}**에게 **${value:,d}**의 돈을 주었습니다!\n현재 소지금액은 **${mn:,d}** 입니다!"
                    )

        elif option == "출석":
            data = [
                691455977270149171,
                262520957233528832,
                262517377575550977,
                262899129276039169,
                263595595019583489,
                262528817942364160,
                262524430058520577,
                236100097656487946,
                263273764312186881,
                264763838673453056,
                370800841055272972,
                394075013541789700,
                263640824170938369,
                262551155815481345,
                512098892674760705,
                279909142955687936,
                280900407021010944,
                310386513236066306,
                310379466578722816,
                332793142745104384,
                584613297643323392,
                178695589788123136,
                316933512852930562,
                333236160853704714,
                320827061952315392,
                1115471474250240050,
                889173206454386689,
                310404488496283653,
                544815696463396885,
                487619829700886567,
                277763741267918848,
                503185794509438976,
                422295213294354432,
                429629511227670528,
                811193433423216650,
                265388034415919104,
                341943143098482689,
                307366878551080975,
                387218121250832385,
                791364491325210625,
                404498587461091328
            ]

            result = ""

            now = datetime.now()
            today = now.strftime('%Y-%m-%d')

            for u in data:

                if q.readDailyDateById(u) == today and not(user == "1"):
                    result += f"**`{q.readTagById(u)}`**Already done!**\n"
                
                else:
                    daily = q.readDailyById(u) + 1
                    xp = 0
                    money = 0

                    if daily < 511:
                        xp = 250 * (1 + (daily // 7)) + int(daily ** 1.6) - 1
                        money = 100 * (1 + (daily // 7)) + int(daily ** 1.5) - 1
                    else:
                        xp = 40000
                        money = 20000
                    
                    q.xpAddById(u, xp)
                    q.moneyAddById(u, money)
                    q.dailyAddById(u)
                    q.dailyDateModifyById(u, today)

                    result += f"`{q.readTagById(u)}` | Day {daily} | +{xp}xp +${money}\n"

            await ctx.reply(result)

        elif option == "개인출석":
            u = kakao[user]
            t_xp = 0
            t_money = 0

            if value > 0:
                for i in range(value):

                    daily = q.readDailyById(u) + 1
                    xp = 0
                    money = 0

                    if daily < 511:
                        xp = 250 * (1 + (daily // 7)) + int(daily ** 1.6) - 1
                        money = 100 * (1 + (daily // 7)) + int(daily ** 1.5) - 1
                    else:
                        xp = 40000
                        money = 20000

                    t_xp += xp
                    t_money += money
                        
                    q.xpAddById(u, xp)
                    q.moneyAddById(u, money)
                    q.dailyAddById(u)

                q.dailyDateModifyById(u, today)

            result = f"`{q.readTagById(u)}` | Day {q.readDailyById(u)} | +{t_xp}xp +${t_money}"

            await ctx.reply(result)

    @kakao.error
    async def kakao_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.reply(i18n.t(ctx.author, "common.server_only", server="전체공룡"))

    # 카카오데이터 [id: 10]
    @commands.command(name='kakaodata', description="...")
    @commands.check(is_server)
    async def kakaodata(self, ctx):

        kakao = dict(
            민규=262520957233528832,
            충환=262517377575550977,
            주원=262899129276039169,
            대헌=263595595019583489,
            동건=262528817942364160,
            태형=262524430058520577,
            민성=236100097656487946,
            태균=263273764312186881,
            성훈=264763838673453056,
            영준=370800841055272972,
            승교=394075013541789700,
            선우=263640824170938369,
            승현=262551155815481345,
            민찬=512098892674760705
            )
        
        path = DATA_DIR / "kakao"
        temp = dict()
        filelist = []

        datalist = path.iterdir()

        for file_path in datalist:
            if not file_path.is_file():
                continue
            with file_path.open(encoding="UTF8") as file:
                filelist += file.readlines()
            file_path.unlink()
        
        for data in filelist:
            try:
                trim = data.replace("[", "")
                trim = trim.replace("\n", "")
                line = trim.split("] ")
                count = kb.count_break_korean(line[2])
                xp_gain = int((count * 0.3) * 4.6 + 1)
                money_gain = r.randint(5, 15)
                
                if line[0] in temp:
                    temp[line[0]][0] += xp_gain
                    temp[line[0]][1] += money_gain
                else:
                    temp[line[0]] = [xp_gain, money_gain]
                
            except:
                pass

        result = ""
        for user in temp.keys():
            q.xpAddById(kakao[user], temp[user][0])
            q.moneyAddById(kakao[user], temp[user][1])
            result += f"**`{q.readTagById(kakao[user])}`** | +{temp[user][0]}xp +${temp[user][1]}\n"
        
        await ctx.reply(result)

        
    @kakaodata.error
    async def kakaodata_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.reply(i18n.t(ctx.author, "common.server_only", server="전체공룡"))

    # LINE 데이터 정산 [ID: 98]
    @commands.command(name="linedata", aliases=["라인데이터"], description="...")
    @commands.check(is_server)
    async def linedata(self, ctx):
        source_dir = DATA_DIR / "line"
        processed_dir = source_dir / "processed"
        source_dir.mkdir(parents=True, exist_ok=True)

        source_files = sorted(
            path for path in source_dir.glob("*.txt") if path.is_file()
        )
        if not source_files:
            await ctx.reply(
                "No LINE export files were found. Place UTF-8 `.txt` files in "
                f"`{source_dir}` and try again."
            )
            return

        rewards_by_name = {}
        unknown_names = {}
        parsed_count = 0
        try:
            for source_file in source_files:
                messages = read_line_export(source_file)
                parsed_count += len(messages)
                for message in messages:
                    user_id = LINE_USERS.get(message.name)
                    if user_id is None:
                        unknown_names[message.name] = (
                            unknown_names.get(message.name, 0) + 1
                        )
                        continue

                    count = kb.count_break_korean(message.content)
                    xp_gain = int((count * 0.3) * 4.6 + 1)
                    money_gain = r.randint(5, 15)
                    reward = rewards_by_name.setdefault(
                        message.name,
                        {"id": user_id, "xp": 0, "money": 0, "messages": 0},
                    )
                    reward["xp"] += xp_gain
                    reward["money"] += money_gain
                    reward["messages"] += 1
        except (OSError, UnicodeError) as error:
            await ctx.reply(f"The LINE export could not be read: `{error}`")
            return

        if not rewards_by_name:
            await ctx.reply(
                "No rewardable LINE messages were found. "
                "Expected format: `00:00 이름 내용`."
            )
            return

        rewards = {
            reward["id"]: (reward["xp"], reward["money"])
            for reward in rewards_by_name.values()
        }
        try:
            import_keys = [
                "line:" + hashlib.sha256(source_file.read_bytes()).hexdigest()
                for source_file in source_files
            ]
            q.rewardsAddBulk(rewards, import_keys=import_keys)
        except (ValueError, OSError) as error:
            await ctx.reply(f"No rewards were paid: `{error}`")
            return

        processed_dir.mkdir(parents=True, exist_ok=True)
        archive_stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        archived_count = 0
        for source_file in source_files:
            destination = processed_dir / source_file.name
            if destination.exists():
                destination = processed_dir / (
                    f"{source_file.stem}-{archive_stamp}{source_file.suffix}"
                )
            try:
                source_file.replace(destination)
                archived_count += 1
            except OSError:
                pass

        result_lines = [
            "**LINE data settlement complete**",
            (
                f"Parsed **{parsed_count:,}** messages from "
                f"**{len(source_files):,}** file(s)."
            ),
        ]
        for name, reward in rewards_by_name.items():
            result_lines.append(
                f"**`{q.readTagById(reward['id'])}`** | "
                f"{reward['messages']:,} messages | "
                f"+{reward['xp']:,}xp +${reward['money']:,}"
            )
        if unknown_names:
            unknown_total = sum(unknown_names.values())
            result_lines.append(
                f"Skipped **{unknown_total:,}** message(s) from unmapped names: "
                + ", ".join(sorted(unknown_names))
            )
        result_lines.append(
            f"Archived **{archived_count}/{len(source_files)}** processed file(s)."
        )
        await ctx.reply("\n".join(result_lines))

    @linedata.error
    async def linedata_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.reply(
                i18n.t(ctx.author, "common.server_only", server="전체공룡")
            )
        else:
            raise error


async def setup(client):
    await client.add_cog(EveryoneDino(client))
