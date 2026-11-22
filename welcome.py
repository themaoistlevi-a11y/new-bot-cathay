import discord
from discord.ext import commands

WELCOME_CHANNEL_ID = 1552513922131820569 # 👈 your channel ID

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):

        channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
        if not channel:
            return


        embed2 = discord.Embed(
            title=f"Welcome onboard Cathay Pacific, {member.mention}!",
            description="Welcome onboard Cathay pacific.\n\n"
            "Thank you for choosing Cathay Pacific, the flag carrier of the Hong Kong SAR. We are commited to delivering a safe, reliable, and comfortable experience through our extensive global network and fleet. Should you require any assistance, please visit our [Helpdesk.](https://discord.com/channels/1552513920579928086/1552513923805225050)",
            color=discord.Color(int("2F6B67", 16))
        )
        embed2.set_image(url="https://cdn.discordapp.com/attachments/1552513922131820564/1553942648317018122/CPA_CX_banner_1.png?ex=6abb155e&is=6ab9c3de&hm=ba1feb7cb37eb82e2ee94f2ce651dbeeb9a7287d3dae57fce3054834b31d5e99&")

        await channel.send(
            embeds=[embed2],
            allowed_mentions=discord.AllowedMentions(users=[member])
        )


async def setup(bot):
    await bot.add_cog(Welcome(bot))