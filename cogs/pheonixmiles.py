import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from datetime import datetime

# =========================================================
# CONFIG
# =========================================================

BANNER = "https://cdn.discordapp.com/attachments/1552513922131820564/1553654184639995945/CPA_CX_banner_1.png?ex=6aba08b7&is=6ab8b737&hm=46620806c1d4699b4bb8893116848fd3293462d2943216c17f37e1db1d5c4588&"
IMAGE = "https://cdn.discordapp.com/attachments/1552513922131820564/1553654193422860450/New_Project_2_1.png?ex=6aba08b9&is=6ab8b739&hm=e07e2d8c6a2a6fefc1ab39e96069dd41b843ed6d8d5b6d9955cc7133ecbee5b2&"

STAFF_ROLE_ID = 1553199004526055514
LOG_CHANNEL_ID = 1552513924681699413

MILE_TIERS = {
    "Cathay Silver": {"req": 30000, "role": 1552513921062281332},
    "Cathay Gold": {"req": 80000, "role": 1552513921062281334},
    "Cathay Diamond": {"req": 200000, "role": 1552513921062281335}
}

DATA_FILE = "data.json"

# =========================================================
# JSON SAFE
# =========================================================

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(DATA_FILE, "r") as f:
            content = f.read().strip()
            return json.loads(content) if content else {}
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# =========================================================
# HELPERS
# =========================================================

def is_staff(member):
    return any(r.id == STAFF_ROLE_ID for r in member.roles)

def get_rank(miles):
    rank = "Cathay Green"
    for name, data in sorted(MILE_TIERS.items(), key=lambda x: x[1]["req"]):
        if miles >= data["req"]:
            rank = name
    return rank

def next_rank(miles):
    for name, data in sorted(MILE_TIERS.items(), key=lambda x: x[1]["req"]):
        if miles < data["req"]:
            return f"{name} ({data['req'] - miles} needed)"
    return "MAX RANK"

async def update_roles(member, miles):
    for tier in MILE_TIERS.values():
        role = member.guild.get_role(tier["role"])
        if role and role in member.roles:
            await member.remove_roles(role)

    for name, data in sorted(MILE_TIERS.items(), key=lambda x: x[1]["req"]):
        if miles >= data["req"]:
            role = member.guild.get_role(data["role"])
            if role:
                await member.add_roles(role)
                
def get_miles_multiplier(member):
    role_multipliers = {
        1552513921062281332: 1.25,
        1552513921062281334: 1.5,
        1552513921062281335: 2.0
    }
    
    multiplier = 1.0
    
    for role_id, bonus in role_multipliers.items():
        if any(role.id == role_id for role in member.roles):
            multiplier = max(multiplier, bonus)
            
    return multiplier

# =========================================================
# LOG SYSTEM
# =========================================================

async def send_log(guild, target, mod, action, desc):
    channel = guild.get_channel(LOG_CHANNEL_ID)
    if not channel:
        return

    e1 = discord.Embed(color=discord.Color(int("2F6B67", 16)))
    e1.set_image(url=BANNER)

    e2 = discord.Embed(
        title="Flight/Miles updated",
        description=f"""Target user: {target.mention}
Moderator: {mod.mention}
Action: {action}

{desc}""",
        color=discord.Color(int("2F6B67", 16)
    ))
    e2.set_image(url=IMAGE)

    await channel.send(embeds=[e1, e2])

# =========================================================
# BUTTON VIEW
# =========================================================

class ProfileView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=120)
        self.user_id = user_id

    @discord.ui.button(label="Flight Log", style=discord.ButtonStyle.danger)
    async def flight_log(self, interaction: discord.Interaction, button: discord.ui.Button):


        data = load_data()
        flights = data.get(str(self.user_id), {}).get("flights", [])

        e1 = discord.Embed(color=discord.Color(int("2F6B67", 16)))
        e1.set_image(url=BANNER)

        text = ""
        for f in flights[-10:][::-1]:
            text += f"{f['flight']} | {f['route']}\n-# {f['time']}\n\n"

        e2 = discord.Embed(
            title=f"{(await interaction.client.fetch_user(self.user_id)).display_name}'s flight log",
            description=text if text else "No flights logged.",
            color=discord.Color(int("2F6B67", 16))
        )
        e2.set_image(url=IMAGE)

        await interaction.response.send_message(embeds=[e1, e2], ephemeral=True)

# =========================================================
# COG
# =========================================================

