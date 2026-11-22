import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Select, Button
import io

# =========================
# CONFIG (CHANGE THESE)
# =========================
SUPPORT_ROLE_ID = 1552513921104216096
CATEGORY_ID = 1552513923805225051
TRANSCRIPT_CHANNEL_ID = 1552513924681699413
STAFF_ROLE_ID = 1552513921141968950

def is_staff(member):
    return any(r.id == STAFF_ROLE_ID for r in member.roles)


# =========================
# TICKET BUTTONS
# =========================
class TicketButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.claimed_by = None

    @discord.ui.button(label="Claim Ticket", style=discord.ButtonStyle.success)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):

        # UNCLAIM
        if button.label == "Unclaim":

            if self.claimed_by != interaction.user.id:
                await interaction.response.send_message(
                    "Only the staff member who claimed this ticket can unclaim it.",
                    ephemeral=True
                )
                return

            self.claimed_by = None

            await interaction.channel.edit(
                name=interaction.channel.name.replace("claimed-", "", 1)
            )

            button.label = "Claim Ticket"
            button.style = discord.ButtonStyle.success

            await interaction.response.edit_message(view=self)

            await interaction.followup.send(
                "You've unclaimed this ticket.",
                ephemeral=True
            )

            await interaction.channel.send(
                "Your ticket has been unclaimed."
            )

            return

        # CLAIM
        if SUPPORT_ROLE_ID not in [r.id for r in interaction.user.roles]:
            await interaction.response.send_message(
                "Only support staff can claim tickets.",
                ephemeral=True
            )
            return

        self.claimed_by = interaction.user.id

        await interaction.channel.edit(
            name=f"claimed-{interaction.channel.name}"
        )

        button.label = "Unclaim"
        button.style = discord.ButtonStyle.danger

        await interaction.response.edit_message(view=self)

        await interaction.followup.send(
            "You've claimed this ticket.",
            ephemeral=True
        )

        await interaction.channel.send(
            f"Your ticket has been claimed and handled by {interaction.user.mention}."
        )

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):

        if SUPPORT_ROLE_ID not in [r.id for r in interaction.user.roles]:
            await interaction.response.send_message(
                "Only support staff can close tickets.",
                ephemeral=True
            )
            return

        await interaction.response.send_message("Closing ticket...")

        transcript = ""
        async for msg in interaction.channel.history(limit=None, oldest_first=True):
            transcript += f"{msg.author}: {msg.content}\n"

        file = discord.File(
            io.StringIO(transcript),
            filename=f"{interaction.channel.name}.txt"
        )

        log_channel = interaction.guild.get_channel(TRANSCRIPT_CHANNEL_ID)

        if log_channel:
            await log_channel.send(
                content=f"Transcript - {interaction.channel.name}",
                file=file
            )

        await interaction.channel.delete()



