import discord
from discord.ext import commands
from discord import app_commands
import fcts.sqlcontrol as q
import fcts.etcfunctions as etc
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
    "dapurm": 141,
    "쿠크다스": 142,
    "라이스썬더": 146,
    "비비빅": 147,
    "오도짜세기합바이크": 151,
    "부경타이타닉": 152,
    "100000words": 155
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

    # 3.3.99. Event Code
    @commands.cooldown(rate=1, per=20, type=commands.BucketType.user)
    @commands.hybrid_command(name='code', description="Input special codes")
    async def code(self, ctx):
        try:
            msg = await ctx.reply(
                "## 깜짝 선물 코드 | Special Code\n아래의 버튼을 클릭하면 마법의 코드를 입력할 수 있는 입력 칸이 나옵니다! (단, 10초가 지나면 버튼이 사라지니 빨리 눌러주세요!)\nClick on the button below and you'll get a box to enter the magic code! (However, the button will disappear after 10 seconds, so please press it quickly!)",
                view=ModalButton())
            await self.client.wait_for("interaction",
                                       check=lambda x: x.user == ctx.author)
            await msg.delete()
        except asyncio.TimeoutError:
            await msg.delete()

    @code.error
    async def code_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = '`(⩌ʌ ⩌;)` This command is ratelimited, please try again in **{:.2f} seconds**.'.format(
                error.retry_after)
            await ctx.send(msg)
        else:
            raise error


async def setup(client):
    await client.add_cog(SpecialCode(client))
