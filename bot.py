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
import random
from gtts import gTTS
import asyncio
# from pynacl import *
# import PyNaCl
# from pynacl import *
def get_prefix(client, message):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    return prefixes[str(message.guild.id)][0]

# client = commands.Bot(command_prefix = '.')
client = commands.Bot(command_prefix = get_prefix)
client.remove_command('help')
# status = cycle(['Status 1', 'Status 2'])
games = []
my_games = []
cluster = MongoClient(os.environ.get('MDB_CONNEC'))
db = cluster['SpaceBot']
# db.add_son_manipulator(Transform())
# collection = db['Stats']
collection = db.get_collection('Stats', codec_options=codec_options)
# collection.insert_one({'_id': 0, 'name': 'Laryn', 'score': 6})

joined = messages = count = 0
first = True
monitoring = False
start_monitor = ''
users = {}
scores = dict()
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

@client.command(aliases=['8ball','eightball', '8b'])
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
    # await ctx.message.add_reaction('\U0001F3B1')
    msg = await ctx.send(f'**Q:** {question} \n**A:** {random.choice(responses)}', file=discord.File('./assets/8ball.png'))
    await msg.add_reaction('\U0001F3B1')


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
async def _quit(ctx, save='save'):
    if monitoring and save != 'ds':
        curr_time, secs = datetime.datetime.now(), time.time()
        pacific = pytz.timezone('US/Pacific')
        loc_dt = pacific.localize(curr_time)
        fmt = '%Y-%m-%d %H:%M:%S %Z%z'
        end = loc_dt.strftime(fmt)
        with open('monitor.json', 'r') as f:
            data = json.load(f)
        if not data:
            data[1] = {'from': start_monitor, 'end': end, 'updates': count}
        else:
            int_keys = [int(k) for k in data]
            data[max(int_keys) + 1] = {'from': start_monitor, 'end': end, 'updates': count}
        with open('monitor.json', 'w') as f:
            json.dump(data, f, indent=4)
    await client.change_presence(status=discord.Status.offline)
    await client.logout()

@client.event
async def on_ready():
    # await client.change_presence(status=discord.Status.dnd, activity=discord.Game('League of Legends'))
    # change_status.start()
    # clear_coll(collection)
    # # update_stats_JSON.start()

    ### cleaning
    # clear_dupes('games.json')

    read_data(collection)
    print(users)
    read_games()
    load_scores()
    update_DB.start()
    add_games.start()
    change_game.start()
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
    embed.add_field(name='/8b', value='Ask the 8ball a question!', inline=False)
    embed.add_field(name='/say', value='Tell SpaceBot something to say.', inline=False)
    embed.add_field(name='/flip', value='Flip a coin.', inline=False)
    embed.add_field(name='/roll', value='Roll up to 163 die.', inline=False)
    embed.add_field(name='/scoreboard', value='Display the die-rolling leaderboard.', inline=False)



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

# @tasks.loop(seconds=10)
@tasks.loop(minutes=10)
async def update_DB():
    global first
    global monitoring
    global start_monitor
    curr_time, secs = datetime.datetime.now(), time.time()
    pacific = pytz.timezone('US/Pacific')
    loc_dt = pacific.localize(curr_time)
    fmt = '%Y-%m-%d %H:%M:%S %Z%z'
    if first:
        first = False
        monitoring = True
        start_monitor = loc_dt.strftime(fmt)
        return
    # global users
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
            try:
                collection.insert_one(post)
            except Exception as e:
                print(e)


    print('Update #' + str(count) + ' at ' + loc_dt.strftime(fmt))
    # print(users)
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

    # global users
    # ignore all bot messages
    user = None
    if not message.author.bot:
        if message.author.id not in users:
            # print('here')
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

    if user and user.scrambled:
        if (time.time() - user.start) > user.dur:
            user.cipher = dict()
            user.start = 0
            user.dur = 0
        else:
            await message.channel.purge(limit=1)
            result = ''
            for c in message.content:
                if c in alphabet:
                    result += user.cipher[c]
                else:
                    result += c
            await message.channel.send(f'{message.author.name} says \"{result}\"')
            # discord disallows editting others' messages
            # await message.edit(content=result)

    # https://stackoverflow.com/questions/49331096/why-does-on-message-stop-commands-from-working
    await client.process_commands(message)

@client.command(aliases=['max'])
async def _max(ctx, member : discord.Member):
    # user = ctx.message.author.id
    name, discriminator = member.name, member.id
    data = collection.find_one({'_id': discriminator})

    # await ctx.send(f'{ctx.message.author.name} has said \'{data["user"].getMax()}\'\n {data["user"].getMaxOccur()} times.')
    await ctx.send(f'{name} has said \"{data["user"].getMax()}\"\n{data["user"].getMaxOccur()} times.')


alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

@client.command()
async def scramble(ctx, member : discord.Member, seconds=15):
    # member.mute(ctx)
    if seconds > 60:
        seconds = 60
    name, id = member.name, member.id
    scralphabet = dict()
    used = 26 * [False]
    for c in alphabet:
        sel = c
        while c == sel or used[alphabet.index(sel)]:
            sel = random.choice(alphabet)
        scralphabet[c] = sel
        used[alphabet.index(sel)] = True
    if id not in users:
        users[id] = User(name, id)
    u = users[id]
    u.cipher = scralphabet
    u.start = time.time()
    u.dur = seconds

def read_data(collection):
    data = collection.find({})
    for result in data:
        users[result['_id']] = result['user']

