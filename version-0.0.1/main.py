import aiohttp
import nextcord
from nextcord.ext import commands
from nextcord.ui import View, button
import pytz
from datetime import datetime

intents = nextcord.Intents.all()
crydayx = commands.Bot(command_prefix='!', intents=intents)

WEBHOOK_URL = ''

class ConfirmationView(View):
    def __init__(self, interaction: nextcord.Interaction, recipient, message):
        super().__init__()
        self.interaction = interaction
        self.recipient = recipient
        self.message = message
    
    @button(label="Confirm", style=nextcord.ButtonStyle.green)
    async def confirm_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        server_name = interaction.guild.name if interaction.guild else 'Direct Message'
        bangkok_tz = pytz.timezone('Asia/Bangkok')
        bangkok_time = datetime.now(bangkok_tz)
        embed = nextcord.Embed(
            title="มีใครบางคนฝากข้อความถึงคุณ:",
            description=self.message,
            color=0xff4e4e
        )
        embed.set_footer(text=f"Server: {server_name} | เวลา: {bangkok_time.strftime('%Y-%m-%d %H:%M:%S')}")
        await self.recipient.send(embed=embed)
        await self.log_message(interaction.user, self.recipient, self.message)
        await interaction.response.send_message("ข้อความถูกส่งสําเร็จ!", ephemeral=True)
        self.stop()

    @button(label="Cancel", style=nextcord.ButtonStyle.red)
    async def cancel_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message("ข้อความถูกยกเลิกสําเร็จ!", ephemeral=True)
        self.stop()

    async def log_message(self, sender, recipient, message):
        embed = {
            "title": "Anonymous Message Sent",
            "fields": [
                {"name": "ผู้ส่ง", "value": sender.mention, "inline": True},
                {"name": "ผู้รับ", "value": recipient.mention, "inline": True},
                {"name": "Message", "value": message, "inline": False},
            ],
            "color": 0xff0004
        }
        async with aiohttp.ClientSession() as session:
            payload = {
                "embeds": [embed],
                "username": "ข้อความไม่ระบุนาม"
            }
            headers = {
                'Content-Type': 'application/json',
            }
            await session.post(WEBHOOK_URL, json=payload, headers=headers)

@crydayx.event
async def on_ready():
    print(f'LOGIN {crydayx.user}')
    await crydayx.change_presence(status=nextcord.Status.idle, activity=nextcord.Game("รับฝากข้อความ-ไม่ระบุตัวตน"))

@crydayx.slash_command(description="ส่งข้อความที่ไม่ระบุชื่อถึงใครบางคน?")
async def send_messages(interaction: nextcord.Interaction, recipient: nextcord.User, *, message: str):
    embed = nextcord.Embed(title="Confirm Message", description=f"คุณแน่ใจหรือไม่ว่าต้องการฝากข้อความต่อไปนี้ถึง: {recipient.mention}?", color=0xffffff)
    embed.set_image(url='https://getwemail.io/app/uploads/2020/10/gifs-in-email.gif')
    embed.add_field(name="Message:", value=message, inline=False)
    await interaction.response.send_message(embed=embed, view=ConfirmationView(interaction, recipient, message), ephemeral=True)

crydayx.run('')
