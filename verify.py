import discord
from discord.ext import commands


# =========================================================
# CONFIGURATION — REPLACE ALL EXAMPLE IDS
# =========================================================

MAIN_SERVER_1_ID = 1552513920579928086
MAIN_SERVER_2_ID = 1563398960507392060
STAFF_SERVER_ID = 1492738800604942496

SETUP_PERMISSION_ROLE_ID = 1499552312811589702


# =========================================================
# MAIN SERVER 1 ROLES cathay
# =========================================================

S1_CC_TRAINEE_ID = 1552513921078919181
S1_CC_EMPLOYEE_ID = 1552513921078919184

S1_GC_TRAINEE_ID = 1552513921078919182
S1_GC_EMPLOYEE_ID = 1552513921078919185

S1_FD_TRAINEE_ID = 1552513921078919183
S1_FD_EMPLOYEE_ID = 1566294925815975976


# =========================================================
# MAIN SERVER 2 ROLES cebu
# =========================================================

S2_CC_TRAINEE_ID = 1566559831454650499
S2_CC_EMPLOYEE_ID = 1563424903045058590

S2_GC_TRAINEE_ID = 1566300861523820674
S2_GC_EMPLOYEE_ID = 1563424937597739018

S2_FD_TRAINEE_ID = 1566559789176332459
S2_FD_EMPLOYEE_ID = 1563424856031363072


# =========================================================
# JOINT STAFF SERVER ROLES
# =========================================================

COMMON_STAFF_ROLE_ID = 1501673290052272188

# Department roles
CC_DEPARTMENT_ROLE_ID = 1494897676926586882
GC_DEPARTMENT_ROLE_ID = 1494899729686073538
FD_DEPARTMENT_ROLE_ID = 1494893217055768707

# Cabin Crew status
CC_TRAINEE_ROLE_ID = 1494898710717661355
CC_EMPLOYEE_ROLE_ID = 1494898586385649834

# Ground Crew status
GC_TRAINEE_ROLE_ID = 1494900680752894165
GC_EMPLOYEE_ROLE_ID = 1494900568957911090

# Flight Deck status
FD_TRAINEE_ROLE_ID = 1494896565276381364
FD_EMPLOYEE_ROLE_ID = 1494896176795750521


# =========================================================
# ROLE MAPPINGS
# Format:
# (main server ID, trainee role ID, employee role ID,
#  staff department role ID, staff trainee role ID,
#  staff employee role ID, department name)
# =========================================================

DEPARTMENTS = [
    (
        MAIN_SERVER_1_ID,
        S1_CC_TRAINEE_ID,
        S1_CC_EMPLOYEE_ID,
        CC_DEPARTMENT_ROLE_ID,
        CC_TRAINEE_ROLE_ID,
        CC_EMPLOYEE_ROLE_ID,
        "Cabin Crew",
    ),
    (
        MAIN_SERVER_1_ID,
        S1_GC_TRAINEE_ID,
        S1_GC_EMPLOYEE_ID,
        GC_DEPARTMENT_ROLE_ID,
        GC_TRAINEE_ROLE_ID,
        GC_EMPLOYEE_ROLE_ID,
        "Ground Crew",
    ),
    (
        MAIN_SERVER_1_ID,
        S1_FD_TRAINEE_ID,
        S1_FD_EMPLOYEE_ID,
        FD_DEPARTMENT_ROLE_ID,
        FD_TRAINEE_ROLE_ID,
        FD_EMPLOYEE_ROLE_ID,
        "Flight Deck",
    ),
    (
        MAIN_SERVER_2_ID,
        S2_CC_TRAINEE_ID,
        S2_CC_EMPLOYEE_ID,
        CC_DEPARTMENT_ROLE_ID,
        CC_TRAINEE_ROLE_ID,
        CC_EMPLOYEE_ROLE_ID,
        "Cabin Crew",
    ),
    (
        MAIN_SERVER_2_ID,
        S2_GC_TRAINEE_ID,
        S2_GC_EMPLOYEE_ID,
        GC_DEPARTMENT_ROLE_ID,
        GC_TRAINEE_ROLE_ID,
        GC_EMPLOYEE_ROLE_ID,
        "Ground Crew",
    ),
    (
        MAIN_SERVER_2_ID,
        S2_FD_TRAINEE_ID,
        S2_FD_EMPLOYEE_ID,
        FD_DEPARTMENT_ROLE_ID,
        FD_TRAINEE_ROLE_ID,
        FD_EMPLOYEE_ROLE_ID,
        "Flight Deck",
    ),
]


