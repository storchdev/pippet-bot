import asyncio
import glob
import json
import os
import discord
from discord.ext import commands
from functions import pg, prodigy
from PIL import Image


class Game(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='launch')
    async def launch_command(self, ctx):
        try:
            yes, no = self.bot.gifs['yes'], self.bot.gifs['no']

            query = 'SELECT username FROM credentials WHERE user_id = $1'
            in_game = await pg.fetchrow(query, (ctx.author.id,))

            if in_game is None:
                await ctx.send(f'{no} You are not logged into an account.')
                return

            username = in_game['username']
            query = 'SELECT * FROM players WHERE username = $1'
            row = await pg.fetchrow(query, (in_game['username'],))

            if row['is_new']:
                loop = asyncio.get_event_loop()
                image = Image.open('./resources/areas/A B.png')

                buffer = await loop.run_in_executor(None, prodigy.noot, image, '4',
                                                    "Hi, and welcome to Pippet bot, the all original emulation of "
                                                    "Prodigy Math Game - in Discord!", 'Send a message in chat to '
                                                                                       'continue')
                await ctx.send(file=discord.File(fp=buffer, filename='welcome.png'))

                def check(m):
                    return m.channel == ctx.channel and m.author == ctx.author

                await self.bot.wait_for('message', check=check)

                text = 'Is your wizard a boy or a girl?'
                buffer = await loop.run_in_executor(None, prodigy.noot, image, '1', text)
                await ctx.send(file=discord.File(fp=buffer, filename='boyorgirl.png'))

                while True:
                    message = await self.bot.wait_for('message', check=check)
                    content = message.content.lower()

                    if content in ['boy', 'b', 'girl', 'g']:
                        break

                    text = "I couldn't make a boy or girl out of that. Say 'boy' or 'girl' in chat."
                    buffer = await loop.run_in_executor(None, prodigy.noot, image, '2', text)
                    await ctx.send(file=discord.File(fp=buffer, filename='boyorgirl.png'))

                gender = 'M' if content in ['boy', 'b'] else 'F'
                query = 'UPDATE players SET gender = $1 WHERE username = $2'
                await pg.execute(query, (gender, username))

                text = "The name's Noot. Who might you be?"
                buffer = prodigy.noot(image, '3', text, "Enter a name in chat under 32 characters.")
                await ctx.send(file=discord.File(fp=buffer, filename='name.png'))

                while True:
                    message = await self.bot.wait_for('message', check=check)
                    name = message.content

                    if 0 < len(name) < 33:
                        break

                    text = "That name isn't under 32 characters..."
                    buffer = await loop.run_in_executor(None, prodigy.noot, image, '2', text,
                                                        "Enter a name in chat under 32 characters.")
                    await ctx.send(file=discord.File(fp=buffer, filename='over32.png'))

                query = 'UPDATE players SET name = $1 WHERE username = $2'
                await pg.execute(query, (name, username))

                text = f'Nice to meet you, {name}.'
                buffer = await loop.run_in_executor(None, prodigy.noot, image, '4', text,
                                                    "Send a message in chat to continue.")
                await ctx.send(file=discord.File(fp=buffer, filename='name-completed.png'))
                await self.bot.wait_for('message', check=check)

                text = "Choose your starter pet! You don't have to battle it, since Stormtorch hasn't done that yet."
                buffer = await loop.run_in_executor(None, prodigy.noot, Image.open('./resources/areas/starters.png'),
                                                    '3', text, "Send either A, B, C, D, or E.")
                await ctx.send(file=discord.File(fp=buffer, filename='starter-pet.png'))

                while True:
                    message = await self.bot.wait_for('message', check=check)
                    content = message.content.lower()

                    if content in 'abcde':
                        break

                    text = 'Please try again; choose a pet by typing a letter from A to E.'
                    buffer = await loop.run_in_executor(None, prodigy.noot, image, '1',
                                                        text)
                    await ctx.send(file=discord.File(fp=buffer, filename='tryagain.png'))

                if content == 'a':
                    pet = 'Dragic'
                elif content == 'b':
                    pet = 'Peeko'
                elif content == 'c':
                    pet = 'Creela'
                else:
                    pet = 'Soral'

                query = 'SELECT pets FROM players WHERE username = $1'
                pets = await pg.fetchrow(query, (username,))
                pets = json.loads(pets['pets'])
                pets[pet] = 1
                pets = json.dumps(pets)
                query = 'UPDATE players SET pets = $1, is_new = $2 WHERE username = $3'
                await pg.execute(query, (pets, False, username))

                background = await loop.run_in_executor(None, prodigy.new_item, 'common',
                                                        './resources/areas/starters.png', pet)
                buffer = await loop.run_in_executor(None, prodigy.noot, background, '4', 'You got your first pet!',
                                                    f'Type "{ctx.prefix}travel B" in chat to continue to next area.')

                await ctx.send(file=discord.File(fp=buffer, filename='end.png'))
            else:
                location = row['location']
                f = None

                for file in os.listdir('./resources/areas'):
                    if file.startswith(f'{location} '):
                        f = f'./resources/areas/{file}'

                if f:
                    await ctx.send(file=discord.File(f))

        except Exception as error:
            await ctx.send(error)

    @commands.command()
    async def travel(self, ctx, location):
        try:
            yes, no = self.bot.gifs['yes'], self.bot.gifs['no']

            query = 'SELECT username FROM credentials WHERE user_id = $1'
            in_game = await pg.fetchrow(query, (ctx.author.id,))

            if in_game is None:
                await ctx.send(f'{no} You are not logged into an account.')
                return

            query = 'SELECT * FROM players WHERE username = $1'
            row = await pg.fetchrow(query, (in_game['username'],))

            if row['is_new']:
                await ctx.send(f'{no} You need to complete the tutorial first with `{ctx.prefix}launch`.')
                return

            f = None
            location_name = row['location']

            for file in glob.glob(f'./resources/areas/{location_name} *'):
                adjacent = file.replace('.png', '').split()[1:]

                if location.upper() in adjacent:
                    f = glob.glob(f'./resources/areas/{location.upper()} *.png')

                    if f:
                        f = f[0]
                        break

            query = 'UPDATE players SET location = $1 WHERE username = $2'
            await pg.execute(query, (location.upper(), row['username']))

            if f:
                await ctx.send(file=discord.File(f))
            else:
                await ctx.send('Uh oh... you cannot reach that location now!')

        except Exception as e:
            await ctx.send(e)


def setup(bot):
    bot.add_cog(Game(bot))
