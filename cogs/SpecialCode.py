import discord
from discord.ext import commands
from discord import app_commands
import fcts.sqlcontrol as q
import fcts.etcfunctions as etc
import fcts.i18n_runtime as i18n
import asyncio

codelist = {
    "CODINFUN!!": 7,
    "dasihanbeon": 8,
    "heart": 9,
    "20200402": 10,
    "sectorform": 11,
    "agility": 12,
    "crossfooting": 13,
    "obliqueroot": 14,
    "avoidnsketch": 15,
    "safetysecurity": 16,
    "deadlycrystal": 17,
    "waiter": 18,
    "yellowcomet": 19,
    "bibibibibic": 21,
    "bloominglady": 24,
    "plain": 59,
    "darkoak": 94,
    "20240210": 102,
    "039350691": 109,
    "555042976": 110,
    "779455719": 111,
    "238970884": 112,
    "791439150": 113,
    "058168539": 114,
    "261546494": 115,
    "198525901": 116,
    "106747930": 117,
    "585232594": 118,
    "403 forbidden": 140,
    "dapurm": 141,
    "쿠크다스": 142,
    "라이스썬더": 146,
    "비비빅": 147,
    "오도짜세기합바이크": 151,
    "부경타이타닉": 152,
    "100000words": 155,
    "chelicerata": 156
}


class InputCode(discord.ui.Modal, title='Input Special Code!!'):
    code = discord.ui.TextInput(label='Input',
                                style=discord.TextStyle.short,
                                placeholder='Input your special code...')

    async def on_submit(self, interaction: discord.Interaction):
        result = codelist.get(self.code.value)
        if result == None:
            await interaction.response.send_message(
                f"`(⩌Δ ⩌ ;)` <@{interaction.user.id}> This code does not exist. Please double check that there are no typos!"
            )
        else:
            storage_list = etc.storageLineRead("all")
            if q.readStorage(interaction.user, result) == 1:
                await interaction.response.send_message(
                    f"`(⩌Δ ⩌ ;)` <@{interaction.user.id}> You have already unlocked this skin!\nInfo: **`{storage_list[result-1][0]}`** {storage_list[result-1][1]}"
                )
            else:
                q.storageModify(interaction.user, result, 1)
                await interaction.response.send_message(
                    f":green_circle: <@{interaction.user.id}> Code entered! Your reward has been received.\nInfo: **`{storage_list[result-1][0]}`** {storage_list[result-1][1]}"
                )


class ModalButton(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=10)

    @discord.ui.button(label='ヾ(｡ꏿ﹏ꏿ)ﾉ', style=discord.ButtonStyle.primary)
    async def button1(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
        await interaction.response.send_modal(InputCode())


class SpecialCode(commands.Cog):  # Cog를 상속하는 클래스를 선언

    def __init__(self, client: commands.Bot):  # 생성자 작성
        self.client = client

    # Event Code [id: 04]
    @commands.cooldown(rate=1, per=20, type=commands.BucketType.user)
    @commands.hybrid_command(name='code', description="Input special codes")
    async def code(self, ctx):
        try:
            msg = await ctx.reply(
                i18n.t(ctx.author, "cmd.04.t001"),
                view=ModalButton())
            await self.client.wait_for("interaction",
                                       check=lambda x: x.user == ctx.author)
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
