import discord
from discord.ext import commands
from discord import app_commands
import fcts.sqlcontrol as q
import fcts.i18n_runtime as i18n
import fcts.skin_catalog as catalog
import asyncio


def find_gift_code(code: str):
    submitted = code.strip()
    for skin in catalog.load_storage():
        if (
            skin["unlock_type"] == "code"
            and str(skin.get("unlock_val", "")) == submitted
        ):
            return skin
    return None


class InputCode(discord.ui.Modal):
    def __init__(self, user):
        super().__init__(
            title=i18n.t(user, "cmd.04.modal.title"),
            timeout=60,
        )
        self.code = discord.ui.TextInput(
            label=i18n.t(user, "cmd.04.modal.label"),
            style=discord.TextStyle.short,
            placeholder=i18n.t(user, "cmd.04.modal.placeholder"),
            required=True,
            max_length=100,
        )
        self.add_item(self.code)

    async def on_submit(self, interaction: discord.Interaction):
        skin = find_gift_code(self.code.value)
        if skin is None:
            await interaction.response.send_message(
                i18n.t(
                    interaction.user,
                    "cmd.04.invalid",
                    user=interaction.user.mention,
                )
            )
            return

        skin_id = int(skin["id"])
        q.ensureStorage(interaction.user)
        if q.readStorage(interaction.user, skin_id) == 1:
            await interaction.response.send_message(
                i18n.t(
                    interaction.user,
                    "cmd.04.already",
                    user=interaction.user.mention,
                    skin_id=skin["id"],
                    skin_name=skin["name"],
                )
            )
            return

        q.storageModify(interaction.user, skin_id, 1)
        await interaction.response.send_message(
            i18n.t(
                interaction.user,
                "cmd.04.success",
                user=interaction.user.mention,
                skin_id=skin["id"],
                skin_name=skin["name"],
            )
        )


class ModalButton(discord.ui.View):

    def __init__(self, user):
        super().__init__(timeout=10)
        self.owner_id = user.id

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id == self.owner_id:
            return True
        await interaction.response.send_message(
            i18n.t(interaction.user, "common.not_allowed"),
            ephemeral=True,
        )
        return False

    @discord.ui.button(label='ヾ(｡ꏿ﹏ꏿ)ﾉ', style=discord.ButtonStyle.primary)
    async def button1(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
        await interaction.response.send_modal(InputCode(interaction.user))


class SpecialCode(commands.Cog):  # Cog를 상속하는 클래스를 선언

    def __init__(self, client: commands.Bot):  # 생성자 작성
        self.client = client

    # Event Code [id: 04]
    @commands.cooldown(rate=1, per=20, type=commands.BucketType.user)
    @commands.hybrid_command(
        name=app_commands.locale_str("code", key="cmd.04.name"),
        description=app_commands.locale_str(
            "Redeem a special gift code",
            key="cmd.04.desc",
        ),
    )
    async def code(self, ctx):
        try:
            msg = await ctx.reply(
                i18n.t(ctx.author, "cmd.04.t001"),
                view=ModalButton(ctx.author))
            await self.client.wait_for("interaction",
                                       check=lambda x: x.user == ctx.author,
                                       timeout=10)
            await msg.delete()
        except asyncio.TimeoutError:
            await msg.delete()

    @code.error
    async def code_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            raise error


async def setup(client):
    await client.add_cog(SpecialCode(client))
