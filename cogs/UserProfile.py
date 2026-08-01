import discord
from discord.ext import commands
from discord import app_commands
import fcts.i18n_runtime as i18n
import fcts.sqlcontrol as q
import fcts.etcfunctions as etc
import fcts.skin_catalog as catalog
from fcts.user_resolver import UserResolutionError, resolve_discord_user
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont
import io
import asyncio
import json
import random
from datetime import datetime, timedelta, timezone
from project_paths import FONT_DIR, RANKCARD_DIR


SKIN_214_COLOR_PRESETS = (
    (255, 0, 0, 0),
    (0, 255, 0, 0),
    (0, 0, 255, 0),
    (255, 255, 0, 0),
    (255, 0, 255, 0),
    (0, 255, 255, 0),
    (255, 255, 255, 0),
    (128, 128, 128, 0),
    (192, 192, 192, 0),
    (128, 0, 128, 0),
    (128, 0, 0, 0),
    (128, 128, 0, 0),
    (0, 128, 0, 0),
    (0, 128, 128, 0),
    (0, 0, 128, 0),
)

SKIN_139_CLOCK_CENTER = (315, 53)
KOREA_TIMEZONE = timezone(timedelta(hours=9))


def _tint_preserving_alpha(
    source: Image.Image,
    color: tuple[int, int, int, int],
) -> Image.Image:
    source = source.convert("RGBA")
    visible_color = (*color[:3], 255)
    tinted = Image.new("RGBA", source.size, visible_color)
    tinted.putalpha(source.getchannel("A"))
    return tinted


def _apply_skin_214_effects(
    background: Image.Image,
    bar: Image.Image,
) -> tuple[Image.Image, Image.Image, tuple[int, int, int, int]]:
    selected_color = random.choice(SKIN_214_COLOR_PRESETS)
    visible_color = (*selected_color[:3], 255)

    image = background.copy().convert("RGBA")
    tinted_bar = _tint_preserving_alpha(bar, selected_color)
    special_directory = RANKCARD_DIR / "special"
    with Image.open(special_directory / "image214a.png") as source_a:
        image_a = _tint_preserving_alpha(source_a, selected_color)
    with Image.open(special_directory / "image214b.png") as source_b:
        image_b = _tint_preserving_alpha(source_b, selected_color)

    max_x = max(0, image.width - image_a.width)
    max_y = max(0, image.height - image_a.height)
    random_position = (
        random.randint(0, max_x),
        random.randint(0, max_y),
    )
    image.alpha_composite(image_a, random_position)
    image.alpha_composite(image_b, (7, 115))
    return image, tinted_bar, visible_color


def _composite_clock_hand(
    image: Image.Image,
    hand: Image.Image,
    angle: float,
) -> None:
    """Rotate a hand clockwise around its lower-center pivot."""
    center_x, center_y = SKIN_139_CLOCK_CENTER
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    try:
        hand_x = center_x - hand.width // 2
        hand_y = center_y - (hand.height - 1)
        layer.alpha_composite(hand, (hand_x, hand_y))
        rotated = layer.rotate(
            -angle,
            resample=Image.Resampling.BICUBIC,
            center=SKIN_139_CLOCK_CENTER,
        )
        try:
            image.alpha_composite(rotated)
        finally:
            rotated.close()
    finally:
        layer.close()


def _apply_skin_139_clock(
    image: Image.Image,
    current_time: datetime | None = None,
) -> Image.Image:
    """Draw skin 139's hour and minute hands using the current Korean time."""
    if current_time is None:
        current_time = datetime.now(KOREA_TIMEZONE)
    elif current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=KOREA_TIMEZONE)
    else:
        current_time = current_time.astimezone(KOREA_TIMEZONE)

    seconds = current_time.second + current_time.microsecond / 1_000_000
    minute_angle = current_time.minute * 6 + seconds * 0.1
    hour_angle = (current_time.hour % 12) * 30 + current_time.minute * 0.5 + seconds / 120
    special_directory = RANKCARD_DIR / "special"

    with Image.open(special_directory / "image139a.png") as source:
        hour_hand = source.convert("RGBA")
    try:
        _composite_clock_hand(image, hour_hand, hour_angle)
    finally:
        hour_hand.close()

    with Image.open(special_directory / "image139b.png") as source:
        minute_hand = source.convert("RGBA")
    try:
        _composite_clock_hand(image, minute_hand, minute_angle)
    finally:
        minute_hand.close()

    return image


