import json

import discord
from discord.ext import commands
from discord.ext.commands import Cog
from discord_slash import SlashCommand


def run_bot(*cogs: Cog, override_token=None):
    if override_token is not None:
        token = override_token
    else:
        with open("secret.json", "r") as f:
            sec = json.loads(f.read())
            token = sec['token']

    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix='?', description="", intents=intents)
    activity = discord.Activity(type=discord.ActivityType.watching, name="the server ⏳")
    slash = SlashCommand(bot, sync_commands=True)
    for cog in cogs:
        bot.add_cog(cog)

    bot.run(token)
