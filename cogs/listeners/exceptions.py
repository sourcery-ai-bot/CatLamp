import discord
from discord.ext import commands
# pylint: disable=import-error
from CatLampPY import colors
from cogs.misc.isAdmin import isAdmin


class Exceptions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @commands.Cog.listener() for a listener event

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        commandName = ctx.message.content.split(' ')[0]
        if not isinstance(error, commands.CommandNotFound):
            if ctx.command.hidden and not isAdmin(ctx):
                return
            # Exception-specific error handling, more may be added later.
            errorStr = None
            if isinstance(error, commands.BadArgument):
                if "int" in str(error) or "float" in str(error):
                    param = (str(error).split("parameter ", 1)[1][:-1]).replace("_", " ")
                    ctx.invoked_with = f"{param} must be a number."
                    await ctx.send_help(ctx.command)
                    return
            elif isinstance(error, commands.MissingRequiredArgument):
                ctx.invoked_with = "This command requires more arguments. See below for details."
                await ctx.send_help(ctx.command)
                return
            elif isinstance(error, commands.BadUnionArgument) and \
                    str(error).startswith('Could not convert "user" into User or int.'):
                errorStr = 'User not found!'
            embed = discord.Embed(title="Error",
                                  description=f"An error occurred while trying to run `{commandName}`!\n"
                                              f"```{errorStr or str(error)}```",
                                  color=colors["error"])
            embed.set_footer(
                text="If you think this shouldn't happen, contact a developer for help in the CatLamp server. (+server)"
            )

            await ctx.send(embed=embed)
            print(f"An error occurred while trying to run '{ctx.message.content}'!")
            if type(error) is not str:
                raise error

    async def errorEmbed(self, cmd, error):
        """[deprecated] Generates an error embed. Please use 'raise CommandErrorMsg("error message")' instead."""
        embed = discord.Embed(title="Error",
                              description=f"An error occurred while trying to run `{cmd}`!\n```{error}```",
                              color=colors["error"])
        user = await self.bot.fetch_user(142664159048368128)
        embed.set_footer(
            text=f"If think this shouldn't happen, go tell {user.name}#{user.discriminator} to not be a dumb dumb "
                 f"and fix it.")
        print(f"An error occurred while trying to run '{cmd}'!\n{error}")
        return embed


def setup(bot):
    bot.add_cog(Exceptions(bot))
