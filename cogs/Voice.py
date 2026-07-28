import discord
import nacl
from discord.ext import commands
import fcts.sqlcontrol as q
import fcts.etcfunctions as etc
import fcts.i18n_runtime as i18n
from PIL import Image, ImageDraw, ImageFont
import io
import json
from config.settings import get_required_env
from project_paths import PROJECT_ROOT
import requests


TTS_PATH = PROJECT_ROOT / "tts.mp3"


class KakaoTTS:
	def __init__(self, text, API_KEY=None):
		API_KEY = API_KEY or get_required_env('KAKAO_REST_API_KEY')
		self.resp = requests.post(
               url="https://kakaoi-newtone-openapi.kakao.com/v1/synthesize",
               headers={
                    "Content-Type": "application/xml",
                    "Authorization": f"KakaoAK {API_KEY}"
                },
                data=f"<speak><voice name='WOMAN_READ_CALM'>{text}</voice></speak>".encode('utf-8')
            )

	def save(self, filename=TTS_PATH):
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
            await ctx.send(i18n.t(ctx.author, "cmd.61.t001", channel=ctx.author.voice.channel))
            await channel.connect()
        else:
            await ctx.send(i18n.t(ctx.author, "cmd.61.error"))

    @join.error
    async def join_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
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
            await ctx.send(i18n.t(ctx.author, "cmd.62.t001", channel=ctx.author.voice.channel))
        except IndexError as error_message:
            print(f"에러 발생: {error_message}")
            await ctx.send(i18n.t(ctx.author, "cmd.62.error1", channel=ctx.author.voice.channel))
        except AttributeError as not_found_channel:
            print(f"에러 발생: {not_found_channel}")
            await ctx.send(i18n.t(ctx.author, "cmd.62.error2"))

    @leave.error
    async def preview_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            raise error
        
    # TTS [ID: 63]
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    @commands.hybrid_command(name='tts',
                             description="The bot will leave the voice channel you are currently in.")
    #@discord.app_commands.describe(user='User mention')
    async def tts(self, ctx, *, text):
        print(text)
        voice = self.client.voice_clients[0]
        # 음성채널에 연결되어있다면
        tts = KakaoTTS(text)
        tts.save(TTS_PATH)
        voice.play(discord.FFmpegPCMAudio(str(TTS_PATH)))

    @tts.error
    async def tts_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            raise error


async def setup(client):
    await client.add_cog(Voice(client))
