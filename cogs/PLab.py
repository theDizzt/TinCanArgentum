import discord
from discord.ext import commands

import fcts.plab as plab


class PLabListView(discord.ui.View):
    """Five-item paginated PLab achievement list."""

    def __init__(self, *, user, state, achievements, all_achievements):
        super().__init__(timeout=300)
        self.user = user
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
        total = len(self.all_achievements)
        percent = (completed / total * 100) if total else 0
        embed = discord.Embed(
            title="PLab Achievement List",
            description=(
                f"Lab Point: **{self.state['lab_point']:,}**\n"
                f"Skill Level: **{self.state['skill_level']:,}**\n"
                f"Started: **{self.state['startdate']}**\n"
                f"Completed: **{completed}/{total} ({percent:.2f}%)**"
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
            is_complete = bool(flags[item["id"]])
            status = "✅ Completed" if is_complete else "⬜ Incomplete"
            details = [
                item["description"] or "No description.",
                f"Tier: **{item['tier']}** | Status: **{status}**",
            ]
            if item["url"]:
                details.append(f"[Open details]({item['url']})")
            embed.add_field(
                name=f"`{item['id']:04d}` {item['name']}",
                value="\n".join(details),
                inline=False,
            )

        embed.set_footer(
            text=(
                f"Page {self.current_page}/{self.max_page()} | "
                f"Showing {len(self.achievements)} achievement(s)"
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
    async def pl(self, ctx, option: str = "", *, keyword: str = ""):
        """Reserved syntax: ;pl <option> <keyword>."""
        if option.strip().casefold() == "list":
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
            "`PLab (ID: 29)` is currently under development.\n"
            "Available syntax: `;pl list [keyword]`"
        )


async def setup(client):
    await client.add_cog(PLab(client))