async def _load_avatar_image(
    user: discord.Member,
    normal_skin_id: int | None,
) -> Image.Image:
    try:
        buffer_avatar = io.BytesIO()
        try:
            await user.display_avatar.save(buffer_avatar)
            buffer_avatar.seek(0)
            with Image.open(buffer_avatar) as source:
                avatar_image = source.convert("RGBA")
        finally:
            buffer_avatar.close()

        if normal_skin_id == 140:
            avatar_image.close()
            with Image.open(
                RANKCARD_DIR / "special" / "image140a.png"
            ) as source:
                avatar_image = source.convert("RGBA")
    except Exception:
        with Image.open(RANKCARD_DIR / "noimage.jpg") as source:
            avatar_image = source.convert("RGBA")

    resized_avatar = avatar_image.resize((96, 96), Image.Resampling.LANCZOS)
    avatar_image.close()
    return resized_avatar


# Black Text Skin
with (FONT_DIR / "font.json").open(encoding="UTF-8") as f:
    font_data = json.load(f)


SUPPORTED_GRADIENT_DIRECTIONS = {
    "vertical",
    "horizontal",
    "diagonal-down",
    "diagonal-up",
}


def _rgba_color(value) -> tuple[int, int, int, int]:
    """Validate and normalize one JSON RGBA color."""
    if (
        not isinstance(value, (list, tuple))
        or len(value) != 4
        or not all(isinstance(component, (int, float)) for component in value)
    ):
        raise ValueError("A color must be an [R, G, B, A] array.")

    color = tuple(int(component) for component in value)
    if any(component < 0 or component > 255 for component in color):
        raise ValueError("RGBA components must be between 0 and 255.")
    return color


def _parse_text_color(value):
    """Accept the legacy RGBA form or two-or-more RGBA gradient stops."""
    try:
        return _rgba_color(value), None
    except ValueError:
        pass

    if not isinstance(value, (list, tuple)) or len(value) < 2:
        raise ValueError(
            "A gradient must contain at least two [R, G, B, A] colors."
        )
    return None, tuple(_rgba_color(stop) for stop in value)


def _parse_text_shadow(value):
    """Parse [offset_x, offset_y, blur, R, G, B, A] or disabled/null."""
    if value is None:
        return None
    if (
        not isinstance(value, (list, tuple))
        or len(value) != 7
        or not all(isinstance(component, (int, float)) for component in value)
    ):
        raise ValueError(
            "A shadow must be [X, Y, blur, R, G, B, A] or null."
        )

    offset_x, offset_y, blur, *rgba = value
    if not -10 <= offset_x <= 10 or not -10 <= offset_y <= 10:
        raise ValueError("Shadow offsets must be between -10 and 10.")
    if not 0 <= blur <= 10:
        raise ValueError("Shadow blur must be between 0 and 10.")
    return float(offset_x), float(offset_y), float(blur), _rgba_color(rgba)


def _interpolate_gradient_color(colors, progress):
    """Interpolate across any number of evenly spaced gradient colors."""
    scaled = max(0.0, min(1.0, progress)) * (len(colors) - 1)
    start_index = min(int(scaled), len(colors) - 2)
    local_progress = scaled - start_index
    start = colors[start_index]
    end = colors[start_index + 1]
    return tuple(
        round(first + (second - first) * local_progress)
        for first, second in zip(start, end)
    )


