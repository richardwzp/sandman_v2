from typing import Optional

from interactions import Extension, Client, CommandContext, extension_command, Option, OptionType, User, Embed, \
    EmbedField, Member, EmbedImageStruct, EmbedAuthor
import interactions

# set to null when goes global
guild_id = [709089549460045945, 753022598392053770][0]


class Moderation(Extension):
    """Command group for moderation command.
       Supported commands:\n
       - warn (reason?)
       - mute (reason?) (duration?)
       - kick (reason?)
       - ban (reason?)
       - channel - lockdown
       - category - lockdown
       - channel - slowmode
       - channel - clear messages
       """

    def __init__(self, client):
        self.client: Client = client

    @staticmethod
    def create_reason_embed(command_name: str, user: Member, reason: Optional[str]):
        if not command_name:
            raise ValueError("given empty command name")

        return Embed(title=command_name[0].upper() + command_name[1:],
                     fields=[EmbedField(name="\u200b",
                                        value=user.mention + " " +
                                              (reason if reason is not None else "no reason given."),
                                        inline=False)],
                     thumbnail=EmbedImageStruct(url=user.user.avatar_url, height=10)._json,
                     color=0xFF0000,
                     #author=author
                     )

    @extension_command(name="warn", description="warn a user with reason",
                       options=[Option(name="user", description="bad user", type=OptionType.USER, required=True),
                                Option(name="reason", description="reason for warning",
                                       type=OptionType.STRING, required=False)],
                       scope=guild_id)
    async def warn(self, ctx: CommandContext, user: Member, reason=None):
        # author = EmbedAuthor(icon_url=ctx.author.user.avatar_url, name="Warning")
        embedded_warning = self.create_reason_embed("warning", user, reason)
        await ctx.send(embeds=[embedded_warning])

    @extension_command(name="kick", description="kick a user with reason",
                       options=[Option(name="user", description="bad user", type=OptionType.USER, required=True),
                                Option(name="reason", description="reason for kicking",
                                       type=OptionType.STRING, required=False)],
                       scope=guild_id)
    async def kick(self, ctx: CommandContext, user: Member, reason=None):
        # author = EmbedAuthor(icon_url=ctx.author.user.avatar_url, name="Warning")
        embedded_warning = self.create_reason_embed("kick", user, reason)
        await user.kick(ctx.guild_id, reason=reason if reason is not None else "no reason given.")
        await ctx.send(embeds=[embedded_warning])

    @extension_command(name="ban", description="ban a user with reason",
                       options=[Option(name="user", description="bad user", type=OptionType.USER, required=True),
                                Option(name="reason", description="reason for banning",
                                       type=OptionType.STRING, required=False),
                                Option(name="message_del_day",
                                       description="how many days of message from user should be delete",
                                       type=OptionType.INTEGER, required=False)],
                       scope=guild_id)
    async def ban(self, ctx: CommandContext, user: Member, reason=None, message_del_day=0):
        # author = EmbedAuthor(icon_url=ctx.author.user.avatar_url, name="Warning")
        embedded_warning = self.create_reason_embed("ban", user, reason)
        await user.ban(ctx.guild_id,
                       reason=reason if reason is not None else "no reason given.",
                       delete_message_days=message_del_day)
        await ctx.send(embeds=[embedded_warning])


