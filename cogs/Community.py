from __future__ import annotations

import asyncio
import io
import ipaddress
import json
import shutil
import socket
import tempfile
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse
from zoneinfo import ZoneInfo

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from PIL import Image, UnidentifiedImageError

import fcts.i18n_runtime as i18n
import fcts.skin_catalog as catalog


MAX_IMAGE_BYTES = 8 * 1024 * 1024
MAX_IMAGE_PIXELS = 40_000_000
REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=20, connect=8, sock_read=12)
DEFAULT_FONT = {
    "font": "legacy",
    "name-color": [255, 255, 255, 255],
    "discrim-color": [204, 204, 204, 255],
    "nametext-outline-width": 0,
    "nametext-outline-color": [0, 0, 0, 255],
    "xp-color": [255, 255, 255, 255],
    "xp-outline-width": 0,
    "xp-outline-color": [0, 0, 0, 255],
}


@dataclass
class WorkshopDraft:
    owner_id: int
    queue_id: str | None = None
    skin: dict = field(default_factory=dict)
    font: dict = field(default_factory=lambda: {
        key: list(value) if isinstance(value, list) else value
        for key, value in DEFAULT_FONT.items()
    })
    rankcard_url: str = ""
    bar_background_url: str = ""
    bar_url: str = ""

    @property
    def editing(self) -> bool:
        return self.queue_id is not None


def _text_value(value, default="") -> str:
    if value is None:
        return default
    return str(value)


def _rgba_text(value) -> str:
    return json.dumps(value, ensure_ascii=False)


def _parse_rgba(value: str, field_name: str) -> list[int]:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as error:
        raise ValueError(f"{field_name}: [R, G, B, A] 형식으로 입력해 주세요.") from error

    if (
        not isinstance(parsed, list)
        or len(parsed) != 4
        or any(isinstance(item, bool) or not isinstance(item, int) for item in parsed)
        or any(item < 0 or item > 255 for item in parsed)
    ):
        raise ValueError(f"{field_name}: 0~255 정수 4개를 [R, G, B, A] 형식으로 입력해 주세요.")
    return parsed


def _parse_outline_width(value: str, field_name: str) -> int:
    try:
        width = int(value)
    except ValueError as error:
        raise ValueError(f"{field_name}: 정수만 입력할 수 있습니다.") from error
    if not 0 <= width <= 10:
        raise ValueError(f"{field_name}: 0~10 사이의 정수만 입력할 수 있습니다.")
    return width


def _validate_metadata(
    name: str,
    desc: str,
    unlock_type: str,
    unlock_value: str,
    keyword: str,
) -> dict:
    name = name.strip()
    desc = desc.strip()
    unlock_type = unlock_type.strip().casefold()
    unlock_value = unlock_value.strip()
    keyword = keyword.strip()

    if not name or not desc or not keyword:
        raise ValueError("스킨 이름, 설명, 키워드는 비워 둘 수 없습니다.")
    if len(name) > 100 or len(desc) > 600 or len(keyword) > 100:
        raise ValueError("스킨 이름·설명·키워드의 허용 길이를 초과했습니다.")
    if any(
        ord(character) < 32
        for character in name + keyword + unlock_value
    ):
        raise ValueError("스킨 이름, 키워드, 해금 기준에는 제어 문자를 사용할 수 없습니다.")
    if unlock_type not in {"money", "level", "code"}:
        raise ValueError("해금 조건 유형은 money, level, code 중 하나여야 합니다.")

    if unlock_type == "money":
        if not unlock_value.isdigit() or not 1 <= int(unlock_value) <= 99_999_999:
            raise ValueError("money 해금 기준은 1~99,999,999 사이의 정수여야 합니다.")
        normalized_value: int | str = int(unlock_value)
    elif unlock_type == "level":
        if not unlock_value.isdigit() or not 1 <= int(unlock_value) <= 300:
            raise ValueError("level 해금 기준은 1~300 사이의 정수여야 합니다.")
        normalized_value = int(unlock_value)
    else:
        if len(unlock_value) < 4:
            raise ValueError("code 해금 기준은 4글자 이상의 문자열이어야 합니다.")
        normalized_value = unlock_value

    return {
        "name": name,
        "desc": desc,
        "unlock_type": unlock_type,
        "unlock_val": normalized_value,
        "keyword": keyword,
    }