def _create_text_gradient(size, colors, direction):
    """Create a card-sized RGBA gradient used through a text mask."""
    normalized_direction = str(direction or "vertical").strip().casefold()
    if normalized_direction not in SUPPORTED_GRADIENT_DIRECTIONS:
        normalized_direction = "vertical"

    width, height = size
    width_scale = max(1, width - 1)
    height_scale = max(1, height - 1)

    # The common vertical/horizontal cases only need a one-pixel strip,
    # avoiding a full Python pixel loop for every text field.
    if normalized_direction in {"vertical", "horizontal"}:
        length = height if normalized_direction == "vertical" else width
        scale = max(1, length - 1)
        strip_colors = [
            _interpolate_gradient_color(colors, index / scale)
            for index in range(length)
        ]
        strip_size = (
            (1, height)
            if normalized_direction == "vertical"
            else (width, 1)
        )
        strip = Image.new("RGBA", strip_size)
        try:
            strip.putdata(strip_colors)
            return strip.resize(size, Image.Resampling.NEAREST)
        finally:
            strip.close()

    pixels = []
    for y in range(height):
        y_progress = y / height_scale
        for x in range(width):
            x_progress = x / width_scale
            if normalized_direction == "diagonal-down":
                progress = (x_progress + y_progress) / 2
            elif normalized_direction == "diagonal-up":
                progress = (x_progress + (1 - y_progress)) / 2
            pixels.append(_interpolate_gradient_color(colors, progress))

    gradient = Image.new("RGBA", size)
    gradient.putdata(pixels)
    return gradient


def _draw_text_shadow(
    image,
    position,
    text,
    *,
    shadow,
    font,
    stroke_width,
):
    """Draw an optional blurred shadow underneath the configured text."""
    parsed_shadow = _parse_text_shadow(shadow)
    if parsed_shadow is None:
        return

    offset_x, offset_y, blur, shadow_color = parsed_shadow
    shadow_position = (
        position[0] + offset_x,
        position[1] + offset_y,
    )
    mask = Image.new("L", image.size, 0)
    blurred_mask = None
    shadow_layer = None
    alpha_layer = None
    try:
        ImageDraw.Draw(mask).text(
            shadow_position,
            text,
            fill=255,
            font=font,
            stroke_width=stroke_width,
            stroke_fill=255,
        )
        if blur:
            blurred_mask = mask.filter(ImageFilter.GaussianBlur(blur))
            active_mask = blurred_mask
        else:
            active_mask = mask

        shadow_layer = Image.new(
            "RGBA",
            image.size,
            (*shadow_color[:3], 0),
        )
        alpha_layer = Image.new("L", image.size, shadow_color[3])
        shadow_layer.putalpha(ImageChops.multiply(active_mask, alpha_layer))
        image.alpha_composite(shadow_layer)
    finally:
        mask.close()
        if blurred_mask is not None:
            blurred_mask.close()
        if shadow_layer is not None:
            shadow_layer.close()
        if alpha_layer is not None:
            alpha_layer.close()


def draw_configured_text(
    image,
    draw,
    position,
    text,
    *,
    color,
    direction="vertical",
    shadow=None,
    font,
    stroke_width=0,
    stroke_fill=(0, 0, 0, 255),
):
    """Draw legacy solid text or gradient text from the same color setting."""
    # Shadows are composited first so the existing outline and glyph remain
    # crisp above them. A missing/null setting has zero visual effect.
    _draw_text_shadow(
        image,
        position,
        text,
        shadow=shadow,
        font=font,
        stroke_width=stroke_width,
    )
    solid_color, gradient_colors = _parse_text_color(color)
    if solid_color is not None:
        # Keep the original ImageDraw path unchanged for all existing skins.
        draw.text(
            position,
            text,
            fill=solid_color,
            font=font,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
        )
        return

    # Draw the configured outline first, then replace only the glyph fill
    # through a mask. This keeps the outline a predictable solid color.
    draw.text(
        position,
        text,
        fill=gradient_colors[0],
        font=font,
        stroke_width=stroke_width,
        stroke_fill=stroke_fill,
    )
    mask = Image.new("L", image.size, 0)
    gradient = None
    try:
        ImageDraw.Draw(mask).text(position, text, fill=255, font=font)
        gradient = _create_text_gradient(
            image.size,
            gradient_colors,
            direction,
        )
        gradient.putalpha(
            ImageChops.multiply(gradient.getchannel("A"), mask)
        )
        image.alpha_composite(gradient)
    finally:
        mask.close()
        if gradient is not None:
            gradient.close()