@client.command()
async def say(ctx, *, message):
    if 'say.wav' in os.listdir('./assets'):
        os.remove('./assets/say.wav')
    tts = gTTS(message)
    tts.save('./assets/say.wav')
    voice = ctx.guild.voice_client
    if voice:
        if voice.is_playing():
            voice.stop()
    # channel = client.get_channel(ctx.channel.id)
    channel = ctx.message.author.voice.channel
    # print(channel)
    try:
        # await client.join_voice_channel(channel)
        await channel.connect()
        await asyncio.sleep(1)
    except Exception as e:
        print(e)
        await ctx.guild.get_member(int(os.environ.get('BOT_ID'))).move_to(channel)
    voice = ctx.guild.voice_client
    voice.play(discord.FFmpegPCMAudio('./assets/say.wav'))
    voice.volume = 70

def read_games():
    global games
    global my_games
    with open('games.json', 'r') as f:
        games_list = json.load(f)
    for game in games_list:
        if games_list[game] not in games:
            games.append(games_list[game])
    with open('my_games.json', 'r') as f:
        games_list = json.load(f)
    for game in games_list:
        if games_list[game] not in my_games:
            my_games.append(games_list[game])
    # print(games)
# @tasks.loop(seconds=60)
@tasks.loop(minutes=7)
async def add_games():
    global games
    for user in client.get_all_members():
        # print(user.name, type(user.status), type(discord.Status.offline))
        # if isinstance(user.activity, discord.Game):
        #     print(user.activity.name)
        #     break
        if user.status != discord.Status.offline and user.activity and user.activity.type == discord.ActivityType.playing and not user.bot:
            name = user.activity.name
            # print(name)
            if name not in games:
                games.append(user.activity.name)
    with open('games.json', 'r') as f:
        data = json.load(f)
    count = 1
    # int_keys = [int(k) for k in data]
    size = len(data)
    for i in range(size, len(games)):
        data[size + count] = games[i]
        count += 1
    with open('games.json', 'w') as f:
        json.dump(data, f, indent=4)

@client.command()
@commands.check(special_check)
async def force(ctx):
    # global users
    curr_time, secs = datetime.datetime.now(), time.time()
    pacific = pytz.timezone('US/Pacific')
    loc_dt = pacific.localize(curr_time)
    fmt = '%Y-%m-%d %H:%M:%S %Z%z'
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
            try:
                collection.insert_one(post)
            except Exception as e:
                print(e)


    print('(Forced) Update #' + str(count) + ' at ' + loc_dt.strftime(fmt))
# @tasks.loop(seconds=10)
@tasks.loop(minutes=30)
async def change_game():
    choices = list(dict.fromkeys(games + my_games))
    # print(choices)
    if client.activity:
        sel = client.activity.name
        while sel == client.activity.name:
            sel = random.choice(choices)
        await client.change_presence(activity=discord.Game(sel))
    else:
        await client.change_presence(activity=discord.Game(random.choice(choices)))

@client.command()
async def flip(ctx):
    # embed = discord.Embed(color=discord.Color(0))
    if random.randint(0, 1) == 1:
        await ctx.send('**Heads!**', file=discord.File('./assets/heads.png'))
        # embed.set_author(name='Heads!')
        # embed.set_image(url='https://github.com/LarynQi/SpaceBot/blob/master/assets/heads.png')
        # await ctx.send(embed=embed)
    else:
        await ctx.send('**Tails!**', file=discord.File('./assets/tails.png'))

die = ('\u2680', '\u2681', '\u2682', '\u2683', '\u2684', '\u2685')
@client.command()
async def roll(ctx, n=1):
    total = 0
    result = ' rolled a **'
    for _ in range(n):
        roll = random.randint(1, 6)
        if total:
            result += ' and a **' + str(roll) + '**'
        else:
            result += str(roll) + '**'
        total += roll
    if n == 1:
        msg = await ctx.send(f'**{ctx.message.author.name}** {result}')
        # await msg.add_reaction(die[roll - 1])
        await msg.add_reaction('\U0001F3B2')
    else:
        msg = await ctx.send(f'**{ctx.message.author.name}** {result}\ntotaling to **{str(total)}**')
        await msg.add_reaction('\U0001F3B2')
    update_score(ctx.author, total)


@client.command()
async def scoreboard(ctx, n=3):
    global scores
    top = []
    top_scores = [v[1] for v in scores.values()]
    top_scores.sort(reverse=True)
    members = ctx.guild.members
    result = ''
    seen = set()
    # print(scores)
    # print(top_scores)
    # print(members)
    # if n > len(members):
    #     n = len(members)
    if n > len(scores):
        n = len(scores)
    for i in range(n):
        score = top_scores[i]
        # for m in members:
        #     if not m.bot and m.id in scores and scores[m.id][1] == score and m.id not in seen:
        #         result += f'{str(1 + i)}. **{m.name}** with **{score}**\n'
        #         print('here')
        #         seen.add(m.id) 
        #         break
        for u in scores:
            if scores[u][1] == score:
                result += f'{str(1 + i)}. **{scores[u][0]}** with **{score}**\n'
                # print('here')
                seen.add(u) 
                break
    await ctx.send(result)

def load_scores():
    global scores
    with open('rolls.json', 'r') as f:
        data = json.load(f)
    for u in data:
        scores[u] = data[u]

def update_score(user, score):
    global scores
    if score > scores.get(user, 0):
        scores[user.id] = (user.name, score)
    with open('rolls.json', 'w') as f:
        json.dump(scores, f, indent=4)


        
client.run(os.environ.get('BOT_KEY'))