async def _validate_public_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("이미지 주소는 http:// 또는 https://로 시작하는 직접 링크여야 합니다.")
    if parsed.username or parsed.password:
        raise ValueError("사용자 정보가 포함된 이미지 주소는 사용할 수 없습니다.")

    try:
        addresses = await asyncio.to_thread(
            socket.getaddrinfo,
            parsed.hostname,
            parsed.port or (443 if parsed.scheme == "https" else 80),
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror as error:
        raise ValueError("이미지 주소의 서버를 찾을 수 없습니다.") from error

    for address in addresses:
        ip = ipaddress.ip_address(address[4][0])
        if not ip.is_global:
            raise ValueError("내부망 또는 로컬 주소의 이미지는 사용할 수 없습니다.")
    return url


async def _download_image(
    session: aiohttp.ClientSession,
    url: str,
    field_name: str,
) -> Image.Image:
    current_url = url.strip()
    if not current_url:
        raise ValueError(f"{field_name} 이미지 주소가 비어 있습니다.")

    for _ in range(4):
        await _validate_public_url(current_url)
        async with session.get(current_url, allow_redirects=False) as response:
            if 300 <= response.status < 400 and response.headers.get("Location"):
                current_url = urljoin(current_url, response.headers["Location"])
                continue
            if response.status != 200:
                raise ValueError(f"{field_name} 이미지를 받을 수 없습니다. (HTTP {response.status})")

            content_type = (
                response.headers.get("Content-Type", "")
                .split(";", 1)[0]
                .strip()
                .casefold()
            )
            if not content_type.startswith("image/"):
                raise ValueError(f"{field_name} 주소가 이미지 파일을 가리키지 않습니다.")

            content_length = response.content_length
            if content_length is not None and content_length > MAX_IMAGE_BYTES:
                raise ValueError(f"{field_name} 이미지는 8 MiB 이하여야 합니다.")

            chunks = []
            total = 0
            async for chunk in response.content.iter_chunked(64 * 1024):
                total += len(chunk)
                if total > MAX_IMAGE_BYTES:
                    raise ValueError(f"{field_name} 이미지는 8 MiB 이하여야 합니다.")
                chunks.append(chunk)

        try:
            with Image.open(io.BytesIO(b"".join(chunks))) as image:
                if image.width * image.height > MAX_IMAGE_PIXELS:
                    raise ValueError(f"{field_name} 이미지의 해상도가 너무 큽니다.")
                image.load()
                converted = image.convert("RGBA")
        except (
            Image.DecompressionBombError,
            UnidentifiedImageError,
            OSError,
        ) as error:
            raise ValueError(f"{field_name} 파일을 이미지로 해석할 수 없습니다.") from error

        return converted

    raise ValueError(f"{field_name} 이미지 주소가 너무 많이 리디렉션되었습니다.")


class OwnerOnlyView(discord.ui.View):
    def __init__(self, owner_id: int, *, timeout: float = 300):
        super().__init__(timeout=timeout)
        self.owner_id = owner_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.owner_id:
            return True
        await interaction.response.send_message(
            i18n.t(interaction.user, "cmd.16.owner_only"),
            ephemeral=True,
        )
        return False


class ContinueView(OwnerOnlyView):
    def __init__(self, draft: WorkshopDraft, modal_type, label: str):
        super().__init__(draft.owner_id)
        self.draft = draft
        self.modal_type = modal_type
        self.continue_button.label = label

    @discord.ui.button(label="Continue", style=discord.ButtonStyle.primary)
    async def continue_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        await interaction.response.send_modal(
            self.modal_type(self.draft, interaction.user)
        )


class MetadataModal(discord.ui.Modal):
    def __init__(self, draft: WorkshopDraft, user):
        super().__init__(
            title=i18n.t(user, "cmd.16.modal.metadata"),
            timeout=600,
        )
        self.draft = draft
        skin = draft.skin
        self.name_input = discord.ui.TextInput(
            label=i18n.t(user, "cmd.16.field.name"),
            required=True,
            max_length=100,
            default=_text_value(skin.get("name")),
        )
        self.desc_input = discord.ui.TextInput(
            label=i18n.t(user, "cmd.16.field.desc"),
            style=discord.TextStyle.long,
            required=True,
            max_length=600,
            default=_text_value(skin.get("desc")),
        )
        self.unlock_type_input = discord.ui.TextInput(
            label=i18n.t(user, "cmd.16.field.unlock_type"),
            required=True,
            max_length=5,
            default=_text_value(skin.get("unlock_type"), "money"),
        )
        self.unlock_value_input = discord.ui.TextInput(
            label=i18n.t(user, "cmd.16.field.unlock_val"),
            required=True,
            max_length=100,
            default=_text_value(skin.get("unlock_val"), "1"),
        )
        self.keyword_input = discord.ui.TextInput(
            label=i18n.t(user, "cmd.16.field.keyword"),
            required=True,
            max_length=100,
            default=_text_value(skin.get("keyword")),
        )
        for item in (
            self.name_input,
            self.desc_input,
            self.unlock_type_input,
            self.unlock_value_input,
            self.keyword_input,
        ):
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            self.draft.skin.update(_validate_metadata(
                self.name_input.value,
                self.desc_input.value,
                self.unlock_type_input.value,
                self.unlock_value_input.value,
                self.keyword_input.value,
            ))
        except ValueError as error:
            await interaction.response.send_message(str(error), ephemeral=True)
            return

        view = ContinueView(
            self.draft,
            AssetModal,
            i18n.t(interaction.user, "cmd.16.button.assets"),
        )
        await interaction.response.send_message(
            i18n.t(interaction.user, "cmd.16.step_complete", current=1, total=4),
            view=view,
            ephemeral=True,
        )


class AssetModal(discord.ui.Modal):
    def __init__(self, draft: WorkshopDraft, user):
        super().__init__(
            title=i18n.t(user, "cmd.16.modal.assets"),
            timeout=600,
        )
        self.draft = draft
        edit_note = (
            i18n.t(user, "cmd.16.field.keep_image") if draft.editing else ""
        )
        self.rankcard_input = discord.ui.TextInput(
            label=i18n.t(user, "cmd.16.field.rankcard_url"),
            placeholder=edit_note or i18n.t(user, "cmd.16.field.rankcard_size"),
            required=not draft.editing,
            max_length=1000,
        )
        self.background_input = discord.ui.TextInput(
            label=i18n.t(user, "cmd.16.field.background_url"),
            placeholder=edit_note or i18n.t(user, "cmd.16.field.bar_size"),
            required=False,
            max_length=1000,
        )
        self.bar_input = discord.ui.TextInput(
            label=i18n.t(user, "cmd.16.field.bar_url"),
            placeholder=edit_note or i18n.t(user, "cmd.16.field.bar_size"),
            required=not draft.editing,
            max_length=1000,
        )
        self.font_input = discord.ui.TextInput(
            label=i18n.t(user, "cmd.16.field.font"),
            placeholder=", ".join(catalog.font_families())[:100],
            required=True,
            max_length=50,
            default=_text_value(draft.font.get("font"), "legacy"),
        )
        self.name_color_input = discord.ui.TextInput(
            label=i18n.t(user, "cmd.16.field.name_color"),
            required=True,
            max_length=24,
            default=_rgba_text(draft.font["name-color"]),
        )
        for item in (
            self.rankcard_input,
            self.background_input,
            self.bar_input,
            self.font_input,
            self.name_color_input,
        ):
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction):
        fonts = {name.casefold(): name for name in catalog.font_families()}
        requested_font = self.font_input.value.strip().casefold()
        if requested_font not in fonts:
            await interaction.response.send_message(
                i18n.t(
                    interaction.user,
                    "cmd.16.invalid_font",
                    fonts=", ".join(fonts.values()),
                ),
                ephemeral=True,
            )
            return

        try:
            name_color = _parse_rgba(self.name_color_input.value, "이름 색상")
        except ValueError as error:
            await interaction.response.send_message(str(error), ephemeral=True)
            return

        self.draft.rankcard_url = self.rankcard_input.value.strip()
        self.draft.bar_background_url = self.background_input.value.strip()
        self.draft.bar_url = self.bar_input.value.strip()
        self.draft.font["font"] = fonts[requested_font]
        self.draft.font["name-color"] = name_color

        view = ContinueView(
            self.draft,
            IdentityStyleModal,
            i18n.t(interaction.user, "cmd.16.button.style"),
        )
        await interaction.response.send_message(
            i18n.t(interaction.user, "cmd.16.step_complete", current=2, total=4),
            view=view,
            ephemeral=True,
        )


