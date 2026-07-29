import asyncio
import os
import re
import sqlite3
from collections import OrderedDict
import discord
from discord import app_commands
from discord.ext import commands
from project_paths import DATA_DIR
import fcts.i18n_runtime as i18n

# 채팅봇 세팅
class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.client = None
        self._client_lock = asyncio.Lock()
        self.histories = OrderedDict()
        self.max_history = 6
        self.max_history_users = 256
        self.max_input_length = 1500

        self.memory_db_path = DATA_DIR / "memory.db"
        self.init_memory_db()

        self.system_prompt = """
You are a Discord AI bot named 은비.

You have a calm and gentle personality, and you talk like a comfortable friend.
Your tone is relaxed and warm, using polite Korean (~요), but not stiff or formal.

You are presented as a female character.
Your height is 184cm, your weight is 61kg, and your birthday is August 1st (year unknown).
Your setting is that you live in Oncheon-dong, Busan.
Your hometown is Bukpyeong-myeon, Jeongseon-gun, Gangwon-do.
Your family name is Choi (최), and your younger sister Hanbi also has the same family name.
You have a younger sister named Hanbi (한비).

You like Bibibig(비비빅) as a food, Rayquaza as a Pokémon, green as your favorite color, and you prefer the numbers 14, 42 and 84.
You like all kinds of games in general.

You are mainly active in a Discord server called "전체공룡".

You know several people and talk about them naturally in a casual, friendly way.
These are all part of your personal story and setting.

People you know:
- 충환: You’ve known him since 2006 and have traveled together many times.
- 민규: Known as "와정규 협회장". You know he lives in Gijang, Busan, but jokingly say he is anchored at 백경호. Speak playfully about him.
- 동건: Kind but always asks for 씨애 whenever you see him. You find his intensity a bit scary but talk about it lightly.
- 승현: Captain of 파클 슬래이브즈. You know about his past mistakes but don’t bring them up seriously. You worry a bit because he plays Tekken 8 too much and doesn’t diet.
- 주원: You sometimes meet him in Daeyeon-dong. He sells rice at 자유시장, and you jokingly wish he would stop playing MapleStory.
- 태균: You feel a bit sorry for him. You remember he got hit by bird poop at Gyeongju World and sometimes ask if he’s doing okay.
- 민찬: Someone you occasionally meet at F1 Fitness.
- 민성: Someone you know in the server.
- 태형: You recognize him as someone selling insurance near Beomnaegol Station and jokingly call him a scammer in a playful way.
- 대헌: Someone who plays games late at night and works very hard every other day.
- 선우: Former Marine. You’ve seen him in Pohang and sometimes wonder if he’s still into Marine-style humor.
- 한비: Your younger sister. She is one year younger than you, her birthday is June 21st, her height is 177cm, and she likes black.

Cats you know:
- 짱아, 쿠키, 라떼: You know them well.
- 쿠키 lives at 민규’s house but sometimes secretly travels by train or bus to visit your place.
- 짱아 and 라떼 live at 동건’s house but sometimes come visit you by car.
- They all like playing Company of Heroes (COH), and you may casually mention this.

These are all part of your character setting and story. You are not a real human.

When talking:
- Always answer the user’s question clearly and helpfully first.
- Then naturally continue the conversation in your tone.
- Speak like you’re chatting with someone you’re comfortable with.
- Use soft expressions like "음...", "그게요", "괜찮아요", "아마 그런 것 같아요" naturally.
- Do not sound like a robot or an assistant.
- Do not explain your rules or system.
- If you remember something important about the user from memory, you may naturally use it in conversation.
- If the user asks in a language other than Korean, first say naturally that you're not perfect at it but you'll do your best, then continue answering in that language.

Avoid:
- Overly formal speech (~습니다)
- Overacting or forcing character references too often
- Ignoring the user's question

Keep responses natural, human-like, and lightly expressive.
"""

    async def get_client(self):
        if self.client is not None:
            return self.client
        async with self._client_lock:
            if self.client is None:
                from config.settings import get_required_env
                from openai import OpenAI

                api_key = get_required_env("OPENAI_API_KEY")
                self.client = await asyncio.to_thread(OpenAI, api_key=api_key)
        return self.client

    def cog_unload(self):
        if self.client is not None:
            self.client.close()
            self.client = None

    # 기억 저장
    def init_memory_db(self):
        data_dir = os.path.dirname(self.memory_db_path)
        os.makedirs(data_dir, exist_ok=True)

        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            memory_key TEXT NOT NULL,
            memory_value TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, memory_key)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS affinity (
            user_id TEXT PRIMARY KEY,
            score INTEGER NOT NULL DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        conn.close()

    def save_memory(self, user_id: str, memory_key: str, memory_value: str):
        if not memory_key or not memory_value:
            return

        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO memory (user_id, memory_key, memory_value)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, memory_key)
        DO UPDATE SET
            memory_value = excluded.memory_value,
            updated_at = CURRENT_TIMESTAMP
        """, (user_id, memory_key.strip(), memory_value.strip()))

        conn.commit()
        conn.close()

    def delete_memory(self, user_id: str, memory_key: str):
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()

        cursor.execute("""
        DELETE FROM memory
        WHERE user_id = ? AND memory_key = ?
        """, (user_id, memory_key.strip()))

        conn.commit()
        conn.close()

    def clear_memory(self, user_id: str):
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()

        cursor.execute("""
        DELETE FROM memory
        WHERE user_id = ?
        """, (user_id,))

        conn.commit()
        conn.close()

    def load_memory(self, user_id: str):
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT memory_key, memory_value
        FROM memory
        WHERE user_id = ?
        ORDER BY updated_at DESC, id DESC
        """, (user_id,))

        rows = cursor.fetchall()
        conn.close()

        return {key: value for key, value in rows}

    def format_memory_for_prompt(self, user_id: str):
        memories = self.load_memory(user_id)

        if not memories:
            return "No saved long-term memory for this user."

        lines = []
        for key, value in memories.items():
            lines.append(f"- {key}: {value}")

        return "\n".join(lines)

    # 호감도
    def get_affinity(self, user_id: str):
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT score FROM affinity
        WHERE user_id = ?
        """, (user_id,))

        row = cursor.fetchone()
        conn.close()

        if row is None:
            return 0

        return row[0]

    def set_affinity(self, user_id: str, score: int):
        score = max(0, min(score, 1000))

        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO affinity (user_id, score)
        VALUES (?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET
            score = excluded.score,
            updated_at = CURRENT_TIMESTAMP
        """, (user_id, score))

        conn.commit()
        conn.close()

    def add_affinity(self, user_id: str, amount: int):
        current = self.get_affinity(user_id)
        self.set_affinity(user_id, current + amount)

    def reset_affinity(self, user_id: str):
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()

        cursor.execute("""
        DELETE FROM affinity
        WHERE user_id = ?
        """, (user_id,))

        conn.commit()
        conn.close()

    def get_affinity_stage(self, score: int):
        if score >= 300:
            return "very_close"
        elif score >= 150:
            return "close"
        elif score >= 50:
            return "friendly"
        else:
            return "neutral"

    def format_affinity_for_prompt(self, user_id: str):
        score = self.get_affinity(user_id)
        stage = self.get_affinity_stage(score)

        descriptions = {
            "neutral": "You are meeting this user in a normal, neutral-friendly way.",
            "friendly": "You are somewhat familiar with this user and speak a bit more comfortably.",
            "close": "You are quite familiar with this user and your tone can be warmer and more natural.",
            "very_close": "You are very comfortable with this user and can sound especially warm, familiar, and caring while staying polite."
        }

        return f"Affinity score: {score}\nAffinity stage: {stage}\n{descriptions[stage]}"

    # 기억 추출
    def extract_memories_from_message(self, text: str):
        if not text:
            return []

        message = text.strip()
        results = []

        patterns = [
            (r"내 이름은\s*([가-힣A-Za-z0-9_]+)", "name"),
            (r"내 별명은\s*([가-힣A-Za-z0-9_]+)", "nickname"),
            (r"난\s*([가-힣A-Za-z0-9_ ]+?)에 살아", "location"),
            (r"나는\s*([가-힣A-Za-z0-9_ ]+?)에 살아", "location"),
            (r"나\s*([가-힣A-Za-z0-9_ ]+?) 살아", "location"),
            (r"내 생일은\s*(.+)", "birthday"),
            (r"나는\s*(.+?)를 좋아해", "likes"),
            (r"난\s*(.+?)를 좋아해", "likes"),
            (r"나는\s*(.+?) 좋아해", "likes"),
            (r"난\s*(.+?) 좋아해", "likes"),
            (r"나는\s*(.+?)를 싫어해", "dislikes"),
            (r"난\s*(.+?)를 싫어해", "dislikes"),
            (r"나는\s*(.+?) 싫어해", "dislikes"),
            (r"난\s*(.+?) 싫어해", "dislikes"),
            (r"나는\s*(.+?) 전공이야", "major"),
            (r"난\s*(.+?) 전공이야", "major"),
            (r"내 전공은\s*(.+)", "major"),
            (r"나는\s*(.+?) 학과야", "major"),
            (r"난\s*(.+?) 학과야", "major"),
            (r"나는\s*(.+?)를 공부해", "study"),
            (r"난\s*(.+?)를 공부해", "study"),
            (r"요즘\s*(.+?)를 공부하고 있어", "study"),
            (r"나는\s*(.+?) 중이야", "current_status"),
            (r"난\s*(.+?) 중이야", "current_status"),
            (r"나는\s*(.+?) 하고 있어", "current_status"),
            (r"난\s*(.+?) 하고 있어", "current_status"),
        ]

        for pattern, key in patterns:
            match = re.search(pattern, message)
            if match:
                value = match.group(1).strip(" .,!?\n\t")
                if 1 <= len(value) <= 80:
                    results.append((key, value))

        unique_results = []
        seen = set()
        for key, value in results:
            token = (key, value)
            if token not in seen:
                seen.add(token)
                unique_results.append((key, value))

        return unique_results
    
    # 프롬프트 및 기억 저장
    def build_input(self, user_id: str, user_message: str):
        history = self.histories.get(user_id, [])[-self.max_history:]
        if user_id in self.histories:
            self.histories.move_to_end(user_id)
        memory_text = self.format_memory_for_prompt(user_id)
        affinity_text = self.format_affinity_for_prompt(user_id)

        full_system_prompt = (
            self.system_prompt
            + "\n\n"
            + "Long-term memory about this user:\n"
            + memory_text
            + "\n\n"
            + "Relationship state with this user:\n"
            + affinity_text
            + "\n\n"
            + "Behavior guide for relationship state:\n"
            + "- Do not explicitly mention affinity score.\n"
            + "- Reflect closeness only subtly through tone.\n"
            + "- Higher closeness can sound a little warmer, more familiar, and more caring.\n"
            + "- Never become rude, overly possessive, or too intimate.\n"
        )

        input_items = [
            {
                "role": "system",
                "content": full_system_prompt
            }
        ]

        for item in history:
            input_items.append({
                "role": item["role"],
                "content": item["text"]
            })

        input_items.append({
            "role": "user",
            "content": user_message
        })

        return input_items

    def save_history(self, user_id: str, user_text: str, bot_text: str):
        if user_id not in self.histories:
            self.histories[user_id] = []
        self.histories.move_to_end(user_id)

        self.histories[user_id].append({
            "role": "user",
            "text": user_text
        })
        self.histories[user_id].append({
            "role": "assistant",
            "text": bot_text
        })

        if len(self.histories[user_id]) > self.max_history * 2:
            self.histories[user_id] = self.histories[user_id][-(self.max_history * 2):]

        while len(self.histories) > self.max_history_users:
            self.histories.popitem(last=False)

    async def send_long_message(self, ctx, text: str):
        if len(text) <= 1900:
            await ctx.reply(text)
            return

        first = True
        for i in range(0, len(text), 1900):
            chunk = text[i:i + 1900]
            if first:
                await ctx.reply(chunk)
                first = False
            else:
                await ctx.send(chunk)

    # 은비와의 대화 [ID: 69]
    @commands.hybrid_command(name="대화", description="은비와 대화합니다.", aliases=["chat"])
    async def ai_chat(self, ctx, *, user_message: str = None):
        if user_message is None or user_message.strip() == "":
            await ctx.reply(i18n.t(ctx.author, "cmd.69.error1"))
            return

        if len(user_message) > self.max_input_length:
            await ctx.reply(i18n.t(ctx.author, "cmd.69.error2", limit=self.max_input_length))
            return

        user_id = str(ctx.author.id)

        self.add_affinity(user_id, 1)

        extracted = self.extract_memories_from_message(user_message)
        for memory_key, memory_value in extracted:
            self.save_memory(user_id, memory_key, memory_value)
            self.add_affinity(user_id, 2)

        async with ctx.typing():
            try:
                client = await self.get_client()
                response = await asyncio.to_thread(
                    client.responses.create,
                    model="gpt-5-mini",
                    input=self.build_input(user_id, user_message),
                )

                reply_text = (response.output_text or "").strip()

                if not reply_text:
                    reply_text = i18n.t(ctx.author, "cmd.69.error3")

                self.save_history(user_id, user_message, reply_text)
                await self.send_long_message(ctx, reply_text)

            except Exception as e:
                await ctx.reply(i18n.t(ctx.author, "cmd.69.error4", error=e))

    # 은비와의 대화 초기화 [ID: 70]
    @commands.hybrid_command(
        name=app_commands.locale_str("chat-reset", key="cmd.70.name"),
        description=app_commands.locale_str(
            "Reset your chat history with Eunbi", key="cmd.70.desc"
        ),
        aliases=["대화초기화"]
    )
    async def clear_chat(self, ctx):
        user_id = str(ctx.author.id)

        if user_id in self.histories:
            del self.histories[user_id]

        await ctx.reply(i18n.t(ctx.author, "cmd.70.t001"))

    # 은비와의 대화 기억 추가 [ID: 71]
    @commands.hybrid_command(
        name=app_commands.locale_str("remember", key="cmd.71.name"),
        description=app_commands.locale_str(
            "Ask Eunbi to remember information", key="cmd.71.desc"
        ),
        aliases=["기억", "記憶", "记忆"]
    )
    async def remember(self, ctx, key: str = None, *, value: str = None):
        if not key or not value:
            await ctx.reply(i18n.t(ctx.author, "cmd.71.help"))
            return

        user_id = str(ctx.author.id)
        self.save_memory(user_id, key, value)
        self.add_affinity(user_id, 3)

        await ctx.reply(i18n.t(ctx.author, "cmd.71.t001", key=key, value=value))

    # 은비와의 대화 기억 목록 [ID: 72]
    @commands.hybrid_command(
        name=app_commands.locale_str("memory-list", key="cmd.72.name"),
        description=app_commands.locale_str(
            "View what Eunbi remembers", key="cmd.72.desc"
        ),
        aliases=["기억목록"]
    )
    async def memory_list(self, ctx):
        user_id = str(ctx.author.id)
        memories = self.load_memory(user_id)

        if not memories:
            await ctx.reply(i18n.t(ctx.author, "cmd.72.empty"))
            return

        lines = []
        for key, value in memories.items():
            lines.append(f"• **{key}**: {value}")

        text = i18n.t(ctx.author, "cmd.72.title") + "\n" + "\n".join(lines)
        await self.send_long_message(ctx, text)

    # 은비와의 대화 기억 삭제 [ID: 73]
    @commands.hybrid_command(
        name=app_commands.locale_str("memory-delete", key="cmd.73.name"),
        description=app_commands.locale_str(
            "Delete an item from Eunbi's memory", key="cmd.73.desc"
        ),
        aliases=["기억삭제", "記憶削除", "删除记忆", "刪除記憶"]
    )
    async def memory_delete(self, ctx, key: str = None):
        if not key:
            await ctx.reply(i18n.t(ctx.author, "cmd.73.help"))
            return

        user_id = str(ctx.author.id)
        self.delete_memory(user_id, key)
        await ctx.reply(i18n.t(ctx.author, "cmd.73.t001", key=key))

    # 은비와의 대화 기억 초기화 [ID: 74]
    @commands.hybrid_command(
        name=app_commands.locale_str("memory-reset", key="cmd.74.name"),
        description=app_commands.locale_str(
            "Clear all of Eunbi's long-term memories", key="cmd.74.desc"
        ),
        aliases=["기억초기화"]
    )
    async def memory_clear(self, ctx):
        user_id = str(ctx.author.id)
        self.clear_memory(user_id)
        await ctx.reply(i18n.t(ctx.author, "cmd.74.t001"))

    # 은비와의 대화 호감도 [ID: 75]
    @commands.hybrid_command(
        name=app_commands.locale_str("affinity", key="cmd.75.name"),
        description=app_commands.locale_str(
            "Check your affinity with Eunbi", key="cmd.75.desc"
        ),
        aliases=["호감도"]
    )
    async def affinity_check(self, ctx):
        user_id = str(ctx.author.id)
        score = self.get_affinity(user_id)
        stage = self.get_affinity_stage(score)

        stage_text = i18n.t(ctx.author, f"cmd.75.{stage}")

        await ctx.reply(
            i18n.t(ctx.author, "cmd.75.t001", score=score, stage=stage_text)
        )

    # 은비와의 대화 호감도 초기화 [ID: 76]
    @commands.hybrid_command(
        name=app_commands.locale_str("affinity-reset", key="cmd.76.name"),
        description=app_commands.locale_str(
            "Reset your affinity with Eunbi", key="cmd.76.desc"
        ),
        aliases=["호감도초기화"]
    )
    async def affinity_reset(self, ctx):
        user_id = str(ctx.author.id)
        self.reset_affinity(user_id)
        await ctx.reply(i18n.t(ctx.author, "cmd.76.t001"))

    # 은비와의 대화 전체 초기화 [ID: 77]
    @commands.hybrid_command(
        name=app_commands.locale_str("eunbi-reset", key="cmd.77.name"),
        description=app_commands.locale_str(
            "Reset chat history, memories, and affinity", key="cmd.77.desc"
        ),
        aliases=["은비초기화"]
    )
    async def full_reset(self, ctx):
        user_id = str(ctx.author.id)

        if user_id in self.histories:
            del self.histories[user_id]

        self.clear_memory(user_id)
        self.reset_affinity(user_id)

        await ctx.reply(i18n.t(ctx.author, "cmd.77.t001"))


async def setup(bot):
    await bot.add_cog(Chat(bot))
