import json
from typing import Callable

import interactions
from interactions import Client, ClientPresence, StatusType, PresenceActivity, PresenceActivityType

from command_groups.starboard import StarBoard
from database.database import Database, SandmanPilot


def run_bot(*cogs: Callable, override_token=None):

    with open("secret.json", "r") as f:
        sec = json.loads(f.read())
        # set the token, read from secret.json if not provided
        if override_token is not None:
            token = override_token
        else:
            token = sec['token']
    with Database(sec['host'], 'devDatabase', sec['username'], sec['password']) as db:
        pilot = SandmanPilot(db)
        activity = PresenceActivity(name="the server ⏳",
                                    type=PresenceActivityType.WATCHING)
        presence = ClientPresence(activities=[activity], status=StatusType.DND)
        bot = Client(token, presence=presence)
        # activity = discord.Activity(type=discord.ActivityType.watching, name="the server ⏳")
        extensions = [extension(bot, pilot) for extension in cogs]

        @bot.event
        async def on_ready():
            print('Logged in as')
            print(bot.me.name)
            if override_token is not None:
                print("<-- overridden instance -->")
            print('-------------------')

            for extension in extensions:
                if hasattr(extension, "starting_work"):
                    await extension.starting_work()

        bot.start()
