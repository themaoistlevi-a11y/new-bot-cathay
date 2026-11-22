import discord
from discord.ext import commands

class GetIDs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="getcategory")
    async def get_category_id(self, ctx):
        if ctx.channel.category:
            await ctx.send(f"Category ID: `{ctx.channel.category.id}`")
        else:
            await ctx.send("❌ This channel is not in a category.")

async def setup(bot):
    await bot.add_cog(GetIDs(bot))