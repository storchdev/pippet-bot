from discord.ext import commands
from functions import pg


class Config(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if isinstance(error, commands.CommandNotFound):
            return

        if ctx.command.name == 'prefix':
            await ctx.send('You are missing the following permissions: `Administrator`')

    @commands.command(name='prefix')
    @commands.has_permissions(administrator=True)
    async def prefix_command(self, ctx, new_prefix=None):

        if new_prefix is None:
            query = 'SELECT prefix FROM prefixes WHERE guild_id = $1'
            prefix = await pg.fetchrow(query, (ctx.guild.id,))
            prefix = 'pmp ' if prefix is None else prefix['prefix']

            await ctx.send(f'My prefix in **{ctx.guild.name}** is `{prefix}`. Run `{prefix}prefix <new prefix>` to '
                           f'change it.')
            return

        if len(new_prefix) > 32:
            await ctx.send('The length of the new prefix must be 32 characters or less.')
            return

        query = 'INSERT INTO prefixes (guild_id, prefix) VALUES ($1, $2) ON CONFLICT ON CONSTRAINT ' \
                'prefixes_guild_id_key DO UPDATE SET prefix = $2'
        await pg.execute(query, (ctx.guild.id, new_prefix))

        await ctx.send(f'The prefix for **{ctx.guild.name}** has been changed to `{new_prefix}`.')


def setup(bot):
    bot.add_cog(Config(bot))
