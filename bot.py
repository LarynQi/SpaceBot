import discord
import random
import os
from discord.ext import commands, tasks
from itertools import cycle
import json
import time
import datetime
import pytz
import pymongo
import dns
from pymongo import MongoClient
from utils import *

def get_prefix(client, message):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    return prefixes[str(message.guild.id)][0]

# client = commands.Bot(command_prefix = '.')
client = commands.Bot(command_prefix = get_prefix)
client.remove_command('help')
status = cycle(['Status 1', 'Status 2'])
cluster = MongoClient(os.environ.get('MDB_CONNEC'))
db = cluster['SpaceBot']
# db.add_son_manipulator(Transform())
# collection = db['Stats']
collection = db.get_collection('Stats', codec_options=codec_options)
# collection.insert_one({'_id': 0, 'name': 'Laryn', 'score': 6})

joined = messages = count = 0
first = True
users = {}
# @client.event
# async def on_ready():
#     print('Bot is ready!')

@client.event
async def on_member_join(member):
    print(f'{member} has joined a server.')

@client.event
async def on_member_remove(member):
    print(f'{member} has left a server.')

# @client.command()
# async def ping(ctx):
#     await ctx.send(f'Pong! {round(client.latency * 1000)}ms')

@client.command(aliases=['8ball','eightball'])
async def _8ball(ctx, *, question):
    responses = ["It is certain.",
                "It is decidedly so.",
                "Without a doubt.",
                "Yes - definitely.",
                "You may rely on it.",
                "As I see it, yes.",
                "Most likely.",
                "Outlook good.",
                "Yes.",
                "Signs point to yes.",
                "Reply hazy, try again.",
                "Ask again later.",
                "Better not tell you now.",
                "Cannot predict now.",
                "Concentrate and ask again.",
                "Don't count on it.",
                "My reply is no.",
                "My sources say no.",
                "Outlook not so good.",
                "Very doubtful."]
    await ctx.send(f'Question: {question} \nAnswer: {random.choice(responses)}')

@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount):
    await ctx.channel.purge(limit=amount)

@client.command()
@commands.check(special_check)
async def kick(ctx, member : discord.Member, *, reason=None):
    print('here')
    await member.kick(reason=reason)
    await ctx.send(f'Kicked {member.mention}')


@client.command()
@commands.check(special_check)
async def ban(ctx, member : discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'Banned {member.mention}')

@client.command()
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    name, discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user
        if (user.name, user.discriminator) == (name, discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {user.mention}')
            return

@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')

@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')

@client.command(aliases=['reload'])
async def _reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

@client.command(aliases=['exit', 'quit'])
@commands.check(special_check)
async def _quit(ctx):
    await client.change_presence(status=discord.Status.offline)
    await client.logout()

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.dnd, activity=discord.Game('League of Legends'))
    change_status.start()
    clear_coll(collection)
    # update_stats_JSON.start()
    update_DB.start()
    print('SpaceBot on standby.')

@tasks.loop(seconds=5)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Command not found.')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('You do not have permission to use this command.')
    else:
        print(error)

@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specifiy an amount of messages to delete.')


@client.command()
@commands.check(special_check)
async def special(ctx):
    await ctx.send(f'Hi im {ctx.author}')

@client.event
async def on_guild_join(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    
    prefixes[str(guild.id)] = ['.', guild.name]

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

@client.event
async def on_guild_remove(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    
    prefixes.pop(str(guild.id))

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

@client.command()
async def prefix(ctx, pre):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    
    prefixes[str(ctx.guild.id)][0] = pre

    with open('prefixes.json', 'w') as f:    
        json.dump(prefixes, f, indent=4)
    
    await ctx.send(f'Prefix changed to: {pre}')

@client.command()
async def help(ctx):
    author = ctx.message.author
    embed = discord.Embed(
        color = discord.Color.orange()
    )
    embed.set_author(name='Command List')
    embed.add_field(name='/ping', value='Display your latency', inline=False)
    embed.add_field(name='/max', value='Display @user\'s most commonly used word', inline=False)
    embed.add_field(name='/8ball', value='Ask the 8ball a question!', inline=False)


    await author.send(embed=embed)

@tasks.loop(seconds=10)
async def update_stats_JSON():
    global first
    if first:
        first = False
        return
    # curr_time, secs = time.gmtime(), time.time()
    curr_time, secs = datetime.datetime.now(), time.time()
    pacific = pytz.timezone('US/Pacific')
    loc_dt = pacific.localize(curr_time)

    # https://stackoverflow.com/questions/1398674/display-the-time-in-a-different-time-zone
    fmt = '%Y-%m-%d %H:%M:%S %Z%z'

    global joined, messages

    try:
        with open('stats.json', 'r') as f:
            stats = json.load(f)
        add = {}
        # add['Time'] = time.strftime('%Y-%m-%d %H:%M:%S %Z%z', curr_time)
        add['Time'] = loc_dt.strftime(fmt)
        add['Members Joined'] = joined
        add['Messages Sent'] = messages
        joined = 0
        messages = 0

        stats[secs] = add

        with open('stats.json', 'w') as f:
            json.dump(stats, f, indent=4)

    except Exception as e:
        print(e)

@tasks.loop(seconds=10)
async def update_DB():
    global first
    if first:
        first = False
        return
    global users
    global count
    count += 1
    # print(users)
    # print('here')
    ids = []
    if collection.count_documents({}) > 0:
        data = collection.find({})
        # for result in data:
        #     print(result)
        ids = [result['_id'] for result in data]
        # print(ids)
        # print(data)
        # print(ids)
        # print(users)
        # print(users[0].id)
    for user in users:
        # print(user)
        u = users[user]
        # print(u)
        # print(u.id)
        if u.id in ids:
            collection.update_one({'_id': u.id}, {'$set': {'user': u}})
        else:
            post = {"_id": u.id, 'user': u}
            collection.insert_one(post)
    print('Update #' + str(count))
        # print(users)


@client.event
async def on_member_join(member):
    global joined
    joined += 1

@client.event
async def on_message(message):
    global messages
    # print(message.author.id)
    # print(int(os.environ.get('BOT_ID')))

    # ignore bot messages 
    # print(message.content)
    # if message.author.id != int(os.environ.get('BOT_ID')):
        # messages += 1

    global users
    # ignore all bot messages
    if not message.author.bot:
        if message.author.id not in users:
            users[message.author.id] = User(message.author.name, message.author.id)
        user = users[message.author.id]
        # user = users.get(message.author.id, User(message.author.id)) 
        if message.content in user.mappings:
            i = user.mappings[message.content]
            user.occurrences[i] += 1
        else:
            user.mappings[message.content] = len(user.words)
            user.words.append(message.content)
            user.occurrences.append(1)
        # print(message.content)
        # print(user)
    # https://stackoverflow.com/questions/49331096/why-does-on-message-stop-commands-from-working
    await client.process_commands(message)

@client.command()
async def max(ctx, member : discord.Member):
    # user = ctx.message.author.id
    name, discriminator = member.name, member.id
    data = collection.find_one({'_id': discriminator})

    # await ctx.send(f'{ctx.message.author.name} has said \'{data["user"].getMax()}\'\n {data["user"].getMaxOccur()} times.')
    await ctx.send(f'{name} has said \"{data["user"].getMax()}\"\n{data["user"].getMaxOccur()} times.')

client.run(os.environ.get('BOT_KEY'))
