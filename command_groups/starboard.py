import asyncio
from typing import Optional, List, Dict
import interactions
from interactions import Channel, Client, extension_command, Option, OptionType, CommandContext, Member, Guild
from command_groups.moderation import permission_wrapper
from database.database import SandmanPilot

from emoji import EMOJI_DATA


def is_emoji(s):
    return s in EMOJI_DATA


guild_id = [709089549460045945, 753022598392053770][0]


class StarboardManagement:
    """
    Represents a starboard for a specific server.
    """

    def __init__(self, db: SandmanPilot, server_id: str, channels: Dict[str, Channel]):
        """
        :param db: the database object
        :param server_id: the id of the server this starboard belongs to
        """
        self.db = db
        self.server_id = server_id
        self.msg_boards = {}

        for board_name, channel_id, emoji_id, emoji_count in self.db.get_starboard_from_server(self.server_id):
            if channel_id not in channels:
                raise ValueError(f"channel with id '{channel_id}' is not found")
            self.msg_boards['board_name'] = channels[channel_id], emoji_id if emoji_id != "NULL" else None, emoji_count

    async def on_emoji_reaction(self,
                                given_emoji_id: str,
                                count: int,
                                msg_content: str,
                                ):
        for board_name, (channel, emoji_id, emoji_count) in self.msg_boards.items():
            if (emoji_id is None or emoji_id == given_emoji_id) and count >= emoji_count:
                await channel.send(msg_content)

    def starboard_creation(self, board_name: str, channel_id: str, emoji_id=None):
        self.db.create_starboard(board_name, channel_id, self.server_id, emoji_id - emoji_id)


class StarBoard(interactions.Extension):
    def __init__(self, client: Client, db: SandmanPilot):
        self.client = client
        self.db = db
        self.channel_cache: Dict[str, Dict[str, Channel]] = {}

    async def starting_work(self):
        print(f"size of guilds: {self.client.guilds}")
        for guild in self.client.guilds:
            await self.generate_channel_cache(guild)

    async def generate_channel_cache(self, guild: Guild):
        self.channel_cache[str(guild.id)] = {}
        cache_location = self.channel_cache[str(guild.id)]
        channels = await guild.get_all_channels()

        for channel in channels:
            cache_location[str(channel.id)] = channel

    @extension_command(name="add_starboard", description="print out all the channels",
                       options=[Option(name="board_name", description="the name of the board",
                                       type=OptionType.STRING, required=True),
                                Option(name="channel", description="the channel this starboard will post to",
                                       type=OptionType.CHANNEL, required=True),
                                Option(name="emoji_count", description="How many emojis will be needed",
                                       type=OptionType.INTEGER, required=False),
                                Option(name="emoji_id", description="the emoji this starboard will use, the id of it",
                                       type=OptionType.STRING, required=False)],
                       scope=guild_id)
    async def add_starboard(self, ctx: CommandContext, board_name: str, channel: Channel, emoji_count, emoji_id=None):
        if channel.type.value != interactions.ChannelType.GUILD_TEXT:
            return await ctx.send("add_starboard expected a channel, but was given something else")
        if emoji_id is not None:
            guild = await ctx.get_guild()
            try:
                emo = await guild.get_emoji(int(emoji_id))
            except ValueError:
                emo = emoji_id
            if not is_emoji(emo) and (not isinstance(emo, interactions.Emoji) or emo.id is None):
                return await ctx.send(f"{emoji_id} is not default emoji, or a usable emoji on this server.")
        else:
            emo = None

        self.db.create_starboard(board_name, str(channel.id), str(ctx.guild_id), emoji_count, emoji_id)
        # if emo is an emoji, use discord format. if it is None, use universal. else its default, just print it
        emo_str = f'<:{emo.name}:{emo.id}>' if isinstance(emo, interactions.Emoji) else \
            ("<UNIVERSAL>" if emo is None else emo)
        await ctx.send(f"created board with name'{board_name}'. Connected to channel {channel.mention}"
                       " emoji: " + emo_str)
