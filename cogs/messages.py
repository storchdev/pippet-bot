import json
import discord
from discord.ext import commands
from datetime import datetime
from functions import pg


async def insert_message(message):
    if not message.guild:
        return

    embed = json.dumps(message.embeds[0].to_dict()) if message.embeds else '{}'
    query = 'INSERT INTO messages (content, message_id, author_id, channel_id, guild_id, timestamp, is_bot, ' \
            'embed, is_deleted, is_edited) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)'
    await pg.execute(query, (message.content, message.id, message.author.id, message.channel.id, message.guild.id,
                             datetime.timestamp(message.created_at), message.author.bot, embed, False, False))


class Messages(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        await insert_message(message)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        query = 'UPDATE messages SET is_deleted = $1 WHERE message_id = $2'
        await pg.execute(query, (True, payload.message_id))

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, payload):
        query = 'UPDATE messages SET is_deleted = $1 WHERE message_id = $2'

        for message_id in payload.message_ids:
            await pg.execute(query, (True, message_id))

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        if message.author.bot:
            return

        query = 'UPDATE messages SET is_edited = $1 WHERE message_id = $2'
        await pg.execute(query, (True, payload.message_id))
        await insert_message(message)

    @commands.command(name='snipe')
    async def snipe_command(self, ctx, amount: int = 1, channel: discord.TextChannel = None):
        amount = abs(amount) - 1
        channel = ctx.channel if channel is None else channel

        query = 'SELECT * FROM messages WHERE channel_id = $1 AND is_deleted = $2 AND content != $3 ' \
                'ORDER BY timestamp DESC'
        deleted = await pg.fetch(query, (channel.id, True, ''))

        if not deleted:
            await ctx.send(f'No messages have been deleted in {channel.mention} since 6/30.')
            return

        try:
            message = deleted[amount]
        except IndexError:
            await ctx.send(f'You can only snipe back to `{len(deleted)}` messages in {channel.mention}.')
            return

        content, author_id, time = message['content'], message['author_id'], \
        datetime.fromtimestamp(message['timestamp'])

        member = ctx.guild.get_member(author_id)

        if member is None:
            embed = discord.Embed(description=content, timestamp=time)
            embed.set_author(name=str(author_id))
        else:
            fmt = 'gif' if member.is_avatar_animated() else 'png'
            embed = discord.Embed(color=member.color, description=content, timestamp=time)
            embed.set_author(name=str(member), icon_url=member.avatar_url_as(format=fmt))

        await ctx.send(embed=embed)

    @commands.command(name='editsnipe')
    async def editsnipe_command(self, ctx, amount: int = 1, channel: discord.TextChannel = None):
        amount = abs(amount) - 1
        channel = ctx.channel if channel is None else channel

        query = 'SELECT * FROM messages WHERE channel_id = $1 AND is_edited = $2 AND content != $3 ' \
                'ORDER BY timestamp DESC'
        deleted = await pg.fetch(query, (channel.id, True, ''))

        if not deleted:
            await ctx.send(f'No messages have been edited in {channel.mention} since 6/30.')
            return

        try:
            message = deleted[amount]
        except IndexError:
            await ctx.send(f'You can only snipe back to `{len(deleted)}` edited messages in {channel.mention}.')
            return

        content, author_id, time = message['content'], message['author_id'], \
        datetime.fromtimestamp(message['timestamp'])
        channel_id, guild_id, message_id = message['channel_id'], message['guild_id'], message['message_id']

        member = ctx.guild.get_member(author_id)
        jump_url = f'https://discordapp.com/channels/{guild_id}/{channel_id}/{message_id}'
        content = f'{content}\n\n[Jump to Message]({jump_url})'

        if member is None:
            embed = discord.Embed(description=content, timestamp=time)
            embed.set_author(name=str(author_id))
        else:
            fmt = 'gif' if member.is_avatar_animated() else 'png'
            embed = discord.Embed(color=member.color, description=content, timestamp=time)
            embed.set_author(name=str(member), icon_url=member.avatar_url_as(format=fmt))

        embed.set_footer(text='Message Sent At -->')
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Messages(bot))
