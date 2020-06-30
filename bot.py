import asyncio
import discord
from discord.ext import commands
from functions import pg
from functions import prodigy


def only_devs(ctx):
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
exts = ['cogs.credentials', 'cogs.config', 'cogs.game']


@bot.event
async def on_ready():
    bot.gifs = {'yes': bot.get_emoji(724691251135381614), 'no': bot.get_emoji(724691249046487050)}
    game = discord.Game('pmp help')
    await bot.change_presence(status=discord.Status.do_not_disturb, activity=game)
    print('Ready')


@bot.event
async def on_message(message):

    if message.author.id in [571881373523247105] and message.channel.id == 705106349922582529 and \
            message.content.lower() == '!work':
        await asyncio.sleep(60)
        channel = bot.get_channel(726442490130989127)
        await channel.send(f'{message.author.mention}, time to do `!work`. <#705106349922582529>')

    if message.author.id == 721146077700685834 and message.content[0].isdigit():
        lines = message.content
        spells = {}

        try:
            import json

            for line in lines.lower().replace('’', "'").splitlines():
                level, slot, spell = int(line.split()[0]), int(line.split()[1]), line.split(None, 2)[2]
                spells[spell] = [level, slot]

            await message.channel.send(f'```json\n{json.dumps(spells)}\n```')
        except ValueError:
            pass

    await bot.process_commands(message)


@bot.command(aliases=['code', 'src'])
async def github(ctx):
    await ctx.send('https://github.com/Stormtorch002/pippet-bot')


@bot.command(hidden=True)
@commands.check(only_devs)
async def reboot(ctx):

    for a in exts:
        bot.unload_extension(a)
        bot.load_extension(a)

    await ctx.send('Done.')


@bot.command(hidden=True)
@commands.check(only_devs)
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
