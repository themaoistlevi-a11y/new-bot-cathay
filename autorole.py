import discord
from discord.ext import commands

ROLE_1_ID = 1552513921062281326 # 👈 first role
ROLE_2_ID = 1552513921062281331 # 👈 second role

class AutoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):

        role1 = member.guild.get_role(ROLE_1_ID)
        role2 = member.guild.get_role(ROLE_2_ID)

        roles_to_add = [r for r in [role1, role2] if r is not None]

        if roles_to_add:
            try:
                await member.add_roles(*roles_to_add)
            except discord.Forbidden:
                print("Missing permissions to add roles")
            except Exception as e:
                print(f"Error adding roles: {e}")


async def setup(bot):
    await bot.add_cog(AutoRole(bot))