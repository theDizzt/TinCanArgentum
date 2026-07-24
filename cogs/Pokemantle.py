import discord
from discord.ext import commands
from games.pokemantle_engine import PokemantleEngine
import asyncio
import fcts.etcfunctions as etc
import fcts.sqlcontrol as q
import fcts.i18n_runtime as i18n
import random
import math

class PokemantleListView(discord.ui.View):
    def __init__(self, data, user, sep=12, title=None, description=None, empty_text=None):
        super().__init__(timeout=300)
        self.data = data
        self.user = user
        self.sep = sep
        self.current_page = 1
        self.message = None
        self.title = title or i18n.t(user, "cmd.47.list.title")
        self.description = description or i18n.t(user, "cmd.47.list.desc")
        self.empty_text = empty_text or i18n.t(user, "cmd.47.list.empty")

    async def send(self, ctx):
        self.message = await ctx.send(i18n.t(self.user, "cmd.47.list.loading"), view=self)
        await self.update_message(self.get_current_page_data())

    def max_page(self):
        return max(1, math.ceil(len(self.data) / self.sep))

    def get_current_page_data(self):
        start = (self.current_page - 1) * self.sep
        end = start + self.sep
        return self.data[start:end]

    def create_embed(self, page_data):
        embed = discord.Embed(
            title=self.title,
            description=self.description,
            color=random.randint(0x111111, 0xFFFFFF)
        )

        lines = []
        for item in page_data:
            lines.append(
                f"**`#{item['rank']:4d}`** • **{item['display_name']}** • `{item['similarity'] * 100:.4f}%`"
            )

        result_text = "\n".join(lines)
        if not result_text:
            result_text = self.empty_text

        embed.add_field(
            name=i18n.t(self.user, "cmd.47.list.field"),
            value=result_text[:1024],
            inline=False
        )

        embed.set_footer(
            text=i18n.t(
                self.user,
                "cmd.47.list.footer",
                current=self.current_page,
                pages=self.max_page(),
                count=len(self.data),
            )
        )
        return embed

    async def update_message(self, page_data):
        self.update_buttons()
        await self.message.edit(embed=self.create_embed(page_data), view=self)

    def update_buttons(self):
        first_page = self.current_page == 1
        last_page = self.current_page == self.max_page()

        self.first_page_button.disabled = first_page
        self.prev_button.disabled = first_page
        self.next_button.disabled = last_page
        self.last_page_button.disabled = last_page

        self.first_page_button.style = discord.ButtonStyle.gray if first_page else discord.ButtonStyle.green
        self.prev_button.style = discord.ButtonStyle.gray if first_page else discord.ButtonStyle.primary
        self.next_button.style = discord.ButtonStyle.gray if last_page else discord.ButtonStyle.primary
        self.last_page_button.style = discord.ButtonStyle.gray if last_page else discord.ButtonStyle.green

    @discord.ui.button(label="|<", style=discord.ButtonStyle.green)
    async def first_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page = 1
        await self.update_message(self.get_current_page_data())

    @discord.ui.button(label="<", style=discord.ButtonStyle.primary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page -= 1
        await self.update_message(self.get_current_page_data())

    @discord.ui.button(label=">", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page += 1
        await self.update_message(self.get_current_page_data())

    @discord.ui.button(label=">|", style=discord.ButtonStyle.green)
    async def last_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page = self.max_page()
        await self.update_message(self.get_current_page_data())


class Pokemantle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.engine = PokemantleEngine()
        self.active_games = set()  # 채널 중복 실행 방지
        self.used_answers = set() # 중복 정답 방지

    def display_name(self, name: str) -> str:
        return self.engine.en_to_ko.get(name.strip().lower(), name)
    
    def build_full_rank_data(self, answer_index: int):
        ranks = self.engine.get_all_ranks_by_index(answer_index)

        return sorted(
            [
                {
                    "rank": item["rank"],
                    "similarity": item["similarity"],
                    "display_name": self.display_name(item["name"])
                }
                for item in ranks
            ],
            key=lambda x: x["rank"]
        )

    # [id: 47] 포케멘틀 게임
    @commands.hybrid_command(name="포케멘틀", description="유사도 수치를 바탕으로 내가 생각하는 포켓몬을 맞출 수 있을까?")
    async def pokemantle(self, ctx):
        if ctx.guild is None:
            await ctx.reply(i18n.t(ctx.author, "cmd.47.server_only"))
            return

        channel_id = ctx.channel.id

        if channel_id in self.active_games:
            await ctx.reply(i18n.t(ctx.author, "cmd.47.already_running"))
            return

        self.active_games.add(channel_id)

        if len(self.used_answers) >= self.engine.pokemon_size:
            self.used_answers.clear()

        while True:
            answer_index = self.engine.get_random_answer_index()
            if answer_index not in self.used_answers:
                break

        self.used_answers.add(answer_index)

        guessed_results = {}
        participants = set()   # discord.Member 저장
        guess_count = 0        # 중복 제외 실제 시도 횟수

        await ctx.reply(i18n.t(ctx.author, "cmd.47.start"))

        print(self.display_name(self.engine.pokedex.iloc[answer_index]["name"]))

        def check(message: discord.Message):
            return (
                message.channel.id == ctx.channel.id
                and not message.author.bot
            )

        try:
            while True:
                try:
                    message = await self.bot.wait_for("message", check=check, timeout=300)
                except asyncio.TimeoutError:
                    await ctx.send(i18n.t(ctx.author, "cmd.47.timeout"))
                    break

                content = message.content.strip()

                if not content:
                    continue

                if content.lower() in [
                    "종료", "그만", "취소", "stop", "cancel", "quit",
                    "終了", "结束", "結束", "キャンセル", "取消"
                ]:
                    await ctx.send(i18n.t(ctx.author, "cmd.47.stopped"))
                    break

                if content.lower() in [
                    "포기", "gg", "give up", "放棄", "放弃"
                ]:
                    index = answer_index
                    answer = self.display_name(self.engine.pokedex.iloc[index]["name"])
                    await ctx.send(i18n.t(ctx.author, "cmd.47.give_up", answer=answer))
                    full_rank_data = self.build_full_rank_data(answer_index)
                    view = PokemantleListView(
                        full_rank_data,
                        ctx.author,
                        sep=12,
                        title=i18n.t(ctx.author, "cmd.47.all.title"),
                        description=i18n.t(ctx.author, "cmd.47.all.desc"),
                        empty_text=i18n.t(ctx.author, "cmd.47.all.empty")
                    )
                    await view.send(ctx)
                    break

                if content == "목록":
                    participants.add(message.author)
                    
                    if not guessed_results:
                        await ctx.send(i18n.t(ctx.author, "cmd.47.no_guesses"))
                        continue

                    sorted_results = sorted(
                        guessed_results.values(),
                        key=lambda x: x["rank"]
                    )

                    view = PokemantleListView(
                        sorted_results,
                        ctx.author,
                        sep=12,
                        title=i18n.t(ctx.author, "cmd.47.list.title"),
                        description=i18n.t(ctx.author, "cmd.47.list.desc"),
                        empty_text=i18n.t(ctx.author, "cmd.47.no_guesses")
                    )
                    await view.send(ctx)
                    continue

                participants.add(message.author)

                # 업적 204: 별명 사용시 해금
                if self.engine.is_alias_input(content):
                    if q.readStorage(message.author, 204) == 0:
                        q.storageModify(message.author, 204, 1)

                result = self.engine.guess_by_index(answer_index, content)

                if result is None:
                    await ctx.send(i18n.t(ctx.author, "cmd.47.unknown"))
                    continue

                # 업적 205: 내가 추측한 포켓몬의 순위가 339위면 해금
                if result["rank"] == 339:
                    if q.readStorage(message.author, 205) == 0:
                        q.storageModify(message.author, 205, 1)

                if result["name"] in guessed_results:
                    old_result = guessed_results[result["name"]]

                    embed = discord.Embed(
                        title=f":exclamation: {old_result['display_name']}",
                        description=i18n.t(ctx.author, "cmd.47.duplicate"),
                        color=random.randint(0x000000, 0xFFFFFF)
                    )
                    embed.add_field(name=i18n.t(ctx.author, "cmd.47.rank"), value=f"{etc.numFont('#'+str(old_result['rank']))}", inline=False)
                    embed.add_field(name=i18n.t(ctx.author, "cmd.47.similarity"), value=f"**`{old_result['similarity']*100:.4f}%`**", inline=False)
                    embed.set_footer(text=i18n.t(ctx.author, "cmd.47.attempts", count=len(guessed_results)))

                    await ctx.send(embed=embed)
                    continue

                guess_count += 1
                guessed_results[result["name"]] = {
                    "rank": result["rank"],
                    "similarity": result["similarity"],
                    "display_name": self.display_name(result["name"])
                }

                if result["is_correct"]:
                    xp_gain = 3000
                    money_gain = 1000

                    for member in participants:
                        q.xpAdd(member, xp_gain)
                        q.moneyAdd(member, money_gain)

                        # 업적 202
                        if guess_count <= 9:
                            if q.readStorage(member, 202) == 0:
                                q.storageModify(member, 202, 1)

                        # 업적 203
                        if guess_count >= 129:
                            if q.readStorage(member, 203) == 0:
                                q.storageModify(member, 203, 1)

                    embed = discord.Embed(
                        title=i18n.t(ctx.author, "cmd.47.correct"),
                        description=f"**{self.display_name(result['name'])}**",
                        color=random.randint(0x000000, 0xFFFFFF)
                    )
                    embed.add_field(name=i18n.t(ctx.author, "cmd.47.attempts.field"), value=i18n.t(ctx.author, "cmd.47.count.times", count=len(guessed_results)))
                    embed.add_field(name=i18n.t(ctx.author, "cmd.47.participants"), value=i18n.t(ctx.author, "cmd.47.count.people", count=len(participants)), inline=True)
                    embed.add_field(name=i18n.t(ctx.author, "cmd.47.reward"), value=i18n.t(ctx.author, "cmd.47.reward.value", xp=xp_gain, money=money_gain), inline=False)
                    await ctx.send(embed=embed)

                    full_rank_data = self.build_full_rank_data(answer_index)
                    view = PokemantleListView(
                        full_rank_data,
                        ctx.author,
                        sep=12,
                        title=i18n.t(ctx.author, "cmd.47.all.title"),
                        description=i18n.t(ctx.author, "cmd.47.all.desc"),
                        empty_text=i18n.t(ctx.author, "cmd.47.all.empty")
                    )
                    await view.send(ctx)
                    break

                embed = discord.Embed(
                    title=f":mag_right: {self.display_name(result['name'])}",
                    color=random.randint(0x000000, 0xFFFFFF)
                )
                embed.add_field(name=i18n.t(ctx.author, "cmd.47.rank"), value=f"{etc.numFont('#'+str(result['rank']))}", inline=False)
                embed.add_field(name=i18n.t(ctx.author, "cmd.47.similarity"), value=f"**`{result['similarity']*100:.4f}%`**", inline=False)
                embed.set_footer(text=i18n.t(ctx.author, "cmd.47.attempts", count=len(guessed_results)))

                await ctx.send(embed=embed)

        finally:
            self.active_games.discard(channel_id)


async def setup(bot):
    await bot.add_cog(Pokemantle(bot))