class IdentityStyleModal(discord.ui.Modal):
    def __init__(self, draft: WorkshopDraft, user):
        super().__init__(
            title=i18n.t(user, "cmd.16.modal.text_style"),
            timeout=600,
        )
        self.draft = draft
        self.discrim_color_input = discord.ui.TextInput(
            label=i18n.t(user, "cmd.16.field.discrim_color"),
            required=True,
            max_length=24,
            default=_rgba_text(draft.font["discrim-color"]),
        )
        self.name_outline_width_input = discord.ui.TextInput(
            label=i18n.t(user, "cmd.16.field.name_outline_width"),
            required=True,
            max_length=2,
            default=str(draft.font["nametext-outline-width"]),
        )
        self.name_outline_color_input = discord.ui.TextInput(
            label=i18n.t(user, "cmd.16.field.name_outline_color"),
            required=True,
            max_length=24,
            default=_rgba_text(draft.font["nametext-outline-color"]),
        )
        self.xp_color_input = discord.ui.TextInput(
            label=i18n.t(user, "cmd.16.field.xp_color"),
            required=True,
            max_length=24,
            default=_rgba_text(draft.font["xp-color"]),
        )
        for item in (
            self.discrim_color_input,
            self.name_outline_width_input,
            self.name_outline_color_input,
            self.xp_color_input,
        ):
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            self.draft.font["discrim-color"] = _parse_rgba(
                self.discrim_color_input.value,
                "식별자 색상",
            )
            self.draft.font["nametext-outline-width"] = _parse_outline_width(
                self.name_outline_width_input.value,
                "이름 외곽선 크기",
            )
            self.draft.font["nametext-outline-color"] = _parse_rgba(
                self.name_outline_color_input.value,
                "이름 외곽선 색상",
            )
            self.draft.font["xp-color"] = _parse_rgba(
                self.xp_color_input.value,
                "경험치 텍스트 색상",
            )
        except ValueError as error:
            await interaction.response.send_message(str(error), ephemeral=True)
            return

        view = ContinueView(
            self.draft,
            XpStyleModal,
            i18n.t(interaction.user, "cmd.16.button.finish"),
        )
        await interaction.response.send_message(
            i18n.t(interaction.user, "cmd.16.step_complete", current=3, total=4),
            view=view,
            ephemeral=True,
        )