# =========================
# DROPDOWN MENU
# =========================
class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="General Inquiry",
                description="General, Asia Miles, Operations inquries.",
                value="general"
            ),
            discord.SelectOption(
                label="Partnership Inquiry",
                description="Partnership and codeshare/Joint Venture request & inquries",
                value="partnership"
            ),
            discord.SelectOption(
                label="Direct-Entry inquiry",
                description="Direct-Entry request & inquries",
                value="direct"
            ),
        ]

        super().__init__(
            placeholder="Select a support category...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild

        category = guild.get_channel(CATEGORY_ID)

        # ❌ One ticket per user
        for ch in category.text_channels:
            if ch.topic == str(interaction.user.id):
                await interaction.response.send_message(
                    "You already have an open ticket, please direct your inquiry to your open ticket.",
                    ephemeral=True
                )
                return

        ticket_type = self.values[0]

        channel = await guild.create_text_channel(
            name=f"{ticket_type}-{interaction.user.name}".lower(),
            category=category,
            topic=str(interaction.user.id),
            overwrites={
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True),
                guild.get_role(SUPPORT_ROLE_ID): discord.PermissionOverwrite(view_channel=True, send_messages=True),
            }
        )

        # =========================
        # GENERAL TICKET
        # =========================
        if ticket_type == "general":

            embed1 = discord.Embed(color=discord.Color(int("2F6B67", 16)))
            embed1.set_image(
                url="https://cdn.discordapp.com/attachments/1552513922131820564/1553654550102151230/CPA_CX_banner_2.png?ex=6aba090e&is=6ab8b78e&hm=fcda1de28acc355536605c6cd88ba2cd34bc528de2a1e3c769d0d7dbeb4739ab&"
            )

            embed2 = discord.Embed(
                title=f"General Inquiry - {interaction.user.name}",
                description=(
                    "Thank you for contacting the Cathay Pacific support team. "
                    "Please describe your inquiry below, and our support team will assist you as soon as possible."
                ),
                color=discord.Color(int("2F6B67", 16))
            )

            embed2.set_image(
                url="https://cdn.discordapp.com/attachments/1552513922131820564/1553654193422860450/New_Project_2_1.png?ex=6aba08b9&is=6ab8b739&hm=e07e2d8c6a2a6fefc1ab39e96069dd41b843ed6d8d5b6d9955cc7133ecbee5b2&"
            )

            await channel.send(
                content=f"{interaction.user.mention} <@&{SUPPORT_ROLE_ID}>",
                embeds=[embed1, embed2],
                view=TicketButtons()
            )

        # =========================
        # PARTNERSHIP TICKET
        # =========================
        elif ticket_type == "partnership":

            embed1 = discord.Embed(color=discord.Color(int("2F6B67", 16)))
            embed1.set_image(
                url="https://cdn.discordapp.com/attachments/1552513922131820564/1553654550102151230/CPA_CX_banner_2.png?ex=6aba090e&is=6ab8b78e&hm=fcda1de28acc355536605c6cd88ba2cd34bc528de2a1e3c769d0d7dbeb4739ab&"
            )

            embed2 = discord.Embed(
                title=f"Partnership Inquiry - {interaction.user.name}",
                description=(
                    "Thank you for contacting the Cathay Pacific support team. "
                    "Please describe your inquiry below, and our support team will assist you as soon as possible.\n\n"
                    "For Partnership requests, please ensure your server meets our requirements in <#1552513922848788501> and list your server link and repersentative below. \n\n"
                    "For codeshare requests, please list your airline, desired route, airline of operations, and time below."
                ),
                color=discord.Color(int("2F6B67", 16))
            )

            embed2.set_image(
                url="https://cdn.discordapp.com/attachments/1552513922131820564/1553654193422860450/New_Project_2_1.png?ex=6aba08b9&is=6ab8b739&hm=e07e2d8c6a2a6fefc1ab39e96069dd41b843ed6d8d5b6d9955cc7133ecbee5b2&"
            )

            await channel.send(
                content=f"{interaction.user.mention} <@&{SUPPORT_ROLE_ID}>",
                embeds=[embed1, embed2],
                view=TicketButtons()
            )

		# =========================
        # PARTNERSHIP TICKET
        # =========================
        elif ticket_type == "direct":

            embed1 = discord.Embed(color=discord.Color(int("2F6B67", 16)))
            embed1.set_image(
                url="https://cdn.discordapp.com/attachments/1552513922131820564/1553654550102151230/CPA_CX_banner_2.png?ex=6aba090e&is=6ab8b78e&hm=fcda1de28acc355536605c6cd88ba2cd34bc528de2a1e3c769d0d7dbeb4739ab&"
            )

            embed2 = discord.Embed(
                title=f"Direct-Entry Inquiry - {interaction.user.name}",
                description=(
                    "Thank you for contacting the Cathay Pacific support team. "
                    "Please describe your inquiry below, and our support team will assist you as soon as possible.\n\n"
                    "For Direct-entry requests, ensure that you meet the requirements listed in <#1552513922131820572>. Provide us with your server of employment, the role your fast-passing for, and proof of employment.\n\n"
                    "Please provide us with a server link for your server of employment and an **uncropped** image of your roles within your server of employment."
                ),
                color=discord.Color(int("2F6B67", 16))
            )

            embed2.set_image(
                url="https://cdn.discordapp.com/attachments/1552513922131820564/1553654193422860450/New_Project_2_1.png?ex=6aba08b9&is=6ab8b739&hm=e07e2d8c6a2a6fefc1ab39e96069dd41b843ed6d8d5b6d9955cc7133ecbee5b2&"
            )

            await channel.send(
                content=f"{interaction.user.mention} <@&{SUPPORT_ROLE_ID}>",
                embeds=[embed1, embed2],
                view=TicketButtons()
            )

        await interaction.response.send_message(
            f"Your ticket has created: {channel.mention}.",
            ephemeral=True
        )