# =========================================================
# VERIFICATION VIEW
# =========================================================

class VerifyView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(
        label="Verify",
        style=discord.ButtonStyle.success,
        emoji="✅",
        custom_id="joint_staff_verification:verify",
    )
    async def verify_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        await self.cog.verify_member(interaction)


# =========================================================
# VERIFICATION COG
# =========================================================

class StaffVerification(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        # Keep the verification button working after restarts.
        self.bot.add_view(VerifyView(self))

    @commands.command(name="Setupverify")
    @commands.guild_only()
    @commands.has_role(SETUP_PERMISSION_ROLE_ID)
    async def setup_verify(self, ctx: commands.Context):
        """Post the joint staff verification embed."""

        if ctx.guild.id != STAFF_SERVER_ID:
            await ctx.reply(
                "❌ This command can only be used in the joint staff server.",
                mention_author=False,
            )
            return

        embed = discord.Embed(
            title="Joint Staff Server Verification",
            description=(
                "Greetings, and welcome to the Pacific Group general staffing server.\n\n"
                "We are pleased to have you join our team and look forward to having you as part of our growing organization. "
                "To gain access to the rest of the server, please click the **Verify** button below.\n\n"
                "Please note that you must hold at least one trainee or staff role in either the Cebu Pacific or Cathay Pacific "
                "server to complete your verification here.\n\n"
                "If you encounter any issues during the verification process or are unable to verify, "
                "please contact our support team for assistance."
            ),
            color=discord.Color(
                int("2f6b67", 16)
            ),
        )

        embed.set_footer(text="Pacific Group Verification System")

        await ctx.send(embed=embed, view=VerifyView(self))

    async def verify_member(
        self,
        interaction: discord.Interaction,
    ):
        """Check both main servers and assign joint staff roles."""

        if (
            interaction.guild is None
            or interaction.guild.id != STAFF_SERVER_ID
        ):
            await interaction.response.send_message(
                "Please use the verification button in the joint staff server.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        user_id = interaction.user.id

        staff_guild = self.bot.get_guild(STAFF_SERVER_ID)

        if staff_guild is None:
            await interaction.followup.send(
                "Pacific group joint staff server could not be found. Contact support. "
                "Please contact an administrator.",
                ephemeral=True,
            )
            return

        # -------------------------------------------------
        # CHECK MEMBERSHIP IN BOTH MAIN SERVERS
        # -------------------------------------------------

        main_server_ids = [
            MAIN_SERVER_1_ID,
            MAIN_SERVER_2_ID,
        ]

        main_members = {}
        membership_check_failed = False

        for server_id in main_server_ids:
            main_guild = self.bot.get_guild(server_id)

            if main_guild is None:
                membership_check_failed = True
                continue

            try:
                member = await main_guild.fetch_member(user_id)
                main_members[server_id] = member

            except discord.NotFound:
                # Not being in one server is okay if the user
                # belongs to the other server.
                continue

            except (discord.Forbidden, discord.HTTPException):
                membership_check_failed = True

        # If no membership could be confirmed, fail safely.
        if not main_members:
            if membership_check_failed:
                await interaction.followup.send(
                    "We cannot verify your role. If you believe this is an error, contact support.",
                    ephemeral=True,
                )
            else:
                await interaction.followup.send(
                    "You must be a member Cathay Pacific or Cebu Pacific.",
                    ephemeral=True,
                )
            return

        # If one server could not be checked, avoid granting roles
        # based on incomplete information.
        if membership_check_failed:
            await interaction.followup.send(
                "I could not check both servers. "
                "Please contact support.",
                ephemeral=True,
            )
            return

        # -------------------------------------------------
        # GET THE USER'S JOINT STAFF SERVER MEMBERSHIP
        # -------------------------------------------------

        try:
            staff_member = await staff_guild.fetch_member(user_id)

        except discord.NotFound:
            await interaction.followup.send(
                "You are not a member of the joint staff server.",
                ephemeral=True,
            )
            return

        except (discord.Forbidden, discord.HTTPException):
            await interaction.followup.send(
                "I could not check your joint staff server membership. "
                "Please contact support.",
                ephemeral=True,
            )
            return

        # -------------------------------------------------
        # COLLECT ELIGIBLE ROLES FROM BOTH MAIN SERVERS
        # -------------------------------------------------

        role_ids_to_add = {COMMON_STAFF_ROLE_ID}
        matched_departments = set()

        # Keep track of status by department.
        # Employee status takes priority if trainee and employee
        # roles are both present for the same department.
        department_status = {}

        for (
            source_server_id,
            trainee_main_id,
            employee_main_id,
            department_role_id,
            trainee_staff_id,
            employee_staff_id,
            department_name,
        ) in DEPARTMENTS:

            source_member = main_members.get(source_server_id)

            if source_member is None:
                continue

            source_role_ids = {
                role.id for role in source_member.roles
            }

            has_trainee = trainee_main_id in source_role_ids
            has_employee = employee_main_id in source_role_ids

            if not has_trainee and not has_employee:
                continue

            matched_departments.add(department_name)

            role_ids_to_add.add(department_role_id)

            # Employee takes priority over trainee for the same
            # department, even if roles are found across both servers.
            if has_employee:
                department_status[department_name] = (
                    employee_staff_id,
                    "Employee",
                )
            elif department_name not in department_status:
                department_status[department_name] = (
                    trainee_staff_id,
                    "Trainee",
                )

        # Add exactly one status role per eligible department.
        for staff_status_role_id, status_name in department_status.values():
            role_ids_to_add.add(staff_status_role_id)

        if not matched_departments:
            await interaction.followup.send(
                "You are not a staff member. If you believe this is a mistake, contact support.",
                ephemeral=True,
            )
            return

        # -------------------------------------------------
        # RESOLVE STAFF SERVER ROLE IDS
        # -------------------------------------------------

        roles_to_add = []
        missing_role_ids = []

        for role_id in role_ids_to_add:
            role = staff_guild.get_role(role_id)

            if role is None:
                missing_role_ids.append(role_id)
            else:
                roles_to_add.append(role)

        if missing_role_ids:
            await interaction.followup.send(
                "One or more configured staff roles could not be "
                "found. Please contact support. ",
                ephemeral=True,
            )
            return

        # -------------------------------------------------
        # ADD ONLY ROLES THE USER DOES NOT ALREADY HAVE
        # -------------------------------------------------

        existing_role_ids = {
            role.id for role in staff_member.roles
        }

        missing_roles = [
            role
            for role in roles_to_add
            if role.id not in existing_role_ids
        ]

        if missing_roles:
            try:
                await staff_member.add_roles(
                    *missing_roles,
                    reason="Joint staff server verification",
                )

            except discord.Forbidden:
                await interaction.followup.send(
                    "I cannot assign one or more roles. "
                    "Please contact support.",
                    ephemeral=True,
                )
                return

            except discord.HTTPException:
                await interaction.followup.send(
                    "Discord could not assign your roles. "
                    "Please try again later.",
                    ephemeral=True,
                )
                return

        # -------------------------------------------------
        # SUCCESS RESPONSE
        # -------------------------------------------------

        department_lines = []

        for department_name in sorted(matched_departments):
            _, status_name = department_status[department_name]
            department_lines.append(
                f"• **{department_name}:** {status_name}"
            )

        embed = discord.Embed(
            title="Verification Successful!",
            description=(
                f"Welcome to the Pacific Group joint staff server, "
                f"{staff_member.mention}!\n\n"
                "**Your verified departments:**\n"
                + "\n".join(department_lines)
                + "\n\nYour staff roles have been checked and assigned."
            ),
            color=discord.Color.green(),
        )

        embed.set_footer(text="Joint Staff Verification System")

        await interaction.followup.send(
            embed=embed,
            ephemeral=True,
        )

    @setup_verify.error
    async def setup_verify_error(
        self,
        ctx: commands.Context,
        error: commands.CommandError,
    ):
        if isinstance(error, commands.MissingRole):
            await ctx.reply(
                "You do not have permission to set up verification.",
                mention_author=False,
            )
        elif isinstance(error, commands.NoPrivateMessage):
            return
        else:
            await ctx.reply(
                "An error occurred while setting up verification.",
                mention_author=False,
            )
            raise error


# =========================================================
# EXTENSION SETUP
# =========================================================

async def setup(bot: commands.Bot):
    await bot.add_cog(StaffVerification(bot))
