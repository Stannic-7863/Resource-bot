import os
import discord 
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# Load token from .env file
load_dotenv()
bot_token = str(os.getenv("DISCORD_TOKEN"))

# Set up bot with all intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord")
    try:
        await bot.tree.sync()
        print("Slash commands synced!")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@bot.tree.command(name="chass_status")
async def chass_status(interaction: discord.Interaction):
    await interaction.response.send_message("Chass Koini!")

web_resource_categories = ["Academics", "Language learning", "Programming", "References", "Game dev", "Business", "General"]

@bot.tree.command(name="add_web_resource_category", description="Add new category")
@app_commands.describe(
        category_name="Name of new category"
        )
async def add_web_resource_category(
        interaction: discord.Interaction,
        category_name: str,
        ):
    web_resource_categories.append(category_name)
    await interaction.response.send_message("Category added", ephemeral=True)

@bot.tree.command(name="remove_web_resource_category", description="Add new category")
@app_commands.describe(
        category_name="Name of category to remove"
        )
@app_commands.choices(category_name=[app_commands.Choice(name=category, value=category) for category in web_resource_categories])
async def remove_web_resource_category(
        interaction: discord.Interaction,
        category_name: str,
        ):
    web_resource_categories.pop(web_resource_categories.index(category_name))
    await interaction.response.send_message("Category removed", ephemeral=True)


@bot.tree.command(name="web_resource", description="Add a web resource")
@app_commands.describe(
    name="Resource name",
    category="Category",
    tags="Comma-separated tags (e.g. python, discord, bot)",
    source_links="Comma-separated links",
    description="Resource description",
)
@app_commands.choices(category=[app_commands.Choice(name=category, value=category) for category in web_resource_categories])
async def web_resource(
    interaction: discord.Interaction,
    name: str,
    category: str, 
    tags: str, 
    source_links: str,
    description: str = "None",
):
   
    if interaction.guild == None:
        await interaction.response.send_message("Command not valid in DM")
        return 

    formatted_tags = "  ".join(f"`{tag.strip()}`" for tag in tags.split(",") if tag.strip())  
    formatted_links = "  ".join(f"<{link.strip()}>" for link in source_links.split(","))

    bot_response = f"**Name:** {name}\n**Category:** {category}, **Tags:** {formatted_tags}\n**Sources:** {formatted_links}\n**Description:** {description}\n**Author:** {interaction.user.mention}"

    resource_channel_name = "useful-web-resources"
    resource_channel = discord.utils.get(interaction.guild.text_channels, name=resource_channel_name)

    if not resource_channel: 
        await interaction.guild.create_text_channel(resource_channel_name)
    
    if resource_channel:

        thread = discord.utils.get(resource_channel.threads, name=category)

        if not thread:
            message = await resource_channel.send(content=category)
            thread = await message.create_thread(name=category)

        await discord.Thread.send(thread, content=bot_response)

    await interaction.response.send_message("Resource added", ephemeral=True)

bot.run(token=bot_token)
