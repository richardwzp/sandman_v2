import json
from typing import Callable

import interactions
from interactions import Client


def run_bot(*cogs: Callable[[Client], None], override_token=None):
    if override_token is not None:
        token = override_token
    else:
        with open("secret.json", "r") as f:
            sec = json.loads(f.read())
            token = sec['token']

    bot = Client(token)

    # activity = discord.Activity(type=discord.ActivityType.watching, name="the server ⏳")

    @bot.event
    async def on_ready():
        print('Logged in as')
        print(bot.me.name)
        if override_token is not None:
            print("<-- overridden instance -->")
        print('-------------------')

    for extension in cogs:
        extension(bot)

    bot.start()