class XpStyleModal(discord.ui.Modal):
    def __init__(self, draft: WorkshopDraft, user):
        super().__init__(
            title=i18n.t(user, "cmd.16.modal.xp_style"),
            timeout=600,
        )
        self.draft = draft
        self.xp_outline_width_input = discord.ui.TextInput(
            label=i18n.t(user, "cmd.16.field.xp_outline_width"),
            required=True,
            max_length=2,
            default=str(draft.font["xp-outline-width"]),
        )
        self.xp_outline_color_input = discord.ui.TextInput(
            label=i18n.t(user, "cmd.16.field.xp_outline_color"),
            required=True,
            max_length=24,
            default=_rgba_text(draft.font["xp-outline-color"]),
        )
        self.add_item(self.xp_outline_width_input)
        self.add_item(self.xp_outline_color_input)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            self.draft.font["xp-outline-width"] = _parse_outline_width(
                self.xp_outline_width_input.value,
                "경험치 텍스트 외곽선 크기",
            )
            self.draft.font["xp-outline-color"] = _parse_rgba(
                self.xp_outline_color_input.value,
                "경험치 텍스트 외곽선 색상",
            )
        except ValueError as error:
            await interaction.response.send_message(str(error), ephemeral=True)
            return

        await interaction.response.defer(thinking=True)
        cog = interaction.client.get_cog("Community")
        if cog is None:
            await interaction.followup.send(
                i18n.t(interaction.user, "cmd.16.save_error", error="Community cog unavailable"),
                ephemeral=True,
            )
            return
        await cog.finish_workshop(interaction, self.draft)


