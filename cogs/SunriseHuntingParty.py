import discord
from discord.ext import commands
import fcts.sqlcontrol as q
import fcts.etcfunctions as etc

#SERVER id
server_id = [842746723067756554, 1114816224522678294, 453906917719408642]


class SunriseHuntingParty(commands.Cog):  # Cog를 상속하는 클래스를 선언

    def __init__(self, client: commands.Bot):  # 생성자 작성
        self.client = client

    async def is_server(ctx):
        return ctx.guild.id in server_id

    # Monchang [ID: 37]
    @commands.hybrid_command(name='똥몬창지수',
                             description="왠지 구린내가 나는 당신... 똥몬창 인가요?")
    @commands.check(is_server)
    #@discord.app_commands.describe(user="검사 대상자 언급")
    async def monchang(self, ctx, user: str = None):
        point = 0

        if user == None:
            id = ctx.author.id

        else:
            id = etc.extractUid(user)

        name = q.readTagById(id)

        if id == 429629511227670528:
            point = 110
        elif id == 277763741267918848:
            point = 97
        elif id == 811193433423216650:
            point = 94
        elif id == 544815696463396885:
            point = 84
        else:
            point = id % 101

        await ctx.reply(
            f"# `{name}` 의 똥몬창 지수는 **{point}tod** 입니다! \n```똥몬창 지수는 지구상 가장 똥몬창인 TOD를 기준으로 당신의 몬창 인생 데이터를 수집하여 분석한 결과 TOD와의 유사성을 나타낸 수치입니다. \n다시 말해 100tod의 똥몬창지수를 가진 당신은 역사상 최고의 똥몬창 입니다.```"
        )

    @monchang.error
    async def monchange_error(self, error, ctx):
        if isinstance(error, commands.CommandError):
            await ctx.reply("`태양수렵단 마이너 갤러리` 전용 명령어 입니다!")


async def setup(client):
    await client.add_cog(SunriseHuntingParty(client))