class PhoenixMiles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ================= ADD MILE =================
    @app_commands.command(name="add-mile", description="Adds Asia Miles to a user")
    @app_commands.describe(user="Target user (Add miles)", amount="Target amount of Asia Miles to add")
    async def add_mile(self, interaction: discord.Interaction, user: discord.Member, amount: int):

        if not is_staff(interaction.user):
            return await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)

        data = load_data()
        uid = str(user.id)
        u = data.get(str(user.id), {"miles": 0, "flights": []})

        data.setdefault(uid, {"miles": 0, "flights": []})
        
        multiplier = get_miles_multiplier(user)
        bonus_miles = int(amount * multiplier)
        data[uid]["miles"] += bonus_miles
        
        save_data(data)

        total = data[uid]["miles"]
        await update_roles(user, total)

        await interaction.response.send_message("Miles added successfully.", ephemeral=True)

        # 🔥 PUBLIC MESSAGE (YOU WERE MISSING THIS)
        await interaction.channel.send(embeds=[
            discord.Embed(color=discord.Color(int("2F6B67", 16))).set_image(url=BANNER),
            discord.Embed(
                title="Miles added successfully",
                description=f"""Target user: {user.mention}
Moderator: {interaction.user.mention}
Action: Added miles
Base miles: {amount}
Multiplier: {multiplier}x
Total miles added: {bonus_miles}
{user.mention}'s remaining miles: {total}
Next upgrade: {next_rank(total)}""",
                color=discord.Color(int("2F6B67", 16))
            ).set_image(url=IMAGE)
        ])

        await send_log(interaction.guild, user, interaction.user, "Add Miles", f"+{amount} | {total}")

    # ================= REMOVE MILE =================
    @app_commands.command(name="remove-mile", description="Removes Asia Miles from a user")
    @app_commands.describe(user="Target user (Remove miles)", amount="Target amount of Asia Miles to remove")
    async def remove_mile(self, interaction: discord.Interaction, user: discord.Member, amount: int):

        if not is_staff(interaction.user):
            return await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)

        data = load_data()
        uid = str(user.id)
        u = data.get(str(user.id), {"miles": 0, "flights": []})

        data.setdefault(uid, {"miles": 0, "flights": []})
        data[uid]["miles"] = max(0, data[uid]["miles"] - amount)
        save_data(data)

        total = data[uid]["miles"]
        await update_roles(user, total)

        await interaction.response.send_message("Miles removed successfully.", ephemeral=True)

        await interaction.channel.send(embeds=[
            discord.Embed(color=discord.Color(int("2F6B67", 16))).set_image(url=BANNER),
            discord.Embed(
                title="Miles removed successfully",
                description=f"""User: {user.mention}
Moderator: {interaction.user.mention}
Action: Removed miles
Total miles removed: {amount}
{user.mention}'s remaining miles: {total}
Next upgrade: {next_rank(u['miles'])}""",
                color=(discord.Color(int("2F6B67", 16)))
            ).set_image(url=IMAGE)
        ])

        await send_log(interaction.guild, user, interaction.user, "Remove Miles", f"-{amount} | {total}")

    # ================= ADD FLIGHT =================
    @app_commands.command(name="add-flight", description="Adds a flight log to a user")
    @app_commands.describe(user="Target user (Add flight)", flight="Flight designator (ex: CX123)", route="Route of flight; IATA codes (ex: PEK - HKG)")
    async def add_flight(self, interaction, user: discord.Member, flight: str, route: str):

        if not is_staff(interaction.user):
            return await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)

        data = load_data()
        uid = str(user.id)

        data.setdefault(uid, {"miles": 0, "flights": []})

        data[uid]["flights"].append({
            "flight": flight,
            "route": route,
            "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        })

        save_data(data)

        await interaction.response.send_message("Flight logged successfully.", ephemeral=True)

        await interaction.channel.send(embeds=[
            discord.Embed(color=discord.Color(int("2F6B67", 16))).set_image(url=BANNER),
            discord.Embed(
                title="Flight added successfully",
                description=f"""Target user: {user.mention}
Moderator: {interaction.user.mention}
Action: Added flight
Flight: {flight}
Route: {route}""",
                color=discord.Color(int("2F6B67", 16))
            ).set_image(url=IMAGE)
        ])

        await send_log(interaction.guild, user, interaction.user, "Add Flight", f"{flight} | {route}")

    # ================= REMOVE FLIGHT =================
        # ================= REMOVE FLIGHT =================
    @app_commands.command(name="remove-flight", description="Removes a flight log from a specific user")
    @app_commands.describe(
        user="Target user (Remove flight)",
        flight="Flight designator (ex: CX123)"
    )
    async def remove_flight(self, interaction: discord.Interaction, user: discord.Member, flight: str):

        if not is_staff(interaction.user):
            return await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)

        data = load_data()
        uid = str(user.id)

        flights = data.get(uid, {}).get("flights", [])

        if not flights:
            return await interaction.response.send_message("No flights found.", ephemeral=True)

        removed = None

        for f in flights:
            if f["flight"].lower() == flight.lower():
                removed = f
                flights.remove(f)
                break

        if not removed:
            return await interaction.response.send_message("Flight not found, ensure flight designator is typed in correctly.", ephemeral=True)

        save_data(data)

        await interaction.response.send_message("Flight log removed successfully", ephemeral=True)

        await interaction.channel.send(
            embeds=[
                discord.Embed(color=discord.Color(int("2F6B67", 16))).set_image(url=BANNER),
                discord.Embed(
                    title="Flight removed successfully",
                    description=f"""Target user: {user.mention}
Moderator: {interaction.user.mention}
Action: Removed flight
Flight: {removed['flight']}
Route: {removed['route']}""",
                    color=discord.Color(int("2F6B67", 16))
                ).set_image(url=IMAGE)
            ]
        )

        await send_log(
            interaction.guild,
            user,
            interaction.user,
            "Remove Flight",
            f"{removed['flight']} | {removed['route']}"
        )
    # ================= PROFILE =================
    @app_commands.command(name="profile", description="View your profile")
    @app_commands.describe(user="Target user (View profile)")
    async def profile(self, interaction, user: discord.Member = None):

        user = user or interaction.user
        data = load_data()
        u = data.get(str(user.id), {"miles": 0, "flights": []})

        e1 = discord.Embed(color=discord.Color(int("2F6B67", 16)))
        e1.set_image(url=BANNER)

        e2 = discord.Embed(
            title=f"{user.display_name}'s Asia Miles status",
            description=f"""User: {user.mention}
Miles: {u['miles']}
Flights: {len(u['flights'])}
Rank: {get_rank(u['miles'])}
Next upgrade: {next_rank(u['miles'])}""",
            color=discord.Color(int("2F6B67", 16))
        )
        e2.set_image(url=IMAGE)

        await interaction.response.send_message(
            embeds=[e1, e2],
            view=ProfileView(user.id)
        )

# =========================================================
# SETUP
# =========================================================

async def setup(bot):
    await bot.add_cog(PhoenixMiles(bot))

