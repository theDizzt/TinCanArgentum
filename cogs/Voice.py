import discord
import nacl
from discord.ext import commands
import fcts.sqlcontrol as q
import fcts.etcfunctions as etc
from PIL import Image, ImageDraw, ImageFont
import io
import json
from config.rootdir import root_dir
import requests

# 자신의 REST_API_KEY를 입력하세요!
REST_API_KEY = "f9f33bf22016361b7a1373da18ed60fe"

class KakaoTTS:
	def __init__(self, text, API_KEY=REST_API_KEY):
		self.resp = requests.post(
               url="https://kakaoi-newtone-openapi.kakao.com/v1/synthesize",
               headers={
                    "Content-Type": "application/xml",
                    "Authorization": f"KakaoAK {API_KEY}"
                },
                data=f"<speak><voice name='WOMAN_READ_CALM'>{text}</voice></speak>".encode('utf-8')
            )

	def save(self, filename="tts.mp3"):
		with open(filename, "wb") as file:
			file.write(self.resp.content)


class Voice(commands.Cog):

    def __init__(self, client: commands.Bot):
        self.client = client

    # Join [ID: 61]
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    @commands.hybrid_command(name='join',
                             description="The bot will join the voice channel you are currently in.")
    async def join(self, ctx):
        if ctx.author.voice and ctx.author.voice.channel:
            channel = ctx.author.voice.channel
            await ctx.send("봇이 **`{0.author.voice.channel}`** 채널에 입장합니다.".format(ctx))
            await channel.connect()
        else:
            await ctx.send("음성 채널이 존재하지 않습니다.")

    @join.error
    async def join_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = '`(⩌ʌ ⩌;)` This command is ratelimited, please try again in **{:.2f} seconds**.'.format(
                error.retry_after)
            await ctx.send(msg)
        else:
            raise error
        
    # Leave [ID: 62]
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    @commands.hybrid_command(name='leave',
                             description="The bot will leave the voice channel you are currently in.")
    #@discord.app_commands.describe(user='User mention')
    async def leave(self, ctx, skin_id: int = None):
        try:
            await ctx.voice_client.disconnect()
            await ctx.send("봇을 **`{0.author.voice.channel}`** 에서 내보냈습니다.".format(ctx))
        except IndexError as error_message:
            print(f"에러 발생: {error_message}")
            await ctx.send("{0.author.voice.channel}에 유저가 존재하지 않거나 봇이 존재하지 않습니다.\\n다시 입장후 퇴장시켜주세요.".format(ctx))
        except AttributeError as not_found_channel:
            print(f"에러 발생: {not_found_channel}")
            await ctx.send("봇이 존재하는 채널을 찾는 데 실패했습니다.")

    @leave.error
    async def preview_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = '`(⩌ʌ ⩌;)` This command is ratelimited, please try again in **{:.2f} seconds**.'.format(
                error.retry_after)
            await ctx.send(msg)
        else:
            raise error
        
    # TTS [ID: 69]
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    @commands.hybrid_command(name='tts',
                             description="The bot will leave the voice channel you are currently in.")
    #@discord.app_commands.describe(user='User mention')
    async def tts(self, ctx, *, text):
        print(text)
        voice = self.client.voice_clients[0]
        # 음성채널에 연결되어있다면
        tts = KakaoTTS(text)
        tts.save('tts.mp3')
        voice.play(discord.FFmpegPCMAudio(f'tts.mp3'))

    @tts.error
    async def tts_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = '`(⩌ʌ ⩌;)` This command is ratelimited, please try again in **{:.2f} seconds**.'.format(
                error.retry_after)
            await ctx.send(msg)
        else:
            raise error


async def setup(client):
    await client.add_cog(Voice(client))
