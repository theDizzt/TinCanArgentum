import discord
from discord.ext import commands
import fcts.sqlcontrol as q
import fcts.etcfunctions as etc
import asyncio


class optionButton(discord.ui.View):

    def __init__(self):
        super().__init__

    @discord.ui.button(label='Upload Skin', style=discord.ButtonStyle.primary)
    async def uploadskin(self, interaction: discord.Interaction,
                         button: discord.ui.Button):
        url = []

        embed = discord.Embed(title="**Upload Rankcard Skin**",
                              description="`Step 1/4`",
                              color=0xF2BE22)
        embed.add_field(
            name=
            "**Please upload the Rankcard Skin image file to the current channel!**",
            value=
            "- The file specification is 384 * 144 [Unit: px].\n- File extensions can only be PNG.",
            inline=False)
        embed.set_image(
            url=
            "https://media.discordapp.net/attachments/1146755294601425037/1155399938646229025/result1.png"
        )

        msg = await interaction.response.send_message('## Skin Upload Manager',
                                                      embed=embed)

        def check(m):
            return m.author == interaction.user

        r = await discord.client.wait_for('message', check=check)
        try:
            if r.attachments[0].url.endswith(
                    'PNG') or r.attachments[0].url.endswith('png'):
                url.append(r.attachments[0].url)
                print(r.attachments[0].url)
            else:
                await interaction.response.send_message('잘못된 형식!')
                boolean = False
            await r.delete()
        except:
            await r.delete()
            await interaction.response.send_message('파일이 업로드 되지 않았습니다!')
            boolean = False

        if boolean:
            embed = discord.Embed(title="**Upload Bar Skin**",
                                  description="`Step 2/4`",
                                  color=0xF2BE22)
            embed.add_field(
                name=
                "**Please upload the Bar Skin image file to the current channel!**",
                value=
                "- The file specification is 368 * 8 [Unit: px].\n- File extensions can only be PNG.",
                inline=False)
            embed.set_image(
                url=
                "https://media.discordapp.net/attachments/1146755294601425037/1155399938834956338/result2.png"
            )

            msg = await interaction.response.send_message(
                '## Skin Upload Manager', embed=embed)

            def check(m):
                return m.author == interaction.user

            r = await self.client.wait_for('message', check=check)
            await msg.delete()
            url.append(r.attachments[0].url)
            try:
                if r.attachments[0].url.endswith(
                        'PNG') or r.attachments[0].url.endswith('png'):
                    pass
                else:
                    await interaction.response.send_message('잘못된 형식!')
                    boolean = False
                await r.delete()
            except:
                await r.delete()
                await interaction.response.send_message('파일이 업로드 되지 않았습니다!')
                boolean = False

    @discord.ui.button(label='Skin Layout', style=discord.ButtonStyle.primary)
    async def skinlayout(self, interaction: discord.Interaction,
                         button: discord.ui.Button):
        embed = discord.Embed(
            title="**Skin Layout**",
            description=
            "You can create a layout with the photo editing program by referring to the manual below!",
            color=0xF2BE22)
        embed.add_field(
            name="RANKCARD IMAGE",
            value=
            "- You need to make three types of Rankcard BG, Rankcard Top Cover, and XP Bar BG and prepare a picture of them being placed in the right position and combined.\n- Please refer to the size and position of each part and the picture below for the detailed settings.\n- The finished picture should be 384*144 size like the sample below!",
            inline=False)
        embed.add_field(
            name="XP BAR IMAGE",
            value=
            "- All you need to do is make one 368*8 size stick-shaped photo!\n- However, it should be designed to be sufficiently distinguished from the background picture.\n- Please refer to the picture below for detailed settings!",
            inline=False)
        embed.set_image(
            url=
            "https://media.discordapp.net/attachments/1146755294601425037/1155411328396181544/layout.png"
        )
        await interaction.response.send_message(embed=embed)


class Community(commands.Cog):

    def __init__(self, client: commands.Bot):
        self.client = client

    # Skin Upload [ID: 18]
    @commands.hybrid_command(name='upload',
                             description="Community Skin Upload")
    async def uploadmenu(self, ctx):
        try:
            embed = discord.Embed(
                title="**Community Skin Manager**",
                description="Expires automatically in 10 seconds.",
                color=0xF2BE22)
            embed.add_field(
                name="**Upload Skin**",
                value=
                "Upload your skin and get reviewed by your administrator!",
                inline=False)
            embed.add_field(
                name="**Skin Layout**",
                value=
                "View details of the layout during skin production and download the Photoshop format file.",
                inline=False)
            msg = await ctx.reply('## Skin Upload Manager',
                                  embed=embed,
                                  view=optionButton())
            await self.client.wait_for("interaction",
                                       check=lambda x: x.user == ctx.author,
                                       timeout=10)
            await msg.delete()

        except asyncio.TimeoutError:
            await msg.delete()


async def setup(client):
    await client.add_cog(Community(client))
