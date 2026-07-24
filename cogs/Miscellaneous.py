import discord
from discord import app_commands
from discord.ext import commands
import fcts.sqlcontrol as q
import fcts.etcfunctions as etc
import fcts.i18n_runtime as i18n
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import io
import asyncio
from fcts.translator import DeepLTranslationError, DeepLTranslator
from config.rootdir import root_dir
from config.settings import get_required_env

GRADIENT_PRESETS = (
    ((168, 230, 207), (189, 224, 254), (205, 180, 219)),
    ((255, 214, 165), (255, 173, 173), (255, 198, 255)),
    ((160, 196, 255), (189, 178, 255), (255, 198, 255)),
    ((255, 175, 204), (255, 200, 221), (255, 229, 236)),
    ((253, 255, 182), (202, 255, 191), (155, 246, 255)),
    ((216, 180, 254), (196, 181, 253), (191, 219, 254)),
    ((254, 202, 202), (254, 215, 170), (167, 243, 208)),
)


def _interpolate_color(colors, position):
    scaled = max(0.0, min(1.0, position)) * (len(colors) - 1)
    index = min(int(scaled), len(colors) - 2)
    ratio = scaled - index
    return tuple(
        round(colors[index][channel] * (1 - ratio)
              + colors[index + 1][channel] * ratio)
        for channel in range(3)
    )


