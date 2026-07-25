import asyncio
import math
import re
import time

import discord
from discord import app_commands
from discord.ext import commands

import fcts.i18n_runtime as i18n
import fcts.sqlcontrol as q


ALERT_COUNT = 32
COOLDOWN_SECONDS = 14400
MAX_TARGETS = 20
CONFIRM_TIMEOUT_SECONDS = 300

MENTION_OR_ID_GROUP = re.compile(
    r"^(?:<@!?\d+>|\d+)(?:\s+(?:<@!?\d+>|\d+))*$"
)
MENTION = re.compile(r"^<@!?(\d+)>$")


def split_user_references(value: str) -> list[str]:
    references = []
    for group in re.split(r"[\n,]+", value):
        group = group.strip()
        if not group:
            continue

        if MENTION_OR_ID_GROUP.fullmatch(group):
            references.extend(group.split())
        else:
            references.append(group)

    return references


def registered_users() -> tuple[dict[int, str], dict[str, int]]:
    users_by_id = {}
    users_by_tag = {}

    for row in q.userList():
        user_id = int(row[0])
        tag = f"{row[2]}#{int(row[1]):04d}"
        users_by_id[user_id] = tag
        users_by_tag[tag.casefold()] = user_id

    return users_by_id, users_by_tag


def resolve_users(value: str) -> tuple[list[int], list[str], dict[int, str]]:
    users_by_id, users_by_tag = registered_users()
    resolved = []
    invalid = []

    for reference in split_user_references(value):
        mention_match = MENTION.fullmatch(reference)
        if mention_match:
            user_id = int(mention_match.group(1))
        elif reference.isdigit():
            user_id = int(reference)
        else:
            user_id = users_by_tag.get(reference.casefold())

        if user_id is None or user_id not in users_by_id:
            invalid.append(reference)
            continue

        if user_id not in resolved:
            resolved.append(user_id)

    return resolved, invalid, users_by_id


class EmergencyCallConfirmView(discord.ui.View):
    def __init__(
        self,
        client: commands.Bot,
        owner: discord.abc.User,
        target_ids: list[int],
        message: str,
    ):
        super().__init__(timeout=CONFIRM_TIMEOUT_SECONDS)
        self.client = client
        self.target_ids = target_ids
        self.alert_message = message
        self.used = False
        self.message = None

        confirm_button = discord.ui.Button(
            label=i18n.t(owner, "cmd.49.confirm.button"),
            style=discord.ButtonStyle.danger,
        )
        confirm_button.callback = self.confirm
        self.add_item(confirm_button)

    async def confirm(self, interaction: discord.Interaction):
        if self.used:
            await interaction.response.send_message(
                i18n.t(interaction.user, "cmd.49.already_used"),
                ephemeral=True,
            )
            return

        # Set this before the first await so two fast interactions cannot both send.
        self.used = True
        for item in self.children:
            item.disabled = True
        self.stop()

        await interaction.response.edit_message(
            content=i18n.t(
                interaction.user,
                "cmd.49.sending",
                count=ALERT_COUNT,
                users=len(self.target_ids),
            ),
            view=self,
        )

        recipients = []
        failed_targets = set()
        for user_id in self.target_ids:
            user = self.client.get_user(user_id)
            if user is None:
                try:
                    user = await self.client.fetch_user(user_id)
                except discord.HTTPException:
                    failed_targets.add(user_id)
                    continue
            recipients.append(user)

        active_recipients = list(recipients)
        sent = 0
        for _ in range(ALERT_COUNT):
            for user in list(active_recipients):
                try:
                    await user.send(
                        self.alert_message,
                        allowed_mentions=discord.AllowedMentions.none(),
                    )
                    sent += 1
                except discord.HTTPException:
                    failed_targets.add(user.id)
                    active_recipients.remove(user)
                await asyncio.sleep(0.25)

        total = len(self.target_ids) * ALERT_COUNT
        if failed_targets:
            await interaction.followup.send(
                i18n.t(
                    interaction.user,
                    "cmd.49.send_failed",
                    sent=sent,
                    total=total,
                    failed=len(failed_targets),
                ),
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            i18n.t(
                interaction.user,
                "cmd.49.sent",
                count=ALERT_COUNT,
                users=len(self.target_ids),
            ),
            ephemeral=True,
        )

    async def on_timeout(self):
        if self.used:
            return

        for item in self.children:
            item.disabled = True

        if self.message is not None:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass


