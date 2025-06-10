
from discord.ext import commands, tasks
from discord import app_commands, Interaction, ButtonStyle, Embed
from discord.ui import View, Button
import discord
import random

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

ITEMS_TO_MONITOR = {
    "universe box": {
        "min_price": 500_000_000,
        "desc": "Contains rare and exclusive items. Can be sold for high profit.",
        "how": "Obtained from giveaways or extremely rare pulls."
    },
    "credit card": {
        "min_price": 70_000_000,
        "desc": "Reduces cooldowns and boosts passive earnings.",
        "how": "Craftable with rare items or sometimes found in events."
    },
    "reversal card": {
        "min_price": 50_000_000,
        "desc": "Used to reverse rob attempts in Dank Memer.",
        "how": "Usually crafted or bought via market during events."
    },
    "meme box": {
        "min_price": 1_000_000,
        "desc": "Gives memes used in /postmemes for XP and coins.",
        "how": "Buy from shop or market."
    },
    "black hole": {
        "min_price": 1_500_000,
        "desc": "Used to remove items from the universe (for chaos or fun).",
        "how": "Market only or rare pulls from boxes."
    }
}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(e)

    if not monitor_market.is_running():
        monitor_market.start()

@bot.tree.command(name="danktip", description="Get helpful tips for money, xp, grinding, etc.")
@app_commands.describe(topic="Select a topic")
@app_commands.choices(topic=[
    app_commands.Choice(name="Money", value="money"),
    app_commands.Choice(name="XP", value="xp"),
    app_commands.Choice(name="Grinding", value="grind")
])
async def danktip(interaction: Interaction, topic: app_commands.Choice[str]):
    tips = {
        "money": "Use /beg, /dig, /hunt, /fish, and flip items. Stack buffs and bank wisely.",
        "xp": "Fish with bosses, /postmemes, do dailies/monthlies, and equip good pets.",
        "grind": "Grind events, flip crates/cards, and chain commands while watching cooldowns."
    }
    await interaction.response.send_message(tips[topic.value], ephemeral=True)

@bot.tree.command(name="calc_money_time", description="Estimate time to earn target money")
@app_commands.describe(target_money="How many coins you want to earn", coins_per_minute="Your average income per minute")
async def calc_money_time(interaction: Interaction, target_money: int, coins_per_minute: int):
    minutes = target_money / coins_per_minute
    await interaction.response.send_message(f"🕒 You'll need about **{round(minutes, 2)} minutes** to earn {target_money:,} coins.", ephemeral=True)

@bot.tree.command(name="calc_xp_goal", description="Estimate time to reach your XP goal")
@app_commands.describe(target_xp="Total XP goal", xp_per_hour="Your XP per hour")
async def calc_xp_goal(interaction: Interaction, target_xp: int, xp_per_hour: int):
    hours = target_xp / xp_per_hour
    await interaction.response.send_message(f"📘 You'll need about **{round(hours, 2)} hours** to gain {target_xp:,} XP.", ephemeral=True)

@bot.tree.command(name="calc_buy_efficiency", description="See how many items you can buy for your coins")
@app_commands.describe(item_price="Item price", total_money="How much money you have")
async def calc_buy_efficiency(interaction: Interaction, item_price: int, total_money: int):
    quantity = total_money // item_price
    await interaction.response.send_message(f"💰 You can buy **{int(quantity)} items** for {total_money:,} coins.", ephemeral=True)

async def send_market_alert(channel: discord.TextChannel, item: str, price: int, listing_id: str):
    embed = Embed(title=f"🔍 {item.title()} Found!", description=f"Price: `{price:,}` coins", color=0xffa500)
    embed.set_footer(text=f"Listing ID: {listing_id}")

    class AlertView(View):
        def __init__(self):
            super().__init__(timeout=None)
            self.command = f"/market view item_filter:{item}"
            info = ITEMS_TO_MONITOR[item]
            self.info = f"🪙 **Item:** {item.title()}\n💰 **Price:** {price:,}\n🧠 **What it does:** {info['desc']}\n🛠 **How to get:** {info['how']}"

        @discord.ui.button(label="Copy Command", style=ButtonStyle.green)
        async def copy_button(self, interaction: Interaction, button: Button):
            await interaction.response.send_message(f"```{self.command}```", ephemeral=True)

        @discord.ui.button(label="Info", style=ButtonStyle.blurple)
        async def info_button(self, interaction: Interaction, button: Button):
            await interaction.response.send_message(f"```{self.info}```", ephemeral=True)

    await channel.send(embed=embed, view=AlertView())

@tasks.loop(seconds=60)
async def monitor_market():
    guild = discord.utils.get(bot.guilds)
    channel = discord.utils.get(guild.text_channels, name="dank-monitor")
    if not channel:
        return
    item = random.choice(list(ITEMS_TO_MONITOR.keys()))
    price = random.randint(ITEMS_TO_MONITOR[item]["min_price"] - 200_000, ITEMS_TO_MONITOR[item]["min_price"])
    listing_id = f"{random.randint(100000,999999)}"
    await send_market_alert(channel, item, price, listing_id)

monitor_market.start()

bot.run("MTM4MjAyOTI1MDA4MDUzODY1NA.GUVpgg.6ZpiAOhSomh2FWw65QBglo0OKvG_hLDIBWBBj0")
