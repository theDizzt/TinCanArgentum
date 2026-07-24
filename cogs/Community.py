import discord
from discord.ext import commands
import fcts.sqlcontrol as q
import fcts.etcfunctions as etc
import fcts.i18n_runtime as i18n
import asyncio


class optionButton(discord.ui.View):

    def __init__(self, client, user):
        super().__init__(timeout=10)
        self.client = client
        self.user = user
        self.uploadskin.label = i18n.t(user, "cmd.16.button.upload")
        self.skinlayout.label = i18n.t(user, "cmd.16.button.layout")

    @discord.ui.button(label='Upload Skin', style=discord.ButtonStyle.primary)
    async def uploadskin(self, interaction: discord.Interaction,
                         button: discord.ui.Button):
        url = []
        boolean = True

        embed = discord.Embed(title=i18n.t(self.user, "cmd.16.rankcard.title"),
                              description=i18n.t(self.user, "cmd.16.step", current=1, total=4),
                              color=0xF2BE22)
        embed.add_field(
            name=i18n.t(self.user, "cmd.16.rankcard.prompt"),
            value=i18n.t(self.user, "cmd.16.rankcard.spec"),
            inline=False)
        embed.set_image(
            url=
            "https://media.discordapp.net/attachments/1146755294601425037/1155399938646229025/result1.png"
        )

        await interaction.response.send_message(i18n.t(self.user, "cmd.16.manager"),
                                                embed=embed)
        msg = await interaction.original_response()

        def check(m):
            return m.author == interaction.user

        r = await self.client.wait_for('message', check=check)
        try:
            if r.attachments[0].url.endswith(
                    'PNG') or r.attachments[0].url.endswith('png'):
                url.append(r.attachments[0].url)
                print(r.attachments[0].url)
            else:
                await interaction.followup.send(i18n.t(self.user, "cmd.16.invalid_format"))
                boolean = False
            await r.delete()
        except:
            await r.delete()
            await interaction.followup.send(i18n.t(self.user, "cmd.16.no_file"))
            boolean = False

        if boolean:
            embed = discord.Embed(title=i18n.t(self.user, "cmd.16.bar.title"),
                                  description=i18n.t(self.user, "cmd.16.step", current=2, total=4),
                                  color=0xF2BE22)
            embed.add_field(
                name=i18n.t(self.user, "cmd.16.bar.prompt"),
                value=i18n.t(self.user, "cmd.16.bar.spec"),
                inline=False)
            embed.set_image(
                url=
                "https://media.discordapp.net/attachments/1146755294601425037/1155399938834956338/result2.png"
            )

            await msg.edit(content=i18n.t(self.user, "cmd.16.manager"), embed=embed)

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
                    await interaction.followup.send(i18n.t(self.user, "cmd.16.invalid_format"))
                    boolean = False
                await r.delete()
            except:
                await r.delete()
                await interaction.followup.send(i18n.t(self.user, "cmd.16.no_file"))
                boolean = False

    @discord.ui.button(label='Skin Layout', style=discord.ButtonStyle.primary)
    async def skinlayout(self, interaction: discord.Interaction,
                         button: discord.ui.Button):
        embed = discord.Embed(
            title=i18n.t(self.user, "cmd.16.layout.title"),
            description=i18n.t(self.user, "cmd.16.layout.desc"),
            color=0xF2BE22)
        embed.add_field(
            name=i18n.t(self.user, "cmd.16.layout.rankcard"),
            value=i18n.t(self.user, "cmd.16.layout.rankcard.desc"),
            inline=False)
        embed.add_field(
            name=i18n.t(self.user, "cmd.16.layout.bar"),
            value=i18n.t(self.user, "cmd.16.layout.bar.desc"),
            inline=False)
        embed.set_image(
            url=
            "https://media.discordapp.net/attachments/1146755294601425037/1155411328396181544/layout.png"
        )
        await interaction.response.send_message(embed=embed)


class Community(commands.Cog):

    def __init__(self, client: commands.Bot):
        self.client = client

    # Skin Upload [ID: 16]
    @commands.hybrid_command(name='upload',
                             description="Community Skin Upload")
    async def uploadmenu(self, ctx):
        try:
            embed = discord.Embed(
                title=i18n.t(ctx.author, "cmd.16.menu.title"),
                description=i18n.t(ctx.author, "cmd.16.menu.expires"),
                color=0xF2BE22)
            embed.add_field(
                name=i18n.t(ctx.author, "cmd.16.button.upload"),
                value=i18n.t(ctx.author, "cmd.16.menu.upload"),
                inline=False)
            embed.add_field(
                name=i18n.t(ctx.author, "cmd.16.button.layout"),
                value=i18n.t(ctx.author, "cmd.16.menu.layout"),
                inline=False)
            msg = await ctx.reply(i18n.t(ctx.author, "cmd.16.manager"),
                                  embed=embed,
                                  view=optionButton(self.client, ctx.author))
            await self.client.wait_for("interaction",
                                       check=lambda x: x.user == ctx.author,
                                       timeout=10)
            await msg.delete()

        except asyncio.TimeoutError:
            await msg.delete()


async def setup(client):
    await client.add_cog(Community(client))
