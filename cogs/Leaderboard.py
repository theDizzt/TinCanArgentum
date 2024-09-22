import discord
from discord.ext import commands
import fcts.sqlcontrol as q
import fcts.leaderboard as l
import fcts.etcfunctions as etc

emoji = {
    'rps': '<:rps:1154728998677512242>',
    'yt': '<:yatzee:1154986928576405534>',
    'wordchain': '<:wordchain:1154986926894485584>',
    'slot': '<:slot:1154986931885719582>',
    'arithmatic': '<:arithmatic:1154352504503537764>'
}


class Dropdown(discord.ui.Select):

    def __init__(self):
        options = [
            discord.SelectOption(
                label='RPS - Score',
                description='In the order of the highest score.',
                emoji=discord.PartialEmoji.from_str(emoji['rps'])),
            discord.SelectOption(
                label='RPS - Counts',
                description='In the order of the highest count.',
                emoji=discord.PartialEmoji.from_str(emoji['rps'])),
            discord.SelectOption(
                label='RPS - Max Chains',
                description='In the order of the highest max chain.',
                emoji=discord.PartialEmoji.from_str(emoji['rps'])),
            discord.SelectOption(
                label='RPS - Wins',
                description='In the order of the highest win.',
                emoji=discord.PartialEmoji.from_str(emoji['rps'])),
            discord.SelectOption(
                label='RPS - Ties',
                description='In the order of the highest tie.',
                emoji=discord.PartialEmoji.from_str(emoji['rps'])),
            discord.SelectOption(label='RPS - My Rank',
                                 description='Show your best record in RPS.',
                                 emoji=discord.PartialEmoji.from_str(
                                     emoji['rps'])),
            discord.SelectOption(
                label='Yahtzee - Score',
                description='In the order of the highest score.',
                emoji=discord.PartialEmoji.from_str(emoji['yt'])),
            discord.SelectOption(
                label='Yahtzee - Play',
                description='In the order of the highest play count.',
                emoji=discord.PartialEmoji.from_str(emoji['yt'])),
            discord.SelectOption(
                label='Yahtzee - Wins',
                description='In the order of the highest win.',
                emoji=discord.PartialEmoji.from_str(emoji['yt'])),
            discord.SelectOption(
                label='Yahtzee - My Rank',
                description='Show your best record in Yahtzee.',
                emoji=discord.PartialEmoji.from_str(emoji['yt'])),
            discord.SelectOption(
                label='Word Chain - Registration',
                description=
                'In the order of the highest word registration counts.',
                emoji=discord.PartialEmoji.from_str(emoji['wordchain'])),
            discord.SelectOption(
                label='Word Chain - Individual - Score',
                description=
                'In the order of the highest score in individual mode.',
                emoji=discord.PartialEmoji.from_str(emoji['wordchain'])),
            discord.SelectOption(
                label='Word Chain - Individual - Chains',
                description=
                'In the order of the highest chains in individual mode.',
                emoji=discord.PartialEmoji.from_str(emoji['wordchain'])),
            discord.SelectOption(
                label='Word Chain - Individual - Wins',
                description=
                'In the order of the highest wins in individual mode.',
                emoji=discord.PartialEmoji.from_str(emoji['wordchain'])),
            discord.SelectOption(
                label='Word Chain - Bot - Score',
                description='In the order of the highest score in bot mode.',
                emoji=discord.PartialEmoji.from_str(emoji['wordchain'])),
            discord.SelectOption(
                label='Word Chain - Bot - Chains',
                description='In the order of the highest chains in bot mode.',
                emoji=discord.PartialEmoji.from_str(emoji['wordchain'])),
            discord.SelectOption(
                label='Word Chain - My Rank',
                description='Show your best record in Word Chain.',
                emoji=discord.PartialEmoji.from_str(emoji['wordchain'])),
            discord.SelectOption(
                label='Arithmatic - Score',
                description='In the order of the highest score.',
                emoji=discord.PartialEmoji.from_str(emoji['arithmatic'])),
            discord.SelectOption(
                label='Arithmatic - Correct',
                description='In the order of the highest corrects.',
                emoji=discord.PartialEmoji.from_str(emoji['arithmatic'])),
            discord.SelectOption(
                label='Arithmatic - My Rank',
                description='Show your best record in Arithmatic.',
                emoji=discord.PartialEmoji.from_str(emoji['arithmatic']))
        ]

        super().__init__(placeholder='Select your option:',
                         min_values=1,
                         max_values=1,
                         options=options)

    async def callback(self, interaction: discord.Interaction):
        result = self.values[0].split(" - ")

        if result[0] == "RPS":
            if result[1] == "Score":
                result = l.rpsDataRanking('score')
                embed = discord.Embed(
                    title=f"{emoji['rps']} **RPS** Global Ranking",
                    description="RPS: Score",
                    color=0xBCE29E)
                for i in range(10):
                    try:
                        temp = result[i]
                        embed.add_field(
                            name=
                            f"{etc.numFont(temp[3])} {q.readTagById(temp[0])}",
                            value=f"**{temp[1]:,d}** points | {temp[2]}",
                            inline=False)
                    except:
                        break
                await interaction.response.send_message(
                    "## :scroll: Leaderboard", embed=embed)

            elif result[1] == "Counts":
                result = l.rpsDataRanking('count')
                embed = discord.Embed(
                    title=f"{emoji['rps']} **RPS** Global Ranking",
                    description="RPS: Counts",
                    color=0xBCE29E)
                for i in range(10):
                    try:
                        temp = result[i]
                        embed.add_field(
                            name=
                            f"{etc.numFont(temp[3])} {q.readTagById(temp[0])}",
                            value=f"**{temp[1]:,d}** counts | {temp[2]}",
                            inline=False)
                    except:
                        break
                await interaction.response.send_message(
                    "## :scroll: Leaderboard", embed=embed)

            elif result[1] == "Max Chains":
                result = l.rpsDataRanking('maxchain')
                embed = discord.Embed(
                    title=f"{emoji['rps']} **RPS** Global Ranking",
                    description="RPS: Max Chains",
                    color=0xBCE29E)
                for i in range(10):
                    try:
                        temp = result[i]
                        embed.add_field(
                            name=
                            f"{etc.numFont(temp[3])} {q.readTagById(temp[0])}",
                            value=f"**{temp[1]:,d}** max chains | {temp[2]}",
                            inline=False)
                    except:
                        break
                await interaction.response.send_message(
                    "## :scroll: Leaderboard", embed=embed)

            elif result[1] == "Wins":
                result = l.rpsDataRanking('win')
                embed = discord.Embed(
                    title=f"{emoji['rps']} **RPS** Global Ranking",
                    description="RPS: Wins",
                    color=0xBCE29E)
                for i in range(10):
                    try:
                        temp = result[i]
                        embed.add_field(
                            name=
                            f"{etc.numFont(temp[3])} {q.readTagById(temp[0])}",
                            value=f"**{temp[1]:,d}** wins | {temp[2]}",
                            inline=False)
                    except:
                        break
                await interaction.response.send_message(
                    "## :scroll: Leaderboard", embed=embed)

            elif result[1] == "Ties":
                result = l.rpsDataRanking('tie')
                embed = discord.Embed(
                    title=f"{emoji['rps']} **RPS** Global Ranking",
                    description="RPS: Ties",
                    color=0xBCE29E)
                for i in range(10):
                    try:
                        temp = result[i]
                        embed.add_field(
                            name=
                            f"{etc.numFont(temp[3])} {q.readTagById(temp[0])}",
                            value=f"**{temp[1]:,d}** ties | {temp[2]}",
                            inline=False)
                    except:
                        break
                await interaction.response.send_message(
                    "## :scroll: Leaderboard", embed=embed)

            elif result[1] == "My Rank":
                try:
                    score = l.rpsDataUserRanking(interaction.user, 'score')
                    count = l.rpsDataUserRanking(interaction.user, 'count')
                    max = l.rpsDataUserRanking(interaction.user, 'maxchain')
                    win = l.rpsDataUserRanking(interaction.user, 'win')
                    tie = l.rpsDataUserRanking(interaction.user, 'tie')

                    embed = discord.Embed(
                        title=f'{q.readTag(interaction.user)}\'s Record',
                        description=f"{emoji['arithmatic']} **Arithmatic**",
                        color=0xBCE29E)
                    embed.add_field(
                        name="SCORE",
                        value=
                        f"**{score[2]}위** | {score[0]:,d} points | {score[1]}",
                        inline=False)
                    embed.add_field(
                        name="COUNTS",
                        value=
                        f"**{count[2]}위** | {count[0]:,d} counts | {count[1]}",
                        inline=False)
                    embed.add_field(
                        name="MAX CHAINS",
                        value=
                        f"**{max[2]}위** | {max[0]:,d} max chains | {max[1]}",
                        inline=False)
                    embed.add_field(
                        name="WINS",
                        value=f"**{win[2]}위** | {win[0]:,d} wins | {win[1]}",
                        inline=False)
                    embed.add_field(
                        name="TIES",
                        value=f"**{tie[2]}위** | {tie[0]:,d} ties | {tie[1]}",
                        inline=False)
                    await interaction.response.send_message(
                        "## :scroll: Leaderboard", embed=embed)
                except:
                    await interaction.response.send_message(
                        "## :scroll: Leaderboard\nNo data")

        elif result[0] == "Yahtzee":
            if result[1] == "Score":
                result = l.ytRanking('score')
                embed = discord.Embed(
                    title=f"{emoji['yt']} **Yahtzee** Global Ranking",
                    description="Yahtzee: Score",
                    color=0xBCE29E)
                for i in range(10):
                    try:
                        temp = result[i]
                        embed.add_field(
                            name=
                            f"{etc.numFont(temp[3])} {q.readTagById(temp[0])}",
                            value=f"**{temp[1]:,d}** points | {temp[2]}",
                            inline=False)
                    except:
                        break
                await interaction.response.send_message(
                    "## :scroll: Leaderboard", embed=embed)

            elif result[1] == "Play":
                result = l.ytRanking('play')
                embed = discord.Embed(
                    title=f"{emoji['yt']} **Yahtzee** Global Ranking",
                    description="Yahtzee: Play",
                    color=0xBCE29E)
                for i in range(10):
                    try:
                        temp = result[i]
                        embed.add_field(
                            name=
                            f"{etc.numFont(temp[2])} {q.readTagById(temp[0])}",
                            value=f"**{temp[1]:,d}** plays",
                            inline=False)
                    except:
                        break
                await interaction.response.send_message(
                    "## :scroll: Leaderboard", embed=embed)

            elif result[1] == "Wins":
                result = l.ytRanking('win')
                embed = discord.Embed(
                    title=f"{emoji['yt']} **Yahtzee** Global Ranking",
                    description="Yahtzee: Wins",
                    color=0xBCE29E)
                for i in range(10):
                    try:
                        temp = result[i]
                        embed.add_field(
                            name=
                            f"{etc.numFont(temp[2])} {q.readTagById(temp[0])}",
                            value=f"**{temp[1]:,d}** wins",
                            inline=False)
                    except:
                        break
                await interaction.response.send_message(
                    "## :scroll: Leaderboard", embed=embed)

            elif result[1] == "My Rank":
                try:
                    score = l.ytUserRanking(interaction.user, 'score')
                    play = l.ytUserRanking(interaction.user, 'play')
                    win = l.ytUserRanking(interaction.user, 'win')

                    embed = discord.Embed(
                        title=f'{q.readTag(interaction.user)}\'s Record',
                        description=f"{emoji['yt']} **Yahtzee**",
                        color=0xBCE29E)
                    embed.add_field(
                        name="SCORE",
                        value=
                        f"**{score[2]}위** | {score[0]:,d} points | {score[1]}",
                        inline=False)
                    embed.add_field(
                        name="COUNTS",
                        value=f"**{play[1]}위** | {play[0]:,d} play",
                        inline=False)
                    embed.add_field(name="WINS",
                                    value=f"**{win[1]}위** | {win[0]:,d} wins",
                                    inline=False)
                    await interaction.response.send_message(
                        "## :scroll: Leaderboard", embed=embed)
                except:
                    await interaction.response.send_message(
                        "## :scroll: Leaderboard\nNo data")

        elif result[0] == "Word Chain":
            if result[1] == "Registration":
                result = l.wcRanking('regist', '')
                embed = discord.Embed(
                    title=f"{emoji['wordchain']} **Word Chain** Global Ranking",
                    description="Word Chain: Word Registration",
                    color=0xBCE29E)
                for i in range(10):
                    try:
                        temp = result[i]
                        embed.add_field(
                            name=
                            f"{etc.numFont(temp[2])} {q.readTagById(temp[0])}",
                            value=f"**{temp[1]:,d}** words",
                            inline=False)
                    except:
                        break
                await interaction.response.send_message(
                    "## :scroll: Leaderboard", embed=embed)

            elif result[1] == "Individual":
                if result[2] == "Score":
                    result = l.wcRanking('indi', 'score')
                    embed = discord.Embed(
                        title=
                        f"{emoji['wordchain']} **Word Chain** Global Ranking",
                        description="Word Chain: Individual | Score",
                        color=0xBCE29E)
                    for i in range(10):
                        try:
                            temp = result[i]
                            embed.add_field(
                                name=
                                f"{etc.numFont(temp[2])} {q.readTagById(temp[0])}",
                                value=f"**{temp[1]:,d}** points",
                                inline=False)
                        except:
                            break
                    await interaction.response.send_message(
                        "## :scroll: Leaderboard", embed=embed)

                elif result[2] == "Chains":
                    result = l.wcRanking('indi', 'count')
                    embed = discord.Embed(
                        title=
                        f"{emoji['wordchain']} **Word Chain** Global Ranking",
                        description="Word Chain: Individual | Chains",
                        color=0xBCE29E)
                    for i in range(10):
                        try:
                            temp = result[i]
                            embed.add_field(
                                name=
                                f"{etc.numFont(temp[2])} {q.readTagById(temp[0])}",
                                value=f"**{temp[1]:,d}** chains",
                                inline=False)
                        except:
                            break
                    await interaction.response.send_message(
                        "## :scroll: Leaderboard", embed=embed)

                elif result[2] == "Wins":
                    result = l.wcRanking('indi', 'win')
                    embed = discord.Embed(
                        title=
                        f"{emoji['wordchain']} **Word Chain** Global Ranking",
                        description="Word Chain: Individual | Wins",
                        color=0xBCE29E)
                    for i in range(10):
                        try:
                            temp = result[i]
                            embed.add_field(
                                name=
                                f"{etc.numFont(temp[3])} {q.readTagById(temp[0])}",
                                value=f"**{temp[1]}** wins ({temp[2]} games)",
                                inline=False)
                        except:
                            break

                    await interaction.response.send_message(
                        "## :scroll: Leaderboard", embed=embed)

            elif result[1] == "Bot":
                if result[2] == "Score":
                    result = l.wcRanking('bot', 'score')
                    print(result)
                    embed = discord.Embed(
                        title=
                        f"{emoji['wordchain']} **Word Chain** Global Ranking",
                        description="Word Chain: Bot | Score",
                        color=0xBCE29E)
                    for i in range(10):
                        try:
                            temp = result[i]
                            embed.add_field(
                                name=
                                f"{etc.numFont(temp[2])} {q.readTagById(temp[0])}",
                                value=f"**{temp[1]:,d}** points",
                                inline=False)
                        except:
                            break
                    await interaction.response.send_message(
                        "## :scroll: Leaderboard", embed=embed)

                elif result[2] == "Chains":
                    result = l.wcRanking('bot', 'count')
                    print(result)
                    embed = discord.Embed(
                        title=
                        f"{emoji['wordchain']} **Word Chain** Global Ranking",
                        description="Word Chain: Bot | Chains",
                        color=0xBCE29E)
                    for i in range(10):
                        try:
                            temp = result[i]
                            embed.add_field(
                                name=
                                f"{etc.numFont(temp[2])} {q.readTagById(temp[0])}",
                                value=f"**{temp[1]:,d}** chains",
                                inline=False)
                        except:
                            break
                    await interaction.response.send_message(
                        "## :scroll: Leaderboard", embed=embed)

            elif result[1] == "My Rank":
                try:
                    reg = l.wcUserRanking(interaction.user, 'regist', '')
                    iscore = l.wcUserRanking(interaction.user, 'indi', 'score')
                    icount = l.wcUserRanking(interaction.user, 'indi', 'count')
                    iwin = l.wcUserRanking(interaction.user, 'indi', 'win')
                    bscore = l.wcUserRanking(interaction.user, 'bot', 'score')
                    bcount = l.wcUserRanking(interaction.user, 'bot', 'count')

                    embed = discord.Embed(
                        title=f'{q.readTag(interaction.user)}\'s Record',
                        description=f"{emoji['wordchain']} **Word Chain**",
                        color=0xBCE29E)
                    embed.add_field(name="Word Registration",
                                    value=f"**{reg[1]}위** | {reg[0]:,d} words",
                                    inline=False)
                    embed.add_field(
                        name="INDIVIDUAL RANKING",
                        value=
                        f"**{iscore[1]}위** | {iscore[0]:,d} points\n**{icount[1]}위** | {icount[0]:,d} chains\n**{iwin[2]}위** | {iwin[0]:,d} wins ({iwin[1]} games)",
                        inline=False)
                    embed.add_field(
                        name="versus BOT",
                        value=
                        f"**{bscore[1]}위** | {bscore[0]:,d} points\n**{bcount[1]}위** | {bcount[0]:,d} chains",
                        inline=False)
                    await interaction.response.send_message(
                        "## :scroll: Leaderboard", embed=embed)
                except:
                    await interaction.response.send_message(
                        "## :scroll: Leaderboard\nNo data")

        elif result[0] == "Arithmatic":
            if result[1] == "Score":
                result = l.mathDataRanking('score')
                embed = discord.Embed(
                    title=
                    f"{emoji['arithmatic']} **Arithmatic** Global Ranking",
                    description="Arithmatic: Score",
                    color=0xBCE29E)
                for i in range(10):
                    try:
                        temp = result[i]
                        embed.add_field(
                            name=
                            f"{etc.numFont(temp[3])} {q.readTagById(temp[0])}",
                            value=f"**{temp[1]:,d}** points | {temp[2]}",
                            inline=False)
                    except:
                        break
                await interaction.response.send_message(
                    "## :scroll: Leaderboard", embed=embed)

            elif result[1] == "Correct":
                result = l.mathDataRanking('count')
                embed = discord.Embed(
                    title=
                    f"{emoji['arithmatic']} **Arithmatic** Global Ranking",
                    description="Arithmatic: Corrects",
                    color=0xBCE29E)
                for i in range(10):
                    try:
                        temp = result[i]
                        embed.add_field(
                            name=
                            f"{etc.numFont(temp[3])} {q.readTagById(temp[0])}",
                            value=f"**{temp[1]:,d}** corrects | {temp[2]}",
                            inline=False)
                    except:
                        break
                await interaction.response.send_message(
                    "## :scroll: Leaderboard", embed=embed)

            elif result[1] == "My Rank":
                try:
                    score = l.mathDataUserRanking(interaction.user, 'score')
                    count = l.mathDataUserRanking(interaction.user, 'count')
                    embed = discord.Embed(
                        title=f'{q.readTag(interaction.user)}\'s Record',
                        description=f"{emoji['arithmatic']} **Arithmatic**",
                        color=0xBCE29E)
                    embed.add_field(
                        name="SCORE",
                        value=
                        f"**{score[2]}위** | {score[0]:,d} points | {score[1]}",
                        inline=False)
                    embed.add_field(
                        name="CORRECTS",
                        value=
                        f"**{count[2]}위** | {count[0]:,d} corrects | {count[1]}",
                        inline=False)
                    await interaction.response.send_message(
                        "## :scroll: Leaderboard", embed=embed)
                except:
                    await interaction.response.send_message(
                        "## :scroll: Leaderboard\nNo data")


class DropdownView(discord.ui.View):

    def __init__(self):
        super().__init__()
        self.add_item(Dropdown())


class Leaderboard(commands.Cog):

    def __init__(self, client: commands.Bot):
        self.client = client

    # Leaderboard [ID: 50]
    @commands.cooldown(rate=1, per=20, type=commands.BucketType.user)
    @commands.hybrid_command(name='leaderboard',
                             description="Show bot game ranking!")
    async def leaderboard(self, ctx):
        view = DropdownView()
        msg = await ctx.reply("## :scroll: Leaderboard", view=view)
        await self.client.wait_for("interaction",
                                   check=lambda x: x.user == ctx.author)
        await msg.delete()

    @leaderboard.error
    async def discrim_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = '`(⩌ʌ ⩌;)` This command is ratelimited, please try again in **{:.2f} seconds**.'.format(
                error.retry_after)
            await ctx.send(msg)
        else:
            raise error


async def setup(client):
    await client.add_cog(Leaderboard(client))