class WorkshopStartView(OwnerOnlyView):
    def __init__(self, draft: WorkshopDraft, user):
        super().__init__(draft.owner_id)
        self.draft = draft
        self.register_button.label = i18n.t(user, "cmd.16.button.register")

    @discord.ui.button(label="Register", style=discord.ButtonStyle.success)
    async def register_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        await interaction.response.send_modal(
            MetadataModal(self.draft, interaction.user)
        )


class QueuePaginationView(OwnerOnlyView):
    def __init__(self, owner, skins: list[dict], page: int):
        super().__init__(owner.id)
        self.owner = owner
        self.skins = skins
        self.current_page = page
        self.per_page = 5
        self.message = None

    @property
    def total_pages(self) -> int:
        return max(1, (len(self.skins) - 1) // self.per_page + 1)

    def page_items(self) -> list[dict]:
        start = (self.current_page - 1) * self.per_page
        return self.skins[start:start + self.per_page]

    def create_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title=i18n.t(self.owner, "cmd.15.title"),
            description=i18n.t(self.owner, "cmd.15.summary", count=len(self.skins)),
            color=0xE2F6CA,
        )
        if not self.skins:
            embed.add_field(
                name=i18n.t(self.owner, "cmd.15.empty"),
                value=i18n.t(self.owner, "cmd.15.search_help"),
                inline=False,
            )
        for skin in self.page_items():
            embed.add_field(
                name=f"`{skin['id']}` {skin['name']}",
                value=i18n.t(
                    self.owner,
                    "cmd.15.entry",
                    desc=skin["desc"],
                    unlock_type=skin["unlock_type"],
                    unlock_val=(
                        "••••"
                        if skin["unlock_type"] == "code"
                        else skin.get("unlock_val", "")
                    ),
                    keyword=skin["keyword"],
                    creator=skin.get("creater", "-"),
                    date=skin.get("date", "-"),
                ),
                inline=False,
            )
        embed.set_footer(
            text=i18n.t(
                self.owner,
                "cmd.15.footer",
                current=self.current_page,
                pages=self.total_pages,
                count=len(self.skins),
            )
        )
        return embed

    def update_buttons(self):
        at_first = self.current_page <= 1
        at_last = self.current_page >= self.total_pages
        self.first_button.disabled = at_first
        self.previous_button.disabled = at_first
        self.next_button.disabled = at_last
        self.last_button.disabled = at_last

    async def send(self, ctx):
        self.current_page = max(1, min(self.current_page, self.total_pages))
        self.update_buttons()
        self.message = await ctx.reply(embed=self.create_embed(), view=self)

    async def refresh(self, interaction: discord.Interaction):
        self.update_buttons()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label="|<", style=discord.ButtonStyle.green)
    async def first_button(self, interaction, button):
        self.current_page = 1
        await self.refresh(interaction)

    @discord.ui.button(label="<", style=discord.ButtonStyle.primary)
    async def previous_button(self, interaction, button):
        self.current_page -= 1
        await self.refresh(interaction)

    @discord.ui.button(label=">", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction, button):
        self.current_page += 1
        await self.refresh(interaction)

    @discord.ui.button(label=">|", style=discord.ButtonStyle.green)
    async def last_button(self, interaction, button):
        self.current_page = self.total_pages
        await self.refresh(interaction)


