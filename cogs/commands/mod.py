import discord
from discord.ext import commands
from typing import Union
from CatLampPY import isGuild, hasPermissions, CommandErrorMsg  # pylint: disable=import-error


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.cmds.append(self.purge)
        self.bot.cmds.append(self.kick)
        self.bot.cmds.append(self.ban)
        self.bot.cmds.append(self.unban)

    async def gf_user(self, user_id: int):
        user = self.bot.get_user(user_id)
        if not user:
            try:
                user = await self.bot.fetch_user(user_id)
            except discord.NotFound:
                raise CommandErrorMsg(f'No user with the ID {user_id} was found!')
        return user

    @commands.command(aliases=["bulkDelete"])
    @isGuild()
    @hasPermissions("manage_messages")
    async def purge(self, ctx, number_of_messages: int):
        """Purges a certain amount of messages up to 100. Only works in servers."""
        if number_of_messages <= 0:
            raise CommandErrorMsg("I need at least 1 message to purge!")
        elif number_of_messages > 100:
            raise CommandErrorMsg("I can't purge more than 100 messages at a time!")
        await ctx.message.delete()
        msgsDeleted = await ctx.channel.purge(limit=number_of_messages)
        msg = await ctx.send(f"Deleted {len(msgsDeleted)} messages.")
        try:
            await msg.delete(delay=5)
        except discord.NotFound:
            pass

    @commands.command(cooldown_after_parsing=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    @hasPermissions("kick_members")
    async def kick(self, ctx, member: discord.Member, reason: str = "No reason specified."):
        """Kick a user with an optional reason. Requires the Kick Members permission."""
        if member.id == self.bot.user.id:
            await ctx.send(":(")
            return
        elif member.id == ctx.guild.owner.id:
            raise CommandErrorMsg("I can't kick the server owner!")
        try:
            await ctx.guild.kick(member,
                                 reason=f"Kicked by {str(ctx.author)} ({ctx.author.id}) with reason: '{reason}'")
        except discord.Forbidden:
            raise CommandErrorMsg("I'm not high enough in the role hierarchy to kick that person!")
        await ctx.send(f"{member.mention} ({str(member)}) has been kicked from the server with reason: '{reason}'")
    
    @commands.command(cooldown_after_parsing=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    @hasPermissions("ban_members")
    async def ban(self, ctx, user: Union[discord.User, int], reason: str = "No reason specified.",
                  days_of_messages_to_delete: int = 0):
        """Ban a user (including someone not in the server) with an optional reason and days of messages to delete.
        Requires the Ban Members permission."""
        if isinstance(user, int):
            user = await self.gf_user(user)
        try:
            await ctx.guild.fetch_ban(user)
            # Since an exception wasn't raised, a ban for this user already exists.
            await ctx.send("That user is already banned!")
            return
        except discord.NotFound:
            if user.id == self.bot.user.id:
                await ctx.send(":(")
                return
            try:
                await ctx.guild.ban(user, reason=f"Banned by {str(ctx.author)} "
                                                 f"({ctx.author.id}) with reason: '{reason}'",
                                    delete_message_days=days_of_messages_to_delete)
            except discord.Forbidden:
                raise CommandErrorMsg("I'm not high enough in the role hierarchy to ban that person!")
            await ctx.send(f"{user.mention} ({str(user)}) has been banned from the server with reason: '{reason}'")
    
    @commands.command(cooldown_after_parsing=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    @hasPermissions("ban_members")
    async def unban(self, ctx, user: Union[discord.User, int]):
        """Unbans a user. Requires the Ban Members permission."""
        if isinstance(user, int):
            user = await self.gf_user(user)
        try:
            # This is to check if the user is actually banned.
            # If the user is not banned, fetch_ban will raise NotFound.
            await ctx.guild.fetch_ban(user)
            await ctx.guild.unban(
                user, reason=f'Unbanned by {ctx.author} ({ctx.author.id})'
            )

            await ctx.send(f'{user.mention} ({user}) has been unbanned from the server.')
        except discord.NotFound:
            raise CommandErrorMsg("That user is not banned!")


def setup(bot):
    bot.add_cog(Moderation(bot))
