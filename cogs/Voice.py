import asyncio
import discord
import logging
import tempfile
from pathlib import Path
from discord.ext import commands
import fcts.i18n_runtime as i18n
from config.settings import get_required_env


logger = logging.getLogger(__name__)


class KakaoTTS:
    def __init__(self, text, api_key=None):
        self.text = text
        self.api_key = api_key or get_required_env("KAKAO_REST_API_KEY")

    def synthesize(self) -> bytes:
        import requests

        with requests.post(
            url="https://kakaoi-newtone-openapi.kakao.com/v1/synthesize",
            headers={
                "Content-Type": "application/xml",
                "Authorization": f"KakaoAK {self.api_key}",
            },
            data=(
                f"<speak><voice name='WOMAN_READ_CALM'>"
                f"{self.text}</voice></speak>"
            ).encode("utf-8"),
            timeout=20,
        ) as response:
            response.raise_for_status()
            return response.content


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
        audio = await asyncio.to_thread(KakaoTTS(text).synthesize)
        with tempfile.NamedTemporaryFile(
            prefix="tincan-tts-",
            suffix=".mp3",
            delete=False,
        ) as temporary:
            temporary.write(audio)
            temporary_path = Path(temporary.name)

        def cleanup(error):
            temporary_path.unlink(missing_ok=True)
            if error is not None:
                logger.error(
                    "TTS playback failed",
                    exc_info=(type(error), error, error.__traceback__),
                )

        try:
            voice.play(
                discord.FFmpegPCMAudio(str(temporary_path)),
                after=cleanup,
            )
        except Exception:
            temporary_path.unlink(missing_ok=True)
            raise

    @tts.error
    async def tts_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            raise error


async def setup(client):
    await client.add_cog(Voice(client))
