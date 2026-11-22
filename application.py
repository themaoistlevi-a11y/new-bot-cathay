import discord
from discord.ext import commands
from aiohttp import web


class Applications(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # ==========================================
        # EDIT THESE
        # ==========================================

        # ID of your DISCORD FORUM CHANNEL
        self.channel_id = 1553237899997089902

        # WispByte port
        self.port = 9757

        # ==========================================

        self.app = web.Application()

        self.app.router.add_post(
            "/application",
            self.receive_application
        )

        self.runner = None
        self.site = None

        self.bot.loop.create_task(
            self.start_web_server()
        )

    async def start_web_server(self):
        await self.bot.wait_until_ready()

        self.runner = web.AppRunner(self.app)
        await self.runner.setup()

        self.site = web.TCPSite(
            self.runner,
            "0.0.0.0",
            self.port
        )

        await self.site.start()

        print(
            f"[Applications] Webhook running on port {self.port}"
        )

    async def receive_application(self, request):
        try:
            data = await request.json()

            print("[Applications] New application received!")

            await self.create_application(data)

            return web.json_response({
                "success": True
            })

        except Exception as error:

            print(
                f"[Applications] Error: {error}"
            )

            return web.json_response({
                "success": False,
                "error": str(error)
            }, status=500)

    async def create_application(self, data):

        channel = self.bot.get_channel(
            self.channel_id
        )

        if channel is None:
            print(
                "[Applications] Forum channel not found."
            )
            return

        # Make sure this is actually a Forum Channel
        if channel.type != discord.ChannelType.forum:
            print(
                "[Applications] ERROR: "
                "The channel is not a Forum Channel."
            )
            return

        # ==========================================
        # GET APPLICANT NAME
        # ==========================================

        applicant_name = (
            data.get("Please state your discord username.")
            or "Unknown Applicant"
        )

        applicant_name = str(
            applicant_name
        ).strip()

        # ==========================================
        # CREATE EMBED
        # ==========================================

        fields = []

        for question, answer in data.items():

            if answer is None:
                continue

            answer = str(answer).strip()

            if not answer:
                continue

            question = str(question).strip()

            if not question:
                continue

            # Discord limits
            question = question[:256]
            answer = answer[:1024]

            fields.append(
                (question, answer)
            )

        # ==========================================
        # CREATE FORUM POST
        # ==========================================

        first_fields = fields[:25]

        embed = discord.Embed(
            title=" New application bitches get reviewing",
            description=(
                f"**Applicant:** {applicant_name}"
            
            ),
            color=discord.Color(int("2F6B67", 16))
        )

        for question, answer in first_fields:

            embed.add_field(
                name=question,
                value=answer,
                inline=False
            )

        embed.set_footer(
            text=f"Application • {applicant_name}"
        )

        # This creates a NEW POST/THREAD
        thread, message = await channel.create_thread(
            name=f"{applicant_name}'s' Application",
            embed=embed
        )

        print(
            f"[Applications] Created forum post: "
            f"{thread.name}"
        )

        # ==========================================
        # SEND REMAINING QUESTIONS
        # ==========================================

        remaining = fields[25:]

        if remaining:

            for start in range(
                0,
                len(remaining),
                25
            ):

                group = remaining[
                    start:start + 25
                ]

                extra_embed = discord.Embed(
                    title="📋 Application — Continued",
                    color=discord.Color.blue()
                )

                for question, answer in group:

                    extra_embed.add_field(
                        name=question,
                        value=answer,
                        inline=False
                    )

                await thread.send(
                    embed=extra_embed
                )

        # ==========================================
        # FINAL MESSAGE
        # ==========================================

        await thread.send(
            content="**<@&1552513921141968950> <@&1552513921129254997> GET BACK TO WORK - REVIEW MY APP**\n\n"
            "Use /pass-applicant and /deny-applicant!!! Their there for a reason!"
          
        )


async def setup(bot):
    await bot.add_cog(
        Applications(bot)
    )