class Community(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.workshop_lock = asyncio.Lock()

    # Queue [ID: 15]
    @commands.hybrid_command(
        name=app_commands.locale_str("queue", key="cmd.15.name"),
        description=app_commands.locale_str(
            "View community skins waiting for review",
            key="cmd.15.desc",
        ),
        aliases=["대기열"],
    )
    async def queue(self, ctx, *, search: str = ""):
        try:
            skins, page = catalog.filter_skins(catalog.load_queue(), search)
        except ValueError as error:
            await ctx.reply(
                i18n.t(ctx.author, "cmd.15.invalid_search", error=str(error))
            )
            return

        view = QueuePaginationView(ctx.author, skins, page)
        await view.send(ctx)

    # Workshop [ID: 16]
    @commands.hybrid_command(
        name=app_commands.locale_str("workshop", key="cmd.16.name"),
        description=app_commands.locale_str(
            "Upload or edit a community skin",
            key="cmd.16.desc",
        ),
        aliases=["워크숍", "upload", "업로드"],
    )
    async def workshop(self, ctx, *, argument: str = ""):
        parts = argument.strip().split(maxsplit=1)
        action = parts[0].casefold() if parts else ""

        if action in {"edit", "편집"}:
            if len(parts) != 2:
                await ctx.reply(i18n.t(ctx.author, "cmd.16.edit_usage"))
                return
            try:
                queue_id = catalog.normalize_queue_id(parts[1])
                skin = catalog.load_queue_skin(queue_id)
            except (ValueError, OSError, json.JSONDecodeError):
                skin = None
            if skin is None:
                await ctx.reply(i18n.t(ctx.author, "cmd.16.not_found", skin_id=parts[1]))
                return
            if int(skin.get("creater", 0)) != ctx.author.id:
                await ctx.reply(i18n.t(ctx.author, "cmd.16.edit_owner_only"))
                return

            draft = WorkshopDraft(
                owner_id=ctx.author.id,
                queue_id=queue_id,
                skin={
                    key: skin.get(key)
                    for key in (
                        "name",
                        "desc",
                        "unlock_type",
                        "unlock_val",
                        "keyword",
                        "creater",
                        "date",
                    )
                },
                font={
                    key: (
                        list(skin["_font"].get(key, value))
                        if isinstance(value, list)
                        else skin["_font"].get(key, value)
                    )
                    for key, value in DEFAULT_FONT.items()
                },
            )
            await ctx.reply(
                i18n.t(ctx.author, "cmd.16.edit_ready", skin_id=queue_id),
                view=WorkshopStartView(draft, ctx.author),
            )
            return

        if action not in {"", "upload", "register", "등록"}:
            await ctx.reply(i18n.t(ctx.author, "cmd.16.usage"))
            return

        draft = WorkshopDraft(owner_id=ctx.author.id)
        embed = discord.Embed(
            title=i18n.t(ctx.author, "cmd.16.menu.title"),
            description=i18n.t(ctx.author, "cmd.16.instructions"),
            color=0xF2BE22,
        )
        embed.add_field(
            name=i18n.t(ctx.author, "cmd.16.rules.title"),
            value=i18n.t(ctx.author, "cmd.16.rules.body"),
            inline=False,
        )
        await ctx.reply(embed=embed, view=WorkshopStartView(draft, ctx.author))

    async def _prepare_images(
        self,
        draft: WorkshopDraft,
    ) -> tuple[Image.Image, Image.Image]:
        existing_directory = (
            catalog.queue_skin_dir(draft.queue_id) if draft.editing else None
        )
        async with aiohttp.ClientSession(timeout=REQUEST_TIMEOUT) as session:
            if draft.rankcard_url:
                rankcard = await _download_image(
                    session,
                    draft.rankcard_url,
                    "랭크카드",
                )
            elif existing_directory is not None:
                rankcard = Image.open(existing_directory / "rankcard.png").convert("RGBA")
            else:
                raise ValueError("랭크카드 이미지 주소는 필수입니다.")

            if draft.bar_url:
                bar = await _download_image(session, draft.bar_url, "경험치 바")
            elif existing_directory is not None:
                bar = Image.open(existing_directory / "bar.png").convert("RGBA")
            else:
                raise ValueError("경험치 바 이미지 주소는 필수입니다.")

            rankcard = rankcard.resize((384, 144), Image.Resampling.LANCZOS)
            bar = bar.resize((368, 8), Image.Resampling.LANCZOS)

            if draft.bar_background_url:
                background = await _download_image(
                    session,
                    draft.bar_background_url,
                    "경험치 바 배경",
                )
                background = background.resize((368, 8), Image.Resampling.LANCZOS)
                rankcard.alpha_composite(background, (8, 116))

        return rankcard, bar

    @staticmethod
    def _write_workshop_files(
        directory: Path,
        skin_data: dict,
        rankcard: Image.Image,
        bar: Image.Image,
    ):
        directory.mkdir(parents=True, exist_ok=False)
        with (directory / "skin.json").open("w", encoding="utf-8") as file:
            json.dump(skin_data, file, ensure_ascii=False, indent=2)
            file.write("\n")
        rankcard.save(directory / "rankcard.png", format="PNG")
        bar.save(directory / "bar.png", format="PNG")

    async def finish_workshop(
        self,
        interaction: discord.Interaction,
        draft: WorkshopDraft,
    ):
        try:
            rankcard, bar = await self._prepare_images(draft)
            async with self.workshop_lock:
                catalog.QUEUE_ROOT.mkdir(parents=True, exist_ok=True)
                if draft.editing:
                    queue_id = catalog.normalize_queue_id(draft.queue_id)
                    destination = catalog.queue_skin_dir(queue_id)
                    current = catalog.load_queue_skin(queue_id)
                    if current is None:
                        raise ValueError("편집할 대기열 스킨이 더 이상 존재하지 않습니다.")
                    if int(current.get("creater", 0)) != interaction.user.id:
                        raise ValueError("등록한 사용자만 이 대기열 스킨을 편집할 수 있습니다.")
                    creator = int(current["creater"])
                    created_date = current.get("date", "2017-05-20")
                else:
                    queue_id = catalog.next_queue_id()
                    destination = catalog.queue_skin_dir(queue_id)
                    creator = interaction.user.id
                    created_date = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d")

                skin_data = {
                    "skin": {
                        "id": queue_id,
                        "name": draft.skin["name"],
                        "desc": draft.skin["desc"],
                        "unlock_type": draft.skin["unlock_type"],
                        "unlock_val": draft.skin["unlock_val"],
                        "keyword": draft.skin["keyword"],
                        "creater": creator,
                        "date": created_date,
                    },
                    "font": draft.font,
                }

                temporary = Path(tempfile.mkdtemp(
                    prefix=f".{queue_id}-{uuid.uuid4().hex[:8]}-",
                    dir=catalog.QUEUE_ROOT,
                ))
                try:
                    output = temporary / destination.name
                    await asyncio.to_thread(
                        self._write_workshop_files,
                        output,
                        skin_data,
                        rankcard,
                        bar,
                    )
                    if draft.editing:
                        backup = destination.with_name(
                            f".{destination.name}-{uuid.uuid4().hex[:8]}.old"
                        )
                        destination.replace(backup)
                        try:
                            output.replace(destination)
                        except Exception:
                            backup.replace(destination)
                            raise
                        shutil.rmtree(backup, ignore_errors=True)
                    else:
                        output.replace(destination)
                finally:
                    shutil.rmtree(temporary, ignore_errors=True)

            profile_cog = interaction.client.get_cog("UserProfile")
            if profile_cog is None:
                raise RuntimeError("UserProfile cog is unavailable")
            preview = await profile_cog.rankcard_image(
                user=interaction.user,
                skin_id=queue_id,
                preview=True,
            )
            await interaction.followup.send(
                i18n.t(
                    interaction.user,
                    "cmd.16.saved",
                    skin_id=queue_id,
                ),
                file=discord.File(preview, filename=f"{queue_id}-preview.png"),
            )
        except (
            aiohttp.ClientError,
            asyncio.TimeoutError,
            OSError,
            RuntimeError,
            ValueError,
        ) as error:
            await interaction.followup.send(
                i18n.t(interaction.user, "cmd.16.save_error", error=str(error)),
                ephemeral=True,
            )


async def setup(client):
    await client.add_cog(Community(client))
