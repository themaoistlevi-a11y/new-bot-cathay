import discord
from discord.ext import commands
from discord import app_commands

# =========================
# CONFIG
# =========================

SUPPORT_ROLE_ID = 1553257456178561044

CABIN_TRAINEE_ROLE = 1552513921078919181
GROUND_TRAINEE_ROLE = 1552513921078919182
FLIGHT_TRAINEE_ROLE = 1552513921078919183

STAFF_MEMBER_ROLE = 1552513921091371080

# Channel where the acceptance announcement will be sent
ANNOUNCEMENT_CHANNEL_ID = 1552513922848788505


# =========================
# COG
# =========================

class ApplicantSystem(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =========================
    # PASS APPLICANT
    # =========================

    @app_commands.command(
        name="pass-applicant",
        description="Accepts an applicant and assigns trainee roles."
    )
    @app_commands.describe(
        user="The applicant to accept",
        application_type="The application department"
    )
    @app_commands.choices(application_type=[
        app_commands.Choice(
            name="Cabin Crew",
            value="cabin"
        ),
        app_commands.Choice(
            name="Ground Crew",
            value="ground"
        ),
        app_commands.Choice(
            name="Flight Deck",
            value="flight"
        ),
    ])
    async def pass_applicant(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        application_type: app_commands.Choice[str]
    ):

        # =========================
        # SUPPORT ROLE CHECK
        # =========================

        if SUPPORT_ROLE_ID not in [r.id for r in interaction.user.roles]:

            await interaction.response.send_message(
                "You do not have permission to use this command.",
                ephemeral=True
            )

            return

        # =========================
        # APPLICATION TYPES
        # =========================

        if application_type.value == "cabin":

            trainee_role_id = CABIN_TRAINEE_ROLE
            trainee_name = "Cabin Crew Trainee"
            duty_name = "Cabin Crew"

        elif application_type.value == "ground":

            trainee_role_id = GROUND_TRAINEE_ROLE
            trainee_name = "Ground Crew Trainee"
            duty_name = "Ground Operator"

        elif application_type.value == "flight":

            trainee_role_id = FLIGHT_TRAINEE_ROLE
            trainee_name = "Flight Deck Trainee"
            duty_name = "Pilot"

        else:

            await interaction.response.send_message(
                "Invalid application type.",
                ephemeral=True
            )

            return

        # =========================
        # GET ROLES
        # =========================

        trainee_role = interaction.guild.get_role(
            trainee_role_id
        )

        staff_role = interaction.guild.get_role(
            STAFF_MEMBER_ROLE
        )

        # =========================
        # CHECK ROLES
        # =========================

        if trainee_role is None:

            await interaction.response.send_message(
                "The trainee role could not be found.",
                ephemeral=True
            )

            return

        if staff_role is None:

            await interaction.response.send_message(
                "The staff member role could not be found.",
                ephemeral=True
            )

            return

        # =========================
        # GIVE ROLES
        # =========================

        try:

            await user.add_roles(
                trainee_role,
                reason="Applicant accepted"
            )

            await user.add_roles(
                staff_role,
                reason="Applicant accepted"
            )

        except discord.Forbidden:

            await interaction.response.send_message(
                "I don't have permission to give one or more of the roles.",
                ephemeral=True
            )

            return

        # =========================
        # ACCEPTANCE EMBED
        # =========================

        embed = discord.Embed(
            title="Application Accepted!",
            description=(
                f"Greetings, {user.mention}\n\n"

                f"Congratulations on the successful completion of the "
                f"Cathay Pacific basic employment application. "
                f"You have successfully received your rank of "
                f"{trainee_name}.\n\n"

                f"**What next?**\n"
                f"You will now have 5 days to join our staff server "
                f"listed in <#1552513923201376284>. "
                f"Failing to do so will result in an automatic "
                f"termination.\n\n"

                f"Before you start your duties as a {duty_name}, "
                f"you will be required to go through our standard "
                f"training program, showcasing your ability to "
                f"effectively perform your duties.\n\n"

                f"**Congratulations, and we are looking forward "
                f"to working with you!**\n\n"

                f"**Sincerely,**\n"
                f"***Cathay Pacific Leadership***"
            ),
            color=discord.Color(
                int("2f6b67", 16)
            )
        )
        
        embed1 = discord.Embed(
            title="<:Pass:1553667532198772757> Application Accepted",
            description=(
                f"**Applicant:** {user.mention}\n"
                f"**Application:** {duty_name}\n\n"
                f"Thank you for your intrest in joining the Cathay Pacific staff team, we are pleased to have you here. Please ensure to join our staff server for trainings and latest news. More information reguarding your new role has been sent to you via DMs."
            ),
            color=discord.Color(
                int("2f6b67", 16)
            )
        )

        # =========================
        # SEND ACCEPTANCE ANNOUNCEMENT
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
                    "[ApplicantSystem] "
                    "I don't have permission to send "
                    "messages in the announcement channel."
                )

        else:

            print(
                "[ApplicantSystem] "
                "Announcement channel not found."
            )

        # =========================
        # DM USER
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
        # COMMAND RESPONSE
        # =========================

        if dm_success:

            await interaction.response.send_message(
                f"Successfully accepted {user.mention}.",
                ephemeral=True
            )
            
            await interaction.channel.send(
            content=f"# APPLICATION ACCEPTED BY {interaction.user.mention}")

        else:

            await interaction.response.send_message(
                f"Successfully accepted {user.mention}, "
                f"but I could not DM them because their DMs "
                f"are closed or unavailable.",
                ephemeral=True
            )


# =========================
# SETUP
# =========================

async def setup(bot):

    await bot.add_cog(
        ApplicantSystem(bot)
    )