# =========================
# VIEW
# =========================
class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())
        
# =========================
# close request
# =========================
class CloseRequestView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.green)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        await interaction.response.send_message(
        	"Closing ticket...",
        	ephemeral=True
        )
        

        transcript = ""
        async for msg in interaction.channel.history(limit=None, oldest_first=True):
            transcript += f"{msg.author}: {msg.content}\n"

        file = discord.File(
            io.StringIO(transcript),
            filename=f"{interaction.channel.name}.txt"
        )

        log_channel = interaction.guild.get_channel(TRANSCRIPT_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                content=f"Transcript - {interaction.channel.name}",
                file=file
            )

        await interaction.channel.delete()
        
    @discord.ui.button(label="Keep Open", style=discord.ButtonStyle.red)
    async def keep_open(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
        	"Your ticket will not be closed. Please state your additional inquries.",
        	ephemeral=False
        )
        

        

    

# =========================
# MAIN COG
# =========================
class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setup")
    async def setup(self, interaction):

        # Admin only
        if not is_staff(interaction.author):
            return await interaction.send("You do not have permission to use this command.", delete_after=2)

        # --- EMBED 1 ---
        embed1 = discord.Embed(color=discord.Color(int("2F6B67", 16)))
        embed1.set_image(
            url="https://cdn.discordapp.com/attachments/1552513922131820564/1553654550102151230/CPA_CX_banner_2.png?ex=6aba090e&is=6ab8b78e&hm=fcda1de28acc355536605c6cd88ba2cd34bc528de2a1e3c769d0d7dbeb4739ab&"
        )

        # --- EMBED 2 (FIXED EXACT TEXT YOU WANTED) ---
        embed2 = discord.Embed(
            title="Cathay Pacific Helpdesk",
            description=(
                "**Thank you for contacting Cathay Pacific Support.**\n\n"
                "Please choose the category that best matches your request so we can connect you with the right team as quickly as possible.\n\n"
                "To help us assist you efficiently, make sure to include all relevant details in your ticket. "
                "Incomplete information may result in delays. Our support staff is here to ensure a smooth and professional experience from start to finish."
            ),
            color=discord.Color(int("2F6B67", 16))
        )

        embed2.set_image(
            url="https://cdn.discordapp.com/attachments/1552513922131820564/1553654193422860450/New_Project_2_1.png?ex=6aba08b9&is=6ab8b739&hm=e07e2d8c6a2a6fefc1ab39e96069dd41b843ed6d8d5b6d9955cc7133ecbee5b2&"
        )

        await interaction.send(
            embeds=[embed1, embed2],
            view=TicketView()
        )
        
    @app_commands.command(name="close-request", description="Sends a ticket close request.")
    async def close_request(self, interaction: discord.Interaction):
        
        channel = interaction.channel
        ticket_owner = int(channel.topic)
        
        if not any(r.id == SUPPORT_ROLE_ID for r in interaction.user.roles):
            return await interaction.response.send_message(
            	"Only support staff can use this command.",
            	ephemeral=True
            )
    
        closereqembed = discord.Embed(
    		title="Has your inquries been resolved?",
    		description="Looks like your inquries has been resolved by one of our support team members. May we close this ticket?",
    		color=discord.Color(int("2F6B67", 16))
   		)
    
        closereqembed.set_footer(text="Cathay Pacific Support Team")
    
        await interaction.response.send_message(
            content=f"<@{ticket_owner}>",
    		embed=closereqembed,
    		view=CloseRequestView()
    	)


async def setup(bot):
    await bot.add_cog(TicketSystem(bot))