def fontsize(type, font):
    if type == "name":
        if font in ["brush", "chalk", "legend", "square", "typewriter"]:
            return 26
        elif font in ["lcd", "minecraft", "serif", "starcraft", "luxury", "nature", "handwrite", "dragon", "ocean", "math", "wanted", "metal", "slay"]:
            return 24
        elif font in ["fluid", "paper", "gothic", "tedne"]:
            return 22
        else:
            return 20
    
    elif type == "xp":
        if font in ["fluid", "lcd", "luxury", "minecraft", "brush", "stencil", "legend", "square", "serif", "math"]:
            return 18
        elif font in ["condense", "handwrite", "stella", "drg", "metal", "distort"]:
            return 20
        elif font in ["jelly"]:
            return 14
        else:
            return 16

def textAltitude(type, font):
    if type == "name":
        if font in ["brush", "legend", "math"]:
            return -6
        elif font in ["chalk", "luxury", "lcd", "handwrite", "nature", "square", "dragon", "modern", "wanted", "jelly"]:
            return -3
        else:
            return 0
        
    elif type == "xp":
        if font in ["pixel", "minecraft", "stencil", "starcraft", "legend", "gothic", "modern", "legacy","paradox"]:
            return 2
        elif font in ["sans", "jelly"]:
            return 3
        elif font in ["fluid"]:
            return 4
        elif font in ["nature"]:
            return 5
        elif font in ["lcd", "stella", "math"]:
            return -1
        else:
            return 0


