import asyncio
import datetime
from discord.ext import commands, tasks

from cogs.commands.fun import sendData


class Name(commands.Cog):
    def __init__(self, bot):
        self.client = bot

        self.statReset.start()

    def cog_unload(self):
        if len(self.client.redditStats) > 1:
            print(f"Reddit data for {self.client.redditStats['Date']}")
            content = ''.join(
                f'\nr/{i}:\n{self.client.redditStats[i]}'
                for i in self.client.redditStats
                if i != 'Date'
            )

            print(content)

    @tasks.loop(hours=24)
    async def statReset(self):
        await sendData(self.client, self.client.get_channel(712489826330345534))
        self.client.redditStats = {'Date': datetime.date.today().isoformat()}  # reset stats

    @statReset.after_loop
    async def on_daily_cancel(self):
        if self.statReset.is_being_cancelled():
            print(f"Reddit data for {self.client.redditStats['Date']}")
            content = ''.join(
                f'\nr/{i}:\n{self.client.redditStats[i]}'
                for i in self.client.redditStats
                if i != 'Date'
            )

            print(content)

    @statReset.before_loop
    async def before_daily(self):
        await self.client.wait_until_ready()
        # sleep until 12 AM
        now = datetime.datetime.utcnow()
        remaining = ((now + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0) - now)
        await asyncio.sleep(remaining.total_seconds())


def setup(bot):
    bot.add_cog(Name(bot))
