from __future__ import annotations

import discord
from discord.ext import commands

import fcts.etcfunctions as etc
import fcts.i18n_runtime as i18n
import fcts.nelgp as nelgp_data
import fcts.sqlcontrol as q


ITEMS_PER_PAGE = 5


def _account_progress(user) -> tuple[int, int, int]:
    xp = q.readXp(user)
    level = etc.level(xp)
    if level >= etc.maxLevel():
        return level, 1, 1
    previous_xp = etc.need_exp(level - 1)
    return level, xp - previous_xp, etc.need_exp(level) - previous_xp


class AchievementCodeModal(discord.ui.Modal, title="NELG++ Achievement Code"):
    code = discord.ui.TextInput(
        label="Code",
        style=discord.TextStyle.short,
        placeholder="Enter the achievement code from NELG++",
        min_length=1,
        max_length=100,
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            catalog = nelgp_data.loadCatalog()
        except (OSError, ValueError) as error:
            await interaction.response.send_message(
                f"NELG++ achievement data could not be loaded: `{error}`",
                ephemeral=True,
            )
            return

        achievement = catalog["codes"].get(str(self.code.value).strip().casefold())
        if achievement is None:
            await interaction.response.send_message(
                "`(⩌Δ ⩌ ;)` This achievement code does not exist. "
                "Please check for typing errors.",
                ephemeral=True,
            )
            return

        if not q.accountExistsById(interaction.user.id):
            await interaction.response.send_message(
                "A bot account is required before claiming NELG++ rewards.",
                ephemeral=True,
            )
            return

        if not nelgp_data.unlockAchievement(
            interaction.user.id, achievement["id"]
        ):
            await interaction.response.send_message(
                "`(⩌Δ ⩌ ;)` You have already unlocked this achievement!\n"
                f"Info: `[{achievement['id']:03d}] {achievement['title']}`",
                ephemeral=True,
            )
            return

        q.xpAdd(interaction.user, achievement["xp"])
        q.moneyAdd(interaction.user, achievement["money"])
        response = (
            ":green_circle: Achievement code accepted!\n"
            f"Info: `[{achievement['id']:03d}] {achievement['title']}` | "
            f"+{achievement['xp']:,}XP, +${achievement['money']:,}"
        )

        skin_id = achievement["skin"]
        if skin_id is not None:
            try:
                if q.readStorage(interaction.user, str(skin_id)) == 0:
                    q.storageModify(interaction.user, skin_id, 1)
                    response += (
                        f"\nSpecial skin **{skin_id}** was also unlocked."
                    )
            except Exception:
                response += "\nThe optional skin reward could not be applied."

        await interaction.response.send_message(response, ephemeral=True)


class NELGPlusAchievementView(discord.ui.View):
    def __init__(self, *, user, catalog, page: int = 1):
        super().__init__(timeout=300)
        self.user = user
        self.catalog = catalog
        self.data = list(catalog["achievements"])
        self.current_page = max(1, min(int(page), self.total_pages))
        self.message = None
        self.code_button.disabled = not bool(self.data)
        self._update_buttons()

    @property
    def total_pages(self) -> int:
        return max(1, (len(self.data) - 1) // ITEMS_PER_PAGE + 1)

    def current_items(self):
        start = (self.current_page - 1) * ITEMS_PER_PAGE
        return self.data[start:start + ITEMS_PER_PAGE]

    def _update_buttons(self):
        at_first = self.current_page <= 1
        at_last = self.current_page >= self.total_pages
        self.first_button.disabled = at_first
        self.previous_button.disabled = at_first
        self.next_button.disabled = at_last
        self.last_button.disabled = at_last

    def create_embed(self):
        state = nelgp_data.achievementState(self.user.id)
        configured_ids = {item["id"] for item in self.data}
        unlocked = len(configured_ids.intersection(state))
        total = len(self.data)
        ratio = unlocked / total if total else 0
        level, current_xp, required_xp = _account_progress(self.user)

        embed = discord.Embed(
            title=(
                f"**{q.readTag(self.user)}'s "
                f"{self.catalog['meta']['title']} Achievements**"
            ),
            description=(
                f"`Progress` **{unlocked}/{total}** ({ratio * 100:.2f}%)\n"
                f"{etc.process_bar(ratio)}\n"
                f"`Level` {etc.lvicon(level)} | "
                f"{current_xp:,} / {required_xp:,} "
                f"({current_xp / required_xp * 100:.2f}%)\n"
                f"{etc.process_bar(current_xp / required_xp)}"
            ),
            color=self.catalog["meta"]["color"],
        )
        embed.set_thumbnail(url=self.user.display_avatar.url)

        if not self.data:
            embed.add_field(
                name="No achievements configured",
                value="Add achievement entries to `config/nelgp.json`.",
                inline=False,
            )
        for item in self.current_items():
            completed = item["id"] in state
            if item["hidden"]:
                description = (
                    "Check it out in-game." if completed else "Hidden Achievement"
                )
            else:
                description = item["description"] or "No description."
            embed.add_field(
                name=(
                    f"[{item['id']:03d}] {item['title']} "
                    f"{etc.checkBox(int(completed))}"
                ),
                value=(
                    f"{description}\n"
                    f"`Award` +{item['xp']:,}XP | +${item['money']:,}\n"
                    f"`Complete` {state.get(item['id'], '-')}"
                ),
                inline=False,
            )

        embed.set_footer(
            text=f"Page : {self.current_page} / {self.total_pages}"
        )
        return embed

    async def send(self, ctx):
        self.message = await ctx.send(
            i18n.t(ctx.author, "reply.complete", name=q.readTag(ctx.author)),
            embed=self.create_embed(),
            view=self,
        )

    async def update_message(self, interaction):
        self._update_buttons()
        await interaction.response.edit_message(
            embed=self.create_embed(), view=self
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.user.id:
            return True
        await interaction.response.send_message(
            "Only the command user can control this achievement list.",
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
        self.data.clear()
        self.message = None

    @discord.ui.button(label="|<", style=discord.ButtonStyle.green)
    async def first_button(self, interaction, button):
        self.current_page = 1
        await self.update_message(interaction)

    @discord.ui.button(label="<", style=discord.ButtonStyle.primary)
    async def previous_button(self, interaction, button):
        self.current_page -= 1
        await self.update_message(interaction)

    @discord.ui.button(label="CODE", style=discord.ButtonStyle.danger)
    async def code_button(self, interaction, button):
        await interaction.response.send_modal(AchievementCodeModal())

    @discord.ui.button(label=">", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction, button):
        self.current_page += 1
        await self.update_message(interaction)

    @discord.ui.button(label=">|", style=discord.ButtonStyle.green)
    async def last_button(self, interaction, button):
        self.current_page = self.total_pages
        await self.update_message(interaction)


class NELGPlusHintView(discord.ui.View):
    def __init__(self, *, user, catalog, level: int):
        super().__init__(timeout=300)
        self.user = user
        self.catalog = catalog
        self.levels = list(catalog["hints"])
        self.level_index = self.levels.index(level)
        self.message = None
        self._update_controls()

    def _update_controls(self):
        self.previous_button.disabled = self.level_index == 0
        self.next_button.disabled = self.level_index == len(self.levels) - 1
        entries = self.catalog["hints"][self.levels[self.level_index]]["hints"]
        self.hint_select.options = [
            discord.SelectOption(label=f"{number}. {item['title']}"[:100], value=str(number))
            for number, item in enumerate(entries, start=1)
        ]

    def create_embed(self):
        level = self.levels[self.level_index]
        entry = self.catalog["hints"][level]
        embed = discord.Embed(
            title=f"NELG Plus Level {level} Hints",
            description=(
                f"**{entry['title']}**\n"
                "Select a hint to receive it in your DMs.\n\n"
                + "\n".join(
                    f"`{number}` {hint['title']}"
                    for number, hint in enumerate(entry["hints"], start=1)
                )
            ),
            color=self.catalog["meta"]["color"],
        )
        embed.set_footer(text=f"Level {self.level_index + 1} / {len(self.levels)}")
        return embed

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.user.id:
            return True
        await interaction.response.send_message(
            "Only the command user can control this hint list.", ephemeral=True
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

    @discord.ui.button(label="<", style=discord.ButtonStyle.primary)
    async def previous_button(self, interaction, button):
        self.level_index -= 1
        self._update_controls()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.select(placeholder="Choose a hint", options=[discord.SelectOption(label="Hint", value="1")])
    async def hint_select(self, interaction, select):
        level = self.levels[self.level_index]
        number = int(select.values[0])
        hint = self.catalog["hints"][level]["hints"][number - 1]
        message = (
            f"## NELG Plus | Level {level}Hint #{number}\n"
            f"### Hint #{number}: {hint['title']}\n"
            f"{hint['text']}"
        )
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            await interaction.user.send(
                message, allowed_mentions=discord.AllowedMentions.none()
            )
        except discord.HTTPException:
            await interaction.edit_original_response(
                content="I couldn't send a DM. Please allow DMs and try again."
            )
            return
        await interaction.edit_original_response(content="Hint sent to your DMs.")

    @discord.ui.button(label=">", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction, button):
        self.level_index += 1
        self._update_controls()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)


class NELGPlus(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    async def is_server(ctx):
        return ctx.channel.id in [1115648878918774794, 1545107072939724932, 908380307223371806]

    # NELG Plus [ID: 52]
    @commands.check(is_server)
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    @commands.hybrid_command(
        name="nelgp",
        aliases=["nelgplus", "nelg++"],
        description="NELG Plus support functions.",
    )
    async def nelgp(self, ctx, option: str = "help", page: int = 1):
        normalized_option = str(option).strip().casefold()
        if not q.accountExistsById(ctx.author.id):
            await ctx.reply(
                "A bot account is required before using NELG Plus features."
            )
            return
        try:
            catalog = nelgp_data.loadCatalog()
        except (OSError, ValueError) as error:
            await ctx.reply(f"NELG+ data could not be loaded: `{error}`")
            return

        if normalized_option in {"help", "h"}:
            embed = discord.Embed(
                title="NELG Plus Support Functions",
                description=catalog["meta"]["release"],
                color=catalog["meta"]["color"],
            )
            embed.add_field(
                name="COMMANDS",
                value=(
                    "`;nelgp help` Show this page.\n"
                    "`;nelgp achievements [page]` Show and unlock your "
                    "achievement list.\n"
                    "`;nelgp user` Show your profile.\n"
                    "`;nelgp hint [level]` Browse level hints sent by DM."
                ),
                inline=False,
            )
            embed.set_footer(
                text=q.readTag(ctx.author),
                icon_url=ctx.author.display_avatar.url,
            )
            await ctx.reply(
                i18n.t(ctx.author, "reply.complete", name=q.readTag(ctx.author)),
                embed=embed,
            )
            return

        if normalized_option in {"achievements", "achievement", "achieve", "a"}:
            nelgp_data.ensureUser(ctx.author.id)
            view = NELGPlusAchievementView(
                user=ctx.author,
                catalog=catalog,
                page=page,
            )
            await view.send(ctx)
            return

        if normalized_option in {"user", "u"}:
            nelgp_data.ensureUser(ctx.author.id)
            name = q.readTag(ctx.author)
            level, current_xp, required_xp = _account_progress(ctx.author)
            xp_ratio = current_xp / required_xp
            state = nelgp_data.achievementState(ctx.author.id)
            configured_ids = {item["id"] for item in catalog["achievements"]}
            total = len(configured_ids)
            unlocked = len(configured_ids.intersection(state))
            achievement_ratio = unlocked / total if total else 0

            embed = discord.Embed(
                title=f"**{name}'s {catalog['meta']['title']} Profile**",
                description=(
                    f"{etc.lvicon(level)} | "
                    f"{current_xp:,} / {required_xp:,} "
                    f"({xp_ratio * 100:.2f}%)\n"
                    f"{etc.process_bar(xp_ratio)}"
                ),
                color=catalog["meta"]["color"],
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            embed.add_field(
                name="Join Date",
                value=nelgp_data.readJoinTime(ctx.author.id),
                inline=False,
            )
            embed.add_field(
                name="Achievements",
                value=(
                    f"{unlocked}/{total} ({achievement_ratio * 100:.2f}%)\n"
                    f"{etc.process_bar(achievement_ratio)}"
                ),
                inline=False,
            )

            await ctx.reply(
                i18n.t(ctx.author, "reply.complete", name=name),
                embed=embed,
            )
            return

        if normalized_option in {"hint", "hints", "ht"}:
            hints = catalog["hints"]
            if not hints:
                await ctx.reply("No level hints are available yet.")
                return
            level = page
            if level == 1 and level not in hints:
                level = next(iter(hints))
            if level not in hints:
                available = ", ".join(str(number) for number in hints)
                await ctx.reply(f"No hints for Level {level}. Available levels: {available}.")
                return
            view = NELGPlusHintView(user=ctx.author, catalog=catalog, level=level)
            view.message = await ctx.reply(
                i18n.t(ctx.author, "reply.complete", name=q.readTag(ctx.author)),
                embed=view.create_embed(),
                view=view,
            )
            return

        await ctx.reply(
            "Unknown option. Use `;nelgp help` or "
            "`;nelgp achievements [page]` or `;nelgp hint [level]`."
        )

    @nelgp.error
    async def nelgp_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            )
        elif isinstance(error, commands.BadArgument):
            await ctx.reply("The page must be a positive integer.")
        elif isinstance(error, commands.errors.CheckFailure):
                    await ctx.reply(
                        "## `(⩌ʌ ⩌;)` NOT ALLOWED\nTo use this command, you need to go to the <#1545107072939724932> channel on the **Stargazer Discord server**!"
                    )
        else:
            raise error


async def setup(client):
    nelgp_data.initSetting()
    await client.add_cog(NELGPlus(client))
