import discord
from discord.ext import commands
from functions import pg
from functions import prodigy


def restricted(ctx):
    return ctx.author.id in [576187414033334282, 571881373523247105, 470595952210739200]


async def get_prefix(x, message):

    if message.guild:
        query = 'SELECT prefix FROM prefixes WHERE guild_id = $1'
        prefix = await pg.fetchrow(query, (message.guild.id,))

        if prefix is not None:
            prefix = prefix['prefix']
            prefixes = [prefix.lower(), prefix.upper(), prefix.capitalize()]
            return prefixes
        else:
            return ['pmp ', 'PMP ', 'Pmp ']
    else:
        return ''


bot = commands.Bot(command_prefix=get_prefix)
exts = ['cogs.credentials', 'cogs.config']


@bot.event
async def on_ready():
    bot.gifs = {'yes': bot.get_emoji(724691251135381614), 'no': bot.get_emoji(724691249046487050)}
    game = discord.Game('pmp help')
    await bot.change_presence(status=discord.Status.do_not_disturb, activity=game)
    print('Ready')


@bot.command(hidden=True)
@commands.check(restricted)
async def reboot(ctx):

    for a in exts:
        bot.unload_extension(a)
        bot.load_extension(a)

    await ctx.send('Done.')


@bot.command(hidden=True)
@commands.check(restricted)
async def database(ctx, *, query):

    try:
        await pg.execute(query)
    except Exception as error:
        await ctx.send(error)
        return

    await ctx.send('Done.')


@bot.command()
async def lvl(ctx, stars: int):
    await ctx.send(prodigy.get_level(stars))


@bot.command(name='stars')
async def stars_command(ctx, level: int):
    await ctx.send(prodigy.get_stars(level))

for extension in exts:
    bot.load_extension(extension)

with open('./logins/token.txt') as token:
    token = token.read()

bot.run(token)
