import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from typing import List

# Load token from .env file
load_dotenv()
bot_token = str(os.getenv("DISCORD_TOKEN"))

# Set up bot with all intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)

# Initialize categories
web_resource_categories = ["Academics", "Language learning", "Programming", 
                          "References", "Game dev", "Business", "General"]

# Autocomplete functions
async def category_autocomplete(
    interaction: discord.Interaction,
    current: str
) -> List[app_commands.Choice[str]]:
    """Dynamic autocomplete for categories"""
    return [
        app_commands.Choice(name=category, value=category)
        for category in web_resource_categories
        if current.lower() in category.lower()
    ]

# Bot events
@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord")
    try:
        await bot.tree.sync()
        print("Slash commands synced!")
    except Exception as e:
        print(f"Error syncing commands: {e}")

# Commands
@bot.tree.command(name="chass_status")
async def chass_status(interaction: discord.Interaction):
    """Check bot status"""
    await interaction.response.send_message("Chass Koini!")

@bot.tree.command(name="add_web_resource_category", description="Add new category")
@app_commands.describe(category_name="Name of new category")
async def add_web_resource_category(
    interaction: discord.Interaction,
    category_name: str,
):
    """Add a new resource category"""
    if category_name in web_resource_categories:
        await interaction.response.send_message("Category already exists!", ephemeral=True)
        return
        
    web_resource_categories.append(category_name)
    await interaction.response.send_message("Category added", ephemeral=True)

@bot.tree.command(name="remove_web_resource_category", description="Remove a category")
@app_commands.describe(category_name="Name of category to remove")
@app_commands.autocomplete(category_name=category_autocomplete)
async def remove_web_resource_category(
    interaction: discord.Interaction,
    category_name: str,
):
    """Remove a resource category"""
    if category_name not in web_resource_categories:
        await interaction.response.send_message("Category not found", ephemeral=True)
        return
        
    web_resource_categories.remove(category_name)
    await interaction.response.send_message("Category removed", ephemeral=True)

@bot.tree.command(name="web_resource", description="Add a web resource")
@app_commands.describe(
    name="Resource name",
    category="Category",
    tags="Comma-separated tags (e.g. python, discord, bot)",
    source_links="Comma-separated links",
    description="Resource description",
)
@app_commands.autocomplete(category=category_autocomplete)
async def web_resource(
    interaction: discord.Interaction,
    name: str,
    category: str, 
    tags: str, 
    source_links: str,
    description: str = "None",
):
    """Add a new web resource"""
    # Server-side validation
    if category not in web_resource_categories:
        await interaction.response.send_message("Invalid category!", ephemeral=True)
        return

    if interaction.guild is None:
        await interaction.response.send_message("Command not valid in DMs", ephemeral=True)
        return

    # Format response
    formatted_tags = "  ".join(f"`{tag.strip()}`" for tag in tags.split(",") if tag.strip())
    formatted_links = "  ".join(f"<{link.strip()}>" for link in source_links.split(","))

    bot_response = (
        f"**Name:** {name}\n"
        f"**Category:** {category}, **Tags:** {formatted_tags}\n"
        f"**Sources:** {formatted_links}\n"
        f"**Description:** {description}\n"
        f"**Author:** {interaction.user.mention}"
    )

    # Channel management
    resource_channel_name = "useful-web-resources"
    resource_channel = discord.utils.get(interaction.guild.text_channels, name=resource_channel_name)

    if not resource_channel:
        resource_channel = await interaction.guild.create_text_channel(resource_channel_name)

    # Thread management
    thread = discord.utils.get(resource_channel.threads, name=category)
    
    if not thread:
        message = await resource_channel.send(content=category)
        thread = await message.create_thread(name=category)

    await thread.send(content=bot_response)
    await interaction.response.send_message("Resource added", ephemeral=True)

bot.run(token=bot_token)