# Ranking View
class PaginationView(discord.ui.View):
    current_page: int = 1
    sep: int = 10
    user = None

    def __init__(self, **kwargs):
        super().__init__(timeout=kwargs.get("timeout"))
        self.data = kwargs.get("data", [])
        self.sep = kwargs.get("sep", 10)
        self.user = kwargs.get("user")
        self.current_page = kwargs.get("page", 1)
        self.myrank = kwargs.get("myrank")

    async def on_timeout(self):
        self.data.clear()
        self.message = None

    @property
    def total_pages(self) -> int:
        if not self.data:
            return 1
        return (len(self.data) - 1) // self.sep + 1

    async def send(self, ctx):
        self.message = await ctx.send(
            i18n.t(ctx.author, "reply.complete", name=q.readTag(ctx.author)),
            view=self)
        await self.update_message(self.get_current_page_data(), self.user)

    def create_embed(self, data, user):
        myrank = self.myrank if self.myrank is not None else q.xpMyRanking(user)
        total = len(self.data)

        embed = discord.Embed(
            title=i18n.t(user, "cmd.14.t001"),
            description=i18n.t(user, "cmd.14.t002", myrank=myrank, total=total),
            color=0xE2F6CA
        )

        embed.set_thumbnail(url=user.display_avatar.url)

        base_index = (self.current_page - 1) * self.sep
        for offset, item in enumerate(data, start=1):
            rank_num = base_index + offset

            embed.add_field(
                name="{} {}#{}".format(
                    etc.numFont(rank_num),
                    item[2],
                    str(item[1]).zfill(4)
                ),
                value="{}　•　{:,d} XP".format(
                    etc.lvicon(etc.level(item[3])),
                    item[3]
                ),
                inline=False
            )

        embed.set_footer(
            text=i18n.t(user, "cmd.14.t003", current=self.current_page, total=self.total_pages),
            icon_url=""
        )

        return embed

    async def update_message(self, data, user):
        self.update_buttons()
        await self.message.edit(embed=self.create_embed(data, user), view=self)

    def update_buttons(self):
        if self.current_page == 1:
            self.first_page_button.disabled = True
            self.prev_button.disabled = True
            self.first_page_button.style = discord.ButtonStyle.gray
            self.prev_button.style = discord.ButtonStyle.gray
        else:
            self.first_page_button.disabled = False
            self.prev_button.disabled = False
            self.first_page_button.style = discord.ButtonStyle.green
            self.prev_button.style = discord.ButtonStyle.primary

        if self.current_page == self.total_pages:
            self.next_button.disabled = True
            self.last_page_button.disabled = True
            self.last_page_button.style = discord.ButtonStyle.gray
            self.next_button.style = discord.ButtonStyle.gray
        else:
            self.next_button.disabled = False
            self.last_page_button.disabled = False
            self.last_page_button.style = discord.ButtonStyle.green
            self.next_button.style = discord.ButtonStyle.primary

    def get_current_page_data(self):
        from_item = (self.current_page - 1) * self.sep
        until_item = min(from_item + self.sep, len(self.data))
        return self.data[from_item:until_item]

    #맨 앞 페이지로 이동
    @discord.ui.button(label="|<", style=discord.ButtonStyle.green)
    async def first_page_button(self, interaction: discord.Interaction,
                                button: discord.ui.Button):
        if interaction.user == self.user:
            await interaction.response.defer()
            self.current_page = 1

            await self.update_message(self.get_current_page_data(), self.user)

    #앞 뒷 페이지로 이동
    @discord.ui.button(label="<", style=discord.ButtonStyle.primary)
    async def prev_button(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
        if interaction.user == self.user:
            await interaction.response.defer()
            self.current_page -= 1
            await self.update_message(self.get_current_page_data(), self.user)

    #뒷 페이지로 이동
    @discord.ui.button(label=">", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
        if interaction.user == self.user:
            await interaction.response.defer()
            self.current_page += 1
            await self.update_message(self.get_current_page_data(), self.user)

    #맨 뒷 페이지로 이동
    @discord.ui.button(label=">|", style=discord.ButtonStyle.green)
    async def last_page_button(self, interaction: discord.Interaction,
                               button: discord.ui.Button):
        if interaction.user == self.user:
            await interaction.response.defer()
            self.current_page = self.total_pages
            await self.update_message(self.get_current_page_data(), self.user)


class UserProfile(commands.Cog):

    def __init__(self, client: commands.Bot):
        self.client = client
        self.render_semaphore = asyncio.Semaphore(2)

    # [id: 11, 20] rankcard generator
    async def rankcard_image(
        self,
        *,
        user: discord.Member,
        skin_id: int | str,
        preview: bool,
    ) -> io.BytesIO:
        async with self.render_semaphore:
            return await self._rankcard_image(
                user=user,
                skin_id=skin_id,
                preview=preview,
            )

    async def _rankcard_image(
        self,
        *,
        user: discord.Member,
        skin_id: int | str,
        preview: bool,
    ) -> io.BytesIO:
        dname = "@" + str(user)
        if dname.endswith("#0"):
            dname = dname[:-2]

        name = q.readNick(user)
        discrim = '#' + q.readDiscrim(user)
        money = '${:,d}'.format(q.readMoney(user))

        xp = q.readXp(user)
        lv = etc.level(xp)

        if lv >= etc.maxLevel():
            xp1 = 1
            xp2 = 1
        else:
            xp1 = xp - etc.need_exp(lv - 1)
            xp2 = etc.need_exp(lv) - etc.need_exp(lv - 1)

        queue_skin = None
        normal_skin_id = None
        if isinstance(skin_id, str) and skin_id.strip().casefold().startswith("t"):
            queue_id = catalog.normalize_queue_id(skin_id)
            queue_skin = catalog.load_queue_skin(queue_id)
            if queue_skin is None:
                raise ValueError(f"Queue skin {queue_id} does not exist.")
            background_path = queue_skin["_path"] / "rankcard.png"
            bar_path = queue_skin["_path"] / "bar.png"
            font_option = queue_skin["_font"]
        else:
            normal_skin_id = int(skin_id)
            background_path = (
                RANKCARD_DIR
                / "rankcard_skins"
                / f"rankcard{normal_skin_id}.png"
            )
            bar_path = (
                RANKCARD_DIR / "bar_skins" / f"bar{normal_skin_id}.png"
            )
            font_option = font_data['profile'][f'skin{normal_skin_id}']

        background_image = Image.open(background_path).convert('RGBA')
        bar_cover_image = Image.open(bar_path).convert('RGBA')
        emblem_image = Image.open(
            RANKCARD_DIR / "emblem" / f"{lv}.png"
        ).convert('RGBA')

        name_outline_color = tuple(font_option['nametext-outline-color'])
        xp_outline_color = tuple(font_option['xp-outline-color'])
        if normal_skin_id == 214:
            image, bar_cover_image, skin_214_color = _apply_skin_214_effects(
                background_image,
                bar_cover_image,
            )
            name_outline_color = skin_214_color
            xp_outline_color = skin_214_color
        else:
            image = background_image.copy()

        if normal_skin_id == 139:
            image = _apply_skin_139_clock(image)

        emblem_image = emblem_image.resize((72, 72))
        bar_cover_image = bar_cover_image.crop((0, 0, 368 * xp1 / xp2, 8))

        rank = emblem_image.copy()
        bar = bar_cover_image.copy()

        avatar_image = await _load_avatar_image(user, normal_skin_id)
        special_overlay_path = (
            RANKCARD_DIR / "special" / f"image{normal_skin_id}.png"
            if normal_skin_id is not None
            else None
        )
        has_special_overlay = (
            special_overlay_path is not None
            and special_overlay_path.is_file()
        )
        if has_special_overlay:
            try:
                image.alpha_composite(avatar_image, (8, 8))
            finally:
                avatar_image.close()
            with Image.open(special_overlay_path) as source:
                special_overlay = source.convert("RGBA")
            try:
                image.alpha_composite(special_overlay, (0, 0))
            finally:
                special_overlay.close()

        draw = ImageDraw.Draw(image)

        text_xp = f"{xp1:,d} / {xp2:,d} | {100 * xp1 / xp2:.2f}% | {xp:,d}"
        emblem = etc.emblemName(lv)

        font_name = ImageFont.truetype(
            FONT_DIR / font_option["font"] / "name.ttf",
            fontsize("name", font_option['font'])
        )
        font_dname = ImageFont.truetype(FONT_DIR / "emblem.ttf", 16)
        font_emblem = ImageFont.truetype(FONT_DIR / "emblem.ttf", 14)
        font_xp = ImageFont.truetype(
            FONT_DIR / font_option["font"] / "xp.ttf",
            fontsize("xp", font_option['font']) - 2
        )

        x1 = 384 - 8 - (draw.textlength(str(name), font=font_name) +
                        draw.textlength(str(discrim), font=font_name))
        y1 = 8 + textAltitude("name", font_option['font'])

        x5 = 384 - 8 - draw.textlength(str(discrim), font=font_name)
        y5 = 8 + textAltitude("name", font_option['font'])

        x2 = 384 - 8 - draw.textlength(dname, font=font_dname)
        y2 = 32

        x3 = 384 - 8 - draw.textlength(emblem, font=font_emblem)
        y3 = 96

        x4 = (384 - draw.textlength(text_xp, font=font_xp)) / 2
        y4 = 124 + textAltitude("xp", font_option['font'])

        x6 = 384 - 8 - draw.textlength(money, font=font_xp)
        y6 = 80

        # A single RGBA array uses the legacy solid renderer. A list of RGBA
        # arrays enables the optional gradient format documented in font.json.
        draw_configured_text(
            image,
            draw,
            (x1, y1),
            str(name),
            color=font_option['name-color'],
            direction=font_option.get('name-color-direction', 'vertical'),
            shadow=font_option.get('nametext-shadow'),
            font=font_name,
            stroke_width=font_option['nametext-outline-width'],
            stroke_fill=name_outline_color
        )
        draw_configured_text(
            image,
            draw,
            (x5, y5),
            str(discrim),
            color=font_option['discrim-color'],
            direction=font_option.get('discrim-color-direction', 'vertical'),
            shadow=font_option.get('nametext-shadow'),
            font=font_name,
            stroke_width=font_option['nametext-outline-width'],
            stroke_fill=name_outline_color
        )
        draw_configured_text(
            image,
            draw,
            (x2, y2),
            dname,
            color=font_option['discrim-color'],
            direction=font_option.get('discrim-color-direction', 'vertical'),
            shadow=font_option.get('nametext-shadow'),
            font=font_dname,
            stroke_width=font_option['nametext-outline-width'],
            stroke_fill=name_outline_color
        )
        draw.text(
            (x3, y3), emblem,
            fill=(255, 255, 255, 255),
            font=font_emblem,
            stroke_width=1,
            stroke_fill=(0, 0, 0, 255)
        )
        draw_configured_text(
            image,
            draw,
            (x4, y4),
            text_xp,
            color=font_option['xp-color'],
            direction=font_option.get('xp-color-direction', 'vertical'),
            shadow=font_option.get('xp-shadow'),
            font=font_xp,
            stroke_width=font_option['xp-outline-width'],
            stroke_fill=xp_outline_color
        )
        draw_configured_text(
            image,
            draw,
            (x6, y6),
            money,
            color=font_option['xp-color'],
            direction=font_option.get('xp-color-direction', 'vertical'),
            shadow=font_option.get('xp-shadow'),
            font=font_xp,
            stroke_width=font_option['xp-outline-width'],
            stroke_fill=xp_outline_color
        )

        if not has_special_overlay:
            try:
                image.paste(avatar_image, (8, 8), mask=avatar_image)
            finally:
                avatar_image.close()
        image.paste(rank, (104, 40), mask=rank)
        image.paste(bar, (8, 116), mask=bar)

        if preview:
            wm = Image.open(
                RANKCARD_DIR / "watermark.png"
            ).convert('RGBA')
            image.paste(wm, (0, 0), mask=wm)

        buffer_output = io.BytesIO()
        image.save(buffer_output, format='PNG')
        buffer_output.seek(0)
        return buffer_output

    # Profile [ID: 11]
    @commands.cooldown(rate=1, per=15, type=commands.BucketType.user)
    @commands.hybrid_command(
        name=app_commands.locale_str("profile", key="cmd.11.name"),
        description=app_commands.locale_str("Show user's profile", key="cmd.11.desc"),
        aliases=["프로필"]
    )
    @discord.app_commands.describe(
        user="User ID, member mention, or nickname tag"
    )
    async def profile(self, ctx, user: str = None):
        try:
            user = await resolve_discord_user(ctx, user)
        except UserResolutionError:
            await ctx.reply(i18n.t(ctx.author, "common.invalid_user"))
            return

        try:
            skin_id = q.readSkin(user)
        except Exception:
            skin_id = 1

        buffer_output = await self.rankcard_image(user=user, skin_id=skin_id, preview=False)

        try:
            await ctx.reply(
                i18n.t(ctx.author, "cmd.11.t001", username=q.readTag(user)),
                file=discord.File(buffer_output, 'myimage.png')
            )
        finally:
            buffer_output.close()

    @profile.error
    async def profile_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    # Emblem [ID: 12]
    @commands.cooldown(rate=1, per=20, type=commands.BucketType.user)
    @commands.hybrid_command(
        name=app_commands.locale_str("emblem", key="cmd.12.name"),
        description=app_commands.locale_str("Show emblem icons", key="cmd.12.desc"),
        aliases=["계급장"]
    )
    #@discord.app_commands.describe(lvl='Choose emblem level to show (default: your level)')
    async def emblem(self, ctx, lvl=None):
        xp = q.readXp(ctx.author)
        user_lv = etc.level(xp)

        if lvl == None:
            lv = user_lv

        else:
            try:
                lv = int(lvl)
            except:
                await ctx.reply(i18n.t(ctx.author, "cmd.12.t001"))

        if lvl == "1":
            emblem = i18n.t(ctx.author, "cmd.12.t002", ename=etc.emblemName(1))
            emblem_image = Image.open(
                    RANKCARD_DIR / "emblem" / "1.png").convert('RGBA')
            emblem_image = emblem_image.resize((128, 128))
            wm = Image.open(RANKCARD_DIR / "watermark.png").convert('RGBA')
            wm = wm.resize((96, 54))

            #duplicate image
            image = emblem_image.copy()

            # create object for drawing
            draw = ImageDraw.Draw(image)
            image.paste(wm, (16, 74), mask=wm)

            #sending image
            buffer_output = io.BytesIO()
            image.save(buffer_output, format='PNG')
            buffer_output.seek(0)

            await ctx.reply(emblem, file=discord.File(buffer_output, 'myimage.png'))

        else:

            if int(lv) <= etc.maxLevel() and int(lv) > 0:

                inf0 = etc.need_exp(lv - 1)
                inf1 = etc.need_exp(lv - 1) - etc.need_exp(lv - 2)

                ptxt = "{:,d} / {:,d} ({:.2f}%)".format(
                    xp, inf0, 100 * (xp / inf0))

                if xp >= inf0:
                    ptxt = i18n.t(ctx.author, "cmd.12.t003")

                tlv = int(lv)
                icon = RANKCARD_DIR / "emblem" / f"{lv}.png"
                emblem = i18n.t(ctx.author, "cmd.12.t004", ename=etc.emblemName(tlv), info0=inf0, info1=inf1, ptxt=ptxt)
                
                emblem_image = Image.open(
                    RANKCARD_DIR / "emblem" / f"{lv}.png").convert('RGBA')
                emblem_image = emblem_image.resize((128, 128))
                wm = Image.open(RANKCARD_DIR / "watermark.png").convert('RGBA')
                wm = wm.resize((96, 54))

                #duplicate image
                image = emblem_image.copy()

                # create object for drawing
                draw = ImageDraw.Draw(image)
                image.paste(wm, (16, 74), mask=wm)

                #sending image
                buffer_output = io.BytesIO()
                image.save(buffer_output, format='PNG')
                buffer_output.seek(0)

                await ctx.reply(emblem, file=discord.File(buffer_output, 'myimage.png'))

            else:
                await ctx.reply(
                    i18n.t(ctx.author, "cmd.12.t005")
                )

    @emblem.error
    async def emblem_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    # My Ranking [ID: 13]
    @commands.cooldown(rate=1, per=20, type=commands.BucketType.user)
    @commands.hybrid_command(
        name=app_commands.locale_str("myrank", key="cmd.13.name"),
        description=app_commands.locale_str("Show your global ranking", key="cmd.13.desc"),
        aliases=["개인랭킹"]
    )
    async def myrank(self, ctx, server="global"):
        if server in ["global", "전역"]:
            rank = q.xpMyRanking(ctx.author)
            xp = q.readXp(ctx.author)
            lv = etc.level(xp)
            await ctx.reply(
                i18n.t(ctx.author, "cmd.13.t001", user=q.readTag(ctx.author), rank=etc.numFont(rank), total=q.userCount(), icon=etc.lvicon(lv), lv=lv,
                        xp=xp)
            )

    @myrank.error
    async def myrank_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    # Ranking [ID: 14]
    @commands.cooldown(rate=1, per=20, type=commands.BucketType.user)
    @commands.hybrid_command(
        name=app_commands.locale_str("ranking", key="cmd.14.name"),
        description=app_commands.locale_str("Show XP leaderboard of this bot", key="cmd.14.desc"),
        aliases=["전체랭킹"]
    )
    #@discord.app_commands.describe(server="Select server (default: global)",page="Page number")
    async def ranking(self, ctx, page: int = 1):
        pagination_view = PaginationView(timeout=300)
        pagination_view.data = q.xpRanking()
        pagination_view.user = ctx.author
        pagination_view.current_page = page
        await pagination_view.send(ctx)

    @ranking.error
    async def ranking_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    # Preview [ID: 20]
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)
    @commands.hybrid_command(
        name=app_commands.locale_str("preview", key="cmd.20.name"),
        description=app_commands.locale_str("Previewing profile skins", key="cmd.20.desc"),
        aliases=["미리보기"]
    )
    async def preview(self, ctx, skin_id: str = "1"):

        user = ctx.author

        try:
            normalized_id: int | str
            if skin_id.strip().casefold().startswith("t"):
                normalized_id = catalog.normalize_queue_id(skin_id)
                if catalog.load_queue_skin(normalized_id) is None:
                    raise ValueError
            else:
                normalized_id = int(skin_id)
                if normalized_id < 1:
                    raise ValueError

            buffer_output = await self.rankcard_image(
                user=user,
                skin_id=normalized_id,
                preview=True,
            )
        except (ValueError, KeyError, FileNotFoundError, json.JSONDecodeError):
            await ctx.reply(
                i18n.t(ctx.author, "cmd.20.invalid_id", skin_id=skin_id)
            )
            return

        try:
            await ctx.reply(
                i18n.t(
                    ctx.author,
                    "cmd.20.complete",
                    name=q.readTag(ctx.author),
                    skin_id=normalized_id,
                ),
                file=discord.File(buffer_output, 'myimage.png')
            )
        finally:
            buffer_output.close()

    @preview.error
    async def preview_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = i18n.t(ctx.author, "reply.ratelimit", second=error.retry_after)
            await ctx.send(msg)
        else:
            raise error

async def setup(client):
    await client.add_cog(UserProfile(client))
