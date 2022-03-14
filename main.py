from interactions import Client
from bot_runner import run_bot
from command_groups.prof_command import Prof_command
from command_groups.moderation import Moderation

if __name__ == '__main__':
    run_bot(Prof_command, Moderation)



