import discord
from discord.ext import commands

import fcts.plab as plab
import fcts.etcfunctions as etc
import fcts.sqlcontrol as q
from fcts.user_resolver import (
    UserResolutionError,
    registered_user_tag,
    resolve_discord_user,
)


class PLabListView(discord.ui.View):
    """Five-item paginated PLab achievement list."""

    def __init__(self, *, user, state, achievements, all_achievements):
        super().__init__(timeout=300)
        self.user = user
        self.user_tag = (
            q.readTagById(user.id)
            if q.accountExistsById(user.id)
            else str(user)
        )
        self.state = state
        self.achievements = achievements
        self.all_achievements = all_achievements
        self.current_page = 1
        self.items_per_page = 5
        self.message = None
        self._update_buttons()

    def max_page(self):
        return max(1, (len(self.achievements) - 1) // self.items_per_page + 1)

    def current_items(self):
        start = (self.current_page - 1) * self.items_per_page
        return self.achievements[start:start + self.items_per_page]

    def _update_buttons(self):
        at_first = self.current_page <= 1
        at_last = self.current_page >= self.max_page()
        self.first_page.disabled = at_first
        self.previous_page.disabled = at_first
        self.next_page.disabled = at_last
        self.last_page.disabled = at_last

    def create_embed(self):
        flags = self.state["flags"]
        completed = sum(
            bool(flags[item["id"]])
            for item in self.all_achievements
        )
        rank = plab.getPlabRank(
                        self.state["lab_point"],
                        self.state["skill_level"],
                    )
        total = len(self.all_achievements)
        percent = (completed / total * 100) if total else 0
        embed = discord.Embed(
            title="PLab Achievement List",
            description=(
                f"`Name` **{self.user_tag}**\n"
                f"`Stats` {etc.ricon(rank)} | {etc.ticon(self.state['skill_level'], False)} | {self.state['lab_point']:,} LP\n"
                f"`Completed` **{completed}**/{total} ({percent:.2f}%)\n"
                f"{etc.process_bar(completed / total)}"
            ),
            color=0xBCE29E,
        )
        embed.set_thumbnail(url=self.user.display_avatar.url)

        items = self.current_items()
        if not items:
            embed.add_field(
                name="No results",
                value="No PLab achievements matched the supplied keyword.",
                inline=False,
            )
        for item in items:
            status = etc.checkBox(flags[item["id"]])
            details = [
                item["description"] or "No description.",
                f"Tier: {etc.ticon(item['tier'])}",
            ]
            if item["url"]:
                details.append(f"[Play now!]({item['url']})")
            embed.add_field(
                name=f"`{item['id']:03d}` {status} {item['name']}",
                value="\n".join(details),
                inline=False,
            )

        embed.set_footer(
            text=(
                f"Page {self.current_page}/{self.max_page()} | "
                f"Showing {len(self.achievements)} games"
            )
        )
        return embed

    async def send(self, ctx):
        self.message = await ctx.reply(embed=self.create_embed(), view=self)

    async def update_message(self, interaction):
        self._update_buttons()
        await interaction.response.edit_message(
            embed=self.create_embed(),
            view=self,
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.user.id:
            return True
        await interaction.response.send_message(
            "Only the command user can control this list.",
            ephemeral=True,
        )
        return False

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if self.message is not None:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass
        self.achievements.clear()
        self.all_achievements.clear()
        self.message = None

    @discord.ui.button(label="|<", style=discord.ButtonStyle.green)
    async def first_page(self, interaction: discord.Interaction, button):
        self.current_page = 1
        await self.update_message(interaction)

    @discord.ui.button(label="<", style=discord.ButtonStyle.primary)
    async def previous_page(self, interaction: discord.Interaction, button):
        self.current_page -= 1
        await self.update_message(interaction)

    @discord.ui.button(label=">", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button):
        self.current_page += 1
        await self.update_message(interaction)

    @discord.ui.button(label=">|", style=discord.ButtonStyle.green)
    async def last_page(self, interaction: discord.Interaction, button):
        self.current_page = self.max_page()
        await self.update_message(interaction)


class PLabRankingView(discord.ui.View):
    """Ten-user paginated leaderboard ordered by LAB points."""

    def __init__(self, *, user, ranking, page=1):
        super().__init__(timeout=300)
        self.user = user
        self.ranking = ranking
        self.items_per_page = 10
        self.current_page = max(1, min(int(page), self.max_page()))
        self.message = None
        self._update_buttons()

    def max_page(self):
        return max(1, (len(self.ranking) - 1) // self.items_per_page + 1)

    def current_items(self):
        start = (self.current_page - 1) * self.items_per_page
        return self.ranking[start:start + self.items_per_page]

    def _update_buttons(self):
        at_first = self.current_page <= 1
        at_last = self.current_page >= self.max_page()
        self.first_page.disabled = at_first
        self.previous_page.disabled = at_first
        self.next_page.disabled = at_last
        self.last_page.disabled = at_last

    def create_embed(self):
        my_rank = plab.getUserRanking(self.user.id)
        my_rank_text = f"#{my_rank:,}" if my_rank is not None else "Unranked"
        embed = discord.Embed(
            title="🏆 PLab Ranking",
            description=(
                f"`My Rank` **{my_rank_text}**\n"
                f"`Total Users` **{len(self.ranking):,}**"
            ),
            color=0xE2F6CA,
        )
        embed.set_thumbnail(url=self.user.display_avatar.url)

        items = self.current_items()
        if not items:
            embed.add_field(
                name="No PLab users",
                value="No users have PLab data yet.",
                inline=False,
            )
        for item in items:
            plab_rank = plab.getPlabRank(
                item["lab_point"], item["skill_level"]
            )
            embed.add_field(
                name=(
                    f"{etc.numFont(item['ranking'])} "
                    f"{registered_user_tag(item['id'])}"
                ),
                value=(
                    f"{etc.ricon(plab_rank)} | "
                    f"{etc.ticon(item['skill_level'], False)} | "
                    f"**{item['lab_point']:,} LP**"
                ),
                inline=False,
            )

        embed.set_footer(
            text=f"Page {self.current_page}/{self.max_page()}"
        )
        return embed

    async def send(self, ctx):
        self.message = await ctx.reply(embed=self.create_embed(), view=self)

    async def update_message(self, interaction):
        self._update_buttons()
        await interaction.response.edit_message(
            embed=self.create_embed(), view=self
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.user.id:
            return True
        await interaction.response.send_message(
            "Only the command user can control this ranking.",
            ephemeral=True,
        )
        return False

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if self.message is not None:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass
        self.ranking.clear()
        self.message = None

    @discord.ui.button(label="|<", style=discord.ButtonStyle.green)
    async def first_page(self, interaction: discord.Interaction, button):
        self.current_page = 1
        await self.update_message(interaction)

    @discord.ui.button(label="<", style=discord.ButtonStyle.primary)
    async def previous_page(self, interaction: discord.Interaction, button):
        self.current_page -= 1
        await self.update_message(interaction)

    @discord.ui.button(label=">", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button):
        self.current_page += 1
        await self.update_message(interaction)

    @discord.ui.button(label=">|", style=discord.ButtonStyle.green)
    async def last_page(self, interaction: discord.Interaction, button):
        self.current_page = self.max_page()
        await self.update_message(interaction)


class PLab(commands.Cog):
    """Command placeholder for the future PLab feature (ID 29)."""

    def __init__(self, client: commands.Bot):
        self.client = client

    # PLab [ID: 29]
    @commands.hybrid_command(
        name="pl",
        aliases=["plab"],
        description="Use PLab features.",
    )
    async def pl(self, ctx, option: str = "stats", *, keyword: str = ""):
        """Use PLab statistics, ranking, and game-list features."""
        normalized_option = option.strip().casefold() or "stats"

        if normalized_option == "stats":
            try:
                user = await resolve_discord_user(ctx, keyword)
            except UserResolutionError as error:
                await ctx.reply(str(error))
                return

            if not q.accountExistsById(user.id):
                await ctx.reply("That user does not have a bot account.")
                return

            try:
                achievements = plab.loadAchievements()
                state = plab.getUserState(user.id)
            except (OSError, ValueError) as error:
                await ctx.reply(f"PLab data could not be loaded: `{error}`")
                return

            xp = q.readXpById(user.id)
            level = etc.level(xp)
            if level >= etc.maxLevel():
                current_xp = required_xp = 1
            else:
                previous_level_xp = etc.need_exp(level - 1)
                current_xp = xp - previous_level_xp
                required_xp = etc.need_exp(level) - previous_level_xp

            completed = sum(
                bool(state["flags"][item["id"]])
                for item in achievements
            )
            total = len(achievements)
            completion_ratio = completed / total if total else 0
            rank = plab.getPlabRank(
                state["lab_point"],
                state["skill_level"],
            )
            tag = q.readTagById(user.id)

            embed = discord.Embed(
                title=f":bar_chart: {tag}'s PLab Statistics",
                description=f"UID: {user.id}",
                color=0xBCE29E,
            )
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.add_field(
                name="Account Info",
                value=(
                    f"`Name` **{tag}**\n"
                    f"`Level` {etc.lvicon(level)}\n"
                    f"`XP` **{current_xp:,}/{required_xp:,} "
                    f"({current_xp / required_xp * 100:.2f}%)**\n"
                    f"{etc.process_bar(current_xp / required_xp)}\n"
                    f"`Total XP` **{xp:,}**"
                ),
                inline=False,
            )
            embed.add_field(
                name="PLab",
                value=(
                    f"`PLab Rank` {etc.ricon(int(rank))}\n"
                    f"`Skill Rank` {etc.ticon(state['skill_level'])}\n"
                    f"`LAB Point` **{state['lab_point']:,}** LP\n"
                    f"`Started` **{state['startdate']}**"
                ),
                inline=False,
            )
            embed.add_field(
                name="Game Completion",
                value=(
                    f"`Completed` **{completed}/{total} "
                    f"({completion_ratio * 100:.2f}%)**\n"
                    f"{etc.process_bar(completion_ratio)}"
                ),
                inline=False,
            )
            await ctx.reply(embed=embed)
            return

        if normalized_option == "ranking":
            try:
                page = int(keyword.strip() or "1")
                if page < 1:
                    raise ValueError
            except ValueError:
                await ctx.reply("The ranking page must be a positive integer.")
                return

            ranking = plab.getRanking()
            view = PLabRankingView(
                user=ctx.author,
                ranking=ranking,
                page=page,
            )
            await view.send(ctx)
            return

        if normalized_option in {"games", "game"}:
            try:
                all_achievements = plab.loadAchievements()
                state = plab.getUserState(ctx.author.id)
            except (OSError, ValueError) as error:
                await ctx.reply(f"PLab data could not be loaded: `{error}`")
                return

            search = keyword.strip().casefold()
            if search:
                achievements = [
                    item
                    for item in all_achievements
                    if search in str(item["id"])
                    or search in item["name"].casefold()
                    or search in item["description"].casefold()
                    or search == f"tier:{item['tier']}"
                ]
            else:
                achievements = list(all_achievements)

            view = PLabListView(
                user=ctx.author,
                state=state,
                achievements=achievements,
                all_achievements=all_achievements,
            )
            await view.send(ctx)
            return

        await ctx.reply(
            "Unknown PLab option.\n"
            "Available syntax: `;pl [stats] [user]`, `;pl ranking [page]`, "
            "or `;pl games [keyword]`"
        )


async def setup(client):
    await client.add_cog(PLab(client))