def create_lucky_number_image(number, font_path, colors):
    width, height = 384, 120
    # Discord 채널 배경이 그대로 비치도록 완전 투명한 캔버스를 사용한다.
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    text = str(number)
    draw = ImageDraw.Draw(image)
    font_size = 88
    while font_size > 24:
        font = ImageFont.truetype(str(font_path), font_size)
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        if right - left <= width - 36 and bottom - top <= height - 24:
            break
        font_size -= 4

    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    text_width = right - left
    text_height = bottom - top
    x = (width - text_width) / 2 - left
    y = (height - text_height) / 2 - top

    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.text((x + 3, y + 4), text, font=font, fill=(0, 0, 0, 210))
    image = Image.alpha_composite(image, shadow.filter(ImageFilter.GaussianBlur(4)))

    # 텍스트 마스크 안에만 7개 프리셋 중 선택된 그라데이션을 채운다.
    text_mask = Image.new("L", image.size, 0)
    mask_draw = ImageDraw.Draw(text_mask)
    mask_draw.text(
        (x, y),
        text,
        font=font,
        fill=255,
        stroke_width=max(1, font_size // 44),
        stroke_fill=230,
    )

    text_gradient = Image.new("RGBA", image.size, (0, 0, 0, 0))
    gradient_pixels = text_gradient.load()
    for column in range(width):
        color = _interpolate_color(colors, column / (width - 1))
        for row in range(height):
            gradient_pixels[column, row] = (*color, 255)

    image = Image.composite(text_gradient, image, text_mask)
    return image


def _wrap_rage_text(draw, text, font, max_width):
    lines = []
    for paragraph in text.splitlines() or [text]:
        if not paragraph:
            lines.append("")
            continue

        current = ""
        for character in paragraph:
            candidate = current + character
            left, _, right, _ = draw.textbbox((0, 0), candidate, font=font)
            if current and right - left > max_width:
                lines.append(current.rstrip())
                current = character.lstrip()
            else:
                current = candidate
        if current or not lines:
            lines.append(current.rstrip())
    return lines


def create_rage_image(text, font_path):
    image = Image.open(
        Path(root_dir) / "config" / "rage" / "ivory_rage.png"
    ).convert("RGBA")
    draw = ImageDraw.Draw(image)

    # 말풍선 내부의 안전 영역
    left, top, right, bottom = 28, 42, 294, 250
    max_width = right - left
    max_height = bottom - top

    selected_font = None
    selected_lines = None
    selected_line_height = None
    for font_size in range(42, 15, -2):
        font = ImageFont.truetype(str(font_path), font_size)
        lines = _wrap_rage_text(draw, text, font, max_width)
        bbox = draw.textbbox((0, 0), "가Ag", font=font)
        line_height = bbox[3] - bbox[1] + max(4, font_size // 6)
        if len(lines) * line_height <= max_height:
            selected_font = font
            selected_lines = lines
            selected_line_height = line_height
            break

    if selected_font is None:
        selected_font = ImageFont.truetype(str(font_path), 16)
        selected_lines = _wrap_rage_text(
            draw, text, selected_font, max_width
        )[:10]
        selected_line_height = 20

    block_height = len(selected_lines) * selected_line_height
    y = top + (max_height - block_height) / 2
    for line in selected_lines:
        line_bbox = draw.textbbox((0, 0), line, font=selected_font)
        line_width = line_bbox[2] - line_bbox[0]
        x = left + (max_width - line_width) / 2
        draw.text((x, y), line, fill=(18, 18, 22, 255), font=selected_font)
        y += selected_line_height

    return image


class Miscellaneous(commands.Cog):  # Cog를 상속하는 클래스를 선언

    def __init__(self, client: commands.Bot):  # 생성자 작성
        self.client = client

    # Random [ID: 31]
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)
    @commands.hybrid_command(
        name=app_commands.locale_str("dice", key="cmd.31.name"),
        aliases=["주사위"],
        description=app_commands.locale_str(
            "Display a random number", key="cmd.31.desc"))
    async def dice(self,
                   ctx,
                   rand: int = 99,
                   non_zero: int = 1,
                   option: int = -1):

        if rand < 1 or rand > 999_999_999_999 or non_zero not in (0, 1):
            await ctx.reply(i18n.t(ctx.author, "cmd.31.invalid_range"))
            return

        lucky_num = random.randint(0 if non_zero == 0 else 1, rand)

        font_paths = sorted(Path(root_dir).glob("font/*/name.ttf"))
        if not font_paths:
            await ctx.reply(i18n.t(ctx.author, "cmd.31.font_error"))
            return

        font_path = random.choice(font_paths)
        preset_index = option if 0 <= option < len(GRADIENT_PRESETS) else random.randrange(len(GRADIENT_PRESETS))
        image = create_lucky_number_image(
            lucky_num,
            font_path,
            GRADIENT_PRESETS[preset_index],
        )

        #sending image
        buffer_output = io.BytesIO()
        image.save(buffer_output, format='PNG')
        buffer_output.seek(0)

        if rand == 222 and lucky_num == 22:
            q.ensureStorage(ctx.author)
            if q.readStorage(ctx.author, 22) == 0:
                q.storageModify(ctx.author, 22, 1)
                await ctx.send(file=discord.File(root_dir + '/config/easter/22222.jpg'))

        await ctx.reply(
            i18n.t(ctx.author, "cmd.31.result"),
            file=discord.File(buffer_output, 'lucky-number.png'),
        )

    @dice.error
    async def dice_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            original = getattr(error, "original", error)
            print(f"[Dice ERROR] {type(original).__name__}: {original}")
            await ctx.send(i18n.t(ctx.author, "cmd.31.error"))

    # Rage [ID: 36]
    @commands.cooldown(rate=1, per=20, type=commands.BucketType.user)
    @commands.hybrid_command(
        name=app_commands.locale_str("rage", key="cmd.36.name"),
        aliases=["사자후"],
        description=app_commands.locale_str(
            "Create an image filled with rage", key="cmd.36.desc"))
    async def rage(self, ctx, *, text: str = ""):
        text = text.strip()
        if not text:
            await ctx.reply(i18n.t(ctx.author, "cmd.36.prompt"))
            return
        if len(text) > 200:
            await ctx.reply(i18n.t(ctx.author, "cmd.36.too_long", limit=200))
            return

        target = None
        message = getattr(ctx, "message", None)
        mentions = getattr(message, "mentions", []) if message else []
        if mentions:
            mentioned_user = mentions[0]
            target = mentioned_user.mention
            text = text.replace(mentioned_user.mention, "", 1)
            text = text.replace(f"<@!{mentioned_user.id}>", "", 1).strip()
            if not text:
                await ctx.reply(i18n.t(ctx.author, "cmd.36.prompt"))
                return

        preferred_font = Path(root_dir) / "font" / "gothic" / "name.ttf"
        font_paths = [preferred_font] if preferred_font.exists() else sorted(
            Path(root_dir).glob("font/*/name.ttf")
        )
        if not font_paths:
            await ctx.reply(i18n.t(ctx.author, "cmd.36.font_error"))
            return

        image = create_rage_image(text, font_paths[0])
        buffer_output = io.BytesIO()
        image.save(buffer_output, format='PNG')
        buffer_output.seek(0)

        await ctx.reply(
            target,
            file=discord.File(buffer_output, "rage.png"),
        )

    @rage.error
    async def rage_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            original = getattr(error, "original", error)
            print(f"[Rage ERROR] {type(original).__name__}: {original}")
            await ctx.send(i18n.t(ctx.author, "cmd.36.error"))

    # Translator [ID: 39]
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    @commands.hybrid_command(
        name=app_commands.locale_str("translate", key="cmd.39.name"),
        description=app_commands.locale_str(
            "Translate your text with DeepL.",
            key="cmd.39.desc"
        ),
        aliases=["번역"]
    )
    #@discord.app_commands.describe(lan1="Language of original text",lan2="Translation result language",text="Write your text to translate")
    async def translate(self, ctx, lan1, lan2, *, text=""):
        text = text.strip()
        if not text:
            await ctx.reply(i18n.t(ctx.author, "cmd.39.t001"))
            return

        if len(text) > 1500:
            await ctx.reply(i18n.t(
                ctx.author,
                "cmd.39.too_long",
                max_length=1500
            ))
            return

        try:
            translator = DeepLTranslator(get_required_env("DEEPL_API_KEY"))
            result = await asyncio.to_thread(
                translator.translate,
                lan1,
                lan2,
                text
            )
            await ctx.reply(result["text"])
        except ValueError:
            await ctx.reply(i18n.t(ctx.author, "cmd.39.invalid_language"))
        except RuntimeError:
            await ctx.reply(i18n.t(ctx.author, "cmd.39.not_configured"))
        except DeepLTranslationError as error:
            status = error.status_code or "-"
            print(f"[DeepL ERROR] status={status}: {error}")
            await ctx.reply(i18n.t(
                ctx.author,
                "cmd.39.error",
                status=status
            ))
        except Exception as error:
            print(f"[Translate ERROR] {type(error).__name__}: {error}")
            await ctx.reply(i18n.t(ctx.author, "cmd.39.error_unknown"))

    @translate.error
    async def translate_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            original = getattr(error, "original", error)
            print(f"[Translate ERROR] {type(original).__name__}: {original}")
            await ctx.send(i18n.t(ctx.author, "cmd.39.error_unknown"))


async def setup(client):
    await client.add_cog(Miscellaneous(client))
