import discord
import asyncio
from discord.ext import commands
from discord import app_commands
import fcts.i18n_runtime as i18n
import fcts.sqlcontrol as q
import fcts.leaderboard as l
import fcts.lklab as lk
import fcts.plab as plab
import fcts.skin_catalog as catalog
from fcts.user_resolver import UserResolutionError, resolve_user_id
import yaml
import fcts.etcfunctions as etc
from project_paths import CONFIG_DIR
import random as r

admin_login = []
with (CONFIG_DIR / "admin.yml").open(encoding="UTF-8") as f:
    admins = yaml.load(f, Loader=yaml.FullLoader)


class Admins(commands.Cog):  # Cog를 상속하는 클래스를 선언

    def __init__(self, client: commands.Bot):  # 생성자 작성
        self.client = client

    async def wait_for_admin_input(self, ctx):
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        try:
            return await self.client.wait_for(
                "message",
                check=check,
                timeout=300,
            )
        except asyncio.TimeoutError:
            await ctx.reply(i18n.t(ctx.author, "cmd.admin.cancel"))
            return None

    # PLab Edit [ID: 28]
    @commands.command(name="pledit")
    async def pledit(
        self,
        ctx,
        user: str = None,
        option: str = None,
        value: str = None,
    ):
        """Administrative PLab editor: pledit <user> <option> <value>."""
        if ctx.author.id not in admin_login:
            await ctx.reply("You must log in with the `login` command first.")
            return

        if str(user or "").strip().casefold() == "recalc":
            try:
                updated_users = plab.recalculateAll()
            except (OSError, ValueError) as error:
                await ctx.reply(f"PLab scores could not be recalculated: `{error}`")
                return
            await ctx.reply(
                f":green_circle: Recalculated LAB points and skill levels for "
                f"**{updated_users:,}** user(s)."
            )
            return

        option = str(option or "").strip().casefold()
        if user is None or not option:
            await ctx.reply(
                "Usage: `;pledit <user> "
                "<create|unlock|lock|first|startdate|labpoint|labpointadd> "
                "<value>` or `;pledit recalc`"
            )
            return

        try:
            target_id = resolve_user_id(user)
            if option == "create":
                if plab.registerUser(target_id):
                    await ctx.reply(
                        f":green_circle: Created PLab data for user `{target_id}`."
                    )
                else:
                    await ctx.reply(
                        f"`(⩌ʌ ⩌;)` PLab data for user `{target_id}` already exists."
                    )
                return

            if value is None:
                await ctx.reply(
                    "Usage: `;pledit <user> "
                    "<unlock|lock|first|startdate|labpoint|labpointadd> <value>`"
                )
                return

            if option in {"unlock", "lock", "first"}:
                if ctx.guild is None:
                    await ctx.reply(
                        "Completion and first-clear records must be edited in a server."
                    )
                    return

                game_id = int(value)
                achievements = {
                    item["id"]: item
                    for item in plab.loadAchievements()
                }
                achievement = achievements.get(game_id)
                if achievement is None:
                    await ctx.reply(f"Game ID `{game_id}` does not exist.")
                    return

                if option == "first":
                    plab.setFirstClear(target_id, game_id, ctx.guild.id)
                    action = "Set as this server's first clearer"
                    first_user_id = target_id
                else:
                    completed = option == "unlock"
                    first_user_id = plab.setGameCompletion(
                        target_id,
                        game_id,
                        completed,
                        ctx.guild.id,
                    )
                    action = "Unlocked" if completed else "Locked"

                state = plab.getUserState(target_id)
                message = (
                    f":green_circle: {action} game `{game_id}` "
                    f"(**{achievement['name']}**) for user `{target_id}`.\n"
                    f"LAB Point: **{state['lab_point']:,}** | "
                    f"Skill Level: **{state['skill_level']:,}**"
                )
                if first_user_id is not None:
                    message += f"\nServer first clearer: `{first_user_id}`"
                await ctx.reply(message)
                return

            if not plab.userExists(target_id):
                await ctx.reply(
                    f"`(⩌ʌ ⩌;)` PLab data for user `{target_id}` does not exist. "
                    f"Run `;pledit {target_id} create` first."
                )
                return

            if option == "startdate":
                updated = plab.startDateModifyById(target_id, value)
            elif option == "labpoint":
                updated = plab.labPointModifyById(target_id, int(value))
            elif option == "labpointadd":
                updated = plab.labPointAddById(target_id, int(value))
            else:
                await ctx.reply(
                    "Unknown option. Available options: `create`, `startdate`, "
                    "`labpoint`, `labpointadd`, `unlock`, `lock`, `first`."
                )
                return

            if updated:
                await ctx.reply(
                    f":green_circle: Updated PLab data for user `{target_id}`."
                )
            else:
                await ctx.reply("The PLab data could not be updated.")
        except (UserResolutionError, TypeError, ValueError, OverflowError):
            await ctx.reply("Invalid user, option value, or date format.")

    # LKedit [ID: 86]
    @commands.command()
    async def lkedit(self,
                       ctx,
                       user: str = None,
                       option: str = None,
                       value: str = None,
                       svalue: str = None):
        if ctx.author.id in admin_login:

            u = int(etc.extractUid(user))

            if option == 'achievement':
                lk.achieveModifyById(u, int(value), int(svalue))
                await ctx.reply(i18n.t(ctx.author, "cmd.admin.accept"))

            elif option == 'startdate':
                lk.dateModifyById(u, str(value)+" "+str(svalue))
                await ctx.reply(i18n.t(ctx.author, "cmd.admin.accept"))

            elif option == 'create':
                lk.newAchieveById(u)
                await ctx.reply(i18n.t(ctx.author, "cmd.admin.accept"))

            else:
                await ctx.reply(i18n.t(ctx.author, "cmd.admin.reject"))

        else:
            await ctx.reply(i18n.t(ctx.author, "cmd.admin.reject"))


    # Admin Login [ID: 89]
    @commands.command(aliases=['로그인'])
    async def login(self, ctx, sid: str = None, spw: str = None):

        try:
            await ctx.message.delete()
        except:
            pass

        try:
            user = "UID" + str(ctx.author.id)

            if admins[user]['id'] == sid and admins[user]['pw'] == spw:
                global admin_login
                admin_login.append(ctx.author.id)
                await ctx.send(i18n.t(ctx.author, "cmd.89.accept", uid=ctx.author.id))
                print(admin_login)
            else:
                await ctx.send(i18n.t(ctx.author, "cmd.89.error", uid=ctx.author.id))

        except:
            await ctx.send(i18n.t(ctx.author, "cmd.89.reject", uid=ctx.author.id))

    # Admin Logout [ID: 90]
    @commands.command(aliases=['로그아웃'])
    async def logout(self, ctx):
        if ctx.author.id in admin_login:
            admin_login.remove(ctx.author.id)
            await ctx.send(i18n.t(ctx.author, "cmd.90.accept", uid=ctx.author.id))
            print(admin_login)

    # XP Editing [ID: 91]
    @commands.hybrid_command(
        name=app_commands.locale_str("xp", key="cmd.91.name"),
        description=app_commands.locale_str("Give XP to selected user", key="cmd.91.desc"),
        aliases=["경험치"]
    )
    async def xp(self, ctx, user:str="all", amount:int=0):
        if (user == "all" or user == "전체") and ctx.author.id in admin_login:
            q.xpAddAll(int(amount))
            await ctx.reply(i18n.t(ctx.author, "cmd.91.t001", val=amount))

        elif ctx.author.id in admin_login:
            u = int(etc.extractUid(user))
            q.xpAddById(u, int(amount))
            xp = q.readXpById(u)
            lv = etc.level(xp)
            xp1 = xp - etc.need_exp(lv - 1)
            xp2 = etc.need_exp(lv) - etc.need_exp(lv - 1)
            text = "[Level] {}, [XP] {:,d} / {:,d} ({:.2f}%), [Total] {:,d}".format(
                lv, xp1, xp2, 100 * xp1 / xp2, xp)
            await ctx.reply(i18n.t(ctx.author, "cmd.91.t002", u=q.readTagById(u), val=amount, pg=text))

    # User List [ID: 92]
    @commands.command(aliases=['유저목록'])
    async def userlist(self, ctx):
        if ctx.author.id in admin_login:
            rank = q.userList()
            await ctx.send(i18n.t(ctx.author, "cmd.92.t001"))
            await ctx.send(i18n.t(ctx.author, "cmd.92.t002", amount=len(rank)))
            for user in rank:
                await ctx.send(
                    "**{}**#{} ({}) | `{} / {}` | `Total : {:,d}`".format(
                        user[2],
                        str(user[1]).zfill(4), user[0], etc.level(user[3]),
                        etc.maxLevel(), user[3]))
            await ctx.send(i18n.t(ctx.author, "cmd.92.t003"))

    # Rank List [ID: 93]
    @commands.command(aliases=['랭킹목록'])
    async def rankinglist(self, ctx):
        if ctx.author.id in admin_login:
            rank = q.xpRanking()
            rank_value = 1
            await ctx.send(i18n.t(ctx.author, "cmd.93.t001"))

            for user in rank:
                await ctx.send(
                    "{} **{}**#{} | `{} / {}` | `Total : {:,d}`".format(
                        etc.numFont(rank_value), user[2],
                        str(user[1]).zfill(4), etc.level(user[3]),
                        etc.maxLevel(), user[3]))
                rank_value += 1

    # Rank Add up [ID: 80]
    @commands.command()
    async def rankingadd(self, ctx):
        if ctx.author.id in admin_login:
            rank = q.xpRanking()
            rank_value = 1
            xp = 100
            print(":green_circle: 랭킹 리스트를 출력합니다! (시간이 오래 걸릴수도 있습니다)")

            for user in rank:
                xp += r.randint(1,50)
                q.xpAddById(user[0], xp)
                print(
                    f"#{rank_value}. **{user[2]}**#{str(user[1]).zfill(4)} | `Total : {q.readXpById(user[0]):,d} (+{xp})`"
                )
                rank_value += 1

    # Leaderboard Edit [ID: 94]
    @commands.command(aliases=['리더보드편집'])
    async def lbedit(self, ctx, user: str = None, option: str = None):
        if ctx.author.id in admin_login:
            u = int(etc.extractUid(user))
            if option in ["mathgame", "사칙연산"]:
                await ctx.reply(i18n.t(ctx.author, "cmd.94.format.math"))

                input_word = await self.wait_for_admin_input(ctx)
                if input_word is None:
                    return
                check = input_word.content
                if check in ["cancel", "취소"]:
                    await ctx.reply(i18n.t(ctx.author, "cmd.admin.cancel"))
                else:
                    try:
                        result = check.split(",")
                        print(u, result)
                        l.mathDataForcedUpdate(u, int(result[0]),
                                               str(result[1]), int(result[2]),
                                               str(result[3]))
                        await ctx.reply(i18n.t(ctx.author, "cmd.admin.accept"))
                    except:
                        await ctx.reply(i18n.t(ctx.author, "cmd.admin.invalid"))

            elif option in ["rps", "가위바위보"]:
                await ctx.reply(i18n.t(ctx.author, "cmd.94.format.rps"))

                input_word = await self.wait_for_admin_input(ctx)
                if input_word is None:
                    return
                check = input_word.content
                if check in ["cancel", "취소"]:
                    await ctx.reply(i18n.t(ctx.author, "cmd.admin.cancel"))
                else:
                    try:
                        result = check.split(",")
                        print(u, result)
                        l.rpsDataForcedUpdate(u, int(result[0]),
                                              str(result[1]), int(result[2]),
                                              str(result[3]), int(result[4]),
                                              str(result[5]), int(result[6]),
                                              str(result[7]), int(result[8]),
                                              str(result[9]))
                        await ctx.reply(i18n.t(ctx.author, "cmd.admin.accept"))
                    except:
                        await ctx.reply(i18n.t(ctx.author, "cmd.admin.invalid"))

            elif option in ["wordchain", "끝말잇기"]:
                await ctx.reply(i18n.t(ctx.author, "cmd.94.format.wordchain"))

                input_word = await self.wait_for_admin_input(ctx)
                if input_word is None:
                    return
                check = input_word.content
                if check in ["cancel", "취소"]:
                    await ctx.reply(i18n.t(ctx.author, "cmd.admin.cancel"))
                else:
                    try:
                        result = check.split(",")
                        print(u, result)
                        l.wcForcedUpdate(u, int(result[0]), int(result[1]),
                                         int(result[2]), int(result[3]),
                                         int(result[4]), int(result[5]),
                                         int(result[6]), int(result[7]),
                                         int(result[8]))
                        await ctx.reply(i18n.t(ctx.author, "cmd.admin.accept"))
                    except:
                        await ctx.reply(i18n.t(ctx.author, "cmd.admin.invalid"))

            elif option in ["yahtzee", "야추다이스"]:
                await ctx.reply(i18n.t(ctx.author, "cmd.94.format.yahtzee"))

                input_word = await self.wait_for_admin_input(ctx)
                if input_word is None:
                    return
                check = input_word.content
                if check in ["cancel", "취소"]:
                    await ctx.reply(i18n.t(ctx.author, "cmd.admin.cancel"))
                else:
                    try:
                        result = check.split(",")
                        print(u, result)
                        l.ytForcedUpdate(u, int(result[0]), str(result[1]),
                                         int(result[2]), int(result[3]))
                        await ctx.reply(i18n.t(ctx.author, "cmd.admin.accept"))
                    except:
                        await ctx.reply(i18n.t(ctx.author, "cmd.admin.invalid"))

            else:
                await ctx.reply(i18n.t(ctx.author, "cmd.94.t001"))

    # Skin Unlock [ID: 95]
    @commands.hybrid_command(
        name=app_commands.locale_str("unlock", key="cmd.95.name"),
        description=app_commands.locale_str("Unlock user's skin", key="cmd.95.desc"),
        aliases=["잠금해제"]
    )
    @discord.app_commands.describe(user="User ID, mention, or nickname tag",
                                   skin="Integer only",
                                   lock="Binary only")
    async def unlock(self,
                     ctx,
                     user: str = None,
                     skin: int = None,
                     lock: int = 1):
        if ctx.author.id not in admin_login:
            await ctx.reply(i18n.t(ctx.author, "cmd.admin.reject"))
            return

        try:
            user_id = etc.extractUid(user)
            user_name = q.readTagById(user_id)
        except (TypeError, ValueError, IndexError):
            await ctx.reply(i18n.t(ctx.author, "common.invalid_user"))
            return

        if lock not in (0, 1) or skin is None:
            await ctx.reply(i18n.t(ctx.author, "cmd.95.t005"))
            return

        skin_data = next(
            (
                item
                for item in catalog.load_storage()
                if int(item["id"]) == skin
            ),
            None,
        )
        if skin_data is None:
            await ctx.reply(i18n.t(ctx.author, "cmd.95.t005"))
            return

        q.ensureStorageById(user_id)
        is_unlocked = bool(q.readStorageById(user_id, skin))
        skin_label = skin_data["id"]

        if lock == 1:
            if not is_unlocked:
                q.storageModifyById(user_id, skin, 1)
                key = "cmd.95.t001"
            else:
                key = "cmd.95.t002"
        elif is_unlocked:
            q.storageModifyById(user_id, skin, 0)
            key = "cmd.95.t003"
        else:
            key = "cmd.95.t004"

        await ctx.reply(
            i18n.t(ctx.author, key, u=user_name, skin=skin_label)
        )

    # Ultimate [ID: 96]
    @commands.command(aliases=["유저편집"])
    async def ultimate(self,
                       ctx,
                       user: str = None,
                       option: str = None,
                       value: str = None):
        if ctx.author.id in admin_login:

            u = int(etc.extractUid(user))

            if option in ['xp', '경험치']:
                q.xpModifyById(u, int(value))
                await ctx.reply(i18n.t(ctx.author, "cmd.admin.accept"))

            elif option in ['money', '돈']:
                q.moneyModifyById(u, int(value))
                await ctx.reply(i18n.t(ctx.author, "cmd.admin.accept"))

            elif option in ['skin', '스킨']:
                q.skinModifyById(u, int(value))
                await ctx.reply(i18n.t(ctx.author, "cmd.admin.accept"))

            elif option in ['discrim', '식별번호']:
                q.discrimModifyById(u, int(value))
                await ctx.reply(i18n.t(ctx.author, "cmd.admin.accept"))

            elif option in ['nick', '별명']:
                q.nickModifyById(u, str(value))
                await ctx.reply(i18n.t(ctx.author, "cmd.admin.accept"))

            elif option in ['startdate', '가입날짜']:
                q.startDateModifyById(u, str(value))
                await ctx.reply(i18n.t(ctx.author, "cmd.admin.accept"))

            elif option in ['create', '생성']:
                q.newAccountById(u, str(value))
                await ctx.reply(i18n.t(ctx.author, "cmd.admin.accept"))
                
            elif option in ['storage', '저장소']:
                q.newStorageById(u)
                await ctx.reply(i18n.t(ctx.author, "cmd.admin.accept"))
                
            elif option in ['daily', '출석']:
                q.dailyModifyById(u, str(value))
                await ctx.reply(i18n.t(ctx.author, "cmd.admin.accept"))

            else:
                await ctx.reply(i18n.t(ctx.author, "cmd.admin.reject"))

        else:
            await ctx.reply(i18n.t(ctx.author, "cmd.admin.reject"))

    # Money Editing [ID: 97]
    @commands.hybrid_command(
        name=app_commands.locale_str("money", key="cmd.97.name"),
        description=app_commands.locale_str("Give money to selected user", key="cmd.97.desc"),
        aliases=["돈"]
    )
    async def money(self, ctx, user:str="all", amount:int=0):
        if (user == "all" or user == "전체") and ctx.author.id in admin_login:
            q.moneyAddAll(amount)
            await ctx.reply(i18n.t(ctx.author, "cmd.97.t001", val=amount))

        elif ctx.author.id in admin_login:
            u = int(etc.extractUid(user))
            q.moneyAddById(u, amount)
            mn = q.readMoneyById(u)
            await ctx.reply(i18n.t(ctx.author, "cmd.97.t002", u=q.readTagById(u),val=amount, pg=mn))

async def setup(client):  # setup 함수로 cog를 추가한다.
    await client.add_cog(Admins(client))