class EmergencyCallModal(discord.ui.Modal):
    def __init__(self, cog, owner: discord.abc.User):
        super().__init__(
            title=i18n.t(owner, "cmd.49.modal.title"),
            timeout=CONFIRM_TIMEOUT_SECONDS,
        )
        self.cog = cog
        self.owner = owner

        self.targets = discord.ui.TextInput(
            label=i18n.t(owner, "cmd.49.modal.targets.label"),
            placeholder=i18n.t(owner, "cmd.49.modal.targets.placeholder"),
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=500,
        )
        self.alert_message = discord.ui.TextInput(
            label=i18n.t(owner, "cmd.49.modal.message.label"),
            placeholder=i18n.t(owner, "cmd.49.modal.message.placeholder"),
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1400,
        )
        self.add_item(self.targets)
        self.add_item(self.alert_message)

    async def on_submit(self, interaction: discord.Interaction):
        target_ids, invalid, users_by_id = resolve_users(self.targets.value)

        if not self.alert_message.value.strip():
            await interaction.response.send_message(
                i18n.t(interaction.user, "cmd.49.message_required"),
                ephemeral=True,
            )
            return

        if invalid or not target_ids:
            invalid_text = ", ".join(
                discord.utils.escape_markdown(reference)
                for reference in invalid
            )
            if not invalid_text:
                invalid_text = i18n.t(interaction.user, "cmd.49.no_targets")

            await interaction.response.send_message(
                i18n.t(
                    interaction.user,
                    "cmd.49.invalid_users",
                    users=invalid_text[:1500],
                ),
                ephemeral=True,
            )
            return

        if len(target_ids) > MAX_TARGETS:
            await interaction.response.send_message(
                i18n.t(
                    interaction.user,
                    "cmd.49.too_many",
                    max_targets=MAX_TARGETS,
                ),
                ephemeral=True,
            )
            return

        retry_after = self.cog.reserve_cooldown(interaction.user.id)
        if retry_after > 0:
            await interaction.response.send_message(
                i18n.t(
                    interaction.user,
                    "reply.ratelimit",
                    second=retry_after,
                ),
                ephemeral=True,
            )
            return

        target_tags = ", ".join(
            discord.utils.escape_markdown(users_by_id[user_id])
            for user_id in target_ids
        )
        view = EmergencyCallConfirmView(
            self.cog.client,
            interaction.user,
            target_ids,
            self.alert_message.value.strip(),
        )
        await interaction.response.send_message(
            i18n.t(
                interaction.user,
                "cmd.49.ready",
                count=len(target_ids),
                users=target_tags,
            ),
            view=view,
        )
        view.message = await interaction.original_response()

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: Exception,
    ):
        message = i18n.t(
            interaction.user,
            "common.command_error",
            error=type(error).__name__,
        )
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)


class EmergencyCallOpenView(discord.ui.View):
    def __init__(self, cog, owner: discord.abc.User):
        super().__init__(timeout=60)
        self.cog = cog
        self.owner = owner
        self.owner_id = owner.id
        self.message = None

        open_button = discord.ui.Button(
            label=i18n.t(owner, "cmd.49.open.button"),
            style=discord.ButtonStyle.primary,
        )
        open_button.callback = self.open_modal
        self.add_item(open_button)

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id == self.owner_id:
            return True

        await interaction.response.send_message(
            i18n.t(interaction.user, "cmd.49.denied"),
            ephemeral=True,
        )
        return False

    async def open_modal(self, interaction: discord.Interaction):
        retry_after = self.cog.get_retry_after(interaction.user.id)
        if retry_after > 0:
            await interaction.response.send_message(
                i18n.t(
                    interaction.user,
                    "reply.ratelimit",
                    second=retry_after,
                ),
                ephemeral=True,
            )
            return

        await interaction.response.send_modal(
            EmergencyCallModal(self.cog, interaction.user)
        )

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        if self.message is not None:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass


class EmergencyCall(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.cooldowns = {}

    def get_retry_after(self, user_id: int) -> int:
        expires_at = self.cooldowns.get(user_id, 0)
        return max(0, math.ceil(expires_at - time.monotonic()))

    def reserve_cooldown(self, user_id: int) -> int:
        retry_after = self.get_retry_after(user_id)
        if retry_after > 0:
            return retry_after

        self.cooldowns[user_id] = time.monotonic() + COOLDOWN_SECONDS
        return 0

    # Emergency Call [ID: 49]
    @commands.hybrid_command(
        name=app_commands.locale_str(
            "emergency-call",
            key="cmd.49.name",
        ),
        description=app_commands.locale_str(
            "Send 32 DM alerts to registered users after confirmation",
            key="cmd.49.desc",
        ),
        aliases=["비상소집"],
    )
    async def emergency_call(self, ctx: commands.Context):
        if ctx.guild is None:
            await ctx.reply(
                i18n.t(ctx.author, "cmd.49.guild_only"),
                ephemeral=ctx.interaction is not None,
            )
            return

        retry_after = self.get_retry_after(ctx.author.id)
        if retry_after > 0:
            await ctx.reply(
                i18n.t(
                    ctx.author,
                    "reply.ratelimit",
                    second=retry_after,
                ),
                ephemeral=ctx.interaction is not None,
            )
            return

        if ctx.interaction is not None:
            await ctx.interaction.response.send_modal(
                EmergencyCallModal(self, ctx.author)
            )
            return

        view = EmergencyCallOpenView(self, ctx.author)
        view.message = await ctx.reply(
            i18n.t(ctx.author, "cmd.49.open"),
            view=view,
        )


async def setup(client):
    await client.add_cog(EmergencyCall(client))
