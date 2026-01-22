import discord
from discord.ext import commands
from discord.ui import Button, View

# ================== 기본 설정 ==================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

ADMIN_ROLE_NAME = "관리자"      # 관리자 역할 이름
LOG_CHANNEL_NAME = "ticket-log" # 로그 채널 이름

# ================== 봇 실행 ==================
@bot.event
async def on_ready():
    print(f"봇 실행됨: {bot.user}")

# ================== 티켓 명령어 ==================
@bot.command()
async def 티켓(ctx):
    create_button = Button(label="🎫 티켓 생성", style=discord.ButtonStyle.green)

    async def create_ticket(interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user

        # 🔒 중복 티켓 방지
        for ch in guild.text_channels:
            if ch.name == f"ticket-{user.name}":
                await interaction.response.send_message(
                    "❌ 이미 열려 있는 티켓이 있습니다.",
                    ephemeral=True
                )
                return

        admin_role = discord.utils.get(guild.roles, name=ADMIN_ROLE_NAME)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True),
            guild.me: discord.PermissionOverwrite(view_channel=True)
        }

        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(view_channel=True)

        # 📂 티켓 채널 생성
        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            overwrites=overwrites
        )

        # ================== 닫기 버튼 ==================
        close_button = Button(label="🔒 티켓 닫기", style=discord.ButtonStyle.red)

        async def close_ticket(inter: discord.Interaction):
            if not admin_role or admin_role not in inter.user.roles:
                await inter.response.send_message(
                    "❌ 관리자만 티켓을 닫을 수 있습니다.",
                    ephemeral=True
                )
                return

            # 📜 로그 저장
            log_channel = discord.utils.get(guild.text_channels, name=LOG_CHANNEL_NAME)
            if log_channel:
                logs = []
                async for msg in channel.history(limit=200):
                    time = msg.created_at.strftime("%Y-%m-%d %H:%M")
                    logs.append(f"[{time}] {msg.author}: {msg.content}")

                await log_channel.send(
                    f"🧾 **티켓 로그 | {channel.name}**\n```"
                    + "\n".join(reversed(logs)) +
                    "```"
                )

            await channel.delete()

        close_button.callback = close_ticket

        view = View()
        view.add_item(close_button)

        # 📢 자동 안내 메시지
        await channel.send(
            "안녕하세요 **플릭 계정상점**입니다 👋\n"
            "구매하실 **계정 종류 또는문의**을 남겨주세요.\n"
            "관리자가 곧 답변드립니다.",
            view=view
        )

        await interaction.response.send_message(
            "✅ 티켓이 생성되었습니다!",
            ephemeral=True
        )

    create_button.callback = create_ticket

    view = View()
    view.add_item(create_button)

    await ctx.send(
        "🎟 **아래 버튼을 눌러 티켓을 생성하세요.**",
        view=view
    )

# ================== 봇 실행 ==================
bot.run("BOT_TOKEN")
