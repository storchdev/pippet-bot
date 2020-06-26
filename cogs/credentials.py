import asyncio
import os
import random
import discord
from discord.ext import commands
from captcha.image import ImageCaptcha
from functions import pg


class Credentials(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='start')
    async def start_command(self, ctx):
        no = self.bot.gifs['no']

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        await ctx.send('Are you sure you want to create a new account?')

        try:
            message = await self.bot.wait_for('message', timeout=15, check=check)
        except asyncio.TimeoutError:
            await ctx.send(f'{no} I timeouted because you took too long to confirm.')
            return

        content = message.content.lower()

        if content not in ['yes', 'y']:
            await ctx.send("That wasn't a yes; I have canceled the creation.")
            return

        try:
            await ctx.author.send('Please enter a username here. It must be between **2** and **32** characters.')
        except discord.Forbidden:
            await ctx.send(f"{no} Your DMs are blocked off from non-friends; please enable them from **everyone**.")
            return

        await ctx.send('Head to my DMs. You will be asked to enter credentials for your new account.')

        def check(m):
            return m.channel == ctx.author.dm_channel and m.author == ctx.author

        try:
            message = await self.bot.wait_for('message', timeout=60, check=check)
        except asyncio.TimeoutError:
            await ctx.author.send(f'{no} You took too long to enter a username; please try again in a server.')
            return

        if not 1 < len(message.content) < 33:
            await ctx.author.send(f'{no} That username is not between 2 and 32 characters; '
                                  f'please run the command again.')
            return

        username = message.content

        query = 'SELECT id FROM credentials WHERE username = $1'
        duplicates = await pg.fetchrow(query, (username,))

        if duplicates is not None:
            await ctx.author.send(f'{no} The username `{username}` is already taken. '
                                  f'Please run the command again and use a different one.')
            return

        await ctx.author.send('Enter a password for your account. It must be between 4 and 16 characters.')

        try:
            message = await self.bot.wait_for('message', timeout=60, check=check)
        except asyncio.TimeoutError:
            await ctx.author.send(f'{no} You took too long to enter a password; please try again in a server.')
            return

        if not 3 < len(message.content) < 17:
            await ctx.author.send(f'{no} That password is not between 4 and 16 characters; '
                                  f'please run the command again.')
            return

        password = message.content

        captcha, letters = '', ' '.join('123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ').split()

        for i in range(5):
            captcha += random.choice(letters)

        image = ImageCaptcha()
        image.write(captcha, f'./{ctx.author.id}.png')
        file = discord.File(f'./{ctx.author.id}.png')

        await ctx.author.send('You have 30 seconds to complete the CAPTCHA below to prove that you are human. '
                              'Case does not matter.', file=file)

        os.remove(f'./{ctx.author.id}.png')

        try:
            message = await self.bot.wait_for('message', timeout=30, check=check)
        except asyncio.TimeoutError:
            await ctx.author.send(f'{no} You took longer than 30 seconds to respond to the Captcha. Account canceled.')
            return

        if message.content.lower() != captcha.lower():
            await ctx.author.send(f'{no} You failed the Captcha; account creation denied.')
            return

        query = 'INSERT INTO credentials (username, password, in_game) VALUES ($1, $2, $3)'
        await pg.execute(query, (username, password, False))
        query = 'INSERT INTO players (username, location, stars, hearts, currency, backpack, pets, equipped, ' \
                'is_new) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)'
        await pg.execute(query, (username, 'A', 0, 530, '{}', '{}', '{}', '{}', True))
        yes = self.bot.gifs['yes']
        await ctx.author.send(f'{yes} Success! Your account `{username}` was created. '
                              f'Do `{ctx.prefix}login` to login again.')

    @commands.command(name='login')
    async def login_command(self, ctx):
        query = 'SELECT id FROM credentials WHERE user_id = $1'
        author_row = await pg.fetchrow(query, (ctx.author.id,))

        if author_row is not None:
            await ctx.send('You are already logged into an account. Please log out of it, then log in again.')
            return

        try:
            await ctx.author.send('Enter username:')
        except discord.Forbidden:
            await ctx.send('Your DMs are blocked off from non-friends; please enable them from **everyone**.')
            return

        await ctx.send('Head to my DMs. You will be asked to login there.')

        def check(m):
            return m.channel == ctx.author.dm_channel and m.author == ctx.author

        try:
            username = await self.bot.wait_for('message', timeout=30, check=check)
        except asyncio.TimeoutError:
            await ctx.author.send('You took more than 30 seconds to enter your username; please try the login again.')
            return

        await ctx.author.send('Enter your password:')

        try:
            password = await self.bot.wait_for('message', timeout=30, check=check)
        except asyncio.TimeoutError:
            await ctx.author.send('You took more than 30 seconds to enter your password; please try the login again.')
            return

        query = 'SELECT id FROM credentials WHERE username = $1 AND password = $2'
        correct_row = await pg.fetchrow(query, (username.content, password.content))

        if correct_row is None:
            await ctx.author.send('Invalid username or password; try the command again.')
            return

        query = 'SELECT id FROM credentials WHERE username = $1 AND in_game = $2'
        check = await pg.fetchrow(query, (username.content, True))

        if check is not None:
            await ctx.author.send(f'Oops! Another user is currently using the account `{username.content}`.',
                                  delete_after=10)
            return

        query = 'UPDATE credentials SET in_game = $1, user_id = $2 WHERE username = $3'
        await pg.execute(query, (True, ctx.author.id, username.content))

        await ctx.author.send(f'You are now logged in! Do `{ctx.prefix}logout` to logout.', delete_after=10)

    @commands.command(name='logout')
    async def logout_command(self, ctx):
        query = 'UPDATE credentials SET in_game = $1, user_id = $2 WHERE user_id = $3'
        await pg.execute(query, (False, None, ctx.author.id))
        await ctx.send('I have logged you out of your account.')


def setup(bot):
    bot.add_cog(Credentials(bot))
