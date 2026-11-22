import discord
from discord.ext import commands
from discord import app_commands

# =========================
# CONFIG
# =========================

SUPPORT_ROLE_ID = 1553257456178561044

ANNOUNCEMENT_CHANNEL_ID = 1552513922848788505


# =========================
# COG
# =========================

class DenyApplicant(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =========================
    # DENY APPLICANT COMMAND
    # =========================

    @app_commands.command(
        name="deny-applicant",
        description="Denies an applicant."
    )
    @app_commands.describe(
        user="The applicant to deny",
        rank="The position they applied for",
        reason="Reason for denial"
    )
    @app_commands.choices(
        rank=[
            app_commands.Choice(
                name="Cabin Crew",
                value="Cabin Crew"
            ),
            app_commands.Choice(
                name="Ground Operator",
                value="Ground Operator"
            ),
            app_commands.Choice(
                name="Pilot",
                value="Pilot"
            ),
        ]
    )
    async def deny_applicant(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        rank: app_commands.Choice[str],
        reason: str
    ):

        # =========================
        # PERMISSION CHECK
        # =========================

        if SUPPORT_ROLE_ID not in [r.id for r in interaction.user.roles]:

            await interaction.response.send_message(
                "You do not have permission to use this command.",
                ephemeral=True
            )

            return

        # =========================
        # EMBED FOR APPLICANT
        # =========================

        embed = discord.Embed(
            title="Application Denied",
            description=(
                f"Greetings, {user.mention}.\n\n"

                f"Thank you for completing the Cathay Pacific Basic "
                f"Employment Application. After careful review and "
                f"consideration by our leadership team, we regret to "
                f"inform you that we are unable to offer you a position "
                f"as a **{rank.value}** at this time due to the "
                f"following reason(s):\n\n"

                f"**Reason(s):**\n"
                f"• {reason}\n\n"

                f"We sincerely appreciate the time, effort, and interest "
                f"you invested in your application. If you believe this "
                f"decision was made in error, please feel free to contact "
                f"our support team for further assistance.\n\n"

                f"**Please note that you are welcome to submit another "
                f"application in the future.**\n\n"

                f"**Thank you,**\n"
                f"***Cathay Pacific Leadership***"
            ),
            color=discord.Color(
                int("2f6b67", 16)
            )
        )

        # =========================
        # PUBLIC ANNOUNCEMENT EMBED
        # =========================

        embed1 = discord.Embed(
            title="<:Deny:1553667563693678712> Application Denied",
            description=(
                f"**Applicant:** {user.mention}\n"
                f"**Application:** {rank.value}\n\n"

                f"Thank you for your interest in joining the "
                f"Cathay Pacific staff team. Unfortunately, after "
                f"careful consideration, we regret to inform you "
                f"that your application was not successful at this "
                f"time. Further information regarding the application "
                f"has been sent to the applicant via direct message."
            ),
            color=discord.Color(
                int("2f6b67", 16)
            )
        )

        # =========================
        # SEND DM
        # =========================

        dm_success = True

        try:

            await user.send(
                content=user.mention,
                embed=embed
            )

        except discord.Forbidden:

            dm_success = False

        except discord.HTTPException:

            dm_success = False

        # =========================
        # SEND ANNOUNCEMENT
        # =========================

        announcement_channel = interaction.guild.get_channel(
            ANNOUNCEMENT_CHANNEL_ID
        )

        if announcement_channel is not None:

            try:

                await announcement_channel.send(
                    content=user.mention,
                    embed=embed1
                )

            except discord.Forbidden:

                print(
                    "[DenyApplicant] "
                    "I don't have permission to send messages "
                    "in the announcement channel."
                )

            except discord.HTTPException as error:

                print(
                    f"[DenyApplicant] "
                    f"Failed to send announcement: {error}"
                )

        else:

            print(
                "[DenyApplicant] "
                "Announcement channel not found."
            )

        # =========================
        # COMMAND RESPONSE
        # =========================

        if dm_success:

            await interaction.response.send_message(
                f"Successfully denied {user.mention}.",
                ephemeral=True
            )

        else:

            await interaction.response.send_message(
                f"Successfully denied {user.mention}, "
                f"but I could not DM them because their DMs "
                f"are closed or unavailable.",
                ephemeral=True
            )

        # =========================
        # DENIED MESSAGE IN COMMAND CHANNEL
        # =========================

        try:

            await interaction.channel.send(
                content=(
                    f"# APPLICATION DENIED BY "
                    f"{interaction.user.mention}"
                )
            )

        except discord.Forbidden:

            print(
                "[DenyApplicant] "
                "I don't have permission to send messages "
                "in the command channel."
            )


# =========================
# LOAD COG
# =========================

async def setup(bot):

    await bot.add_cog(
        DenyApplicant(bot)
    )
